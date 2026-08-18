import bcrypt


def hash_password(plain_password):
    """Hash a plain text password using bcrypt."""
    return bcrypt.hashpw(plain_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def check_password(plain_password, hashed_password):
    """Verify a plain text password against its bcrypt hash."""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
