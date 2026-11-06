"""Classe mère des contrôleurs : la gestion du token commune à tous."""

from datetime import datetime, timedelta, timezone

import jwt

from crm.database import get_env
from crm.managers.token import TokenManager

JWT_ALGORITHM = "HS256"
TOKEN_LIFETIME = timedelta(hours=1)


class Controller:
    """Crée le token de connexion et le confie au TokenManager."""

    def __init__(self):
        self.tokens = TokenManager()

    def create_token(self, user):
        """Retourne un token JWT signé avec JWT_SECRET, valable TOKEN_LIFETIME."""
        payload = {
            "sub": str(user.id),
            "group": user.group.name,
            "exp": datetime.now(timezone.utc) + TOKEN_LIFETIME,
        }
        return jwt.encode(payload, get_env("JWT_SECRET"), algorithm=JWT_ALGORITHM)
