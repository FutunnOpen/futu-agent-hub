#!/usr/bin/env bash
# One-time cleanup for renamed skill directories.
# `npx skills update` refreshes the new slug and leaves the old directory in place.
set -euo pipefail

OLD_SLUGS=(
  news-search
  stock-digest
  comment-sentiment
  install-opend
  capital-anomaly
  derivatives-anomaly
  technical-anomaly
  futu-capital-anomaly
  futu-derivatives-anomaly
  futu-technical-anomaly
  futuapi
  install-futu-opend
)

ROOTS=(
  "${HOME}/.agents/skills"
  "${HOME}/.claude/skills"
  "${HOME}/.codex/skills"
  "${HOME}/.cursor/skills"
)

removed=0
for root in "${ROOTS[@]}"; do
  if [[ ! -d "${root}" ]]; then
    continue
  fi
  for slug in "${OLD_SLUGS[@]}"; do
    target="${root}/${slug}"
    if [[ -e "${target}" || -L "${target}" ]]; then
      rm -rf -- "${target}"
      echo "removed ${target}"
      removed=$((removed + 1))
    fi
  done
done

if [[ "${removed}" -eq 0 ]]; then
  echo "No retired skill directories found."
fi

echo
echo "Install the current skills with:"
echo "  npx skills add -y -g FutunnOpen/futu-agent-hub"
