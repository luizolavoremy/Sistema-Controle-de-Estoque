# Este endpoint existe so pra DEMONSTRACAO: ele dispara duas "compras"
# simultaneas no mesmo produto e devolve um relatorio mostrando o
# lock otimista resolvendo o conflito, ao vivo, numa unica resposta.

import asyncio
from fastapi import APIRouter, Depends, HTTPException
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.orm import Session

from app.database import SessionLocal, get_db
from app.models.product import Product
from app.models.movement import Movement, MovementType
from app.models.user import User
from app.services.dependencies import get_current_user

router = APIRouter(prefix="/demo", tags=["demo"])


def _tentar_compra(product_id: int, quantity: int, version_lida: int, user_id: int) -> dict:
    db: Session = SessionLocal()
    try:
        # CORRECAO: adicionado is_active=True aqui tambem -- esse
        # arquivo tem sua PROPRIA copia da logica de movimentacao
        # (em vez de reusar a de /movements), entao a correcao de
        # soft delete precisa ser aplicada aqui separadamente.
        product = (
            db.query(Product)
            .filter(Product.id == product_id, Product.is_active == True)
            .first()
        )
        if product is None:
            return {"sucesso": False, "detalhe": "Produto nao encontrado ou inativo"}

        if quantity > product.stock_quantity:
            return {"sucesso": False, "detalhe": "Estoque insuficiente"}

        new_quantity = product.stock_quantity - quantity

        result = (
            db.query(Product)
            .filter(
                Product.id == product_id,
                Product.version == version_lida,
                Product.is_active == True,
            )
            .update(
                {"stock_quantity": new_quantity, "version": Product.version + 1},
                synchronize_session=False,
            )
        )

        if result == 0:
            db.rollback()
            return {
                "sucesso": False,
                "detalhe": "Bloqueado pelo lock otimista -- outra "
                           "'compra' ja tinha alterado a versao do produto",
            }

        db.add(Movement(
            product_id=product_id,
            user_id=user_id,
            type=MovementType.OUT,
            quantity=quantity,
        ))
        db.commit()

        return {"sucesso": True, "detalhe": f"Compra aprovada, {quantity} unidade(s) vendida(s)"}
    finally:
        db.close()


@router.post("/concurrency-test/{product_id}")
async def demo_concorrencia(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # CORRECAO: mesma checagem de is_active aplicada aqui na rota
    # principal, nao so dentro do _tentar_compra.
    product = (
        db.query(Product)
        .filter(Product.id == product_id, Product.is_active == True)
        .first()
    )
    if product is None:
        raise HTTPException(status_code=404, detail="Produto nao encontrado ou inativo")

    versao_lida = product.version
    estoque_antes = product.stock_quantity

    quantidade_por_tentativa = max(1, int(estoque_antes * 0.6))

    resultado_1, resultado_2 = await asyncio.gather(
        run_in_threadpool(_tentar_compra, product_id, quantidade_por_tentativa, versao_lida, current_user.id),
        run_in_threadpool(_tentar_compra, product_id, quantidade_por_tentativa, versao_lida, current_user.id),
    )

    db.refresh(product)

    return {
        "produto": product.name,
        "estoque_antes": estoque_antes,
        "quantidade_tentada_por_compra": quantidade_por_tentativa,
        "compra_1": resultado_1,
        "compra_2": resultado_2,
        "estoque_depois": product.stock_quantity,
        "explicacao": (
            "As duas compras tentaram descontar do estoque ao mesmo tempo, "
            "usando a mesma versao lida. O lock otimista garantiu que so UMA "
            "fosse aceita -- a outra foi bloqueada, evitando estoque negativo."
        ),
    }
