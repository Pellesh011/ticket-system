from app.infrastructure.security.password import hash_password, verify_password


class PasswordService:
    async def hash(self, password: str) -> str:
        return await hash_password(password)

    async def verify(self, plain_password: str, hashed_password: str) -> bool:
        return await verify_password(plain_password, hashed_password)
