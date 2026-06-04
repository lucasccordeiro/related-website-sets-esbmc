# Harness: RwsCheck.find_invalid_alias_eSLDs — ".com"-variant rule (BUGGY)
#
# Non-vacuity / negative control for `alias_com_variant_rule.py`.  Mutation: the
# `aliased_tld in icanns` condition is dropped, so "com" is ALWAYS allowed —
# letting a ".com" variant alias a non-ccTLD site (e.g. brand.com aliasing
# brand.com), violating the documented rule.  ESBMC must catch it.
#
# Expected verdict: FAILED.

def main():
    aliased_tld_ccTLD = nondet_int()   # noqa: F821
    eSLD_match = nondet_int()          # noqa: F821
    tld_ccTLD = nondet_int()           # noqa: F821
    tld_com = nondet_int()             # noqa: F821

    __ESBMC_assume(aliased_tld_ccTLD == 0 or aliased_tld_ccTLD == 1)  # noqa: F821
    __ESBMC_assume(eSLD_match == 0 or eSLD_match == 1)                # noqa: F821
    __ESBMC_assume(tld_ccTLD == 0 or tld_ccTLD == 1)                  # noqa: F821
    __ESBMC_assume(tld_com == 0 or tld_com == 1)                      # noqa: F821
    __ESBMC_assume(not (tld_com == 1 and tld_ccTLD == 1))             # noqa: F821

    # BUG: "com" is allowed unconditionally (the aliased-tld-is-ccTLD guard is gone).
    tld_allowed = (tld_ccTLD == 1) or (tld_com == 1)
    accepted = (eSLD_match == 1) and tld_allowed

    if accepted and tld_com == 1:
        assert aliased_tld_ccTLD == 1   # FAILS: a .com variant of a non-ccTLD site


main()
