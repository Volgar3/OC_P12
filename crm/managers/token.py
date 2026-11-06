"""Accès au token de connexion (fichier `.token` à la racine du projet)."""

from pathlib import Path

TOKEN_FILE = Path(__file__).resolve().parents[2] / ".token"


class TokenManager:
    """Lecture et écriture du token dans le fichier `.token`."""

    def __init__(self, path=TOKEN_FILE):
        self.path = path

    def save(self, token):
        """Écrit le token, lisible uniquement par son propriétaire."""
        self.path.write_text(token)
        self.path.chmod(0o600)

    def load(self):
        """Retourne le token enregistré, ou None s'il n'y en a pas."""
        if not self.path.exists():
            return None
        return self.path.read_text().strip()

    def delete(self):
        """Supprime le token (déconnexion)."""
        self.path.unlink(missing_ok=True)
