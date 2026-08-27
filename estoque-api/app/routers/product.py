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


@router.get("/", response_model=list[ProductOut])
def list_products(db: Session = Depends(get_db)):
    return db.query(Product).all()


@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()

    if product is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    return product


# ==========================================
# ATUALIZAR um produto -- PROTEGIDO + LOCK OTIMISTA
#
# CORREÇÃO IMPORTANTE: a versão anterior desse endpoint atualizava
# o produto direto (product.name = data.name, etc.) sem NUNCA
# comparar data.version com product.version. Isso significava que
# duas edições simultâneas do mesmo produto colidiam sem proteção
# nenhuma -- o mesmo problema que o lock otimista existe pra resolver,
# só que ele não estava sendo aplicado aqui.
# ==========================================
@router.put("/{product_id}", response_model=ProductOut)
def update_product(
    product_id: int,
    data: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Primeiro confirma que o produto existe de fato --
    # sem essa checagem, um id inexistente cairia direto no
    # UPDATE abaixo, que retornaria 0 linhas afetadas, e a gente
    # devolveria erro 409 (conflito) quando na verdade o certo
    # seria 404 (não encontrado). São erros diferentes!
    produto_existe = db.query(Product).filter(Product.id == product_id).first()
    if produto_existe is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    # Este é o UPDATE atômico -- o coração do lock otimista.
    # A cláusula WHERE tem DUAS condições ao mesmo tempo:
    # "esse é o produto certo" E "a versão ainda é a que a pessoa leu".
    # Se qualquer pessoa mais tiver alterado esse produto entre a
    # leitura e essa escrita, a versão no banco já não bate mais,
    # e o UPDATE não afeta NENHUMA linha -- mesmo o produto existindo.
    result = (
        db.query(Product)
        .filter(Product.id == product_id, Product.version == data.version)
        .update(
            {
                "name": data.name,
                "description": data.description,
                "price": data.price,
                "category_id": data.category_id,
                # Product.version + 1 é calculado PELO BANCO, no
                # momento exato do UPDATE -- não é um número que a
                # gente calculou em Python antes, o que evitaria
                # outro tipo sutil de condição de corrida.
                "version": Product.version + 1,
            },
            synchronize_session=False,
        )
    )

    # "result" é a quantidade de linhas que o UPDATE realmente mudou.
    # Se for 0, a condição do WHERE não bateu com nenhuma linha --
    # ou seja, a versão já tinha mudado. Rejeitamos com 409 (Conflict).
    if result == 0:
        db.rollback()  # desfaz qualquer coisa pendente nessa sessão
        raise HTTPException(
            status_code=409,
            detail="Este produto foi modificado por outra requisição. "
                   "Recarregue os dados e tente novamente.",
        )

    # Se chegou até aqui, o UPDATE foi aceito -- confirma a transação
    db.commit()

    # "produto_existe" é o objeto Python que carregamos lá em cima,
    # ANTES do update -- ele está com os dados antigos na memória.
    # db.refresh() busca ele de novo no banco, trazendo os valores
    # atualizados (nome novo, versão nova, etc.) pro objeto Python.
    db.refresh(produto_existe)

    return produto_existe


@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    product = db.query(Product).filter(Product.id == product_id).first()

    if product is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    db.delete(product)
    db.commit()

    return {"mensagem": "Produto apagado com sucesso"}
