#!/usr/bin/env python3
"""
Phase 1: Setup Verification & Validation
Run this before any OpenCode session to ensure environment is correct.
"""

import os
import sys
import json
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple

ROOT = Path(__file__).parent.parent

class Phase1Verifier:
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.checks_passed: List[str] = []

    def check_node(self) -> bool:
        try:
            result = subprocess.run(["node", "--version"], capture_output=True, text=True)
            if result.returncode != 0:
                self.errors.append("Node.js not found")
                return False
            version = result.stdout.strip()
            major = int(version.lstrip('v').split('.')[0])
            if major < 20:
                self.warnings.append(f"Node.js {version} < v20. Upgrade recommended.")
            else:
                self.checks_passed.append(f"Node.js {version} OK")
            return True
        except FileNotFoundError:
            self.errors.append("Node.js not installed")
            return False

    def check_opencode(self) -> bool:
        try:
            result = subprocess.run([shutil.which("opencode") or "opencode", "--version"], capture_output=True, text=True)
            if result.returncode != 0:
                self.errors.append("OpenCode not installed or not in PATH")
                return False
            self.checks_passed.append(f"OpenCode {result.stdout.strip()} OK")
            return True
        except FileNotFoundError:
            self.errors.append("OpenCode command not found")
            return False

    def check_api_key(self) -> bool:
        key = os.environ.get("NVIDIA_API_KEY", "")
        if not key:
            self.errors.append("NVIDIA_API_KEY environment variable not set")
            return False
        if not key.startswith("nvapi-"):
            self.errors.append("NVIDIA_API_KEY format invalid (must start with 'nvapi-')")
            return False
        if len(key) < 45:
            self.errors.append("NVIDIA_API_KEY too short")
            return False
        self.checks_passed.append("NVIDIA_API_KEY format OK")
        return True

    def check_config(self) -> bool:
        config_paths = [
            Path.home() / ".config" / "opencode" / "opencode.json",
            ROOT / "examples" / "opencode.example.json",
        ]
        found = False
        for p in config_paths:
            if p.exists():
                try:
                    with open(p) as f:
                        config = json.load(f)
                    if config.get("model") == "nvidia/nvidia/nemotron-3-ultra-550b-a55b":
                        self.checks_passed.append(f"OpenCode config found at {p}")
                        found = True
                        break
                except json.JSONDecodeError:
                    self.warnings.append(f"Config at {p} has invalid JSON")
        if not found:
            self.errors.append("OpenCode config not found or model not set to Nemotron 3 Ultra")
            return False
        return True

    def check_memory_structure(self) -> bool:
        required = [
            ROOT / "memory" / "global" / "MEMORY.md",
            ROOT / "scripts" / "memory_manager.py",
        ]
        for p in required:
            if not p.exists():
                self.errors.append(f"Missing required file: {p}")
                return False
        self.checks_passed.append("Memory structure OK")
        return True

    def check_project(self, project_name: str) -> bool:
        project_path = ROOT / "projects" / project_name
        if not project_path.exists():
            self.warnings.append(f"Project '{project_name}' not initialized. Run: python scripts/memory_manager.py init {project_name}")
            return False
        required = [
            project_path / "MEMORY.md",
            project_path / "input",
            project_path / "output",
            project_path / "cache",
        ]
        for p in required:
            if not p.exists():
                self.errors.append(f"Project structure incomplete: missing {p}")
                return False
        self.checks_passed.append(f"Project '{project_name}' structure OK")
        return True

    def run_all(self, project_name: str = "default") -> bool:
        print("=" * 60)
        print("PHASE 1: SETUP VERIFICATION")
        print("=" * 60)

        checks = [
            ("Node.js", self.check_node),
            ("OpenCode", self.check_opencode),
            ("API Key", self.check_api_key),
            ("OpenCode Config", self.check_config),
            ("Memory Structure", self.check_memory_structure),
            (f"Project '{project_name}'", lambda: self.check_project(project_name)),
        ]

        all_passed = True
        for name, check in checks:
            print(f"\nChecking {name}...")
            try:
                if not check():
                    all_passed = False
            except Exception as e:
                self.errors.append(f"{name} check failed: {e}")
                all_passed = False

        print("\n" + "=" * 60)
        print("RESULTS")
        print("=" * 60)

        for c in self.checks_passed:
            print(f"  PASS  {c}")
        for w in self.warnings:
            print(f"  WARN  {w}")
        for e in self.errors:
            print(f"  FAIL  {e}")

        print(f"\nPassed: {len(self.checks_passed)} | Warnings: {len(self.warnings)} | Errors: {len(self.errors)}")
        return all_passed and len(self.errors) == 0


if __name__ == "__main__":
    project = sys.argv[1] if len(sys.argv) > 1 else "default"
    verifier = Phase1Verifier()
    success = verifier.run_all(project)
    sys.exit(0 if success else 1)