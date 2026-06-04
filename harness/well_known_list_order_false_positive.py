# Harness: RwsCheck.check_well_known_list — Finding RWS-1 (false-positive)
#
# Source: RwsCheck.py:336-358
#   if list1 == list2:                      # gates on LIST equality (order + dups)
#       return []
#   diff = sorted(set(list1) ^ set(list2))  # computes the symmetric diff...
#   return [f"...Diff was: {diff}."]         # ...but errors even when diff == []
#
# The docstring says it "returns an empty list if the 2 fields are symmetric"
# (symmetric == symmetric diff empty == set-equal).  But the code only
# short-circuits on exact LIST equality and otherwise ALWAYS returns an error —
# even when the symmetric diff is empty (same sites, different order, or a
# duplicate).  So a PR/well-known pair that is set-equal but reordered triggers a
# false-positive mismatch error literally reading "Diff was: []".
#
# Booleans as 0/1.  lists_equal == 1 implies sets_equal == 1 (exact-equal lists
# are necessarily set-equal).
#
# Expected verdict: FAILED — the documented set-symmetry contract is violated
# (an over-strict false positive that rejects a benign submission).

def check_well_known_list_errors(lists_equal, sets_equal):
    # RwsCheck.check_well_known_list (current code):
    #   if list1 == list2: return []   (no error)
    #   else: return [error...]        (error even if symmetric diff empty)
    if lists_equal == 1:
        return 0
    return 1


def main():
    lists_equal = nondet_int()  # noqa: F821
    sets_equal = nondet_int()   # noqa: F821
    __ESBMC_assume(lists_equal == 0 or lists_equal == 1)  # noqa: F821
    __ESBMC_assume(sets_equal == 0 or sets_equal == 1)    # noqa: F821
    __ESBMC_assume(not (lists_equal == 1 and sets_equal == 0))  # noqa: F821

    error = check_well_known_list_errors(lists_equal, sets_equal)

    # Documented contract: symmetric (set-equal) lists yield no error.
    if sets_equal == 1:
        assert error == 0   # FAILS: set-equal but reordered/duplicated -> spurious error


main()
