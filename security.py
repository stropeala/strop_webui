from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes = ['argon2'],
    default = 'argon2',
    argon2__memory_cost = 19456,
    argon2__parallelism = 2,
    argon2__time_cost = 2,
)