#!/usr/bin/env python3
"""
Nemotron 3 Ultra + OpenCode: Full Phase Integration
Runs Phase 1 (verify), Phase 2 (activate), Phase 3 (verify responses).
Use as: python scripts/opencode_runner.py [project] [--verify-only] [--skip-phase1]
"""

import os
import sys
import json
import shutil
import subprocess
import argparse
from pathlib import Path

ROOT = Path(__file__).parent.parent

# Import phase modules
sys.path.insert(0, str(ROOT / "scripts"))
from phase1_verify import Phase1Verifier
from phase2_activate import Phase2Activator
from phase3_verify import verify_response


class OpenCodeRunner:
    def __init__(self, project_name: str = "default"):
        self.project_name = project_name
        self.project_path = ROOT / "projects" / project_name

    def run_phase1(self, skip: bool = False) -> bool:
        if skip:
            print("Phase 1: SKIPPED (--skip-phase1)")
            return True

        print("\n" + "=" * 60)
        print("PHASE 1: SETUP VERIFICATION")
        print("=" * 60)

        verifier = Phase1Verifier()
        success = verifier.run_all(self.project_name)

        if not success:
            print("\n[FAIL] Phase 1 FAILED. Fix errors before proceeding.")
            print("Run: python scripts/phase1_verify.py", self.project_name)
            return False

        print("\n[PASS] Phase 1 PASSED")
        return True

    def run_phase2(self) -> Dict:
        print("\n" + "=" * 60)
        print("PHASE 2: MEMORY & PROMPT ACTIVATION")
        print("=" * 60)

        activator = Phase2Activator(self.project_name)
        summary = activator.write_activation_files()

        print(f"[PASS] Phase 2 COMPLETE")
        print(f"   System prompt: {summary['system_prompt_file']}")
        print(f"   Init script: {summary['init_script_file']}")
        print(f"   Global memory: {summary['global_memory_chars']} chars")
        print(f"   Project memory: {summary['project_memory_chars']} chars")

        return summary

    def run_opencode(self, phase2_summary: Dict) -> int:
        """Launch OpenCode with activated context."""
        print("\n" + "=" * 60)
        print("LAUNCHING OPENCODE")
        print("=" * 60)

        # Set environment for OpenCode
        env = os.environ.copy()
        env["NEMOTRON_PROJECT"] = self.project_name
        env["NEMOTRON_SYSTEM_PROMPT"] = phase2_summary["system_prompt_file"]
        env["NEMOTRON_INIT_SCRIPT"] = phase2_summary["init_script_file"]

        # Change to project directory
        os.chdir(self.project_path)

        print(f"Project: {self.project_name}")
        print(f"Working dir: {self.project_path}")
        print(f"System prompt loaded from: {phase2_summary['system_prompt_file']}")
        print("\nStarting OpenCode... (Type '/models' to select Nemotron 3 Ultra)")
        print("Phase 3 verification active: ALL responses will be double-checked")
        print("=" * 60)

        # Launch OpenCode
        try:
            result = subprocess.run([shutil.which("opencode") or "opencode"], env=env)
            return result.returncode
        except KeyboardInterrupt:
            print("\nOpenCode interrupted.")
            return 130
        except FileNotFoundError:
            print("ERROR: OpenCode not found. Run Phase 1 first.")
            return 1

    def test_phase3(self):
        """Test Phase 3 verification with sample responses."""
        print("\n" + "=" * 60)
        print("PHASE 3: TESTING DUAL-VERIFICATION")
        print("=" * 60)

        test_cases = [
            {
                "request": "What is Nemotron 3 Ultra?",
                "response": "Nemotron 3 Ultra is a 550B parameter model with 55B active, using LatentMoE architecture. Context up to 1M tokens.",
            },
            {
                "request": "Write a Python function to add two numbers",
                "response": "def add(a, b): return a + b",
            },
            {
                "request": "What is the capital of France?",
                "response": "The capital of France is Paris.",
            },
        ]

        for i, tc in enumerate(test_cases, 1):
            print(f"\nTest {i}: {tc['request']}")
            result = verify_response(tc["response"], tc["request"], self.project_name)
            status = "[APPROVED]" if result["approved"] else "[REJECTED]"
            print(f"  {status} (confidence: {result['confidence']:.2f})")
            if not result["approved"]:
                print(f"  Reason: {result['message']}")
                for p in [1, 2]:
                    for check in result["details"][f"pass{p}"]["checks"]:
                        if not check["passed"]:
                            print(f"    FAIL [{check['check_name']}]: {check['details']}")

    def run_all(self, skip_phase1: bool = False, verify_only: bool = False) -> int:
        print("=" * 60)
        print(f"NEMOTRON 3 ULTRA + OPENCODE - PROJECT: {self.project_name}")
        print("=" * 60)

        # Phase 1
        if not self.run_phase1(skip_phase1):
            return 1

        # Phase 2
        phase2_summary = self.run_phase2()

        if verify_only:
            self.test_phase3()
            print("\n[PASS] All phases complete (verify-only mode)")
            return 0

        # Phase 3 is integrated into OpenCode via system prompt
        print("\nPhase 3: Dual-verification ENABLED via system prompt")
        print("   Every response will pass 2 verification rounds before output")

        # Launch OpenCode
        return self.run_opencode(phase2_summary)


def main():
    parser = argparse.ArgumentParser(
        description="Nemotron 3 Ultra + OpenCode Phase Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/opencode_runner.py my-project
  python scripts/opencode_runner.py default --skip-phase1
  python scripts/opencode_runner.py test-project --verify-only
        """
    )
    parser.add_argument("project", nargs="?", default="default", help="Project name")
    parser.add_argument("--skip-phase1", action="store_true", help="Skip setup verification")
    parser.add_argument("--verify-only", action="store_true", help="Run phases 1-3 test only, don't launch OpenCode")
    parser.add_argument("--init", action="store_true", help="Initialize project before running")

    args = parser.parse_args()

    # Initialize project if requested
    if args.init:
        from memory_manager import init_project
        init_project(args.project, f"Initialized via opencode_runner")
        print(f"Initialized project: {args.project}")

    runner = OpenCodeRunner(args.project)
    exit_code = runner.run_all(skip_phase1=args.skip_phase1, verify_only=args.verify_only)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()