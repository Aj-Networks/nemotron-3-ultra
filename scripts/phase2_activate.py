#!/usr/bin/env python3
"""
Phase 2: Memory & Prompt Auto-Activation
Loads global memory and project memory, then writes them to AGENTS.md in the
project folder. OpenCode reads AGENTS.md automatically when it starts there.
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Optional

ROOT = Path(__file__).parent.parent

class Phase2Activator:
    def __init__(self, project_name: str = "default"):
        self.project_name = project_name
        self.project_path = ROOT / "projects" / project_name
        self.global_memory_path = ROOT / "memory" / "global" / "MEMORY.md"
        self.project_memory_path = self.project_path / "MEMORY.md"
        self.limitations_path = ROOT / "docs" / "00-limitations.md"

    def load_file(self, path: Path) -> str:
        if path.exists():
            return path.read_text(encoding="utf-8")
        return ""

    def load_global_memory(self) -> str:
        return self.load_file(self.global_memory_path)

    def load_project_memory(self) -> str:
        return self.load_file(self.project_memory_path)

    def load_limitations(self) -> str:
        return self.load_file(self.limitations_path)

    def load_recent_cache(self, max_entries: int = 5) -> List[Dict]:
        """Load recent cache entries for context."""
        cache_dir = ROOT / "cache" / "projects" / self.project_name
        if not cache_dir.exists():
            return []
        entries = []
        for cache_file in sorted(cache_dir.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True)[:max_entries]:
            try:
                data = json.loads(cache_file.read_text())
                entries.append({
                    "key": cache_file.stem,
                    "response": data.get("response", "")[:500],  # Truncate
                    "timestamp": data.get("timestamp", ""),
                })
            except:
                pass
        return entries

    def build_system_prompt(self) -> str:
        """Build the complete system prompt with all memories and rules."""
        parts = []

        # 1. Core Identity & Rules
        parts.append("""# SYSTEM PROMPT: Nemotron 3 Ultra + OpenCode
You are a coding assistant running via OpenCode with NVIDIA Nemotron 3 Ultra (550B-A55B).
Model: nvidia/nvidia/nemotron-3-ultra-550b-a55b via NVIDIA free API (build.nvidia.com).

## CORE RULES (HIGHEST PRIORITY)
1. Solution first, education second. Lead with answer/fix/action. No preambles.
2. Minimum words. Default reply = short: do the thing, one confirmation line, stop.
3. Direct questions get direct answers. Number, ratio, yes/no, name, path → reply with ONLY that.
4. Never use em-dash symbol. Use period, colon, parens, or "and" instead.
5. Confirm before writing to disk. Ask before saving/modifying any file.
6. Stay strictly within scope. Only touch the section/file/area the user named.
7. Run lint/typecheck after edits if commands provided.

## ACCURACY PROTOCOL (MANDATORY)
- Check your answer at least TWICE before responding
- Verify facts against loaded memory and documentation
- If uncertain, say "uncertain" and ask for clarification
- No hallucination. No fabrication. No guessing.""")

        # 2. Global Memory
        global_mem = self.load_global_memory()
        if global_mem:
            parts.append(f"\n## GLOBAL MEMORY (Persistent Across All Projects)\n{global_mem}")

        # 3. Project Memory
        project_mem = self.load_project_memory()
        if project_mem:
            parts.append(f"\n## PROJECT MEMORY: {self.project_name}\n{project_mem}")

        # 4. Official Limitations
        limitations = self.load_limitations()
        if limitations:
            parts.append(f"\n## OFFICIAL MODEL LIMITATIONS (from NVIDIA)\n{limitations[:3000]}...")

        # 5. Recent Cache Context
        cache_entries = self.load_recent_cache()
        if cache_entries:
            parts.append("\n## RECENT CACHE CONTEXT")
            for e in cache_entries:
                parts.append(f"- [{e['timestamp']}] {e['key']}: {e['response']}...")

        # 6. Project Structure
        parts.append(f"""
## PROJECT STRUCTURE
- Root: {ROOT}
- Project: {self.project_path}
- Input: {self.project_path / "input"}
- Output: {self.project_path / "output"}
- Cache: {ROOT / "cache" / "projects" / self.project_name}
- Global Memory: {self.global_memory_path}
- Project Memory: {self.project_memory_path}

## WORKFLOW TRIGGERS
- "sync" or "pull latest" → git pull in main path, rebase worktree
- "push to local" → write to both main path and worktree, end with "LocP: <detail>"
- "push to git" → git status, verify, commit, push, end with "GitP: <branch>@<commit>"
- "force" → discard local conflicts, take remote, redo work

## VISUAL MARKERS (Chat Only)
- ⚠️ CRITICAL: System-breaking changes, data loss, security hazards
- 💡 HINT: Optional optimization or faster path
- 💭 COMMENT/THOUGHT: Observation or reasoning

One marker per callout. Place AFTER solution. Never stack.""")

        return "\n".join(parts)

    def write_activation_files(self):
        """Write activation files for OpenCode to consume."""
        # Write system prompt
        prompt = self.build_system_prompt()
        prompt_file = self.project_path / "cache" / "system_prompt.md"
        prompt_file.parent.mkdir(parents=True, exist_ok=True)
        prompt_file.write_text(prompt, encoding="utf-8")

        # Write AGENTS.md (OpenCode loads it from the working folder on startup)
        agents_file = self.project_path / "AGENTS.md"
        agents_file.write_text(prompt, encoding="utf-8")

        # Write summary
        summary = {
            "project": self.project_name,
            "timestamp": __import__("datetime").datetime.now().isoformat(),
            "global_memory_chars": len(self.load_global_memory()),
            "project_memory_chars": len(self.load_project_memory()),
            "limitations_chars": len(self.load_limitations()),
            "cache_entries": len(self.load_recent_cache()),
            "system_prompt_file": str(prompt_file),
            "agents_file": str(agents_file),
        }
        summary_file = self.project_path / "cache" / "activation_summary.json"
        summary_file.write_text(json.dumps(summary, indent=2))

        print(f"Phase 2: Activation files written to {self.project_path / 'cache'}")
        return summary


if __name__ == "__main__":
    project = sys.argv[1] if len(sys.argv) > 1 else "default"
    activator = Phase2Activator(project)
    summary = activator.write_activation_files()
    print(json.dumps(summary, indent=2))