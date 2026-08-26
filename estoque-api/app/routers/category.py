# Este arquivo define as rotas (endereços) da API relacionadas a categorias.
# Ex: POST /categories, GET /categories, etc.

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryOut

# "router" é como uma mini-API só pra categorias.
# Depois a gente conecta ela na aplicação principal (main.py)
router = APIRouter(prefix="/categories", tags=["categories"])


# ==========================================
# CRIAR uma categoria nova
# ==========================================
@router.post("/", response_model=CategoryOut)
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    # "category" já chega aqui validado pelo Pydantic (CategoryCreate)
    # Agora criamos o objeto do SQLAlchemy (a linha que vai pro banco)
    new_category = Category(name=category.name, description=category.description)

    db.add(new_category)      # prepara pra salvar
    db.commit()                # salva de verdade no banco
    db.refresh(new_category)   # atualiza o objeto com o id que o banco gerou

    return new_category  # o FastAPI converte isso pro formato CategoryOut sozinho


# ==========================================
# LISTAR todas as categorias
# ==========================================
@router.get("/", response_model=list[CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    return db.query(Category).all()


# ==========================================
# BUSCAR uma categoria específica pelo id
# ==========================================
@router.get("/{category_id}", response_model=CategoryOut)
def get_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == category_id).first()

    if category is None:
        # se não achar, devolve erro 404 (não encontrado) com mensagem clara
        raise HTTPException(status_code=404, detail="Categoria não encontrada")

    return category


# ==========================================
# ATUALIZAR uma categoria existente
# ==========================================
@router.put("/{category_id}", response_model=CategoryOut)
def update_category(category_id: int, data: CategoryUpdate, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == category_id).first()

    if category is None:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")

    category.name = data.name
    category.description = data.description

    db.commit()
    db.refresh(category)

    return category


# ==========================================
# APAGAR uma categoria
# ==========================================
@router.delete("/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == category_id).first()

    if category is None:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")

    db.delete(category)
    db.commit()

    return {"mensagem": "Categoria apagada com sucesso"}