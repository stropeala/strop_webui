# Import CryptContext, which manages password hashing settings
# and makes it easy to hash or verify passwords
from passlib.context import CryptContext


# Create a CryptContext object that defines how passwords should be hashed and verified
#
# This setup uses the Argon2 hashing algorithm which is one of the most secure password hashing methods available today
pwd_context = CryptContext(
    schemes=['argon2'],           # Only allow Argon2 hashing
    default='argon2',             # Use Argon2 by default


    # ---- Argon2 parameters ----
    # These settings adjust the security level:
    # - memory_cost: how much RAM the hashing uses (higher = more secure)
    # - parallelism: how many CPU threads are used
    # - time_cost: how many rounds the hashing performs
    argon2__memory_cost=19456,    # Amount of RAM used by the hash function
    argon2__parallelism=2,        # Number of CPU threads used
    argon2__time_cost=2,          # How many hash iterations to run
)