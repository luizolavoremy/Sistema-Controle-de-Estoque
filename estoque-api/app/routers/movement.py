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
    product = (
        db.query(Product)
        .filter(Product.id == data.product_id, Product.is_active == True)
        .first()
    )
    if product is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    if data.type == MovementType.OUT and data.quantity > product.stock_quantity:
        raise HTTPException(
            status_code=400,
            detail=f"Estoque insuficiente. Disponível: {product.stock_quantity}",
        )

    if data.type == MovementType.IN:
        new_quantity = product.stock_quantity + data.quantity
    else:
        new_quantity = product.stock_quantity - data.quantity

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


# ==========================================
# NOVO: lista movimentações, opcionalmente filtradas por produto.
# Criado pra permitir que os testes provem de verdade que uma
# movimentação foi (ou não foi) criada -- antes disso, não existia
# nenhuma forma de consultar o histórico pela API.
# ==========================================
@router.get("/", response_model=list[MovementOut])
def list_movements(product_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(Movement)
    if product_id is not None:
        query = query.filter(Movement.product_id == product_id)
    return query.all()
