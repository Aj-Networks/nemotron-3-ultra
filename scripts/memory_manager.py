#!/usr/bin/env python3
"""
Nemotron 3 Ultra Memory & Cache Manager
Handles project isolation, global memory, caching, and session sync.
"""

import os
import json
import hashlib
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List

ROOT = Path(__file__).parent.parent
MEMORY_GLOBAL = ROOT / "memory" / "global" / "MEMORY.md"
MEMORY_PROJECTS = ROOT / "projects"
CACHE_GLOBAL = ROOT / "cache" / "global"
CACHE_PROJECTS = ROOT / "cache" / "projects"


def ensure_dirs():
    """Create all required directories."""
    for d in [MEMORY_PROJECTS, CACHE_GLOBAL, CACHE_PROJECTS]:
        d.mkdir(parents=True, exist_ok=True)


def get_project_path(name: str) -> Path:
    """Get project directory, create if needed."""
    path = MEMORY_PROJECTS / name
    path.mkdir(parents=True, exist_ok=True)
    (path / "input").mkdir(exist_ok=True)
    (path / "output").mkdir(exist_ok=True)
    (path / "cache").mkdir(exist_ok=True)
    return path


def get_project_memory(name: str) -> Path:
    """Get project MEMORY.md path."""
    return get_project_path(name) / "MEMORY.md"


def get_project_cache(name: str) -> Path:
    """Get project cache directory."""
    path = CACHE_PROJECTS / name
    path.mkdir(parents=True, exist_ok=True)
    return path


def read_memory(path: Path) -> str:
    """Read memory file."""
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


def write_memory(path: Path, content: str):
    """Write memory file with timestamp."""
    header = f"# Updated: {datetime.now().isoformat()}\n\n"
    path.write_text(header + content, encoding="utf-8")


def init_project(name: str, description: str = "") -> Dict[str, Any]:
    """Initialize a new project with memory and cache."""
    ensure_dirs()
    project_path = get_project_path(name)
    memory_path = get_project_memory(name)

    if not memory_path.exists():
        template = f"""# Project Memory: {name}

## Description
{description or "No description provided."}

## Context
- Created: {datetime.now().isoformat()}
- Model: Nemotron 3 Ultra 550B-A55B
- Provider: NVIDIA Free API (build.nvidia.com)

## Project-Specific Rules
- Add rules here that override global memory

## Key Files & Artifacts
- Input folder: `projects/{name}/input/`
- Output folder: `projects/{name}/output/`
- Cache folder: `cache/projects/{name}/`

## Session History
- Session 1: {datetime.now().date()} - Initialized

## Important Context
- Add critical context that persists across sessions
"""
        write_memory(memory_path, template)

    return {
        "name": name,
        "path": str(project_path),
        "memory": str(memory_path),
        "input": str(project_path / "input"),
        "output": str(project_path / "output"),
        "cache": str(get_project_cache(name)),
    }


def cache_key(prompt: str, context: str = "") -> str:
    """Generate cache key from prompt + context."""
    combined = f"{prompt}|{context}"
    return hashlib.sha256(combined.encode()).hexdigest()[:16]


def cache_get(project: str, key: str) -> Optional[str]:
    """Retrieve cached response."""
    cache_dir = CACHE_GLOBAL if project == "global" else get_project_cache(project)
    cache_file = cache_dir / f"{key}.json"
    if cache_file.exists():
        data = json.loads(cache_file.read_text())
        # Check TTL (default 24 hours)
        if (datetime.now() - datetime.fromisoformat(data["timestamp"])).total_seconds() < 86400:
            return data["response"]
    return None


def cache_set(project: str, key: str, response: str, metadata: Dict = None):
    """Store response in cache."""
    cache_dir = CACHE_GLOBAL if project == "global" else get_project_cache(project)
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_file = cache_dir / f"{key}.json"
    data = {
        "timestamp": datetime.now().isoformat(),
        "response": response,
        "metadata": metadata or {},
    }
    cache_file.write_text(json.dumps(data, indent=2))


def list_projects() -> List[str]:
    """List all projects."""
    ensure_dirs()
    return [d.name for d in MEMORY_PROJECTS.iterdir() if d.is_dir()]


def sync_global_memory():
    """Pull latest global memory (placeholder for git sync)."""
    # In production: git pull origin main -- memory/global/MEMORY.md
    print("Global memory sync: manual git pull required")
    return read_memory(MEMORY_GLOBAL)


def show_status():
    """Show system status."""
    ensure_dirs()
    print(f"Root: {ROOT}")
    print(f"Global Memory: {MEMORY_GLOBAL} ({'exists' if MEMORY_GLOBAL.exists() else 'missing'})")
    print(f"Projects: {list_projects()}")
    print(f"Global Cache: {len(list(CACHE_GLOBAL.glob('*.json')))} entries")
    for p in list_projects():
        pcache = get_project_cache(p)
        print(f"  Project '{p}': {len(list(pcache.glob('*.json')))} cache entries")


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python memory_manager.py <command> [args]")
        print("Commands: init <name> [desc], list, status, sync, cache-get <project> <key>, cache-set <project> <key> <response>")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "init":
        name = sys.argv[2] if len(sys.argv) > 2 else "default"
        desc = sys.argv[3] if len(sys.argv) > 3 else ""
        result = init_project(name, desc)
        print(f"Initialized project: {result}")
    elif cmd == "list":
        print("Projects:", list_projects())
    elif cmd == "status":
        show_status()
    elif cmd == "sync":
        sync_global_memory()
    elif cmd == "cache-get":
        project, key = sys.argv[2], sys.argv[3]
        val = cache_get(project, key)
        print(val if val else "MISS")
    elif cmd == "cache-set":
        project, key, response = sys.argv[2], sys.argv[3], sys.argv[4]
        cache_set(project, key, response)
        print("OK")
    else:
        print(f"Unknown command: {cmd}")