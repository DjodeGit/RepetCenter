# TODO — Reorganisation UI (input.css, templates, js)

## Étape 1 — Analyse & charte
- [ ] Valider contenu actuel de `static/src/input.css` (theme + composants existants)
- [ ] Extraire les composants récurrents (boutons, inputs, cards, table, pagination, filter bar)

## Étape 2 — Nouveau `input.css`
- [ ] Remplacer palette existante par la charte demandée:
  - Bleu Royal #1A3A6E
  - Bleu Académique #2A5298
  - Blanc Pur #FFFFFF
  - Or Prestige #C9A227
  - Gris Perle #F5F7FA
  - Gris Ardoise #6B7A95
- [ ] Ajouter classes/variables UI (uniformes) et tailles de police professionnelles
- [ ] S’assurer que les templates n’ont plus de `<style>` et utilisent ces classes

## Étape 3 — Page login (layout 50/50)
- [ ] Mettre `templates/accounts/login.html` avec layout 50/50
- [ ] Alignements: textes à gauche plus grands et cohérents avec la charte
- [ ] Supprimer `<style>` et convertir en classes Tailwind + classes via `@apply` dans `input.css`

## Étape 4 — JS hors templates
- [x] Créer `static/js/auth/login.js` (togglePassword + auto-hide alerts)
- [ ] Créer `static/js/layout/sidebar-menus.js` (toggle menus base)
- [ ] Supprimer les `<script>` inline de `login.html` et `base.html`
- [ ] Charger via `<script src="/static/js/...">` dans `base.html`

## Étape 5 — Pagination/Filtre harmonisés
- [ ] Inspecter tous les partials pagination/filtre
- [ ] Remplacer par une structure identique:
  - Boutons recherche/filtre
  - Bouton **Réinitialiser** visible après action
- [ ] Mettre classes identiques partout

## Étape 6 — Nettoyage templates & cohérence
- [ ] Parcourir pages list/CRUD pour uniformiser (apprenants/enseignants/centre/accounts)
- [ ] S’assurer absence de `<style>` et réduction des classes ad-hoc

## Étape 7 — Build / test
- [ ] Construire `static/src/output.css` si nécessaire
- [ ] Tester login, pagination, filtres

