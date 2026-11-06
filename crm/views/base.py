"""Classe mère des vues : l'affichage commun à tous les écrans."""


class View:
    """Affichage partagé par toutes les vues."""

    def show_error(self, message):
        print(f"Erreur : {message}")
