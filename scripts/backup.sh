#!/bin/bash
# Backup: copy personal vault data from VPS to local via SSH
# Usage: bash scripts/backup.sh

set -e

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
VAULT_DIR="$PROJECT_DIR/vault"
REMOTE_HOST="brain"
REMOTE_PATH="/home/agent-second-brain/vault"

# Directories not tracked by git (personal data)
DIRS=(
    "daily"
    "thoughts"
    "contacts"
    "finances"
    "attachments"
    "business"
    "projects"
    ".session"
    ".sessions"
    ".graph"
)

echo "=== Backup from $REMOTE_HOST:$REMOTE_PATH ==="
echo "=== To: $VAULT_DIR ==="
echo ""

mkdir -p "$VAULT_DIR"

for dir in "${DIRS[@]}"; do
    echo -n "  $dir ... "
    mkdir -p "$VAULT_DIR/$dir"

    if command -v rsync &>/dev/null; then
        rsync -az --delete \
            "$REMOTE_HOST:$REMOTE_PATH/$dir/" \
            "$VAULT_DIR/$dir/" \
            && echo "OK" \
            || echo "SKIP (not found on remote)"
    else
        scp -r -q "$REMOTE_HOST:$REMOTE_PATH/$dir/." "$VAULT_DIR/$dir/" \
            && echo "OK" \
            || echo "SKIP (not found on remote)"
    fi
done

echo ""
echo "=== Backup done ==="
