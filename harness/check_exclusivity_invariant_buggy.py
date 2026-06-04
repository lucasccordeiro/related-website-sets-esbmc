# Harness: RwsCheck.check_exclusivity — exclusivity invariant (BUGGY)
#
# Non-vacuity / negative control for `check_exclusivity_invariant.py`.  Mutation:
# set B is added to site_list without consulting it first (the
# `overlap = set(...) & site_list; if overlap: error` step is dropped), so a
# site claimed by both set A and set B is NOT flagged — silently registered in
# two related website sets.  ESBMC must catch it.
#
# Expected verdict: FAILED.

def check_exclusivity_flags_buggy(in_A, in_B):
    in_list = 0
    flagged = 0
    if in_A == 1:
        if in_list == 1:
            flagged = 1
        else:
            in_list = 1
    if in_B == 1:
        # BUG: no overlap check against site_list -> cross-set duplicate missed.
        in_list = 1
    return flagged


def main():
    in_A = nondet_int()  # noqa: F821
    in_B = nondet_int()  # noqa: F821
    __ESBMC_assume(in_A == 0 or in_A == 1)  # noqa: F821
    __ESBMC_assume(in_B == 0 or in_B == 1)  # noqa: F821

    flagged = check_exclusivity_flags_buggy(in_A, in_B)

    if in_A == 1 and in_B == 1:
        assert flagged == 1   # FAILS: duplicate across sets is not flagged


main()
