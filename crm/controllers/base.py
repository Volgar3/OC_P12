"""Classe mère des contrôleurs : la gestion du token et des permissions commune à
tous."""

from datetime import datetime, timedelta, timezone
from functools import wraps

import jwt

from crm.database import get_env
from crm.exceptions import AuthenticationError
from crm.managers.token import TokenManager
from crm.managers.user import UserManager

JWT_ALGORITHM = "HS256"
TOKEN_LIFETIME = timedelta(hours=1)

# Permission -> action en français, pour le message de refus
PERMISSION_LABELS = {
    "read_clients": "consulter les clients",
    "read_contracts": "consulter les contrats",
    "read_events": "consulter les événements",
    "create_own_client": "créer un client",
    "update_own_client": "modifier un client",
    "update_own_contract": "modifier un contrat",
    "create_event": "créer un événement",
    "create_contract": "créer un contrat",
    "update_contract": "modifier un contrat",
    "update_event": "modifier un événement",
    "update_own_event": "modifier un événement",
    "create_user": "créer un utilisateur",
    "update_user": "modifier un utilisateur",
    "delete_user": "supprimer un utilisateur",
}


def require_permission(permission):
    """Décorateur : n'exécute la méthode que si le collaborateur connecté a
    `permission` ; sinon la vue affiche pourquoi et la méthode retourne None."""

    def decorator(method):
        @wraps(method)
        def wrapper(self, *args, **kwargs):
            if not self.authorize(permission):
                return None
            return method(self, *args, **kwargs)

        return wrapper

    return decorator


class Controller:
    """Crée et vérifie le token de connexion, puis contrôle les permissions."""

    def __init__(self, session):
        self.tokens = TokenManager()
        self.users = UserManager(session)
        self.current_user = None

    def create_token(self, user):
        """Retourne un token JWT signé avec JWT_SECRET, valable TOKEN_LIFETIME."""
        payload = {
            "sub": str(user.id),
            "group": user.group.name,
            "exp": datetime.now(timezone.utc) + TOKEN_LIFETIME,
        }
        return jwt.encode(payload, get_env("JWT_SECRET"), algorithm=JWT_ALGORITHM)

    def get_current_user(self):
        """Relit le token, le vérifie et retourne le collaborateur connecté.

        Lève AuthenticationError si le token est absent, expiré ou invalide."""
        token = self.tokens.load()
        if token is None:
            raise AuthenticationError("vous n'êtes pas connecté : lancez login.")
        try:
            payload = jwt.decode(
                token, get_env("JWT_SECRET"), algorithms=[JWT_ALGORITHM]
            )
        except jwt.ExpiredSignatureError:
            raise AuthenticationError(
                "session expirée : reconnectez-vous avec login."
            ) from None
        except jwt.InvalidTokenError:
            raise AuthenticationError(
                "session invalide : reconnectez-vous avec login."
            ) from None
        user = self.users.get_by_id(int(payload["sub"]))
        if user is None:
            raise AuthenticationError("ce compte n'existe plus : reconnectez-vous.")
        return user

    def authorize(self, permission):
        """Retourne True si le collaborateur connecté a `permission` (et le garde
        dans `self.current_user`), sinon affiche pourquoi et retourne False."""
        try:
            user = self.get_current_user()
        except AuthenticationError as error:
            self.view.show_error(error)
            return False
        if permission not in [p.name for p in user.group.permissions]:
            action = PERMISSION_LABELS.get(permission, permission)
            self.view.show_error(f"vous n'avez pas les droits de {action}.")
            return False
        self.current_user = user
        return True
