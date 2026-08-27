# Este arquivo define as rotas (endereços) da API relacionadas a categorias.

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.category import Category
from app.models.user import User
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryOut
from app.services.dependencies import get_current_user

router = APIRouter(prefix="/categories", tags=["categories"])


# ==========================================
# LISTAR e BUSCAR continuam ABERTAS -- qualquer um pode
# ver quais categorias existem, mesmo sem estar logado.
# ==========================================
@router.get("/", response_model=list[CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    return db.query(Category).all()


@router.get("/{category_id}", response_model=CategoryOut)
def get_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == category_id).first()

    if category is None:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")

    return category


# ==========================================
# CRIAR, ATUALIZAR e APAGAR agora exigem login --
# mesma proteção que produtos e movimentações já tinham.
# CORREÇÃO: essas 3 rotas foram criadas no Passo 3, ANTES da gente
# implementar JWT no Passo 4, e nunca receberam a proteção depois.
# ==========================================
@router.post("/", response_model=CategoryOut)
def create_category(
    category: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    new_category = Category(name=category.name, description=category.description)

    db.add(new_category)
    db.commit()
    db.refresh(new_category)

    return new_category


@router.put("/{category_id}", response_model=CategoryOut)
def update_category(
    category_id: int,
    data: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    category = db.query(Category).filter(Category.id == category_id).first()

    if category is None:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")

    category.name = data.name
    category.description = data.description

    db.commit()
    db.refresh(category)

    return category


@router.delete("/{category_id}")
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    category = db.query(Category).filter(Category.id == category_id).first()

    if category is None:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")

    db.delete(category)
    db.commit()

    return {"mensagem": "Categoria apagada com sucesso"}
