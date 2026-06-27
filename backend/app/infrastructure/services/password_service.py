from app.core.services.password_service import IPasswordService
from app.infrastructure.security.password import hash_password, verify_password


class PasswordService:
    def hash(self, password: str) -> str:
        return hash_password(password)

    def verify(self, plain_password: str, hashed_password: str) -> bool:
        return verify_password(plain_password, hashed_password)
