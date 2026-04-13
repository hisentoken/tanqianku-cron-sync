---
name: hermes-gateway-troubleshooting
description: Diagnose and fix Hermes gateway service failures, Telegram polling conflicts, and systemd restart loops
category: devops
---

# Hermes Gateway Troubleshooting

## Common Failure Modes

### 1. Telegram Polling Conflict
**Symptom**: `[Telegram] Telegram polling conflict (1/3)` repeated in logs, or `Unauthorized user` despite correct config.

**Cause**: Another instance of the gateway is already running (often from a previous session or manual start).

**Diagnosis**:
```bash
hermes logs --lines 50
journalctl --user -xeu hermes-gateway.service --no-pager -n 100
ps aux | grep hermes
```

**Fix**: Find and kill the stale process:
```bash
# Find the old PID from journalctl logs (look for python processes)
kill <old_pid>
# Or kill all hermes python processes except the current one
pkill -f "hermes.*gateway" && hermes gateway start
```

### 2. Systemd Service in "failed" State (exit-code 75)
**Symptom**: `systemctl --user start hermes-gateway.service` fails with "Start request repeated too quickly" or exit-code 75.

**Cause**: Gateway crashed/restarted too many times in quick succession, and systemd put it in a failed/abort state.

**Fix**:
```bash
systemctl --user reset-failed hermes-gateway.service
systemctl --user start hermes-gateway.service
```

### 3. Gateway Running but Users Still Unauthorized
**Symptom**: Gateway is `active (running)` but users get `Unauthorized user` warnings.

**Fix**: Set the allowlist explicitly in `.env`:
```bash
# Add to ~/.hermes/.env
echo 'TELEGRAM_ALLOWED_USERS=your_user_id' >> ~/.hermes/.env
hermes gateway restart
```

The config via `hermes config set` may not be picked up correctly — adding directly to `.env` is more reliable.

## Quick Reference

```bash
# Check gateway status
hermes gateway status

# View recent logs
hermes logs --lines 30

# Full journald logs
journalctl --user -xeu hermes-gateway.service --no-pager -n 50

# Restart cleanly
systemctl --user reset-failed hermes-gateway.service
hermes gateway restart

# If all else fails, foreground debug
hermes gateway run
```

### 4. Telegram Connection Fails with `httpx.ConnectError` Behind Proxy
**Symptom**: Logs show `telegram.error.NetworkError: httpx.ConnectError:` and Telegram fails to connect, even though proxy works in terminal.

**Cause**: The systemd service does NOT inherit the user's shell environment variables (http_proxy, https_proxy, all_proxy). It runs in an isolated environment.

**Diagnosis**:
```bash
hermes logs --lines 20
# Look for: httpx.ConnectError
```

**Fix**: Edit the systemd service to include proxy environment variables:
```bash
# 1. Stop the service
systemctl --user stop hermes-gateway.service

# 2. Edit the service file to add proxy env vars
cat > ~/.config/systemd/user/hermes-gateway.service << 'EOF'
[Unit]
Description=Hermes Agent Gateway - Messaging Platform Integration
After=network.target
StartLimitIntervalSec=600
StartLimitBurst=5

[Service]
Type=simple
ExecStart=/home/user/.hermes/hermes-agent/venv/bin/python -m hermes_cli.main gateway run --replace
WorkingDirectory=/home/user/.hermes/hermes-agent
Environment="PATH=/home/user/.hermes/hermes-agent/venv/bin:..."
Environment="VIRTUAL_ENV=/home/user/.hermes/hermes-agent/venv"
Environment="HERMES_HOME=/home/user/.hermes"
Environment="http_proxy=http://127.0.0.1:7897"
Environment="https_proxy=http://127.0.0.1:7897"
Environment="all_proxy=socks5://127.0.0.1:7897"
Environment="no_proxy=localhost,127.0.0.1,192.168.0.0/16,10.0.0.0/8,172.16.0.0/12,::1"
Restart=on-failure
RestartSec=30
RestartForceExitStatus=75
KillMode=mixed
KillSignal=SIGTERM
ExecReload=/bin/kill -USR1 $MAINPID
TimeoutStopSec=60
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=default.target
EOF

# 3. Reload and start
systemctl --user daemon-reload
systemctl --user start hermes-gateway.service
```

**Alternative — set proxy in `.env`** (less reliable for systemd):
```bash
echo 'http_proxy=http://127.0.0.1:7897' >> ~/.hermes/.env
echo 'https_proxy=http://127.0.0.1:7897' >> ~/.hermes/.env
hermes gateway restart
```

### 5. Token Config Key Format
**Symptom**: `ValueError: Invalid environment variable name: 'TELEGRAM.BOT_TOKEN'`

**Cause**: Wrong format used with `hermes config set`.

**Fix**: Use underscore format, not dot:
```bash
# WRONG:
hermes config set telegram.bot_token TOKEN

# CORRECT:
hermes config set TELEGRAM_BOT_TOKEN TOKEN
```

## Key Lessons

1. **Always check for stale processes first** — the most common cause of polling conflicts
2. **Systemd can enter a "failed" state** that blocks further restarts; must `reset-failed` before starting again
3. **Direct `.env` editing is more reliable than `hermes config set`** for environment variables like `TELEGRAM_ALLOWED_USERS`
4. **Exit code 75** from the gateway is an auto-restart abort, not a config error
5. **Behind a proxy, systemd services don't inherit shell env vars** — proxy must be explicitly set in the service file Environment= directives
6. **Token config uses underscore format** (`TELEGRAM_BOT_TOKEN`), not dot format (`telegram.bot_token`)
