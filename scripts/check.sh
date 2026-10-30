#!/bin/sh
# Vérifie que le code est propre (Ruff).
# Lancé automatiquement avant chaque `git push` (voir .githooks/pre-push),
# et utilisable à la main : ./scripts/check.sh
set -e
cd "$(git rev-parse --show-toplevel)"

# Python du projet : venv activé, sinon env/, venv/ ou .venv/
if [ -n "$VIRTUAL_ENV" ]; then
    PY="$VIRTUAL_ENV/bin/python"
else
    for dir in env venv .venv; do
        if [ -x "$dir/bin/python" ]; then PY="$dir/bin/python"; break; fi
    done
fi
if [ -z "$PY" ]; then
    echo "Environnement virtuel introuvable (env/, venv/ ou .venv/)." >&2
    exit 1
fi

echo "1/2 Ruff : règles de code (PEP 8, imports, nommage, bugs fréquents)"
"$PY" -m ruff check .
echo "2/2 Ruff : formatage"
"$PY" -m ruff format --check .
echo "Tout est propre."
