# Este arquivo define as rotas da API relacionadas a produtos.

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.product import Product
from app.models.user import User
from app.schemas.product import ProductCreate, ProductUpdate, ProductOut
from app.services.dependencies import get_current_user

router = APIRouter(prefix="/products", tags=["products"])


# ==========================================
# CRIAR um produto novo -- PROTEGIDO: exige login
# ==========================================
@router.post("/", response_model=ProductOut)
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  # <-- exige token válido
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
# LISTAR todos os produtos -- ABERTO: qualquer um pode ver
# ==========================================
@router.get("/", response_model=list[ProductOut])
def list_products(db: Session = Depends(get_db)):
    return db.query(Product).all()


# ==========================================
# BUSCAR um produto específico -- ABERTO
# ==========================================
@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()

    if product is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    return product


# ==========================================
# ATUALIZAR um produto -- PROTEGIDO: exige login
# ==========================================
@router.put("/{product_id}", response_model=ProductOut)
def update_product(
    product_id: int,
    data: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  # <-- exige token válido
):
    product = db.query(Product).filter(Product.id == product_id).first()

    if product is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    product.name = data.name
    product.description = data.description
    product.price = data.price
    product.category_id = data.category_id
    product.version += 1

    db.commit()
    db.refresh(product)

    return product


# ==========================================
# APAGAR um produto -- PROTEGIDO: exige login
# ==========================================
@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  # <-- exige token válido
):
    product = db.query(Product).filter(Product.id == product_id).first()

    if product is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    db.delete(product)
    db.commit()

    return {"mensagem": "Produto apagado com sucesso"}