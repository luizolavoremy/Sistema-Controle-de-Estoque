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
    current_user: User = Depends(get_current_user),  # exige login
):
    # ==========================================
    # PASSO 1: o produto existe?
    # ==========================================
    product = db.query(Product).filter(Product.id == data.product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    # ==========================================
    # PASSO 2: se for uma SAÍDA, tem estoque suficiente?
    # (checar isso ANTES do lock evita mensagem de erro confusa
    # pra quem só queria comprar mais do que existe)
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
    else:  # OUT
        new_quantity = product.stock_quantity - data.quantity

    # ==========================================
    # PASSO 4: O LOCK OTIMISTA DE VERDADE.
    #
    # Em vez de fazer "ler o produto -> depois escrever", que tem
    # uma brecha de tempo entre os dois passos (é exatamente aí que
    # a condição de corrida acontece), a gente faz um UPDATE que já
    # INCLUI a checagem de versão na mesma operação atômica do banco:
    #
    #   "Atualiza o produto ... MAS SÓ SE a versão ainda for a que
    #    a pessoa leu (data.version)"
    #
    # Isso é uma ÚNICA instrução pro banco -- não dá brecha de tempo
    # pra outra requisição se meter no meio.
    # ==========================================
    result = (
        db.query(Product)
        .filter(Product.id == data.product_id, Product.version == data.version)
        .update(
            {
                "stock_quantity": new_quantity,
                "version": Product.version + 1,
            },
            synchronize_session=False,
        )
    )

    # "result" é quantas linhas foram realmente alteradas.
    # Se for 0, significa que a condição "id=X AND version=Y" não
    # bateu com nenhuma linha -- ou seja, a versão já tinha mudado
    # (outra pessoa mexeu no produto entre a hora que este usuário
    # leu e a hora que ele mandou essa requisição).
    if result == 0:
        db.rollback()  # desfaz qualquer coisa pendente nessa sessão
        raise HTTPException(
            status_code=409,  # 409 = Conflict, o código certo pra isso
            detail="Este produto foi modificado por outra requisição. "
                   "Recarregue os dados e tente novamente.",
        )

    # ==========================================
    # PASSO 5: se chegou até aqui, o UPDATE foi aceito.
    # Agora registramos a movimentação no histórico.
    # ==========================================
    new_movement = Movement(
        product_id=data.product_id,
        user_id=current_user.id,  # pega do token, não do que a pessoa mandou
        type=data.type,
        quantity=data.quantity,
    )

    db.add(new_movement)
    db.commit()
    db.refresh(new_movement)

    return new_movement