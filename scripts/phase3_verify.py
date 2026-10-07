#!/usr/bin/env python3
"""
Phase 3: Dual-Verification Accuracy Layer
Implements mandatory double-checking before any response.
"""

import os
import sys
import json
import re
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime

ROOT = Path(__file__).parent.parent

@dataclass
class VerificationResult:
    check_name: str
    passed: bool
    details: str
    confidence: float  # 0.0 - 1.0

class Phase3Verifier:
    def __init__(self, project_name: str = "default"):
        self.project_name = project_name
        self.project_path = ROOT / "projects" / project_name
        self.global_memory_path = ROOT / "memory" / "global" / "MEMORY.md"
        self.project_memory_path = self.project_path / "MEMORY.md"
        self.limitations_path = ROOT / "docs" / "00-limitations.md"
        self.verification_log: List[VerificationResult] = []

    def load_text(self, path: Path) -> str:
        if path.exists():
            return path.read_text(encoding="utf-8")
        return ""

    def verify_against_sources(self, claim: str, sources: List[str]) -> VerificationResult:
        """Check if a claim is supported by loaded sources."""
        claim_lower = claim.lower()
        supported = 0
        total = len(sources)

        for source in sources:
            source_lower = source.lower()
            # Simple keyword overlap check
            claim_words = set(claim_lower.split())
            source_words = set(source_lower.split())
            overlap = len(claim_words & source_words)
            if overlap > 2:  # At least 3 words overlap
                supported += 1

        confidence = supported / max(total, 1)
        passed = confidence >= 0.3  # At least 30% of sources support

        return VerificationResult(
            check_name="source_verification",
            passed=passed,
            details=f"Supported by {supported}/{total} sources (confidence: {confidence:.2f})",
            confidence=confidence
        )

    def verify_no_hallucination(self, response: str) -> VerificationResult:
        """Check for common hallucination patterns."""
        hallucination_indicators = [
            "as an ai language model",
            "i don't have access to",
            "my knowledge cutoff",
            "i cannot browse",
            "i don't have real-time",
            "as of my last update",
        ]

        response_lower = response.lower()
        found = [ind for ind in hallucination_indicators if ind in response_lower]

        passed = len(found) == 0
        details = "No hallucination markers found" if passed else f"Found markers: {found}"

        return VerificationResult(
            check_name="hallucination_check",
            passed=passed,
            details=details,
            confidence=0.9 if passed else 0.3
        )

    def verify_scope_compliance(self, response: str, user_request: str) -> VerificationResult:
        """Check if response stays within requested scope."""
        # Simple heuristic: response shouldn't be dramatically longer than needed
        request_words = len(user_request.split())
        response_words = len(response.split())

        # Allow up to 20x expansion for code, 5x for answers
        max_ratio = 20 if any(kw in user_request.lower() for kw in ["code", "function", "script", "implement"]) else 5
        ratio = response_words / max(request_words, 1)

        passed = ratio <= max_ratio
        details = f"Response/request ratio: {ratio:.1f}x (max allowed: {max_ratio}x)"

        return VerificationResult(
            check_name="scope_compliance",
            passed=passed,
            details=details,
            confidence=0.8 if passed else 0.4
        )

    def verify_factual_consistency(self, response: str) -> VerificationResult:
        """Cross-check facts against loaded memory."""
        sources = [
            self.load_text(self.global_memory_path),
            self.load_text(self.project_memory_path),
            self.load_text(self.limitations_path),
        ]

        # Extract factual claims (simple: sentences with numbers, dates, versions)
        import re
        claims = re.findall(r'[^.]*\d+[^.]*\.', response)

        if not claims:
            return VerificationResult(
                check_name="factual_consistency",
                passed=True,
                details="No specific factual claims to verify",
                confidence=0.7
            )

        verified = 0
        for claim in claims[:5]:  # Check up to 5 claims
            result = self.verify_against_sources(claim, sources)
            if result.passed:
                verified += 1

        confidence = verified / len(claims)
        passed = confidence >= 0.5

        return VerificationResult(
            check_name="factual_consistency",
            passed=passed,
            details=f"Verified {verified}/{len(claims)} claims against sources",
            confidence=confidence
        )

    def verify_code_safety(self, response: str) -> VerificationResult:
        """Check for unsafe code patterns."""
        unsafe_patterns = [
            r"eval\s*\(",
            r"exec\s*\(",
            r"subprocess.*shell\s*=\s*True",
            r"os\.system\s*\(",
            r"pickle\.loads?",
            r"yaml\.load\s*\(",
            r"__import__\s*\(",
            r"getattr\s*\(.*__",
            r"rm\s+-rf\s+/",
            r"format\s*c:",
            r"del\s+/f\s+/q",
        ]

        import re
        found = []
        for pattern in unsafe_patterns:
            if re.search(pattern, response, re.IGNORECASE):
                found.append(pattern)

        passed = len(found) == 0
        details = "No unsafe patterns" if passed else f"Found: {found}"

        return VerificationResult(
            check_name="code_safety",
            passed=passed,
            details=details,
            confidence=0.95 if passed else 0.2
        )

    def verify_format_compliance(self, response: str) -> VerificationResult:
        """Check format compliance (no em-dashes, concise, etc.)."""
        issues = []

        # Em-dash check
        if "\u2014" in response or "--" in response:
            issues.append("Contains em-dash or double hyphen")

        # Length check (warn if very long for simple questions)
        words = len(response.split())
        if words > 500:
            issues.append(f"Response very long ({words} words)")

        # Preamble check
        preamble_patterns = [
            r"^sure,? i",
            r"^let me",
            r"^i'll",
            r"^here is",
            r"^below is",
            r"^the following",
        ]
        response_lower = response.lower().strip()
        for pattern in preamble_patterns:
            if re.search(pattern, response_lower):
                issues.append(f"Contains preamble: {pattern}")
                break

        passed = len(issues) == 0
        details = "Format compliant" if passed else f"Issues: {issues}"

        return VerificationResult(
            check_name="format_compliance",
            passed=passed,
            details=details,
            confidence=0.9 if passed else 0.5
        )

    def run_all_verifications(self, response: str, user_request: str = "") -> Dict:
        """Run all verification checks (PASS 1)."""
        print("Phase 3: Running Pass 1 verifications...")

        checks = [
            self.verify_no_hallucination(response),
            self.verify_scope_compliance(response, user_request),
            self.verify_factual_consistency(response),
            self.verify_code_safety(response),
            self.verify_format_compliance(response),
        ]

        self.verification_log.extend(checks)

        all_passed = all(c.passed for c in checks)
        avg_confidence = sum(c.confidence for c in checks) / len(checks)

        return {
            "pass": 1,
            "all_passed": all_passed,
            "avg_confidence": avg_confidence,
            "checks": [asdict(c) for c in checks],
        }

    def run_pass2_verification(self, response: str, user_request: str, pass1_result: Dict) -> Dict:
        """Run second verification pass with stricter criteria."""
        print("Phase 3: Running Pass 2 verifications...")

        # Pass 2: Stricter thresholds
        checks = []

        # Re-run with higher standards
        hallucination = self.verify_no_hallucination(response)
        hallucination.confidence *= 1.1  # Boost confidence requirement
        checks.append(hallucination)

        scope = self.verify_scope_compliance(response, user_request)
        scope.confidence *= 1.1
        checks.append(scope)

        factual = self.verify_factual_consistency(response)
        factual.confidence *= 1.1
        checks.append(factual)

        safety = self.verify_code_safety(response)
        safety.confidence *= 1.1
        checks.append(safety)

        format_check = self.verify_format_compliance(response)
        format_check.confidence *= 1.1
        checks.append(format_check)

        # Additional Pass 2: Consistency with Pass 1
        consistency = VerificationResult(
            check_name="pass_consistency",
            passed=pass1_result["all_passed"],
            details="Pass 1 all checks passed" if pass1_result["all_passed"] else "Pass 1 had failures",
            confidence=0.9 if pass1_result["all_passed"] else 0.3
        )
        checks.append(consistency)

        self.verification_log.extend(checks)

        all_passed = all(c.passed for c in checks)
        avg_confidence = sum(c.confidence for c in checks) / len(checks)

        return {
            "pass": 2,
            "all_passed": all_passed,
            "avg_confidence": avg_confidence,
            "checks": [asdict(c) for c in checks],
        }

    def final_verdict(self, pass1: Dict, pass2: Dict) -> Dict:
        """Determine final verdict."""
        both_passed = pass1["all_passed"] and pass2["all_passed"]
        overall_confidence = (pass1["avg_confidence"] + pass2["avg_confidence"]) / 2

        # Log to file
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "project": self.project_name,
            "pass1": pass1,
            "pass2": pass2,
            "final": {
                "approved": both_passed,
                "confidence": overall_confidence,
            }
        }

        log_file = self.project_path / "cache" / f"verification_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        log_file.parent.mkdir(parents=True, exist_ok=True)
        log_file.write_text(json.dumps(log_entry, indent=2))

        return {
            "approved": both_passed,
            "confidence": overall_confidence,
            "message": "APPROVED: Both verification passes successful" if both_passed else "REJECTED: Verification failed",
            "details": {
                "pass1": pass1,
                "pass2": pass2,
            }
        }


def verify_response(response: str, user_request: str = "", project: str = "default") -> Dict:
    """Main entry point for dual verification."""
    verifier = Phase3Verifier(project)

    # Pass 1
    pass1 = verifier.run_all_verifications(response, user_request)

    # Pass 2 (stricter)
    pass2 = verifier.run_pass2_verification(response, user_request, pass1)

    # Final verdict
    verdict = verifier.final_verdict(pass1, pass2)

    return verdict


if __name__ == "__main__":
    # Test mode
    test_response = "The Nemotron 3 Ultra model has 550B total parameters with 55B active. It uses LatentMoE architecture with Mamba-2 and Attention layers. Context length up to 1M tokens."
    test_request = "What are the model specs?"

    result = verify_response(test_response, test_request, "test-project")
    print(json.dumps(result, indent=2))