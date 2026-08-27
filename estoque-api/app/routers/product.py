# Este arquivo define as rotas da API relacionadas a produtos.

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.product import Product
from app.models.user import User
from app.schemas.product import ProductCreate, ProductUpdate, ProductOut
from app.services.dependencies import get_current_user

router = APIRouter(prefix="/products", tags=["products"])


@router.post("/", response_model=ProductOut)
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    new_product = Product(
        name=product.name,
        description=product.description,
        price=product.price,
        stock_quantity=product.stock_quantity,
        category_id=product.category_id,
        version=0,
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return new_product


# ==========================================
# LISTAR -- agora só mostra produtos ATIVOS (is_active=True).
# Produtos "apagados" (soft delete) não aparecem mais aqui.
# ==========================================
@router.get("/", response_model=list[ProductOut])
def list_products(db: Session = Depends(get_db)):
    return db.query(Product).filter(Product.is_active == True).all()


@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = (
        db.query(Product)
        .filter(Product.id == product_id, Product.is_active == True)
        .first()
    )

    if product is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    return product


@router.put("/{product_id}", response_model=ProductOut)
def update_product(
    product_id: int,
    data: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    produto_existe = (
        db.query(Product)
        .filter(Product.id == product_id, Product.is_active == True)
        .first()
    )
    if produto_existe is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    result = (
        db.query(Product)
        .filter(Product.id == product_id, Product.version == data.version)
        .update(
            {
                "name": data.name,
                "description": data.description,
                "price": data.price,
                "category_id": data.category_id,
                "version": Product.version + 1,
            },
            synchronize_session=False,
        )
    )

    if result == 0:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Este produto foi modificado por outra requisição. "
                   "Recarregue os dados e tente novamente.",
        )

    db.commit()
    db.refresh(produto_existe)

    return produto_existe


# ==========================================
# APAGAR -- agora é SOFT DELETE: marca is_active=False,
# em vez de apagar a linha de verdade. Isso preserva o
# histórico de movimentações ligado a esse produto.
# ==========================================
@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    product = (
        db.query(Product)
        .filter(Product.id == product_id, Product.is_active == True)
        .first()
    )

    if product is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    product.is_active = False
    db.commit()

    return {"mensagem": "Produto apagado com sucesso"}
