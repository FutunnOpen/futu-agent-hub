#!/usr/bin/env bash
# Futu Skills Hub CLI — one-line installer (deploys CLI under ~/.futu-skillhub, adds ~/.local/bin to PATH).
# Usage:
#   curl -fsSL "https://gitlab.futunn.com/futu-common/futu-skills-hub/-/raw/v20260428-futu-cli_v2/internal/futu/futu-install.sh" | bash
#   ./futu-install.sh
#
# Override remote git repo (takes precedence over cli_update_manifest.json):
#   export FUTU_SKILLHUB_REPO_URL="https://github.com/your-org/futu-skills-hub"
#   export FUTU_SKILLHUB_REPO_REF="main"
#   export FUTU_SKILLHUB_REPO_PATH="internal/futu/futu-skill-manager"
#
# Offline / dev: run from repo root so local futu-skill-manager/ is copied.

set -euo pipefail

HUB_HOME="${HOME}/.futu-skillhub"
CLI_DEST="${HUB_HOME}/futu-skill-manager"
BIN_DIR="${HOME}/.local/bin"
WRAPPER="${BIN_DIR}/futu-skills"

# Resolve remote repo: env override > cli_update_manifest.json > hardcoded fallback.
FALLBACK_REPO_URL="https://gitlab.futunn.com/futu-common/futu-skills-hub"
FALLBACK_REPO_REF="main"
FALLBACK_REPO_PATH="internal/futu/futu-skill-manager"
REMOTE_REPO_URL="${FUTU_SKILLHUB_REPO_URL:-}"
REMOTE_REPO_REF="${FUTU_SKILLHUB_REPO_REF:-}"
REMOTE_REPO_PATH="${FUTU_SKILLHUB_REPO_PATH:-}"
if [[ -z "${REMOTE_REPO_URL}" || -z "${REMOTE_REPO_REF}" || -z "${REMOTE_REPO_PATH}" ]]; then
  MANIFEST=""
  if [[ -n "${BASH_SOURCE[0]:-}" ]]; then
    MANIFEST="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/futu-skill-manager/cli_update_manifest.json"
  fi
  if [[ -f "${MANIFEST:-}" ]] && command -v python3 >/dev/null 2>&1; then
    REMOTE_REPO_URL="${REMOTE_REPO_URL:-$(python3 -c "import json,sys;print(json.load(open(sys.argv[1])).get('cli_repo_url',''))" "${MANIFEST}" 2>/dev/null || echo "")}"
    REMOTE_REPO_REF="${REMOTE_REPO_REF:-$(python3 -c "import json,sys;print(json.load(open(sys.argv[1])).get('cli_repo_ref',''))" "${MANIFEST}" 2>/dev/null || echo "")}"
    REMOTE_REPO_PATH="${REMOTE_REPO_PATH:-$(python3 -c "import json,sys;print(json.load(open(sys.argv[1])).get('cli_repo_path',''))" "${MANIFEST}" 2>/dev/null || echo "")}"
  fi
fi
REMOTE_REPO_URL="${REMOTE_REPO_URL:-${FALLBACK_REPO_URL}}"
REMOTE_REPO_REF="${REMOTE_REPO_REF:-${FALLBACK_REPO_REF}}"
REMOTE_REPO_PATH="${REMOTE_REPO_PATH:-${FALLBACK_REPO_PATH}}"

die() {
  echo "error: $*" >&2
  exit 1
}

command -v python3 >/dev/null 2>&1 || die "python3 is required"

SCRIPT_PATH=""
if [[ -n "${BASH_SOURCE[0]:-}" ]]; then
  SCRIPT_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
fi

mkdir -p "${CLI_DEST}" "${BIN_DIR}"

copy_local() {
  local src="$1"
  [[ -d "${src}/futu-skill-manager" ]] || return 1
  echo "Installing from local directory: ${src}/futu-skill-manager"
  cp -f "${src}/futu-skill-manager/futu_skills.py" "${CLI_DEST}/"
  cp -f "${src}/futu-skill-manager/metadata.json" "${CLI_DEST}/" 2>/dev/null || true
  cp -f "${src}/futu-skill-manager/version.json" "${CLI_DEST}/" 2>/dev/null || true
  cp -f "${src}/futu-skill-manager/skill_index.json" "${CLI_DEST}/" 2>/dev/null || true
  cp -f "${src}/futu-skill-manager/cli_update_manifest.json" "${CLI_DEST}/" 2>/dev/null || true
  cp -f "${src}/futu-skill-manager/skill_catalog.json" "${CLI_DEST}/" 2>/dev/null || true
  chmod +x "${CLI_DEST}/futu_skills.py"
  return 0
}

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

if [[ -n "${SCRIPT_PATH}" ]] && copy_local "${SCRIPT_PATH}"; then
  :
elif fetch_remote; then
  :
else
  die "Set FUTU_SKILLHUB_REPO_URL to the CLI git repo, or run this script from the futu-skills-hub repo root."
fi

cat > "${WRAPPER}" <<'EOF'
#!/usr/bin/env bash
exec python3 "${HOME}/.futu-skillhub/futu-skill-manager/futu_skills.py" "$@"
EOF
chmod +x "${WRAPPER}"

if python3 "${CLI_DEST}/futu_skills.py" --version >/dev/null 2>&1; then
  echo "Smoke test OK: $(python3 "${CLI_DEST}/futu_skills.py" --version)"
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
