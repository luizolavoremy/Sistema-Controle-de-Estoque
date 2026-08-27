# Este é o arquivo mais importante do projeto: aqui a movimentação
# de estoque acontece de verdade, com o LOCK OTIMISTA implementado.

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.product import Product
from app.models.movement import Movement, MovementType
from app.models.user import User
from app.schemas.movement import MovementCreate, MovementOut
from app.services.dependencies import get_current_user

router = APIRouter(prefix="/movements", tags=["movements"])


@router.post("/", response_model=MovementOut)
def create_movement(
    data: MovementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # ==========================================
    # PASSO 1: o produto existe E está ativo?
    #
    # CORREÇÃO: antes, essa checagem não considerava is_active --
    # um produto "apagado" (soft delete) ainda podia ser movimentado
    # por quem chamasse a API diretamente, mesmo já não aparecendo
    # na listagem/frontend. Isso é uma consequência direta de termos
    # implementado soft delete sem propagar a regra pra esse endpoint.
    # ==========================================
    product = (
        db.query(Product)
        .filter(Product.id == data.product_id, Product.is_active == True)
        .first()
    )
    if product is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    # ==========================================
    # PASSO 2: se for uma SAÍDA, tem estoque suficiente?
    # ==========================================
    if data.type == MovementType.OUT and data.quantity > product.stock_quantity:
        raise HTTPException(
            status_code=400,
            detail=f"Estoque insuficiente. Disponível: {product.stock_quantity}",
        )

    # ==========================================
    # PASSO 3: calcula o novo estoque
    # ==========================================
    if data.type == MovementType.IN:
        new_quantity = product.stock_quantity + data.quantity
    else:
        new_quantity = product.stock_quantity - data.quantity

    # ==========================================
    # PASSO 4: O LOCK OTIMISTA -- agora TAMBÉM exige is_active=True
    # nessa mesma instrução atômica. Isso é uma segunda camada de
    # proteção: mesmo que alguém desative o produto bem no meio do
    # tempo entre o PASSO 1 e esse UPDATE, a condição aqui ainda
    # bloqueia a movimentação.
    # ==========================================
    result = (
        db.query(Product)
        .filter(
            Product.id == data.product_id,
            Product.version == data.version,
            Product.is_active == True,
        )
        .update(
            {
                "stock_quantity": new_quantity,
                "version": Product.version + 1,
            },
            synchronize_session=False,
        )
    )

    if result == 0:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Este produto foi modificado por outra requisição, ou "
                   "foi desativado. Recarregue os dados e tente novamente.",
        )

    # ==========================================
    # PASSO 5: registra a movimentação no histórico
    # ==========================================
    new_movement = Movement(
        product_id=data.product_id,
        user_id=current_user.id,
        type=data.type,
        quantity=data.quantity,
    )

    db.add(new_movement)
    db.commit()
    db.refresh(new_movement)

    return new_movement
