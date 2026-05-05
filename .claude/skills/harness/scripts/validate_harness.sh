#!/usr/bin/env bash
# validate_harness.sh — Recorre los 5 checkpoints C1-C5 en un proyecto.
# Uso: validate_harness.sh [PROJECT_DIR]   (default: cwd)

set -uo pipefail
TARGET="${1:-.}"
cd "$TARGET" || { echo "[validate] no puedo entrar a $TARGET" >&2; exit 2; }

PASS=0
FAIL=0
ok()   { echo "  ✓ $1"; PASS=$((PASS+1)); }
fail() { echo "  ✗ $1"; FAIL=$((FAIL+1)); }

echo "=== validando harness en $(pwd) ==="

echo "[C1] Arnés completo"
for f in AGENTS.md CHECKPOINTS.md feature_list.json init.sh \
         progress/current.md progress/history.md \
         docs/architecture.md docs/conventions.md docs/verification.md \
         .claude/settings.json \
         .claude/agents/leader.md .claude/agents/implementer.md .claude/agents/reviewer.md; do
    [ -f "$f" ] && ok "$f" || fail "falta $f"
done
[ -x init.sh ] && ok "init.sh ejecutable" || fail "init.sh no es ejecutable"

echo "[C2] Estado coherente"
if [ -f feature_list.json ]; then
    in_progress=$(python3 -c "
import json
with open('feature_list.json') as f:
    data = json.load(f)
print(sum(1 for x in data['features'] if x['status'] == 'in_progress'))
" 2>/dev/null || echo "?")
    if [ "$in_progress" = "?" ]; then
        fail "feature_list.json mal formado"
    elif [ "$in_progress" -le 1 ]; then
        ok "max 1 feature in_progress (encontradas: $in_progress)"
    else
        fail "más de una feature in_progress: $in_progress"
    fi
fi

echo "[C3] Arquitectura (heurística)"
debug_hits=$(grep -rn -E '(^|[[:space:]])(print\(|console\.log|dbg!)' \
    --include="*.py" --include="*.ts" --include="*.js" --include="*.rs" --include="*.go" \
    src 2>/dev/null | grep -v -E '(test|spec)' | wc -l)
if [ "$debug_hits" -eq 0 ]; then
    ok "sin print/console.log/dbg! sospechosos en src/"
else
    fail "$debug_hits print/console.log/dbg! en src/ (revisa)"
fi

echo "[C4] Verificación"
if [ -d tests ] || [ -d internal ]; then
    ok "directorio de tests presente"
else
    fail "no hay tests/ ni internal/"
fi

echo "[C5] Sesión cerrada"
if [ -f progress/current.md ]; then
    cur_curso=$(grep -c 'Feature en curso:.*ninguna' progress/current.md 2>/dev/null || echo 0)
    if [ "$cur_curso" -ge 1 ]; then
        ok "current.md vacío (sesión cerrada)"
    else
        ok "current.md describe sesión activa"
    fi
fi

echo ""
echo "=== resumen: $PASS OK, $FAIL FAIL ==="
[ "$FAIL" -eq 0 ]
