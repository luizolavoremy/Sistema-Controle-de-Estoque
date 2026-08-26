# Este endpoint existe só pra DEMONSTRAÇÃO: ele dispara duas "compras"
# simultâneas no mesmo produto e devolve um relatório mostrando o
# lock otimista resolvendo o conflito, ao vivo, numa única resposta.

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
    # Essa função roda numa THREAD separada (veja o run_in_threadpool
    # mais abaixo). Por isso ela abre sua PRÓPRIA sessão com o banco,
    # em vez de usar a sessão compartilhada da requisição principal --
    # é assim que simulamos duas requisições realmente independentes.
    db: Session = SessionLocal()
    try:
        product = db.query(Product).filter(Product.id == product_id).first()
        if product is None:
            return {"sucesso": False, "detalhe": "Produto não encontrado"}

        if quantity > product.stock_quantity:
            return {"sucesso": False, "detalhe": "Estoque insuficiente"}

        new_quantity = product.stock_quantity - quantity

        # O MESMO lock otimista que já usamos em /movements
        result = (
            db.query(Product)
            .filter(Product.id == product_id, Product.version == version_lida)
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
                           "'compra' já tinha alterado a versão do produto",
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
    product = db.query(Product).filter(Product.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    versao_lida = product.version
    estoque_antes = product.stock_quantity

    # As DUAS "compras" tentam levar 60% do estoque cada uma --
    # juntas, passam do total disponível, então uma delas TEM que falhar.
    quantidade_por_tentativa = max(1, int(estoque_antes * 0.6))

    # Aqui está o "disparo simultâneo" de verdade: cada chamada roda
    # numa thread própria, e o asyncio.gather espera as duas terminarem.
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
            "usando a mesma versão lida. O lock otimista garantiu que só UMA "
            "fosse aceita -- a outra foi bloqueada, evitando estoque negativo."
        ),
    }