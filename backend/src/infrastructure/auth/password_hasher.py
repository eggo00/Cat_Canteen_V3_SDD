"""Password hashing utilities using bcrypt."""
from passlib.context import CryptContext

# Configure password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class PasswordHasher:
    """Handler for password hashing and verification."""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a plain text password.

        Args:
            password: Plain text password

        Returns:
            str: Hashed password
        """
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a plain text password against a hashed password.

        Args:
            plain_password: Plain text password to verify
            hashed_password: Hashed password from database

        Returns:
            bool: True if password matches, False otherwise
        """
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def needs_rehash(hashed_password: str) -> bool:
        """Check if a hashed password needs to be rehashed.

        Useful for updating passwords when the hashing algorithm is upgraded.

        Args:
            hashed_password: Hashed password to check

        Returns:
            bool: True if password needs rehashing
        """
        return pwd_context.needs_update(hashed_password)
