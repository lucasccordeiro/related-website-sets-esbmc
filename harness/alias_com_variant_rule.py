# Harness: RwsCheck.find_invalid_alias_eSLDs — ccTLD ".com"-variant rule
#
# Source: RwsCheck.py:455-498 (find_invalid_alias_eSLDs)
#   if aliased_tld in self.icanns:
#       icann_check = self.icanns.union({"com"})
#   else:
#       icann_check = self.icanns
#   for site, eSLD, tld in variants:
#       if eSLD != aliased_eSLD:           # error: brand label must match
#       if tld not in icann_check:         # error: tld must be ICANN ccTLD (or "com")
#
# An alias is ACCEPTED (no error) iff eSLD == aliased_eSLD AND tld in icann_check.
# Documented rule (RwsCheck.py:461-462): "A site may list a variant with 'com' as
# its eTLD IFF the site being aliased has an eTLD on ICANN's list of country codes."
#
# Verified property: an accepted alias whose TLD is "com" implies the aliased
# site's TLD is an ICANN country code.  (A derived consequence of the icann_check
# construction — not a restatement of a single guard.)
#
# Modelled as an integer/boolean abstraction of the domain attributes.  The
# faithful string-level model (real split(".") on symbolic domains) is BLOCKED by
# esbmc/esbmc#5110 (str.split unsound on symbolic strings); this abstraction is
# sound today and will be replaced once #5110 is fixed.
#
# Expected verdict: SUCCESSFUL (Phase 1 and Phase 2).

def main():
    # Domain attributes as 0/1 booleans.
    aliased_tld_ccTLD = nondet_int()   # noqa: F821  aliased site's TLD is an ICANN cc
    eSLD_match = nondet_int()          # noqa: F821  brand label matches
    tld_ccTLD = nondet_int()           # noqa: F821  variant TLD is an ICANN cc
    tld_com = nondet_int()             # noqa: F821  variant TLD == "com"

    __ESBMC_assume(aliased_tld_ccTLD == 0 or aliased_tld_ccTLD == 1)  # noqa: F821
    __ESBMC_assume(eSLD_match == 0 or eSLD_match == 1)                # noqa: F821
    __ESBMC_assume(tld_ccTLD == 0 or tld_ccTLD == 1)                  # noqa: F821
    __ESBMC_assume(tld_com == 0 or tld_com == 1)                      # noqa: F821
    # "com" is not an ICANN country code, so a TLD cannot be both.
    __ESBMC_assume(not (tld_com == 1 and tld_ccTLD == 1))             # noqa: F821

    # icann_check contains the variant TLD iff it is a ccTLD, or it is "com" and
    # the aliased site's TLD is a ccTLD.
    tld_allowed = (tld_ccTLD == 1) or (tld_com == 1 and aliased_tld_ccTLD == 1)
    accepted = (eSLD_match == 1) and tld_allowed

    # Rule: a ".com" variant is accepted only if the aliased TLD is an ICANN cc.
    if accepted and tld_com == 1:
        assert aliased_tld_ccTLD == 1


main()
