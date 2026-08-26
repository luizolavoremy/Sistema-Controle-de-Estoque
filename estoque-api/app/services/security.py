# Este arquivo cuida de duas coisas relacionadas a senha:
# 1) transformar a senha digitada em um hash (embaralhado, irreversível)
# 2) conferir se uma senha digitada bate com o hash salvo no banco
#
# Usamos a biblioteca "bcrypt" direto (sem passar pelo passlib),
# porque o passlib tem um bug de compatibilidade com versões
# mais novas do bcrypt.

import bcrypt


def hash_password(password: str) -> str:
    # bcrypt trabalha com bytes, não com texto puro -- por isso o .encode()
    # Gera um "salt" (tempero aleatório) e embaralha a senha com ele.
    password_bytes = password.encode("utf-8")
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())

    # Salvamos como texto (str) no banco, não como bytes
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Confere se a senha digitada, quando embaralhada, bate com o hash salvo
    plain_bytes = plain_password.encode("utf-8")
    hashed_bytes = hashed_password.encode("utf-8")

    return bcrypt.checkpw(plain_bytes, hashed_bytes)