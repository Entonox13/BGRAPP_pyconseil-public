#!/usr/bin/env bash
#
# Publie l'état courant de la branche de dev privée vers le dépôt PUBLIC,
# en un commit de "release" propre (sans l'historique privé), puis pousse un tag
# qui déclenche la compilation (AppImage Linux / EXE Windows) via GitHub Actions.
#
# Modèle :
#   - origin (privé)      : tout l'historique de dev
#   - public (public)     : un commit propre par release + tags vX.Y.Z
#   - branche locale "public-clean" : passerelle dont l'arbre est recopié depuis main
#
# Usage :
#   scripts/publish_public.sh v1.0.0            # publie main -> public, tag v1.0.0
#   scripts/publish_public.sh v1.1.0 ma-branche # publie une autre branche source
#
set -euo pipefail

TAG="${1:-}"
SRC_BRANCH="${2:-main}"

PUBLIC_REMOTE="public"
PUBLIC_BRANCH="main"
WORK_BRANCH="public-clean"

err() { echo "❌ $*" >&2; exit 1; }

[[ -n "$TAG" ]] || err "Usage: $0 vX.Y.Z [branche_source]"
[[ "$TAG" =~ ^v[0-9] ]] || err "Le tag doit commencer par 'v' (ex: v1.0.0) pour déclencher la release CI."

# 1. Arbre de travail propre obligatoire
[[ -z "$(git status --porcelain)" ]] || err "Arbre de travail non propre : committez ou stashez d'abord."

# 2. Mémoriser la branche courante pour y revenir à la fin
START_REF="$(git symbolic-ref --quiet --short HEAD || git rev-parse HEAD)"

# 3. Se placer sur la branche de release (la créer en orpheline si elle n'existe pas)
if git show-ref --verify --quiet "refs/heads/$WORK_BRANCH"; then
  git checkout "$WORK_BRANCH"
else
  echo "ℹ️  Création de la branche orpheline '$WORK_BRANCH' (sans historique)."
  git checkout --orphan "$WORK_BRANCH"
fi

# 4. Synchroniser l'arbre EXACTEMENT sur la branche source (gère ajouts ET suppressions).
#    git rm ne touche que les fichiers suivis : .env et autres fichiers ignorés restent intacts.
git rm -rqf . >/dev/null 2>&1 || true
git checkout "$SRC_BRANCH" -- .
git add -A

# 5. Commit de release (s'il y a quelque chose à publier)
if [[ -n "$(git diff --cached --name-only)" ]] || ! git rev-parse --verify --quiet HEAD >/dev/null; then
  git commit -q -m "Release $TAG"
  echo "✅ Commit de release créé pour $TAG"
else
  echo "ℹ️  Aucun changement depuis la dernière publication (on pousse quand même le tag)."
fi

# 6. Tag (forçable si on rejoue le même tag)
git tag -f "$TAG"

# 7. Pousser branche + tag vers le dépôt public
echo "⏫ Push vers $PUBLIC_REMOTE/$PUBLIC_BRANCH ..."
git push "$PUBLIC_REMOTE" "$WORK_BRANCH:$PUBLIC_BRANCH"
git push -f "$PUBLIC_REMOTE" "$TAG"

# 8. Revenir sur la branche de dev de départ
git checkout "$START_REF"

echo ""
echo "🎉 $TAG publié sur $PUBLIC_REMOTE ($PUBLIC_BRANCH)."
echo "   GitHub Actions va compiler l'AppImage + l'EXE et créer la Release."
