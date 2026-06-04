# Harness: RwsCheck.has_all_rationales — Finding RWS-2 (false-positive)
#
# Source: RwsCheck.py:111-127
#   sites = rwset.get("associatedSites", []) + rwset.get("serviceSites", [])
#   rationales = rwset.get("rationaleBySite", None)
#   if sites and rationales is not None:
#       ... # every site must have a rationale
#   if sites is not None and rationales is None:     # <-- always-true guard
#       error("A rationaleBySite field is required ... none is provided.")
#
# `sites` is the concatenation of two `.get(..., [])` lists, so it is ALWAYS a
# list, never None — making `sites is not None` vacuously true.  Therefore the
# "rationaleBySite is required" error fires whenever the field is absent, even
# for a set with NO associated/service sites (a valid set of just a primary +
# ccTLDs), which has no sites needing a rationale.
#
# Booleans as 0/1.  Confirmed under CPython
# (reproducer/rws2_rationales_empty_sites.py): a primary-only set with no
# rationaleBySite yields ["A rationaleBySite field is required ..."].
#
# Expected verdict: FAILED — the documented intent (rationale required only when
# there are sites to rationalise) is violated by the always-true guard.

def rationale_required_error(has_sites, has_rationales):
    """Models the 'rationaleBySite required' error (current code).

    The `sites is not None` guard is vacuously true (sites is a list), so this
    fires whenever rationaleBySite is absent, regardless of has_sites.
    """
    if has_rationales == 0:
        return 1
    return 0


def main():
    has_sites = nondet_int()       # noqa: F821  associated/service sites present?
    has_rationales = nondet_int()  # noqa: F821  rationaleBySite field present?
    __ESBMC_assume(has_sites == 0 or has_sites == 1)            # noqa: F821
    __ESBMC_assume(has_rationales == 0 or has_rationales == 1)  # noqa: F821

    err = rationale_required_error(has_sites, has_rationales)

    # Contract: rationaleBySite is only *required* when there ARE associated/
    # service sites that need one.
    if err == 1:
        assert has_sites == 1   # FAILS: empty-sites + no-rationale -> spurious error


main()
