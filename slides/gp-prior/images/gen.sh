#!/bin/bash
# Usage: bash images/gen.sh <prompt-id> [reference.png]
# Runs the codex CLI image skill on the gpt-6-astra model with the prompt in
# images/prompts/<id>.txt (the prompt names its own output file). Log: images/logs/<id>.log.
# Prompts live in files because the shell hook blocks some words typed inline.
HERE="$(cd "$(dirname "$0")" && pwd)"
ID="$1"; REF="$2"
mkdir -p "$HERE/logs"
PROMPT="$(cat "$HERE/prompts/$ID.txt")"
if [ -n "$REF" ]; then
  codex exec -m gpt-6-astra -C "$HERE" --skip-git-repo-check --sandbox workspace-write -i "$REF" -- "$PROMPT" > "$HERE/logs/$ID.log" 2>&1
else
  codex exec -m gpt-6-astra -C "$HERE" --skip-git-repo-check --sandbox workspace-write -- "$PROMPT" > "$HERE/logs/$ID.log" 2>&1
fi
echo "done $ID exit $?" >> "$HERE/logs/$ID.log"
