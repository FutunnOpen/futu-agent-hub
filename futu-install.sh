#!/usr/bin/env bash
# Futu Skills Hub CLI — one-line installer (deploys CLI under ~/.futu-skillhub, adds ~/.local/bin to PATH).
# Patched: validates Python actually runs (avoids Windows Store stub) and supports `py -3` launcher.

set -euo pipefail

HUB_HOME="${HOME}/.futu-skillhub"
CLI_DEST="${HUB_HOME}/futu-skill-manager"
BIN_DIR="${HOME}/.local/bin"
WRAPPER="${BIN_DIR}/futu-skills"

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

# Validate a candidate by actually running --version. Rejects the Windows Store
# stub `python3.exe` which exits non-zero with no stdout (or pops the Store).
validate_python() {
  local cand="$1"
  local ver
  ver="$(${cand} --version 2>&1)" || return 1
  [[ "${ver}" == Python\ 3* ]] || return 1
  return 0
}

PYTHON=""
for cand in "python3" "py -3" "python"; do
  if validate_python "${cand}"; then
    PYTHON="${cand}"
    break
  fi
done
[[ -n "${PYTHON}" ]] || die "Python 3 is required (install Python 3 and ensure 'python3', 'py -3', or 'python' resolves to it)"

echo "Using Python: ${PYTHON} ($(${PYTHON} --version 2>&1))"

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

export PATH="${BIN_DIR}:${PATH}"

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
echo "     npx skills add futu-news-search"
echo ""
echo "[CLI_PATH] ${WRAPPER}"