# Ansible — Prod Deploy (dts-cryptobot.fr)

Configures the OVH VPS and deploys cryptobot-fin via GitHub Actions.

## Layout

```
infra/ansible/
├── ansible.cfg
├── group_vars/vps.yml         # domain, app_services, system config
├── inventories/
│   ├── production.ini         # ${VPS_HOST} env-driven
│   └── production.ini.example # template
├── playbooks/
│   ├── provision.yml          # ONE-TIME (fresh VPS) — apt, docker, nginx, fail2ban, ufw
│   ├── ssl.yml                # ONE-TIME (fresh VPS) — Let's Encrypt cert via --webroot
│   ├── deploy.yml             # RECURRING — 2 plays: app sync + nginx vhost setup
│   └── backup.yml             # STUB iter 1 — tar data/ dir
└── templates/
    ├── jail.local.j2          # fail2ban
    ├── nginx-host.conf.j2     # /etc/nginx/nginx.conf
    ├── nginx-vhost.conf.j2    # cryptobot vhost (proxy → 8000/8501)
    ├── nginx-proxy-params.conf.j2  # /etc/nginx/snippets/proxy-params.conf
    └── sshd_config.j2         # SSH hardening
```

## One-Time Setup (VPS déjà provisionné, cas courant)

Le VPS OVH est déjà provisionné (docker, nginx, fail2ban, ufw, cert Let's Encrypt en place).
**Tu ne lances PAS `provision.yml` ni `ssl.yml`.** Tu fais juste le cleanup de l'ancien code + tu pushes le `.env`.

### 1. Cleanup ancien code sur le VPS

```bash
ssh ubuntu@<VPS_IP>

# Identifier l'ancien dossier
ls -la ~/
docker ps -a

# Stopper l'ancien (backup déjà sur la branche agent/backup-prod-2026-05-27)
cd ~/<ancien-dossier>
docker compose down -v --remove-orphans
cd ~

# Supprimer l'ancien dossier
\rm -rf ~/<ancien-dossier>

# Créer le nouveau dossier vide (sera populé par rsync au premier deploy)
mkdir -p ~/cryptobot
```

### 2. Pousser le .env de prod

```bash
scp .env.prod ubuntu@<VPS_IP>:/home/ubuntu/cryptobot/.env
```

### 3. Configurer les GitHub secrets

Repo Settings → Environments → `production` :

| Secret | Valeur |
|---|---|
| `VPS_HOST` | IP publique OVH |
| `VPS_SSH_KEY` | clé privée ed25519 du user `ubuntu` |

### 4. (Optionnel) Vérifier le cert SSL existant

```bash
ssh ubuntu@<VPS_IP> 'sudo certbot certificates'
```

Le cert pour `dts-cryptobot.fr` doit être listé. Si auto-renew pas configuré :

```bash
ssh ubuntu@<VPS_IP> 'sudo crontab -l | grep certbot'
```

Si vide, ajouter (one-shot) :

```bash
ssh ubuntu@<VPS_IP> "echo '0 2 * * * certbot renew --quiet --post-hook \"systemctl reload nginx\"' | sudo crontab -"
```

## Recurring Deploys

Triggered automatically on push to `main` by `.github/workflows/deploy.yml` :

1. CI gate (lint + tests + docker build) — `ci.yml` reused
2. Runner installs `ansible-core` + collections + configures SSH (uses `VPS_SSH_KEY` secret)
3. `ansible-lint` (non-blocking warnings)
4. `ansible-playbook playbooks/deploy.yml` runs **2 plays**:
   - **Play 1** (no escalation) : rsync repo → `/home/ubuntu/cryptobot/`, vérifie `.env`, exécute `scripts/deploy.sh` (compose build + up -d + healthcheck poll)
   - **Play 2** (`become: true`) : idempotent — template du vhost nginx `/etc/nginx/sites-available/cryptobot.conf` + symlink sites-enabled, suppression auto des anciens vhosts pour `dts-cryptobot.fr`, `nginx -t` strict, reload
5. External smoke test : `curl https://dts-cryptobot.fr/health` depuis le runner

Manual trigger : `gh workflow run "Deploy to VPS"`.

## Rollback

SSH au VPS et pin à un commit précédent :

```bash
ssh ubuntu@<VPS_IP>
cd /home/ubuntu/cryptobot
git log --oneline -10
git reset --hard <previous-sha>
bash scripts/deploy.sh
```

## Fresh VPS Bootstrap (rare, premier provisioning)

Pour un VPS vierge, dans cet ordre :

```bash
export VPS_HOST=<IP>
cd infra/ansible
ansible-playbook -i inventories/production.ini playbooks/provision.yml --ask-become-pass
ansible-playbook -i inventories/production.ini playbooks/ssl.yml
scp .env.prod ubuntu@$VPS_HOST:/home/ubuntu/cryptobot/.env
```

## Out of Scope (iter 1)

- TimescaleDB / MinIO / Prometheus / Grafana services (not in current docker-compose.yml)
- Real DB backup (`backup.yml` is a stub — tars `data/` dir only)
- Ansible Vault for `.env` (manual scp for now)
- Staging environment

See `.omc/plans/cb-master-roadmap.md` Phase 4 for deferred items.
