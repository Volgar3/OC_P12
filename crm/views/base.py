"""Classe mère des vues : l'affichage commun à tous les écrans."""

DATE_FORMAT = "%d/%m/%Y %H:%M"


class View:
    """Affichage partagé par toutes les vues."""

    def show_error(self, message):
        print(f"Erreur : {message}")

    def show_title(self, title):
        print(f"\n=== {title} ===")

    def show_list(self, title, items, format_item):
        """Affiche le titre puis une ligne par élément, mise en forme par
        `format_item` (ou « Aucun résultat. » si la liste est vide)."""
        self.show_title(title)
        if not items:
            print("Aucun résultat.")
        for item in items:
            print(format_item(item))
