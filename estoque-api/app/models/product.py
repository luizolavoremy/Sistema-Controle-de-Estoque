from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime, CheckConstraint, Boolean
from sqlalchemy.sql import func
from app.database import Base


class Product(Base):

    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    stock_quantity = Column(Integer, nullable=False, default=0)
    category_id = Column(Integer, ForeignKey("categories.id"))
    version = Column(Integer, nullable=False, default=0)

    # SOFT DELETE: em vez de apagar o produto de verdade (o que
    # quebraria o histórico de movimentações ligado a ele), a gente
    # só marca como inativo. True = visível/ativo, False = "apagado".
    is_active = Column(Boolean, nullable=False, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        CheckConstraint("price >= 0", name="check_price_nao_negativo"),
        CheckConstraint("stock_quantity >= 0", name="check_stock_nao_negativo"),
    )
