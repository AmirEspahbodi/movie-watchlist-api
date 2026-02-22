import bcrypt


class SecurityUtils:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        # bcrypt requires bytes for both the password and the hash
        return bcrypt.checkpw(
            password=plain_password.encode("utf-8"),
            hashed_password=hashed_password.encode("utf-8"),
        )

    @staticmethod
    def get_password_hash(password: str) -> str:
        # Generate salt and hash the password (requires bytes)
        salt = bcrypt.gensalt()
        hashed_bytes = bcrypt.hashpw(password.encode("utf-8"), salt)

        # Decode back to a string so it can be safely stored in the database
        return hashed_bytes.decode("utf-8")
