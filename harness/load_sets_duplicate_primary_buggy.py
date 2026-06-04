# Harness: RwsCheck.load_sets — duplicate-primary detection (BUGGY)
#
# Non-vacuity / negative control for `load_sets_duplicate_primary_detected.py`.
# Mutation: the `if primary in check_sets.keys()` membership check is dropped, so
# the primary is stored unconditionally and a second listing is never flagged —
# a duplicate primary slips through silently.  ESBMC must catch it.
#
# Expected verdict: FAILED.

def load_sets_flags_buggy(in_A, in_B):
    primary_stored = 0
    flagged = 0
    if in_A == 1:
        primary_stored = 1
    if in_B == 1:
        # BUG: no `primary in check_sets.keys()` check -> duplicate not flagged.
        primary_stored = 1
    return flagged


def main():
    in_A = nondet_int()  # noqa: F821
    in_B = nondet_int()  # noqa: F821
    __ESBMC_assume(in_A == 0 or in_A == 1)  # noqa: F821
    __ESBMC_assume(in_B == 0 or in_B == 1)  # noqa: F821

    flagged = load_sets_flags_buggy(in_A, in_B)

    if in_A == 1 and in_B == 1:
        assert flagged == 1   # FAILS: duplicate primary not flagged


main()
