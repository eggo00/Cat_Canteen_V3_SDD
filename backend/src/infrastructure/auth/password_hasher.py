"""Password hashing utilities using bcrypt directly."""
import bcrypt


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
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

    # Alias for backward compatibility
    hash = hash_password

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a plain text password against a hashed password.

        Args:
            plain_password: Plain text password to verify
            hashed_password: Hashed password from database

        Returns:
            bool: True if password matches, False otherwise
        """
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )

    # Alias for backward compatibility
    verify = verify_password
