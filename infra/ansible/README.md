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
│   ├── provision.yml          # ONE-TIME — apt, docker, nginx, fail2ban, ufw
│   ├── ssl.yml                # ONE-TIME — Let's Encrypt cert via --webroot
│   ├── deploy.yml             # RECURRING — rsync repo + run scripts/deploy.sh
│   └── backup.yml             # STUB iter 1 — tar data/ dir
└── templates/
    ├── jail.local.j2          # fail2ban
    ├── nginx-host.conf.j2     # /etc/nginx/nginx.conf
    ├── nginx-vhost.conf.j2    # cryptobot vhost (proxy → 8000/8501)
    ├── nginx-proxy-params.conf.j2  # /etc/nginx/snippets/proxy-params.conf
    └── sshd_config.j2         # SSH hardening
```

## Prerequisites

1. **DNS** — A records configured BEFORE running `ssl.yml`:
   ```
   dts-cryptobot.fr.       A    <VPS_PUBLIC_IP>
   www.dts-cryptobot.fr.   A    <VPS_PUBLIC_IP>
   ```
   Verify: `dig +short dts-cryptobot.fr`

2. **GitHub secrets** — set in repo Settings → Environments → `production`:
   | Secret | Value |
   |---|---|
   | `VPS_HOST` | OVH public IP |
   | `VPS_SSH_KEY` | SSH private key (ed25519) for user `ubuntu` |

3. **Local Ansible** — for the one-time bootstrap, you need ansible installed locally:
   ```bash
   pip install "ansible-core>=2.16,<2.18"
   ansible-galaxy collection install community.docker community.general ansible.posix
   ```

## One-Time Bootstrap (owner: Jules)

Run from your laptop, NOT from GitHub Actions:

```bash
export VPS_HOST=<OVH_IP>
cd infra/ansible

# 1. Base provision (apt, docker, nginx + config, fail2ban, ufw, swap)
ansible-playbook -i inventories/production.ini playbooks/provision.yml --ask-become-pass

# 2. SSL cert (after DNS A records propagated)
ansible-playbook -i inventories/production.ini playbooks/ssl.yml

# 3. Push the application .env to the VPS (NOT versioned)
scp .env.prod ubuntu@$VPS_HOST:/home/ubuntu/cryptobot/.env
```

## Recurring Deploys

Triggered automatically on push to `main` by `.github/workflows/deploy.yml`:

1. CI gate (lint + tests + docker build) — `ci.yml` reused
2. SSH setup on runner (uses `VPS_SSH_KEY` secret)
3. `ansible-lint` (non-blocking warnings)
4. `ansible-playbook playbooks/deploy.yml` from runner →
   - rsync repo → `/home/ubuntu/cryptobot/`
   - verify `.env` exists
   - run `scripts/deploy.sh` (compose build + up -d + healthcheck poll)
5. External smoke test: `curl https://dts-cryptobot.fr/health` from runner

Manual trigger: `gh workflow run "Deploy to VPS"`.

## Rollback

SSH to VPS and pin to previous git ref:
```bash
ssh ubuntu@$VPS_HOST
cd /home/ubuntu/cryptobot
git log --oneline -10
git reset --hard <previous-sha>
bash scripts/deploy.sh
```

## Out of Scope (iter 1)

- TimescaleDB / MinIO / Prometheus / Grafana services (not in current docker-compose.yml)
- Real DB backup (backup.yml is a stub — tars data/ dir only)
- Ansible Vault for .env (manual scp for now)
- Staging environment

See `.omc/plans/cb-master-roadmap.md` Phase 4 for deferred items.
