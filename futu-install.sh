#!/usr/bin/env bash
# Futu Skills Hub CLI — one-line installer (deploys CLI under ~/.futu-skillhub, adds ~/.local/bin to PATH).
# Usage:
#   curl -fsSL "https://raw.githubusercontent.com/FutunnOpen/futu-agent-hub/feature/v202060511-add-skill/futu-install.sh" | bash
#
# Override remote git repo (takes precedence over cli_update_manifest.json):
#   export FUTU_SKILLHUB_REPO_URL="https://github.com/FutunnOpen/futu-agent-hub"
#   export FUTU_SKILLHUB_REPO_REF="feature/v202060511-add-skill"
#   export FUTU_SKILLHUB_REPO_PATH="manager"

set -euo pipefail

HUB_HOME="${HOME}/.futu-skillhub"
CLI_DEST="${HUB_HOME}/futu-skill-manager"
BIN_DIR="${HOME}/.local/bin"
WRAPPER="${BIN_DIR}/futu-skills"

# Resolve remote repo: env override > cli_update_manifest.json > hardcoded fallback.
FALLBACK_REPO_URL="https://github.com/FutunnOpen/futu-agent-hub"
FALLBACK_REPO_REF="feature/v202060511-add-skill"
FALLBACK_REPO_PATH="manager"
REMOTE_REPO_URL="${FUTU_SKILLHUB_REPO_URL:-${FALLBACK_REPO_URL}}"
REMOTE_REPO_REF="${FUTU_SKILLHUB_REPO_REF:-${FALLBACK_REPO_REF}}"
REMOTE_REPO_PATH="${FUTU_SKILLHUB_REPO_PATH:-${FALLBACK_REPO_PATH}}"

die() {
  echo "error: $*" >&2
  exit 1
}

# Prefer python3; fall back to python if it's Python 3
PYTHON=""
if command -v python3 >/dev/null 2>&1; then
  PYTHON="python3"
elif command -v python >/dev/null 2>&1 && python -c "import sys; sys.exit(0 if sys.version_info[0]==3 else 1)" 2>/dev/null; then
  PYTHON="python"
else
  die "Python 3 is required (install python3 or ensure 'python' points to Python 3)"
fi

mkdir -p "${CLI_DEST}" "${BIN_DIR}"

fetch_remote() {
  [[ -n "${REMOTE_REPO_URL}" ]] || return 1
  command -v git >/dev/null 2>&1 || die "git is required to clone the CLI"
  echo "Cloning CLI from: ${REMOTE_REPO_URL} (ref ${REMOTE_REPO_REF})"
  local tmp_repo
  tmp_repo="$(mktemp -d "${TMPDIR:-/tmp}/futu-skill-manager-XXXXXX")"
  git clone --depth=1 --branch "${REMOTE_REPO_REF}" "${REMOTE_REPO_URL}" "${tmp_repo}" >/dev/null
  local src="${tmp_repo}"
  if [[ -n "${REMOTE_REPO_PATH}" ]]; then
    src="${tmp_repo}/${REMOTE_REPO_PATH}"
  fi
  [[ -d "${src}" ]] || { rm -rf "${tmp_repo}"; die "cli_repo_path not found in repo: ${REMOTE_REPO_PATH:-<root>}"; }
  cp -R "${src}/." "${CLI_DEST}/"
  rm -rf "${tmp_repo}"
  chmod +x "${CLI_DEST}/futu_skills.py"
  return 0
}

fetch_remote || die "Failed to fetch CLI from ${REMOTE_REPO_URL} (ref ${REMOTE_REPO_REF})."

cat > "${WRAPPER}" <<EOF
#!/usr/bin/env bash
exec ${PYTHON} "\${HOME}/.futu-skillhub/futu-skill-manager/futu_skills.py" "\$@"
EOF
chmod +x "${WRAPPER}"

if ${PYTHON} "${CLI_DEST}/futu_skills.py" --version >/dev/null 2>&1; then
  echo "Smoke test OK: $(${PYTHON} "${CLI_DEST}/futu_skills.py" --version)"
else
  die "CLI smoke test failed"
fi

ensure_path() {
  local line='export PATH="${HOME}/.local/bin:${PATH}"'
  case "${SHELL##*/}" in
    zsh)
      local rc="${HOME}/.zshrc"
      if [[ -f "${rc}" ]] && grep -q '^[^#]*\.local/bin' "${rc}" 2>/dev/null; then
        return 0
      fi
      echo "" >> "${rc}"
      echo "# futu-skills" >> "${rc}"
      echo "${line}" >> "${rc}"
      echo "Appended PATH hint to ${rc}"
      ;;
    bash)
      local rc="${HOME}/.bash_profile"
      [[ -f "${HOME}/.bash_profile" ]] || rc="${HOME}/.profile"
      if [[ -f "${rc}" ]] && grep -q '^[^#]*\.local/bin' "${rc}" 2>/dev/null; then
        return 0
      fi
      echo "" >> "${rc}"
      echo "# futu-skills" >> "${rc}"
      echo "${line}" >> "${rc}"
      echo "Appended PATH hint to ${rc}"
      ;;
    *)
      echo "Add ${BIN_DIR} to PATH manually, e.g.:"
      echo "  ${line}"
      ;;
  esac
}

ensure_path

# Make futu-skills available in the current session immediately
export PATH="${BIN_DIR}:${PATH}"

# Refresh discovery skill so first-time installs immediately get a SKILL.md listing
"${WRAPPER}" refresh-discovery >/dev/null 2>&1 || true

echo ""
echo "Installed: ${WRAPPER}"
echo ""
echo "To use futu-skills right away, run one of the following:"
echo "  source ~/.zshrc        # if using zsh"
echo "  source ~/.bash_profile # if using bash"
echo "  export PATH=\"\${HOME}/.local/bin:\${PATH}\"  # or set PATH directly"
echo ""
echo "Try: futu-skills search news"
echo "     futu-skills detect"
echo "     npx skills add futu-news-search   # install a skill via npx"
echo ""
echo "[CLI_PATH] ${WRAPPER}"
