# Harness: RwsCheck.has_all_rationales — Finding RWS-2 (fix)
#
# Positive control for `rationales_empty_sites_false_positive.py`.  Models the
# fix: require rationaleBySite only when there ARE associated/service sites
# (`if sites and rationales is None:` instead of `if sites is not None ...`).
# Then a primary-only set with no rationaleBySite is no longer flagged.
#
# Expected verdict: SUCCESSFUL (Phase 1 and Phase 2).

def rationale_required_error_fixed(has_sites, has_rationales):
    # Fix: required only when there are sites to rationalise.
    if has_sites == 1 and has_rationales == 0:
        return 1
    return 0


def main():
    has_sites = nondet_int()       # noqa: F821
    has_rationales = nondet_int()  # noqa: F821
    __ESBMC_assume(has_sites == 0 or has_sites == 1)            # noqa: F821
    __ESBMC_assume(has_rationales == 0 or has_rationales == 1)  # noqa: F821

    err = rationale_required_error_fixed(has_sites, has_rationales)

    if err == 1:
        assert has_sites == 1   # holds: rationale only required when sites exist


main()
