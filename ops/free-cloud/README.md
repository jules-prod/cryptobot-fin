# Déploiement Free Cloud (référence — non maintenu)

Déploiement gratuit sur **Render.com + Supabase** mis en place par **Mikaël**.
Archivé ici pour conserver le travail ; **ce n'est pas le déploiement de production actuel**
(la prod tourne sur VPS via `infra/ansible/` + `docker compose`).

> ⚠️ Statut : référence historique. Les chemins (`./api/Dockerfile`, etc.) datent d'avant
> le refactor `src/` et ne sont pas garantis fonctionnels en l'état.

## Contenu

| Fichier | Rôle |
|---|---|
| `render.yaml` | Manifest Render.com (service web Docker, plan `free`, healthcheck `/health`) |
| `devcontainer/devcontainer.json` | Dev Container (environnement de dev reproductible, contribution de Mikaël) |

## Principe (Render + Supabase)

- **Render.com** héberge l'API (conteneur Docker, plan gratuit) à partir de `render.yaml`.
- **Supabase** fournit la base PostgreSQL managée gratuite (`CRYPTO_BOT_DB_URL`).
- Les secrets (`BINANCE_API_KEY`, `COINMARKETCAP_API_KEY`, SMTP…) se saisissent dans le
  dashboard Render (`sync: false`).

## Pour réutiliser (indicatif)

1. Adapter `render.yaml` aux chemins actuels (`dockerfilePath: ./src/api/Dockerfile`).
2. Créer un projet Supabase, récupérer l'URL PostgreSQL.
3. Connecter le repo à Render, renseigner les variables d'environnement.

→ Voir aussi `../local/` pour le déploiement local et `infra/` pour la prod VPS.
