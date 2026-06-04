# related-website-sets ESBMC-Python verification orchestrator.
#
# Single source of truth for: target name -> entry script -> expected verdict,
# per phase. Mirrors the chromium-dashboard PoC scheme.
#
# Phases:
#   Phase 1: default flags. Functional contracts via `assert`.
#   Phase 2: --overflow-check (CWE-190 / CWE-369).
#
# A target with `safety_expected=None` skips Phase 2 (buggy/non-vacuity controls
# whose Phase 1 already FAILS).
#
# NOTE: every current target is an integer/boolean abstraction. The faithful
# string-level harnesses (real split(".")/replace() on symbolic domain strings)
# are blocked by esbmc/esbmc#5110 (str.split unsound on symbolic strings) and
# will be added once that is fixed. See ROADMAP.md.

from __future__ import annotations

import argparse
import os
import re
import shlex
import subprocess
import sys
from dataclasses import dataclass

ROOT = os.path.dirname(os.path.abspath(__file__))
HARNESS_DIR = os.path.join(ROOT, "harness")
ESBMC = os.environ.get("ESBMC", "esbmc")

_SAFETY: tuple[str, ...] = ("--overflow-check",)


@dataclass
class Target:
    name: str
    entry: str
    esbmc_args: tuple[str, ...] = ()
    expected: str | None = "SUCCESSFUL"
    safety_args: tuple[str, ...] = _SAFETY
    safety_expected: str | None = "SUCCESSFUL"


TARGETS: list[Target] = [
    # --- Finding RWS-1: check_well_known_list over-strict false positive ---
    Target(
        # check_well_known_list gates the no-error path on exact LIST equality but
        # documents set-symmetry; a set-equal-but-reordered/duplicated pair yields
        # a spurious "Diff was: []" error. Contract: set-equal => no error.
        name="well_known_list_order_false_positive",
        entry="well_known_list_order_false_positive.py",
        expected="FAILED",
        safety_expected=None,
    ),
    Target(
        # Positive control: gating on the symmetric diff (set-equality) honors the
        # documented contract for any order/duplicates.
        name="well_known_list_setdiff_validated",
        entry="well_known_list_setdiff_validated.py",
        expected="SUCCESSFUL",
        safety_expected="SUCCESSFUL",
    ),

    # --- find_invalid_alias_eSLDs: ccTLD ".com"-variant rule (proof of absence) ---
    Target(
        # A ".com" variant is accepted only if the aliased site's TLD is an ICANN
        # country code (the documented IFF rule). Holds.
        name="alias_com_variant_rule",
        entry="alias_com_variant_rule.py",
        expected="SUCCESSFUL",
        safety_expected="SUCCESSFUL",
    ),
    Target(
        # Non-vacuity control: dropping the aliased-tld-is-ccTLD guard (always
        # allow "com") violates the rule. ESBMC catches it.
        name="alias_com_variant_rule_buggy",
        entry="alias_com_variant_rule_buggy.py",
        expected="FAILED",
        safety_expected=None,
    ),
]


def _verdict_from_output(out: str) -> str:
    if "VERIFICATION SUCCESSFUL" in out:
        return "SUCCESSFUL"
    if "VERIFICATION FAILED" in out:
        return "FAILED"
    return "ERROR"


_VCC_RE = re.compile(r"Generated (\d+) VCC\(s\)")


def _vcc_count(out: str) -> int | None:
    m = _VCC_RE.search(out)
    return int(m.group(1)) if m else None


def _run_esbmc(entry: str, args: tuple[str, ...]) -> tuple[str, int | None, str]:
    proc = subprocess.run(
        [ESBMC, *args, entry], capture_output=True, text=True, cwd=HARNESS_DIR
    )
    output = proc.stdout + proc.stderr
    return _verdict_from_output(output), _vcc_count(output), output[-400:]


def _run_target(target: Target, phases: tuple[int, ...]) -> int:
    failures = 0
    for phase in phases:
        if phase == 1:
            expected, extra_args = target.expected, target.esbmc_args
        else:
            expected = target.safety_expected
            extra_args = target.esbmc_args + target.safety_args
        if expected is None:
            print(f"  [Phase {phase}] skipped")
            continue
        verdict, vcc, tail = _run_esbmc(target.entry, extra_args)
        vacuous = verdict == "SUCCESSFUL" and vcc == 0
        ok = verdict == expected and not vacuous
        marker = "FAIL (vacuous: 0 VCCs)" if vacuous else ("PASS" if ok else "FAIL")
        vcc_str = "?" if vcc is None else str(vcc)
        cmd_str = shlex.join((ESBMC, *extra_args, target.entry))
        print(f"  [Phase {phase}] {marker}: verdict={verdict} vcc={vcc_str} "
              f"expected={expected}  ({cmd_str})")
        if not ok:
            failures += 1
            print(f"      tail: {tail!r}")
    return failures


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", choices=("1", "2", "all"), default="all")
    ap.add_argument("--only", nargs="*", default=None)
    args = ap.parse_args()
    phases: tuple[int, ...] = (1, 2) if args.phase == "all" else (int(args.phase),)
    selected = TARGETS
    if args.only:
        selected = [t for t in TARGETS if t.name in set(args.only)]
        if not selected:
            print(f"no matching targets in {args.only!r}", file=sys.stderr)
            return 2
    total = 0
    for t in selected:
        print(f"== {t.name} ==")
        total += _run_target(t, phases)
    print()
    print(f"total failures: {total}")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
