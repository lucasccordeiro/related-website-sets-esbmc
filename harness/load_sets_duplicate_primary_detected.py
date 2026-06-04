# Harness: RwsCheck.load_sets — duplicate-primary detection (proof of absence)
#
# Source: RwsCheck.py:79-94
#   check_sets = {}
#   for rwset in self.rws_sites["sets"]:
#       primary = rwset.get("primary")
#       if primary in check_sets.keys():
#           load_sets_errors.append(f"{primary} is already a primary of another site")
#       else:
#           check_sets[primary] = RwsSet(...)
#
# Invariant (from the docstring): "If any given primary is listed multiple times,
# [it] will append an error ... for any primary past the first."  check_sets is
# keyed by primary; the first occurrence is stored, every later occurrence is
# flagged as a duplicate.
#
# Modelled over one symbolic primary listed by set A (processed first) and/or set
# B, as a cumulative key-membership abstraction.  (The faithful string-keyed dict
# model is deferred — see ROADMAP / esbmc#5110.)
#
# Verified property: a primary listed by two sets is flagged.
# Expected verdict: SUCCESSFUL (Phase 1 and Phase 2).

def load_sets_flags(in_A, in_B):
    """Cumulative key-membership: a primary is flagged on its second listing."""
    primary_stored = 0
    flagged = 0
    if in_A == 1:                    # set A processed first
        if primary_stored == 1:      # primary in check_sets.keys()?
            flagged = 1
        else:
            primary_stored = 1
    if in_B == 1:                    # set B
        if primary_stored == 1:
            flagged = 1
        else:
            primary_stored = 1
    return flagged


def main():
    in_A = nondet_int()  # noqa: F821  primary listed by set A?
    in_B = nondet_int()  # noqa: F821  primary listed by set B?
    __ESBMC_assume(in_A == 0 or in_A == 1)  # noqa: F821
    __ESBMC_assume(in_B == 0 or in_B == 1)  # noqa: F821

    flagged = load_sets_flags(in_A, in_B)

    # A primary listed by two sets must be flagged ("already a primary of
    # another site").
    if in_A == 1 and in_B == 1:
        assert flagged == 1


main()
