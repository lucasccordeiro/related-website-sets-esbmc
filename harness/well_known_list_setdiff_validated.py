# Harness: RwsCheck.check_well_known_list — Finding RWS-1 (fix)
#
# Positive control for `well_known_list_order_false_positive.py`.  Models the
# fix: gate the no-error path on the symmetric diff (set-equality), matching the
# docstring, instead of on exact list equality:
#   diff = set(list1) ^ set(list2)
#   return [] if not diff else [error...]
# Then set-symmetric lists (any order, duplicates) correctly produce no error.
#
# Expected verdict: SUCCESSFUL (Phase 1 and Phase 2).

def check_well_known_list_errors_fixed(lists_equal, sets_equal):
    # Fix: no error iff the symmetric diff is empty (set-equal).
    if sets_equal == 1:
        return 0
    return 1


def main():
    lists_equal = nondet_int()  # noqa: F821
    sets_equal = nondet_int()   # noqa: F821
    __ESBMC_assume(lists_equal == 0 or lists_equal == 1)  # noqa: F821
    __ESBMC_assume(sets_equal == 0 or sets_equal == 1)    # noqa: F821
    __ESBMC_assume(not (lists_equal == 1 and sets_equal == 0))  # noqa: F821

    error = check_well_known_list_errors_fixed(lists_equal, sets_equal)

    if sets_equal == 1:
        assert error == 0   # holds for the diff-based check


main()
