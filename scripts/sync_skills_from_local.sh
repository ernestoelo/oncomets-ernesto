#!/usr/bin/env bash
# sync_skills_from_local.sh
# Copies @dev-workflow and @harness from ~/.claude/skills/ on the LAPTOP
# into this repo's .claude/skills/. Run on laptop, then commit and push.
#
# Why: skills are bundled in the repo so Werner has them without needing
# the laptop's full ~/.claude/skills/ tree.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TARGET="${REPO_ROOT}/.claude/skills"
SOURCE="${HOME}/.claude/skills"

log() { printf '\033[1;34m[sync-skills]\033[0m %s\n' "$*"; }
err() { printf '\033[1;31m[sync-skills ERROR]\033[0m %s\n' "$*" >&2; }

[[ -d "${SOURCE}" ]] || { err "source not found: ${SOURCE}"; exit 1; }

mkdir -p "${TARGET}"

for skill in dev-workflow harness; do
    src="${SOURCE}/${skill}"
    dst="${TARGET}/${skill}"
    if [[ ! -d "${src}" ]]; then
        err "skill '${skill}' not in ${SOURCE} — skip"
        continue
    fi
    log "syncing ${skill}..."
    rm -rf "${dst}"
    rsync -a --exclude='.git' --exclude='__pycache__' "${src}/" "${dst}/"
    log "   ok: ${dst}"
done

log "done. don't forget to:"
log "    git add .claude/skills/"
log "    git commit -m 'feat: bundle dev-workflow and harness skills'"
log "    git push"
