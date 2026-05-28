#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Futu Skills Hub CLI — lightweight skill manager (stdlib only).
Uses a local index, lockfile, and install/upgrade flows.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Paths & constants
# ---------------------------------------------------------------------------

ENV_SKILLS_DIR = "FUTU_SKILLHUB_DIR"
ENV_CONFIG = "FUTU_SKILLHUB_CONFIG"
ENV_SKIP_CACHE = "FUTU_SKILLHUB_NO_CACHE"
ENV_VERBOSE = "FUTU_SKILLHUB_VERBOSE"
ENV_CACHE_DIR = "FUTU_SKILLHUB_CACHE_DIR"
ENV_CURSOR_SKILLS = "CURSOR_SKILLS_DIR"
ENV_SKIP_SELF_UPGRADE = "FUTU_SKILLHUB_SKIP_SELF_UPGRADE"
ENV_SELF_UPGRADE_REEXEC = "FUTU_SKILLHUB_SELF_UPGRADE_REEXEC"
ENV_ANNOUNCE_UPDATES = "FUTU_SKILLHUB_ANNOUNCE_UPDATES"


def cli_dir() -> Path:
    return Path(__file__).resolve().parent


def hub_home() -> Path:
    return Path.home() / ".futu-skillhub"


def cache_dir() -> Path:
    env = os.environ.get(ENV_CACHE_DIR)
    if env:
        d = Path(env).expanduser().resolve()
    else:
        d = hub_home() / "cache"
    d.mkdir(parents=True, exist_ok=True)
    return d


def load_json(path: Path) -> Any:
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        print(f"error: invalid JSON: {path}", file=sys.stderr)
        raise SystemExit(10)


def save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def verbose(msg: str) -> None:
    if os.environ.get(ENV_VERBOSE) in ("1", "true", "TRUE", "yes"):
        print(msg, file=sys.stderr)


def parse_version_key(s: Optional[str]) -> Optional[Tuple[int, ...]]:
    """Parse dotted version string into a numeric tuple for comparison."""
    if not s:
        return None
    s = s.strip()
    if s.startswith("v") or s.startswith("V"):
        s = s[1:]
    if "-" in s:
        s = s.split("-", 1)[0]
    if "+" in s:
        s = s.split("+", 1)[0]
    parts: List[int] = []
    for p in re.split(r"[^\d]+", s):
        if p.isdigit():
            parts.append(int(p))
    return tuple(parts) if parts else None


def version_is_newer(remote: Optional[str], local: Optional[str]) -> bool:
    if not remote:
        return False
    if not local:
        return True
    ra, la = parse_version_key(remote), parse_version_key(local)
    if ra is not None and la is not None:
        return ra > la
    return remote != local


def hub_config_path() -> Path:
    return hub_home() / "config.json"


def load_hub_config() -> Dict[str, Any]:
    data = load_json(hub_config_path())
    return data if isinstance(data, dict) else {}


def detect_ai_client() -> Tuple[Optional[str], Optional[Path]]:
    """Detect the current AI client from environment variables.
    Returns (client_name, skills_dir) or (None, None) if unknown.
    """
    home = Path.home()
    # Claude Code
    if os.environ.get("CLAUDECODE") or os.environ.get("CLAUDE_CODE_ENTRYPOINT"):
        return "Claude Code", home / ".claude" / "skills"
    term = os.environ.get("TERM_PROGRAM", "").lower()
    terminal_emu = os.environ.get("TERMINAL_EMULATOR", "").lower()
    bundle_id = os.environ.get("__CFBundleIdentifier", "").lower()
    # Cursor
    if "cursor" in term:
        return "Cursor", home / ".cursor" / "skills"
    # VS Code (with Claude extension → ~/.claude/skills)
    if "vscode" in term:
        return "VS Code", home / ".claude" / "skills"
    # JetBrains
    if "jetbrains" in terminal_emu or "jetbrains" in bundle_id:
        # JetBrains with Claude extension → ~/.claude/skills
        claude_dir = home / ".claude" / "skills"
        if claude_dir.is_dir():
            return "JetBrains (Claude)", claude_dir
        # JetBrains built-in AI → ~/.junie/guidelines
        junie_dir = home / ".junie" / "guidelines"
        if junie_dir.is_dir():
            return "JetBrains (Junie)", junie_dir
        return "JetBrains", claude_dir
    # OpenClaw
    if os.environ.get("OPENCLAW"):
        return "OpenClaw", home / ".openclaw" / "skills"
    # Codex (OpenAI Codex CLI) — env var hint or presence of ~/.codex
    if os.environ.get("CODEX_HOME") or os.environ.get("CODEX_ENV") or os.environ.get("CODEX_CLI"):
        return "Codex", home / ".codex" / "skills"
    if (home / ".codex").is_dir():
        return "Codex", home / ".codex" / "skills"
    return None, None


def resolve_skills_dir() -> Tuple[str, str]:
    """
    Resolve default skills install root.
    Priority: env override > AI client detection > workspace walk > known dirs > fallback.
    Returns (path_string, reason_for_debug).
    """
    if os.environ.get(ENV_SKILLS_DIR):
        p = Path(os.environ[ENV_SKILLS_DIR]).expanduser().resolve()
        return str(p), f"env {ENV_SKILLS_DIR}"
    if os.environ.get(ENV_CURSOR_SKILLS):
        p = Path(os.environ[ENV_CURSOR_SKILLS]).expanduser().resolve()
        return str(p), f"env {ENV_CURSOR_SKILLS}"
    # AI client auto-detection
    client, client_dir = detect_ai_client()
    if client and client_dir:
        client_dir.mkdir(parents=True, exist_ok=True)
        return str(client_dir.resolve()), f"{client} {client_dir}"
    # Workspace walk (legacy Cursor detection)
    here = Path.cwd().resolve()
    for parent in [here, *here.parents]:
        ws = parent / ".cursor" / "skills"
        if ws.is_dir():
            return str(ws.resolve()), f"workspace {ws}"
    # Check known directories
    for d in [
        Path.home() / ".claude" / "skills",
        Path.home() / ".cursor" / "skills",
        Path.home() / ".openclaw" / "skills",
        Path.home() / ".codex" / "skills",
        Path.home() / ".junie" / "guidelines",
    ]:
        if d.is_dir():
            return str(d.resolve()), f"home {d}"
    return "./skills", "fallback (create --dir or mkdir ~/.claude/skills)"


def read_skill_version(skill_dir: Path) -> str:
    """Read version from SKILL.md frontmatter metadata.version if present."""
    p = skill_dir / "SKILL.md"
    if not p.is_file():
        return ""
    try:
        text = p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""
    m = re.search(
        r"^metadata:\s*\n(?:.*\n)*?\s+version:\s*[\"']?([0-9][^\"'\s]*)[\"']?",
        text,
        re.MULTILINE,
    )
    if m:
        return m.group(1).strip()
    m2 = re.search(r"^\s+version:\s*[\"']?([0-9][^\"'\s]*)[\"']?", text, re.MULTILINE)
    return m2.group(1).strip() if m2 else ""


def read_skill_deps(skill_dir: Path) -> List[str]:
    """Read declared skill-to-skill deps from SKILL.md frontmatter.

    Canonical path is ``metadata.requires.skills``. The parser accepts a
    ``skills:`` list under any ``requires:`` block in the frontmatter, so
    extra namespace levels (e.g. legacy ``metadata.openclaw.requires``) also
    work. Returns slug list in declared order, deduped. Empty list if
    frontmatter is absent or the field is missing.
    """
    p = skill_dir / "SKILL.md"
    if not p.is_file():
        return []
    try:
        text = p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    m = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return []
    lines = m.group(1).splitlines()
    in_requires = False
    requires_indent = -1
    in_skills_list = False
    skills_indent = -1
    deps: List[str] = []
    seen: set = set()

    def _push(item: str) -> None:
        s = item.strip().strip("'\"")
        if s and s not in seen:
            seen.add(s)
            deps.append(s)

    for line in lines:
        stripped = line.lstrip(" ")
        indent = len(line) - len(stripped)
        if not stripped or stripped.startswith("#"):
            continue
        if in_skills_list:
            if indent > skills_indent and stripped.startswith("- "):
                _push(stripped[2:])
                continue
            in_skills_list = False
        if in_requires:
            if indent <= requires_indent:
                in_requires = False
            elif stripped.startswith("skills:"):
                rest = stripped[len("skills:"):].strip()
                if rest.startswith("[") and rest.endswith("]"):
                    for item in rest[1:-1].split(","):
                        _push(item)
                else:
                    in_skills_list = True
                    skills_indent = indent
                continue
        if stripped.startswith("requires:"):
            in_requires = True
            requires_indent = indent
    return deps


def resolve_skill_version(
    skill_dir: Path,
    slug: str,
    catalog: Optional[Dict[str, Any]] = None,
) -> str:
    """Return best-effort version: SKILL.md > catalog > 'latest'."""
    ver = read_skill_version(skill_dir)
    if ver:
        return ver
    if catalog:
        cat_ver = parse_catalog_skill_version(catalog, slug)
        if cat_ver:
            return cat_ver
    return "latest"


def download_url(url: str, dest: Path, timeout: int = 60) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "futu-skills/1"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = resp.read()
    dest.write_bytes(data)


def fetch_json_url(url: str, timeout: int) -> Optional[Dict[str, Any]]:
    try:
        if url.startswith("file://"):
            path = Path(url[7:]).expanduser().resolve()
            raw = path.read_text(encoding="utf-8", errors="replace")
        elif url.startswith("/") and Path(url).is_file():
            raw = Path(url).read_text(encoding="utf-8", errors="replace")
        else:
            req = urllib.request.Request(url, headers={"User-Agent": "futu-skills/1"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                raw = resp.read().decode("utf-8", errors="replace")
        data = json.loads(raw)
        return data if isinstance(data, dict) else None
    except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError) as e:
        verbose(f"fetch_json_url failed: {url} ({e})")
        return None


def self_update_manifest_url() -> str:
    # 1. metadata.json shipped with the CLI package.
    meta = load_metadata()
    u2 = meta.get("cli_update_manifest_url")
    if isinstance(u2, str) and u2.strip():
        return u2.strip()
    # 2. Hub config cache – lowest priority; may contain stale URLs.
    cfg = load_hub_config()
    u = cfg.get("cli_update_manifest_url")
    if isinstance(u, str) and u.strip():
        return u.strip()
    return ""


def apply_cli_update_from_manifest(
    manifest: Dict[str, Any], *, timeout: int, dry_run: bool = False
) -> None:
    remote_ver = str(manifest.get("version") or "").strip()
    base = str(manifest.get("files_base_url") or "").rstrip("/")
    files = manifest.get("files") or []
    if not remote_ver or not base or not files:
        print("error: manifest missing version, files_base_url, or files", file=sys.stderr)
        raise SystemExit(10)
    if dry_run:
        print(f"would update CLI to {remote_ver} from {base}")
        return

    tmp = Path(tempfile.mkdtemp(prefix="futu-skills-upd-"))
    try:
        for item in files:
            if isinstance(item, str):
                name = item
                expect_sha = None
            elif isinstance(item, dict):
                name = str(item.get("name") or "")
                expect_sha = item.get("sha256") or item.get("sha_256")
            else:
                continue
            if not name:
                continue
            url = base + "/" + name.replace("\\", "/").lstrip("/")
            dest_part = tmp / name
            dest_part.parent.mkdir(parents=True, exist_ok=True)
            download_url(url, dest_part, timeout=timeout)
            # Validate downloaded content to prevent HTML error pages from overwriting CLI files.
            raw = dest_part.read_text(encoding="utf-8", errors="replace").lstrip()
            if name.endswith(".json"):
                try:
                    json.loads(raw)
                except json.JSONDecodeError:
                    verbose(f"downloaded {name} is not valid JSON, aborting upgrade")
                    raise SystemExit(4)
            elif name.endswith(".py"):
                if raw.startswith("<") or "<!DOCTYPE" in raw[:200]:
                    verbose(f"downloaded {name} looks like HTML, aborting upgrade")
                    raise SystemExit(4)
            if expect_sha:
                h = hashlib.sha256()
                with open(dest_part, "rb") as f:
                    for chunk in iter(lambda: f.read(65536), b""):
                        h.update(chunk)
                if h.hexdigest().lower() != str(expect_sha).lower():
                    print(f"error: sha256 mismatch for {name}", file=sys.stderr)
                    raise SystemExit(4)

        cdir = cli_dir()
        bak_files: List[Path] = []
        for item in files:
            name = item if isinstance(item, str) else str((item or {}).get("name") or "")
            if not name:
                continue
            src = tmp / name
            if not src.is_file():
                continue
            dst = cdir / name
            if dst.is_file():
                bak = dst.with_name(dst.name + ".bak")
                shutil.copy2(dst, bak)
                bak_files.append(bak)
            shutil.copy2(src, dst)
            if name.endswith(".py"):
                mode = dst.stat().st_mode
                dst.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # All files replaced successfully — remove backups.
    for bak in bak_files:
        bak.unlink(missing_ok=True)

    # Sync URL fields from the newly downloaded metadata.json into hub config,
    # so stale config values don't override the updated metadata.
    _sync_metadata_urls_to_config()


def _sync_metadata_urls_to_config() -> None:
    """Copy URL fields from metadata.json to hub config.json so they stay in sync."""
    meta = load_metadata()
    if not meta:
        return
    sync_keys = ("skill_catalog_url", "cli_update_manifest_url")
    cfg_path = hub_config_path()
    cfg = load_hub_config()
    changed = False
    for key in sync_keys:
        new_val = meta.get(key)
        if isinstance(new_val, str) and new_val.strip() and cfg.get(key) != new_val:
            cfg[key] = new_val
            changed = True
    if changed:
        save_json(cfg_path, cfg)
        verbose("synced metadata URLs to hub config")


def apply_cli_update_from_git(
    manifest: Dict[str, Any], *, timeout: int, dry_run: bool = False
) -> None:
    """Clone the CLI git repo and copy cli_repo_path into cli_dir()."""
    remote_ver = str(manifest.get("version") or "").strip()
    repo_url = str(manifest.get("cli_repo_url") or "").strip()
    repo_ref = str(manifest.get("cli_repo_ref") or "main").strip() or "main"
    repo_path = str(manifest.get("cli_repo_path") or "").strip().replace("\\", "/").strip("/")
    if not remote_ver or not repo_url:
        print("error: manifest missing version or cli_repo_url", file=sys.stderr)
        raise SystemExit(10)
    if dry_run:
        label = f"{repo_url}#{repo_ref}"
        if repo_path:
            label += f"/{repo_path}"
        print(f"would update CLI to {remote_ver} from {label}")
        return
    if shutil.which("git") is None:
        print("error: git is required to self-upgrade", file=sys.stderr)
        raise SystemExit(3)

    tmp = Path(tempfile.mkdtemp(prefix="futu-skills-upd-"))
    clone_dir = tmp / "repo"
    try:
        print(f"git clone {repo_url} (ref {repo_ref})", file=sys.stderr)
        try:
            subprocess.run(
                ["git", "clone", "--depth=1", "--branch", repo_ref, repo_url, str(clone_dir)],
                check=True, capture_output=True, timeout=max(timeout, 30),
            )
        except subprocess.CalledProcessError as e:
            err = (e.stderr or b"").decode("utf-8", errors="replace").strip()
            print(f"error: git clone failed: {err or e}", file=sys.stderr)
            raise SystemExit(3)
        except subprocess.TimeoutExpired:
            print("error: git clone timed out", file=sys.stderr)
            raise SystemExit(3)

        src_root = clone_dir if not repo_path else (clone_dir / repo_path)
        if not src_root.is_dir():
            print(f"error: cli_repo_path not found in repo: {repo_path or '<root>'}", file=sys.stderr)
            raise SystemExit(4)

        target_dir = cli_dir()
        bak_files: List[Path] = []
        for root, dirs, filenames in os.walk(src_root):
            if ".git" in dirs:
                dirs.remove(".git")
            for fname in filenames:
                src = Path(root) / fname
                rel = src.relative_to(src_root)
                dst = target_dir / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                if dst.is_file():
                    bak = dst.with_name(dst.name + ".bak")
                    shutil.copy2(dst, bak)
                    bak_files.append(bak)
                shutil.copy2(src, dst)
                if fname.endswith(".py"):
                    mode = dst.stat().st_mode
                    dst.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # All files replaced successfully — remove backups.
    for bak in bak_files:
        bak.unlink(missing_ok=True)

    _sync_metadata_urls_to_config()


def run_self_upgrade(
    *,
    check_only: bool,
    timeout: int,
    force_exec: bool,
    force: bool = False,
) -> bool:
    """
    Returns True if the process was replaced via os.execv (caller must not continue).
    """
    if os.environ.get(ENV_SELF_UPGRADE_REEXEC) == "1":
        return False

    local_ver = load_version()
    url = self_update_manifest_url()
    if not url:
        print("error: no cli_update_manifest_url (metadata/config/env)", file=sys.stderr)
        raise SystemExit(10)

    manifest = fetch_json_url(url, timeout=timeout)
    if not manifest:
        print(f"error: could not fetch update manifest: {url}", file=sys.stderr)
        raise SystemExit(3)

    remote_ver = str(manifest.get("version") or "").strip()
    if not force and not version_is_newer(remote_ver, local_ver):
        if not check_only:
            print(f"CLI already up to date ({local_ver})")
        else:
            print(f"check-only: local={local_ver} remote={remote_ver} (no update)")
        return False

    if check_only:
        if force and not version_is_newer(remote_ver, local_ver):
            print(f"check-only: local={local_ver} remote={remote_ver} (no update, --force would reinstall)")
        else:
            print(f"update available: {local_ver} -> {remote_ver}")
        return False

    action = "reinstalling" if not version_is_newer(remote_ver, local_ver) else "upgrading"
    print(f"{action} CLI {local_ver} -> {remote_ver} ...", file=sys.stderr)
    if manifest.get("cli_repo_url"):
        apply_cli_update_from_git(manifest, timeout=timeout, dry_run=False)
    else:
        apply_cli_update_from_manifest(manifest, timeout=timeout, dry_run=False)
    print(f"CLI updated to {remote_ver}", file=sys.stderr)

    if force_exec:
        os.environ[ENV_SELF_UPGRADE_REEXEC] = "1"
        script = os.path.abspath(sys.argv[0])
        new_argv = [sys.executable, script, *sys.argv[1:]]
        verbose(f"re-exec: {new_argv}")
        os.execv(sys.executable, new_argv)
    return False


def maybe_startup_self_upgrade(argv: List[str]) -> bool:
    """
    Lightweight OTA check before user subcommand. Silent on failure.
    Returns True if execv was called (process replaced).
    """
    if os.environ.get(ENV_SELF_UPGRADE_REEXEC) == "1":
        return False
    if "--skip-self-upgrade" in argv:
        return False
    if os.environ.get(ENV_SKIP_SELF_UPGRADE, "").lower() in (
        "1",
        "true",
        "yes",
    ):
        return False
    cfg = load_hub_config()
    if cfg.get("auto_self_upgrade") is False:
        return False

    url = self_update_manifest_url()
    if not url:
        return False

    manifest = fetch_json_url(url, timeout=3)
    if not manifest:
        return False
    remote_ver = str(manifest.get("version") or "").strip()
    local_ver = load_version()
    if not version_is_newer(remote_ver, local_ver):
        return False

    try:
        if manifest.get("cli_repo_url"):
            apply_cli_update_from_git(manifest, timeout=20, dry_run=False)
        else:
            apply_cli_update_from_manifest(manifest, timeout=20, dry_run=False)
    except (Exception, SystemExit) as e:
        verbose(f"startup self-upgrade failed: {e}")
        return False

    # Guard: if version didn't actually change after upgrade (e.g. remote
    # ref still holds an older version.json), skip re-exec to avoid infinite loop.
    new_local_ver = load_version()
    if not version_is_newer(new_local_ver, local_ver):
        verbose(f"startup self-upgrade: version unchanged after update "
                f"({local_ver} -> {new_local_ver}), skipping re-exec")
        return False

    os.environ[ENV_SELF_UPGRADE_REEXEC] = "1"
    script = os.path.abspath(argv[0])
    new_argv = [sys.executable, script, *argv[1:]]
    os.execv(sys.executable, new_argv)
    return True


# ---------------------------------------------------------------------------
# Index & metadata
# ---------------------------------------------------------------------------


def load_metadata() -> Dict[str, Any]:
    meta_path = cli_dir() / "metadata.json"
    data = load_json(meta_path)
    if not isinstance(data, dict):
        print("error: metadata.json missing or invalid", file=sys.stderr)
        raise SystemExit(10)
    return data


def load_version() -> str:
    vpath = cli_dir() / "version.json"
    data = load_json(vpath)
    if isinstance(data, dict) and data.get("version"):
        return str(data["version"])
    return "0.0.0"


def load_index() -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    meta = load_metadata()
    index_name = meta.get("index_file") or "skill_index.json"
    ip = cli_dir() / index_name
    raw = load_json(ip)
    if not isinstance(raw, dict) or not isinstance(raw.get("skills"), list):
        print("error: skill index invalid", file=sys.stderr)
        raise SystemExit(10)
    return meta, raw["skills"]


def resolve_repo_url(meta: Dict[str, Any], entry: Optional[Dict[str, Any]] = None) -> str:
    if entry:
        ev = str(entry.get("repo_url") or "").strip()
        if ev:
            return ev
    u = meta.get("repo_url")
    if not isinstance(u, str) or not u.strip():
        print("error: metadata.repo_url is not configured", file=sys.stderr)
        raise SystemExit(10)
    return u.strip()


def resolve_repo_ref(meta: Dict[str, Any], entry: Optional[Dict[str, Any]] = None) -> str:
    if entry:
        ev = str(entry.get("repo_ref") or "").strip()
        if ev:
            return ev
    r = str(meta.get("repo_ref") or "").strip()
    return r or "main"


def _npx_skills_source(repo_url: str) -> str:
    """Return the shortest form `npx skills add` accepts for this repo URL.

    GitHub HTTPS URLs collapse to `owner/repo` shorthand; anything else
    (SSH, GitLab, self-hosted) falls back to the original URL.
    """
    u = (repo_url or "").strip()
    m = re.match(r"^https?://github\.com/([^/]+)/([^/]+?)(?:\.git)?/?$", u)
    if m:
        return f"{m.group(1)}/{m.group(2)}"
    return u


def get_skill_entry(skills: List[Dict[str, Any]], slug: str) -> Optional[Dict[str, Any]]:
    for s in skills:
        if s.get("slug") == slug:
            return s
    return None


def skill_catalog_url() -> str:
    # 1. metadata.json remote URL (authoritative for version checks)
    meta = load_metadata()
    u2 = meta.get("skill_catalog_url")
    if isinstance(u2, str) and u2.strip():
        return u2.strip()
    # 2. Hub config cache
    cfg = load_hub_config()
    u = cfg.get("skill_catalog_url")
    if isinstance(u, str) and u.strip():
        return u.strip()
    # 3. Local sibling file as fallback (offline)
    local = cli_dir() / "skill_catalog.json"
    if local.is_file():
        return local.as_uri()
    return ""


def parse_catalog_skill_version(catalog: Dict[str, Any], slug: str) -> Optional[str]:
    skills = catalog.get("skills") or {}
    raw = skills.get(slug)
    if isinstance(raw, str):
        v = raw.strip()
        return v or None
    if isinstance(raw, dict):
        v = str(raw.get("version") or "").strip()
        return v or None
    return None


def parse_catalog_deprecation(
    catalog: Dict[str, Any], slug: str
) -> Optional[Dict[str, str]]:
    """Return deprecation entry for *slug* if present, else None.

    Expected catalog shape:
      "deprecations": {
        "old-slug": {"action": "remove",  "message": "..."},
        "old-slug": {"action": "migrate", "replace_with": "new-slug", "message": "..."}
      }
    """
    deps = catalog.get("deprecations") or {}
    entry = deps.get(slug)
    if isinstance(entry, dict) and entry.get("action"):
        return entry
    return None


def _hub_product(meta: Dict[str, Any]) -> Optional[str]:
    """Derive the product name from metadata hub_name (e.g. 'futu-skillhub' -> 'futu')."""
    hub = str(meta.get("hub_name") or "")
    if hub.endswith("-skillhub"):
        return hub[: -len("-skillhub")].lower() or None
    return None


def run_update_check(install_root: Path, *, timeout: int) -> Dict[str, Any]:
    """Compare local CLI + lockfile skills vs remote manifest + skill catalog."""
    meta = load_metadata()
    local_cli = load_version()
    own_product = _hub_product(meta)
    out: Dict[str, Any] = {
        "cli": {"local": local_cli, "remote": None, "outdated": False},
        "skills": [],
        "catalog_error": None,
        "outdated": False,
    }
    murl = self_update_manifest_url()
    if murl:
        manifest = fetch_json_url(murl, timeout=min(timeout, 10))
        if manifest:
            rv = str(manifest.get("version") or "").strip()
            out["cli"]["remote"] = rv
            out["cli"]["outdated"] = version_is_newer(rv, local_cli)
            if out["cli"]["outdated"]:
                out["outdated"] = True

    curl = skill_catalog_url()
    catalog: Optional[Dict[str, Any]] = None
    if curl:
        catalog = fetch_json_url(curl, timeout=timeout)
        if not catalog:
            out["catalog_error"] = f"could not fetch skill catalog ({curl})"

    try:
        _, idx_skills = load_index()
        reconcile_lockfile_with_disk(install_root, meta, idx_skills, catalog)
    except SystemExit:
        raise
    except Exception as e:
        verbose(f"reconcile skipped: {e}")
    lock = read_lock(install_root, meta)
    installed = lock.get("skills") or {}

    for slug, info in installed.items():
        # Skip skills belonging to a different product
        if own_product and str((info or {}).get("product") or "").lower() not in ("", own_product):
            continue
        local_ver = str((info or {}).get("version") or "")
        dest = install_root / slug
        if not local_ver or local_ver == "unknown":
            local_ver = read_skill_version(dest) or local_ver
        remote_ver: Optional[str] = None
        status = "no_catalog"
        dep_info: Optional[Dict[str, str]] = None
        if catalog:
            dep_info = parse_catalog_deprecation(catalog, slug)
            if dep_info:
                action = dep_info.get("action", "remove")
                if action == "migrate":
                    status = "deprecated_migrate"
                else:
                    status = "deprecated_remove"
                out["outdated"] = True
            else:
                remote_ver = parse_catalog_skill_version(catalog, slug)
                if not remote_ver:
                    status = "not_in_catalog"
                elif version_is_newer(remote_ver, local_ver):
                    status = "update_available"
                    out["outdated"] = True
                else:
                    status = "up_to_date"
        skill_entry: Dict[str, Any] = {
            "slug": slug,
            "local": local_ver or "?",
            "remote": remote_ver,
            "status": status,
        }
        if dep_info:
            skill_entry["deprecation"] = dep_info
        out["skills"].append(skill_entry)

    return out


# ---------------------------------------------------------------------------
# Lockfile
# ---------------------------------------------------------------------------


def lockfile_path(install_root: Path, meta: Dict[str, Any]) -> Path:
    name = meta.get("skills_lock_filename") or ".skills_store_lock.json"
    return install_root / name


def read_lock(install_root: Path, meta: Dict[str, Any]) -> Dict[str, Any]:
    p = lockfile_path(install_root, meta)
    data = load_json(p)
    if not data:
        return {"version": 1, "skills": {}}
    if not isinstance(data, dict):
        return {"version": 1, "skills": {}}
    if "skills" not in data or not isinstance(data["skills"], dict):
        data["skills"] = {}
    data.setdefault("version", 1)
    return data


def write_lock(install_root: Path, meta: Dict[str, Any], lock: Dict[str, Any]) -> None:
    save_json(lockfile_path(install_root, meta), lock)


def reconcile_lockfile_with_disk(
    install_root: Path,
    meta: Dict[str, Any],
    skills: List[Dict[str, Any]],
    catalog: Optional[Dict[str, Any]] = None,
) -> int:
    """Adopt skills installed outside this CLI (e.g. via ``npx skills add``)
    into the lockfile so subsequent list/upgrade/check commands manage them.

    Scans *install_root* for sibling directories with a ``SKILL.md`` whose
    name matches a slug in this hub's index and is not yet locked. Returns
    the number of newly tracked entries.
    """
    if not install_root.is_dir():
        return 0
    lock = read_lock(install_root, meta)
    locked = lock.setdefault("skills", {})
    by_slug = {s.get("slug"): s for s in skills if s.get("slug")}
    reserved = {_discovery_dir_name(meta), DISCOVERY_DIR_NAME, "_futu-skill-guard"}
    added = 0
    for child in install_root.iterdir():
        slug = child.name
        if slug in reserved or slug.startswith(".") or slug in locked:
            continue
        if not child.is_dir() or not (child / "SKILL.md").is_file():
            continue
        entry = by_slug.get(slug)
        if not entry:
            continue
        ver = resolve_skill_version(child, slug, catalog)
        locked[slug] = {
            "name": entry.get("name") or slug,
            "version": ver,
            "source": "futu-skillhub",
            "source_url": resolve_repo_url(meta, entry),
            "product": entry.get("product"),
            "adopted": True,
        }
        added += 1
    if added:
        write_lock(install_root, meta, lock)
        verbose(f"reconciled {added} skill(s) into lockfile")
    return added


# ---------------------------------------------------------------------------
# Discovery skill (auto-generated catalog of uninstalled skills)
# ---------------------------------------------------------------------------

DISCOVERY_DIR_NAME = "_futu-skillhub"


def _discovery_dir_name(meta: Dict[str, Any]) -> str:
    """Return the discovery skill directory name derived from hub_name metadata."""
    hub = str(meta.get("hub_name") or "")
    if hub:
        return f"_{hub}"
    return DISCOVERY_DIR_NAME


def _refresh_discovery_skill(
    install_root: Path,
    meta: Dict[str, Any],
    skills: List[Dict[str, Any]],
) -> None:
    """Generate or remove the discovery skill that lists uninstalled skills.

    Creates ``_<hub_name>/SKILL.md`` containing trigger descriptions for
    every skill that is available in the index but NOT currently installed.
    The AI client reads this like any other skill and can suggest installation
    when the user's intent matches an uninstalled skill.

    If all skills are installed the directory is removed entirely.
    """
    discovery_dir = install_root / _discovery_dir_name(meta)
    lock = read_lock(install_root, meta)
    installed_slugs = set(lock.get("skills", {}).keys())
    # Count skills installed directly via `npx skills add` (bypassing the CLI):
    # treat any sibling directory that contains a SKILL.md as installed.
    if install_root.is_dir():
        reserved = {_discovery_dir_name(meta), DISCOVERY_DIR_NAME, "_futu-skill-guard"}
        for child in install_root.iterdir():
            if child.name in reserved or child.name.startswith("."):
                continue
            if child.is_dir() and (child / "SKILL.md").is_file():
                installed_slugs.add(child.name)

    uninstalled = [s for s in skills if s.get("slug") not in installed_slugs]

    # --- Compute category complements ---
    # Categories with BOTH installed and uninstalled skills → append suggestions
    # after installed skills complete, rather than blocking them.
    category_groups: Dict[str, List[Dict[str, Any]]] = {}
    for s in skills:
        cat = s.get("category") or ""
        if cat:
            category_groups.setdefault(cat, []).append(s)

    complements: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}
    for cat, cat_skills in category_groups.items():
        installed_in_cat = [s for s in cat_skills if s.get("slug") in installed_slugs]
        uninstalled_in_cat = [s for s in cat_skills if s.get("slug") not in installed_slugs]
        if installed_in_cat and uninstalled_in_cat:
            complements[cat] = {"installed": installed_in_cat, "uninstalled": uninstalled_in_cat}

    if not uninstalled and not complements:
        if discovery_dir.is_dir():
            shutil.rmtree(discovery_dir)
            verbose("discovery skill removed (all skills installed)")
        return

    # --- Build description line with ONLY keywords from uninstalled skills ---
    all_keywords: List[str] = []
    for s in uninstalled:
        all_keywords.extend(s.get("keywords") or [])
    kw_str = ", ".join(dict.fromkeys(all_keywords))  # dedupe, preserve order

    # --- Build SKILL.md content ---
    hub_name = str(meta.get("hub_name") or "futu-skillhub")
    hub_title = hub_name.replace("-", " ").title().replace("Skillhub", "SkillHub")
    lines: List[str] = []
    lines.append("---")
    lines.append(f"name: {hub_name}")
    # Keep description concise — only keywords, detailed matching logic lives in body
    desc = (
        f"{hub_title} skill discovery. Suggests installing uninstalled skills "
        f"when user intent matches. Keywords: {kw_str}."
    )
    # Enforce 1024 char limit on description
    if len(desc) > 1024:
        prefix = f"{hub_title} skill discovery. Suggests installing uninstalled skills when user intent matches. Keywords: "
        suffix = "."
        max_kw_len = 1024 - len(prefix) - len(suffix)
        truncated_kw = kw_str[:max_kw_len].rsplit(", ", 1)[0]
        desc = f"{prefix}{truncated_kw}{suffix}"
    lines.append("description: >-")
    # Wrap description at ~78 chars for readability
    _wrap_yaml(lines, desc, indent=2)
    lines.append("metadata:")
    lines.append("  version: auto")
    lines.append(f"  author: {hub_title} CLI")
    lines.append("---")
    lines.append("")
    lines.append(f"# {hub_title} — Available but Not Installed Skills")
    lines.append("")
    lines.append("The following skills can be installed via the `npx skills add` commands shown below.")
    lines.append("When the user's request matches a skill listed below,")
    lines.append("tell the user this skill is available and ask: **If you'd like, I can install it for you right now.**")
    lines.append("")
    lines.append("**IMPORTANT**: If the user's request matches an uninstalled skill below,")
    lines.append("do NOT use another installed skill as a substitute — prompt the user to install")
    lines.append("the correct skill instead. Each skill has a distinct purpose.")
    lines.append("")
    lines.append("## Post-install behavior")
    lines.append("")
    lines.append("After the user agrees to install, execute in this order — **do NOT ask the user to repeat their original request**:")
    lines.append("")
    lines.append("1. Run the corresponding `npx skills add` install command shown below.")
    lines.append("2. After successful installation, **directly read** the `SKILL.md` in the newly installed directory (use the Read tool with the file path),")
    lines.append("   then follow its instructions to fulfill the user's **original request**.")
    lines.append("   - Note: The Skill tool allowlist is locked at session start; the new slug is usually not in it.")
    lines.append("     **Do NOT** try to invoke the new slug via the Skill tool — it will be rejected. Instead, Read the SKILL.md directly and follow its instructions.")
    lines.append("3. Do not ask the user \"what would you like to do now\" — the original intent is already in context.")
    lines.append("")
    lines.append("## Decline fallback")
    lines.append("")
    lines.append("If the user **declines** or **explicitly says they don't want to install**, **do NOT** ask again or substitute with another installed skill.")
    lines.append("Instead, **use your general capabilities** to answer the user's original question (based on training knowledge, reasoning,")
    lines.append("and existing context), and briefly note that a specialized skill exists but is not installed, so the answer may be less precise.")
    lines.append("")
    lines.append("## Multi-match handling")
    lines.append("")
    lines.append("**When the user's request matches multiple uninstalled skills below, NEVER install all of them at once.**")
    lines.append("You must first list all matching skills (slug + brief description), then ask the user which ones to install, for example:")
    lines.append("")
    lines.append("> Your request matches multiple installable skills: `a`, `b`, `c`.")
    lines.append("> Use `--skill a` to install one, or `--skill a,b` to install multiple (comma-separated, no spaces);")
    lines.append("> or reply `--skill all` to install all of them.")
    lines.append("")
    lines.append("Parse the `--skill` parameter from the user's reply:")
    lines.append("- `--skill <slug>`: Install only that single skill.")
    lines.append("- `--skill <slug1>,<slug2>,...`: Install only the slugs explicitly listed (comma-separated).")
    lines.append("- `--skill all`: Install all matches (only when the user explicitly states this).")
    lines.append("- No `--skill` specified or no explicit confirmation → **do NOT install anything**, ask again.")
    lines.append("")
    lines.append("For each slug the user specifies, run its corresponding `npx skills add` command below;")
    lines.append("**NEVER** install slugs that are not in the user's `--skill` list.")
    lines.append("")

    # --- Category complement section (only when applicable) ---
    if complements:
        lines.append("## Category Complement")
        lines.append("")
        lines.append("When the user's request is handled by an installed skill (PRIMARY trigger not met),")
        lines.append("but there are still uninstalled skills in the same category:")
        lines.append("**Do NOT interrupt the installed skill's execution.** Append a lightweight hint at the end of its response:")
        lines.append("")
        lines.append("> 💡 There's also **`<slug>`** (`<description>`) in the same category that isn't installed yet — it can provide a more complete perspective. If you'd like, I can install it for you.")
        lines.append("")
        for cat, info in complements.items():
            installed_names = ", ".join(f"`{s['slug']}`" for s in info["installed"])
            lines.append(f"### {cat}")
            lines.append(f"- **Installed**: {installed_names}")
            for u in info["uninstalled"]:
                u_slug = u.get("slug", "")
                u_desc = u.get("description", "")
                u_hint = u.get("discovery_hint", "")
                s_url = resolve_repo_url(meta, u)
                s_ref = resolve_repo_ref(meta, u)
                s_src = _npx_skills_source(s_url)
                install_cmd = (
                    f"npx skills add -y -g {s_src}"
                    if s_ref in ("", "main")
                    else f"npx skills add -y -g {s_src}#{s_ref}"
                )
                lines.append(f"- **Not installed**: `{u_slug}` — {u_desc}")
                if u_hint:
                    lines.append(f"  - When to suggest: {u_hint}")
                lines.append(f"  - Install: `{install_cmd}`")
            lines.append("")
        lines.append("> **Rule**: Slugs listed in this file = not installed; slugs NOT in this file = already installed.")
        lines.append("")

    for s in uninstalled:
        slug = s.get("slug", "")
        desc_short = s.get("description", "")
        hint = s.get("discovery_hint", "")
        s_url = resolve_repo_url(meta, s)
        s_ref = resolve_repo_ref(meta, s)
        s_src = _npx_skills_source(s_url)
        install_cmd = (
            f"npx skills add -y -g {s_src}"
            if s_ref in ("", "main")
            else f"npx skills add -y -g {s_src}#{s_ref}"
        )
        lines.append(f"## {slug}")
        lines.append(f"- **Description**: {desc_short}")
        if hint:
            lines.append(f"- **When to suggest**: {hint}")
        lines.append(f"- **Install**: `{install_cmd}`")
        lines.append("")

    lines.append("> This file is auto-updated after install/uninstall/upgrade.")
    lines.append("> It will be removed once all skills are installed.")
    lines.append("")

    discovery_dir.mkdir(parents=True, exist_ok=True)
    (discovery_dir / "SKILL.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )
    verbose(f"discovery skill refreshed: {len(uninstalled)} uninstalled skill(s)")


def _wrap_yaml(lines: List[str], text: str, indent: int = 2) -> None:
    """Append *text* to *lines* with simple wrapping for YAML block scalars."""
    prefix = " " * indent
    words = text.split()
    current = prefix
    for w in words:
        if len(current) + len(w) + 1 > 80 and current.strip():
            lines.append(current)
            current = prefix + w
        else:
            current = current + " " + w if current.strip() else prefix + w
    if current.strip():
        lines.append(current)


# ---------------------------------------------------------------------------
# Version-check injection (installed SKILL.md post-processing)
# ---------------------------------------------------------------------------

_VC_MARKERS = ("## CLI: Version Update Check", "## CLI: 版本更新检查")

_VC_EN = (
    "## CLI: Version Update Check\n"
    "\n"
    "Embed the version check into the skill's **single Bash call**. "
    "**Do not create any separate tool call** for the version check.\n"
    "\n"
    "Start the check as a backgrounded subprocess **before** the business "
    "command (e.g. `curl`), then append `wait` **after** the business command "
    "to collect the result, all in one invocation:\n"
    "\n"
    "```bash\n"
    "{cli} check --quiet --slug {slug} 2>/dev/null "
    "> /tmp/.{slug}-update 2>/dev/null & "
    "curl -sG '...' ...; "
    "wait; "
    "cat /tmp/.{slug}-update 2>/dev/null; "
    "rm -f /tmp/.{slug}-update\n"
    "```\n"
    "\n"
    "Inspect the `cat` output line by line:\n"
    "\n"
    "- **No content** (everything up-to-date, `{cli}` not installed, or check "
    "failed): do not show any upgrade prompt.\n"
    "- **A line starting with `{slug}`** (this skill has an update available): "
    "append a notice at the **end** of your reply:\n"
    "  > `{slug}` has a new version available. If you agree, I can upgrade "
    "it for you right away.\n"
    "\n"
    "  If the user agrees, run `{cli} upgrade {slug}` to perform the upgrade. "
    "(This command also auto-upgrades the CLI itself, so no separate CLI "
    "prompt is needed when a skill update is present.)\n"
    "- **Only a line starting with `cli`** (skill is current, but the CLI "
    "manager itself has an update): append a notice at the **end** of your "
    "reply:\n"
    "  > The `{cli}` manager has a new version available. If you agree, I can "
    "upgrade it for you right away.\n"
    "\n"
    "  If the user agrees, run `{cli} self-upgrade` to perform the upgrade.\n"
    "\n"
    "If both lines are present, only show the skill upgrade prompt — the CLI "
    "will be refreshed as a side effect of `{cli} upgrade {slug}`.\n"
    "\n"
    "If `{cli}` is not installed or the check encounters any error, silently "
    "skip without affecting normal skill execution.\n"
    "\n"
    "**Important**: The version check (write + read) must all be embedded in "
    "this single Bash call. Do not produce any additional tool calls.\n"
)

_VC_ZH = (
    "## CLI: 版本更新检查\n"
    "\n"
    "将版本检查**嵌入技能的唯一一次 Bash 调用**中，"
    "**不得为版本检查单独发起任何工具调用**。\n"
    "\n"
    "在业务命令（如 `curl`）**前面**以后台子进程启动检查，"
    "在业务命令**后面**用 `wait` 等待检查完成并读取结果，整体结构如下：\n"
    "\n"
    "```bash\n"
    "{cli} check --quiet --slug {slug} 2>/dev/null "
    "> /tmp/.{slug}-update 2>/dev/null & "
    "curl -sG '...' ...; "
    "wait; "
    "cat /tmp/.{slug}-update 2>/dev/null; "
    "rm -f /tmp/.{slug}-update\n"
    "```\n"
    "\n"
    "按行检查 `cat` 的输出：\n"
    "\n"
    "- **无内容**（全部已是最新、`{cli}` 未安装、或检查失败）："
    "不显示任何升级提示。\n"
    "- **包含以 `{slug}` 开头的行**（当前技能有新版本）：在回复**末尾**追加提示：\n"
    "  > `{slug}` 有新版本可用，若您同意，我可以立即为您升级。\n"
    "\n"
    "  如果用户同意，执行 `{cli} upgrade {slug}` 进行升级。"
    "（该命令会自动顺带升级 CLI 本身，因此当技能存在更新时无需再单独提示 CLI 升级。）\n"
    "- **只包含以 `cli` 开头的行**（技能已是最新，但管理工具 CLI 自身有新版本）："
    "在回复**末尾**追加提示：\n"
    "  > 管理工具 `{cli}` 有新版本可用，若您同意，我可以立即为您升级。\n"
    "\n"
    "  如果用户同意，执行 `{cli} self-upgrade` 进行升级。\n"
    "\n"
    "若两类行同时出现，只展示技能升级提示——`{cli} upgrade {slug}` 会顺带刷新 CLI。\n"
    "\n"
    "若 `{cli}` 未安装或检查遇到任何错误，静默跳过，不影响技能正常执行。\n"
    "\n"
    "**重要**：版本检查（写入 + 读取）必须全部嵌入这一次 Bash 调用，"
    "不得产生额外的工具调用。\n"
)


def _inject_version_check(skill_dir: Path, slug: str, cli: str) -> None:
    """Inject version-check instructions into the installed SKILL.md.

    Only the *installed copy* is modified – the upstream source maintained by
    business teams is never touched.  Idempotent: skips if the marker heading
    already exists.
    """
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        return

    text = skill_md.read_text(encoding="utf-8")

    # Idempotency: skip if already present
    for marker in _VC_MARKERS:
        if marker in text:
            return

    # Language detection – check body (after frontmatter) for CJK vs Latin ratio
    body = text
    parts = text.split("---", 2)
    if len(parts) >= 3:
        body = parts[2]
    cjk_count = len(re.findall(r"[\u4e00-\u9fff]", body))
    latin_count = len(re.findall(r"[a-zA-Z]", body))
    is_chinese = cjk_count > latin_count * 0.3 if latin_count else cjk_count > 0

    section = (_VC_ZH if is_chinese else _VC_EN).format(cli=cli, slug=slug)

    # Insert after frontmatter, before first body content
    if len(parts) >= 3:
        new_text = "---" + parts[1] + "---\n\n" + section + "\n" + parts[2].lstrip("\n")
    else:
        new_text = text + "\n\n" + section + "\n"

    skill_md.write_text(new_text, encoding="utf-8")
    verbose(f"injected version check into {slug}/SKILL.md")


def _cleanup_guard_skill(install_root: Path) -> None:
    """Remove the legacy guard skill directory if it exists."""
    guard_dir = install_root / "_futu-skill-guard"
    if guard_dir.is_dir():
        shutil.rmtree(guard_dir)
        verbose("removed legacy guard skill")


# ---------------------------------------------------------------------------
# Install / copy
# ---------------------------------------------------------------------------


def _repo_cache_dir(url: str, ref: str) -> Path:
    """Stable per-(repo,ref) cache directory under ~/.futu-skillhub/cache/repos/."""
    key = hashlib.sha256(f"{url}#{ref}".encode("utf-8")).hexdigest()[:16]
    return cache_dir() / "repos" / key


def _git_ensure_repo(url: str, ref: str, *, force_refresh: bool) -> Path:
    """Clone or refresh a shallow local copy of the skill repo. Returns the working tree path."""
    if shutil.which("git") is None:
        print("error: git is required to install skills", file=sys.stderr)
        raise SystemExit(3)

    target = _repo_cache_dir(url, ref)
    if target.is_dir() and not force_refresh and (target / ".git").exists():
        try:
            subprocess.run(
                ["git", "-C", str(target), "fetch", "--depth=1", "origin", ref],
                check=True, capture_output=True, timeout=120,
            )
            subprocess.run(
                ["git", "-C", str(target), "reset", "--hard", f"origin/{ref}"],
                check=True, capture_output=True, timeout=60,
            )
            return target
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            verbose(f"git refresh failed, re-cloning: {e}")
            shutil.rmtree(target, ignore_errors=True)

    if target.exists():
        shutil.rmtree(target, ignore_errors=True)
    target.parent.mkdir(parents=True, exist_ok=True)
    print(f"git clone {url} (ref {ref})", file=sys.stderr)
    try:
        subprocess.run(
            ["git", "clone", "--depth=1", "--branch", ref, url, str(target)],
            check=True, capture_output=True, timeout=300,
        )
    except subprocess.CalledProcessError as e:
        err = (e.stderr or b"").decode("utf-8", errors="replace").strip()
        print(f"error: git clone failed: {err or e}", file=sys.stderr)
        raise SystemExit(3)
    return target


def _try_npx_skills_add(slug: str, dest_skill: Path) -> bool:
    """Try `npx skills add <slug> --dir <parent>`. Returns True iff dest_skill now exists."""
    if shutil.which("npx") is None:
        return False
    try:
        proc = subprocess.run(
            ["npx", "-y", "skills", "add", slug, "--dir", str(dest_skill.parent)],
            capture_output=True, timeout=180,
        )
        if proc.returncode != 0:
            verbose(f"npx skills add {slug} exited {proc.returncode}: "
                    f"{proc.stderr.decode(errors='ignore').strip()}")
            return False
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        verbose(f"npx skills add {slug} failed: {e}")
        return False
    return dest_skill.is_dir()


def install_from_source(
    meta: Dict[str, Any],
    entry: Dict[str, Any],
    slug: str,
    dest_skill: Path,
    *,
    force_refresh: bool,
) -> None:
    """
    Install a skill from its git repo.

    Strategy: prefer `npx skills add` when available; otherwise clone the repo
    declared in metadata.repo_url and locate the skill directory by convention:
    a directory named `<slug>` containing `SKILL.md`. If the repo root itself
    matches (single-skill repo), use the repo root.
    """
    if _try_npx_skills_add(slug, dest_skill):
        return

    url = resolve_repo_url(meta, entry)
    ref = resolve_repo_ref(meta, entry)
    repo = _git_ensure_repo(url, ref, force_refresh=force_refresh)

    src = _locate_skill_dir(repo, slug)
    if src is None:
        print(
            f"error: could not locate skill directory for slug {slug!r} "
            f"in repo (expected a folder named {slug!r} containing SKILL.md, "
            f"or SKILL.md at repo root)",
            file=sys.stderr,
        )
        raise SystemExit(3)

    _remove_skill_path(dest_skill)
    dest_skill.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, dest_skill, ignore=shutil.ignore_patterns(".git"))


def _locate_skill_dir(repo: Path, slug: str) -> Optional[Path]:
    """Find the skill directory inside *repo* by convention.

    Order:
      1. Repo root itself contains SKILL.md (single-skill repo).
      2. A directory named exactly *slug* anywhere under the repo that
         contains SKILL.md.
    """
    if (repo / "SKILL.md").is_file():
        return repo
    for p in repo.rglob(slug):
        if p.is_dir() and (p / "SKILL.md").is_file():
            # Skip anything under .git
            if ".git" in p.parts:
                continue
            return p
    return None


def _remove_skill_path(dest: Path) -> bool:
    """Remove *dest* whether it's a directory, file, or (possibly broken) symlink.

    Returns True if anything was removed. ``Path.is_dir()`` returns False for
    broken symlinks, so callers that only checked ``is_dir()`` would silently
    leave dangling links behind and later trip ``shutil.copytree`` on reinstall.
    """
    if dest.is_symlink() or dest.is_file():
        try:
            dest.unlink()
            return True
        except FileNotFoundError:
            return False
    if dest.is_dir():
        shutil.rmtree(dest)
        return True
    return False


def cmd_uninstall(args: argparse.Namespace) -> None:
    meta, skills = load_index()
    slug = args.slug
    if not get_skill_entry(skills, slug):
        print(f"warning: slug {slug!r} not in index (continuing)", file=sys.stderr)
    install_root = Path(args.dir).expanduser().resolve()
    dest = install_root / slug
    if _remove_skill_path(dest):
        print(f"removed {dest}")
    else:
        print(f"not found (skipped): {dest}")
    lock = read_lock(install_root, meta)
    if slug in lock.get("skills", {}):
        del lock["skills"][slug]
        write_lock(install_root, meta, lock)
    _refresh_discovery_skill(install_root, meta, skills)
    _cleanup_guard_skill(install_root)


def cmd_list(args: argparse.Namespace) -> None:
    meta, idx_skills = load_index()
    own_product = _hub_product(meta)
    install_root = Path(args.dir).expanduser().resolve()
    catalog = _fetch_catalog(timeout=10)
    reconcile_lockfile_with_disk(install_root, meta, idx_skills, catalog)
    lock = read_lock(install_root, meta)
    skills = lock.get("skills") or {}
    # Filter to only skills belonging to this product
    if own_product:
        skills = {
            k: v for k, v in skills.items()
            if str((v or {}).get("product") or "").lower() in ("", own_product)
        }
    if not skills:
        print("(no skills in lockfile)")
        return
    headers = ("Skill", "Version")
    rows = []
    need_lock_update = False
    for slug in sorted(skills.keys()):
        info = skills[slug] or {}
        ver = info.get("version") or ""
        if not ver or ver in ("unknown", "?"):
            dest = install_root / slug
            ver = resolve_skill_version(dest, slug, catalog)
            if ver and ver != "latest":
                info["version"] = ver
                need_lock_update = True
        rows.append((slug, ver))
    if need_lock_update:
        write_lock(install_root, meta, lock)
    col_widths = [
        max(len(headers[i]), max(len(r[i]) for r in rows)) for i in range(2)
    ]
    fmt = "  ".join(f"{{:<{w}}}" for w in col_widths)
    print(fmt.format(*headers))
    print("  ".join("-" * w for w in col_widths))
    for r in rows:
        print(fmt.format(*r))
    print(f"\n{len(rows)} skill(s) installed")


def cmd_search(args: argparse.Namespace) -> None:
    _, skills = load_index()
    q = " ".join(args.query or "").strip().lower()
    product = (args.product or "").lower() or None
    results: List[Dict[str, Any]] = []
    for s in skills:
        if product and str(s.get("product", "")).lower() != product:
            continue
        if not q:
            results.append(s)
            continue
        hay = " ".join(
            [
                str(s.get("slug", "")),
                str(s.get("name", "")),
                str(s.get("description", "")),
                " ".join(s.get("keywords") or []),
            ]
        ).lower()
        if all(part in hay for part in q.split()):
            results.append(s)

    if args.count:
        print(len(results))
        return
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return
    if not results:
        print("No skills found.")
        return

    # Resolve install root; load local catalog as fallback, remote catalog for latest
    install_root = Path(args.dir).expanduser().resolve()
    local_catalog = _load_local_catalog()
    remote_catalog = _fetch_catalog(timeout=5)

    headers = ("Skill", "Product", "Installed", "Local", "Remote", "Description")
    rows = []
    for s in results:
        slug = str(s.get("slug", ""))
        dest = install_root / slug
        installed = "yes" if dest.is_dir() else "no"
        # Local: read actual installed SKILL.md version first, fallback to local catalog
        local_ver = read_skill_version(dest) if dest.is_dir() else ""
        if not local_ver and local_catalog:
            local_ver = parse_catalog_skill_version(local_catalog, slug) or ""
        if not local_ver:
            local_ver = "-"
        remote_ver = parse_catalog_skill_version(remote_catalog, slug) if remote_catalog else "-"
        if not remote_ver:
            remote_ver = "-"
        rows.append((
            slug,
            str(s.get("product", "")),
            installed,
            local_ver,
            remote_ver,
            str(s.get("description", ""))[:60],
        ))
    col_widths = [
        max(len(headers[i]), max(len(r[i]) for r in rows)) for i in range(len(headers))
    ]
    fmt = "  ".join(f"{{:<{w}}}" for w in col_widths)
    print(fmt.format(*headers))
    print("  ".join("-" * w for w in col_widths))
    for r in rows:
        print(fmt.format(*r))
    print(f"\n{len(results)} skill(s) found")


def _load_local_catalog() -> Optional[Dict[str, Any]]:
    """Load the local skill_catalog.json shipped with the CLI package."""
    p = cli_dir() / "skill_catalog.json"
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _update_local_catalog_version(slug: str, version: str) -> None:
    """Update a skill's version in the local skill_catalog.json."""
    p = cli_dir() / "skill_catalog.json"
    catalog = _load_local_catalog()
    if catalog is None:
        catalog = {"skills": {}}
    skills = catalog.setdefault("skills", {})
    if skills.get(slug) == version:
        return
    skills[slug] = version
    save_json(p, catalog)
    verbose(f"local catalog updated: {slug} -> {version}")


def _fetch_catalog(timeout: int) -> Optional[Dict[str, Any]]:
    """Fetch skill catalog for version comparison. Returns None on failure."""
    curl = skill_catalog_url()
    if not curl:
        return None
    return fetch_json_url(curl, timeout=timeout)


def cmd_upgrade(args: argparse.Namespace) -> None:
    """Upgrade installed skills, skipping those already at the latest catalog version."""
    meta, skills = load_index()
    own_product = _hub_product(meta)
    install_root = Path(args.dir).expanduser().resolve()
    reconcile_lockfile_with_disk(install_root, meta, skills)
    lock = read_lock(install_root, meta)
    installed = lock.get("skills") or {}
    # Filter to only skills belonging to this product
    if own_product:
        installed = {
            k: v for k, v in installed.items()
            if str((v or {}).get("product") or "").lower() in ("", own_product)
        }
    targets = []
    if args.slug:
        if args.slug not in installed:
            print(f"error: skill not installed: {args.slug}", file=sys.stderr)
            raise SystemExit(1)
        targets = [args.slug]
    else:
        targets = list(installed.keys())

    catalog = _fetch_catalog(timeout=args.timeout)
    if not catalog and not args.force:
        print(
            "warning: could not fetch skill catalog; use --force to upgrade without version check",
            file=sys.stderr,
        )

    # --- Deprecation handling ---
    deprecated_slugs: List[str] = []
    migrate_installs: List[str] = []  # new slugs to install after removing old ones
    if catalog:
        for slug in list(targets):
            dep = parse_catalog_deprecation(catalog, slug)
            if not dep:
                continue
            action = dep.get("action", "remove")
            message = dep.get("message", "")
            if action == "migrate":
                new_slug = dep.get("replace_with", "")
                if args.check_only:
                    print(f"{slug}\tDEPRECATED -> migrate to {new_slug}. {message}")
                else:
                    print(f"deprecated: {slug} -> migrating to {new_slug}. {message}")
                    if new_slug:
                        migrate_installs.append(new_slug)
            else:
                if args.check_only:
                    print(f"{slug}\tDEPRECATED -> will be removed. {message}")
                else:
                    print(f"deprecated: {slug} -> removing. {message}")
            deprecated_slugs.append(slug)
            targets.remove(slug)

    initial_targets = set(targets)
    migration_set = set(migrate_installs)

    def _enqueue_deps(skill_dir: Path, queue: List[str], seen: set) -> None:
        if not skill_dir.is_dir():
            return
        for d in read_skill_deps(skill_dir):
            if d not in seen and d not in queue:
                queue.append(d)

    if args.check_only:
        queue = list(targets)
        seen: set = set()
        while queue:
            slug = queue.pop(0)
            if slug in seen:
                continue
            seen.add(slug)
            entry = get_skill_entry(skills, slug)
            if not entry:
                print(f"{slug}\tskip (unknown slug)")
                continue
            dest = install_root / slug
            local_ver = read_skill_version(dest) if dest.is_dir() else ""
            remote_ver = parse_catalog_skill_version(catalog, slug) if catalog else None
            origin = "" if slug in initial_targets else "\t(dependency)"
            if not dest.is_dir():
                status = "missing (will install)"
            elif remote_ver and local_ver and not version_is_newer(remote_ver, local_ver):
                status = "up to date"
            elif remote_ver:
                status = "update available"
            else:
                status = "no catalog info"
            print(f"{slug}\tlocal={local_ver or '?'}\tremote={remote_ver or '?'}\t{status}{origin}")
            _enqueue_deps(dest, queue, seen)
        return

    # Process deprecation removals
    removed = 0
    for slug in deprecated_slugs:
        dest = install_root / slug
        _remove_skill_path(dest)
        if slug in lock.get("skills", {}):
            del lock["skills"][slug]
        removed += 1

    # --- Unified install/upgrade queue (migrations + normal targets + transitive deps) ---
    upgrade_queue: List[str] = list(migrate_installs) + list(targets)
    processed: set = set()
    failed = 0
    skipped = 0
    upgraded = 0
    migrated = 0
    dep_added = 0
    repo_refreshed: set = set()
    while upgrade_queue:
        slug = upgrade_queue.pop(0)
        if slug in processed:
            continue
        processed.add(slug)
        entry = get_skill_entry(skills, slug)
        if not entry:
            print(f"skip unknown slug: {slug}", file=sys.stderr)
            failed += 1
            continue
        dest = install_root / slug
        is_migration = slug in migration_set
        is_dep = slug not in initial_targets and not is_migration

        # Version-skip only applies to already-installed, non-migration skills.
        if not args.force and catalog and dest.is_dir() and not is_migration:
            local_ver = read_skill_version(dest)
            remote_ver = parse_catalog_skill_version(catalog, slug)
            if remote_ver and local_ver and not version_is_newer(remote_ver, local_ver):
                verbose(f"{slug}: already up to date ({local_ver})")
                skipped += 1
                _enqueue_deps(dest, upgrade_queue, processed)
                continue

        try:
            cur_url = resolve_repo_url(meta, entry)
            force_refresh = is_migration or (cur_url not in repo_refreshed)
            install_from_source(meta, entry, slug, dest, force_refresh=force_refresh)
            repo_refreshed.add(cur_url)
            _inject_version_check(dest, slug, "futu-skills")
            ver = resolve_skill_version(dest, slug, catalog)
            lock["skills"][slug] = {
                "name": entry.get("name") or slug,
                "version": ver,
                "source": "futu-skillhub",
                "source_url": resolve_repo_url(meta, entry),
                "product": entry.get("product"),
            }
            _update_local_catalog_version(slug, ver)
            if is_migration:
                migrated += 1
                print(f"installed {slug} (migration) -> {ver}")
            elif is_dep:
                dep_added += 1
                print(f"installed dependency {slug} -> {ver}")
            else:
                upgraded += 1
                print(f"upgraded {slug} -> {ver}")
            _enqueue_deps(dest, upgrade_queue, processed)
        except SystemExit:
            raise
        except Exception as e:
            kind = "migrate install" if is_migration else ("install dep" if is_dep else "upgrade")
            print(f"error: {kind} {slug}: {e}", file=sys.stderr)
            failed += 1
    write_lock(install_root, meta, lock)

    # Summary
    parts = []
    if removed:
        parts.append(f"{removed} removed")
    if migrated:
        parts.append(f"{migrated} migrated")
    if upgraded:
        parts.append(f"{upgraded} upgraded")
    if dep_added:
        parts.append(f"{dep_added} dependency installed")
    if skipped:
        parts.append(f"{skipped} up to date")
    if failed:
        parts.append(f"{failed} failed")
    if parts:
        print(f"\nSummary: {', '.join(parts)}")
    _refresh_discovery_skill(install_root, meta, skills)
    _cleanup_guard_skill(install_root)
    if failed:
        raise SystemExit(2)


def default_skills_dir() -> str:
    return resolve_skills_dir()[0]


def cmd_self_upgrade(args: argparse.Namespace) -> None:
    run_self_upgrade(
        check_only=args.check_only,
        timeout=args.timeout,
        force_exec=False,
        force=args.force,
    )
    # After manual self-upgrade, refresh discovery skill (index may have new skills)
    if not args.check_only:
        try:
            ir = Path(default_skills_dir()).expanduser().resolve()
            if ir.is_dir():
                meta, skills = load_index()
                _refresh_discovery_skill(ir, meta, skills)
                _cleanup_guard_skill(ir)
        except Exception as e:
            verbose(f"post-self-upgrade discovery refresh skipped: {e}")


def cmd_detect(args: argparse.Namespace) -> None:
    path, reason = resolve_skills_dir()
    if args.json:
        print(json.dumps({"path": path, "resolution": reason}, ensure_ascii=False))
    else:
        print(f"# {reason}", file=sys.stderr)
        print(path)


def cmd_check_opend(args: argparse.Namespace) -> None:
    """Check if OpenD is reachable on the configured host:port."""
    import socket

    host = args.host or os.environ.get("FUTU_OPEND_HOST", "127.0.0.1")
    port = args.port or int(os.environ.get("FUTU_OPEND_PORT", "11111"))
    timeout = args.timeout

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect((host, port))
        s.close()
        print("ok")
    except (OSError, socket.timeout):
        print("not-running")
        raise SystemExit(1)


def cmd_refresh_discovery(args: argparse.Namespace) -> None:
    """Regenerate the discovery SKILL.md based on current install state."""
    install_root = Path(args.dir).expanduser().resolve()
    meta, skills = load_index()
    _refresh_discovery_skill(install_root, meta, skills)
    _cleanup_guard_skill(install_root)
    print(f"discovery skill refreshed at {install_root / _discovery_dir_name(meta)}")


def cmd_check(args: argparse.Namespace) -> None:
    install_root = Path(args.dir).expanduser().resolve()
    r = run_update_check(install_root, timeout=args.timeout)

    # Refresh discovery skill based on current disk + lockfile state, so users
    # who installed skills directly via `npx skills add` (bypassing the CLI)
    # also get their _*-skillhub/SKILL.md reconciled on the next `check`.
    try:
        meta, skills = load_index()
        _refresh_discovery_skill(install_root, meta, skills)
        _cleanup_guard_skill(install_root)
    except Exception as e:
        verbose(f"discovery refresh skipped: {e}")

    if args.quiet:
        if not r["outdated"]:
            return
        slug_filter = getattr(args, "slug", None)
        show_cli = not slug_filter or slug_filter == "cli"
        if show_cli and r["cli"]["outdated"]:
            print(f"cli\t{r['cli']['local']}\t{r['cli']['remote']}")
        for s in r["skills"]:
            if slug_filter and s["slug"] != slug_filter:
                continue
            if s["status"] == "update_available":
                print(f"{s['slug']}\t{s['local']}\t{s['remote']}")
            elif s["status"] in ("deprecated_remove", "deprecated_migrate"):
                dep = s.get("deprecation") or {}
                print(f"{s['slug']}\tdeprecated\t{dep.get('action', 'remove')}")
        raise SystemExit(1)

    if args.json:
        print(json.dumps(r, ensure_ascii=False, indent=2))
        if args.strict and r["outdated"]:
            raise SystemExit(1)
        return

    c = r["cli"]
    if c.get("remote"):
        tag = "update available" if c["outdated"] else "up to date"
        print(f"CLI: {tag} (local {c['local']}, remote {c['remote']})")
    else:
        print(f"CLI: manifest unavailable (local {c['local']})")

    if r.get("catalog_error"):
        print(f"Skills: {r['catalog_error']}", file=sys.stderr)
    elif not r["skills"]:
        print("Skills: (none in lockfile)")
    else:
        print("Skills:")
        for s in r["skills"]:
            if s["status"] == "deprecated_remove":
                dep = s.get("deprecation") or {}
                msg = dep.get("message", "")
                print(f"  {s['slug']}: DEPRECATED — will be removed on upgrade. {msg}")
            elif s["status"] == "deprecated_migrate":
                dep = s.get("deprecation") or {}
                new = dep.get("replace_with", "?")
                msg = dep.get("message", "")
                print(f"  {s['slug']}: DEPRECATED — will be replaced by {new} on upgrade. {msg}")
            elif s["status"] == "update_available":
                print(
                    f"  {s['slug']}: update available "
                    f"(local {s['local']} -> catalog {s['remote']})"
                )
            elif s["status"] == "up_to_date":
                print(f"  {s['slug']}: up to date ({s['local']})")
            elif s["status"] == "not_in_catalog":
                print(f"  {s['slug']}: not listed in catalog (local {s['local']})")
            else:
                print(f"  {s['slug']}: {s['status']} (local {s['local']})")

    if r["outdated"]:
        print(
            "\nIf you'd like, I can upgrade them for you right now.",
            file=sys.stderr,
        )
    if args.strict and r["outdated"]:
        raise SystemExit(1)


def maybe_announce_skill_updates(args: argparse.Namespace) -> None:
    if os.environ.get(ENV_ANNOUNCE_UPDATES, "").lower() not in (
        "1",
        "true",
        "yes",
    ):
        return
    if args.cmd in ("check", "self-upgrade", "detect"):
        return
    dir_arg = getattr(args, "dir", None)
    if not dir_arg:
        return
    install_root = Path(dir_arg).expanduser().resolve()
    try:
        r = run_update_check(install_root, timeout=3)
    except Exception as e:
        verbose(f"announce updates skipped: {e}")
        return
    if not r["outdated"]:
        return
    parts: List[str] = []
    if r["cli"]["outdated"]:
        parts.append("CLI")
    for s in r["skills"]:
        if s["status"] == "update_available":
            parts.append(s["slug"])
    if not parts:
        return
    hub_name = str(load_metadata().get("hub_name") or "futu-skillhub")
    print(
        f"[{hub_name}] Updates available: "
        + ", ".join(parts)
        + ". If you'd like, I can upgrade them for you right now.",
        file=sys.stderr,
    )


def build_parser() -> argparse.ArgumentParser:
    ver = load_version()
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(
        "--dir",
        dest="dir",
        default=default_skills_dir(),
        help=(
            "skills install root (default: resolve Cursor ~/.cursor/skills, "
            f"workspace .cursor/skills, env {ENV_SKILLS_DIR} / {ENV_CURSOR_SKILLS}, "
            "else ./skills — see detect)"
        ),
    )
    p = argparse.ArgumentParser(
        prog="futu-skills",
        description="Futu AI skills manager",
    )
    p.add_argument("--version", action="version", version=f"%(prog)s {ver}")
    p.add_argument(
        "--skip-self-upgrade",
        action="store_true",
        help="skip automatic CLI update check on startup (before other subcommands)",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser(
        "search",
        help="search local skill index",
        parents=[common],
    )
    sp.add_argument("query", nargs="*", help="keywords (AND match)")
    sp.add_argument("--json", action="store_true", help="JSON output")
    sp.add_argument("--count", action="store_true", help="print only the number of matching skills")
    sp.add_argument(
        "--product",
        choices=["futu"],
        help="filter by product",
    )
    sp.set_defaults(func=cmd_search)

    sub.add_parser(
        "list",
        help="list installed skills (from lockfile)",
        parents=[common],
    ).set_defaults(func=cmd_list)

    up = sub.add_parser(
        "upgrade",
        help="upgrade installed skills (skip if already at latest catalog version)",
        parents=[common],
    )
    up.add_argument("slug", nargs="?", help="upgrade one slug; default: all")
    up.add_argument(
        "--check-only",
        action="store_true",
        help="compare local vs catalog versions without downloading",
    )
    up.add_argument(
        "--force",
        action="store_true",
        help="re-download and overwrite even if already up to date",
    )
    up.add_argument(
        "--timeout",
        type=int,
        default=10,
        metavar="SEC",
        help="HTTP timeout for catalog fetch (default: 10)",
    )
    up.set_defaults(func=cmd_upgrade)

    un = sub.add_parser(
        "uninstall",
        help="remove an installed skill",
        parents=[common],
    )
    un.add_argument("slug")
    un.set_defaults(func=cmd_uninstall)

    su = sub.add_parser(
        "self-upgrade",
        help="fetch cli_update_manifest.json and upgrade CLI files in-place",
    )
    su.add_argument(
        "--check-only",
        action="store_true",
        help="only compare versions, do not download",
    )
    su.add_argument(
        "--force",
        action="store_true",
        help="reinstall even if versions match",
    )
    su.add_argument(
        "--timeout",
        type=int,
        default=25,
        metavar="SEC",
        help="HTTP timeout for manifest and file downloads (default: 25)",
    )
    su.set_defaults(func=cmd_self_upgrade)

    det = sub.add_parser(
        "detect",
        help="print resolved default skills directory (Cursor / workspace / env)",
    )
    det.add_argument("--json", action="store_true", help="JSON with path and resolution")
    det.set_defaults(func=cmd_detect)

    chk = sub.add_parser(
        "check",
        help="compare CLI + installed skills vs remote manifest and skill catalog",
        parents=[common],
    )
    chk.add_argument(
        "--json",
        action="store_true",
        help="machine-readable report",
    )
    chk.add_argument(
        "--quiet",
        action="store_true",
        help="only print outdated lines; exit 1 if any",
    )
    chk.add_argument(
        "--strict",
        action="store_true",
        help="exit with status 1 if anything is outdated (use with human or --json)",
    )
    chk.add_argument(
        "--timeout",
        type=int,
        default=8,
        metavar="SEC",
        help="HTTP timeout for manifest and catalog (default: 8)",
    )
    chk.add_argument(
        "--slug",
        default=None,
        help="filter quiet output to this slug (and cli); replaces external grep",
    )
    chk.set_defaults(func=cmd_check)

    rd = sub.add_parser(
        "refresh-discovery",
        help="regenerate the discovery SKILL.md from current install state",
        parents=[common],
    )
    rd.set_defaults(func=cmd_refresh_discovery)

    co = sub.add_parser(
        "check-opend",
        help="check if OpenD is reachable (cross-platform, exits 0=ok, 1=not running)",
    )
    co.add_argument("--host", default=None, help="OpenD host (default: $FUTU_OPEND_HOST or 127.0.0.1)")
    co.add_argument("--port", type=int, default=None, help="OpenD port (default: $FUTU_OPEND_PORT or 11111)")
    co.add_argument("--timeout", type=float, default=2.0, help="connection timeout in seconds (default: 2)")
    co.set_defaults(func=cmd_check_opend)

    return p


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if (
        not args.skip_self_upgrade
        and args.cmd not in ("self-upgrade", "check", "detect")
        and os.environ.get(ENV_SELF_UPGRADE_REEXEC) != "1"
    ):
        try:
            maybe_startup_self_upgrade(sys.argv)
        except (Exception, SystemExit) as e:
            verbose(f"startup self-upgrade skipped: {e}")

    # After CLI self-upgrade re-exec, the index may contain new skills.
    # Refresh the discovery skill so uninstalled ones become visible.
    if os.environ.get(ENV_SELF_UPGRADE_REEXEC) == "1":
        try:
            dir_arg = getattr(args, "dir", None) or default_skills_dir()
            ir = Path(dir_arg).expanduser().resolve()
            if ir.is_dir():
                meta, skills = load_index()
                _refresh_discovery_skill(ir, meta, skills)
                _cleanup_guard_skill(ir)
        except Exception as e:
            verbose(f"post-upgrade discovery refresh skipped: {e}")

    try:
        maybe_announce_skill_updates(args)
    except Exception as e:
        verbose(f"announce updates skipped: {e}")
    args.func(args)


if __name__ == "__main__":
    main()
