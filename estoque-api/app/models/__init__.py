# Este arquivo existe só pra "juntar" todas as tabelas num lugar só.
# Assim, quando outro arquivo precisar de qualquer tabela, ele pode
# importar direto de "app.models" em vez de ficar procurando
# arquivo por arquivo.

from app.models.product import Product
from app.models.category import Category
from app.models.user import User
from app.models.movement import Movement, MovementType