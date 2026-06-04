# Harness: RwsCheck.check_exclusivity — site-exclusivity invariant (proof of absence)
#
# Source: RwsCheck.py:128-179
#   site_list = set()
#   for primary, rws in check_sets.items():
#       if primary in site_list: error(...)
#       else: site_list.add(primary)
#       overlap = set(rws.associated_sites) & site_list
#       if overlap: error(...) else: site_list.update(rws.associated_sites)
#       ... (service sites, ccTLD aliases — same pattern)
#
# Exclusivity invariant: a site claimed by two different sets must be flagged —
# `check_exclusivity` accumulates a cumulative `site_list` and reports an overlap
# whenever a later set re-uses a site already registered by an earlier one.
#
# Modelled over one symbolic site claimed by set A (processed first) and/or set B
# (the cumulative-membership core of the check), as a boolean abstraction.  The
# faithful string-set model is deferred (see ROADMAP / esbmc#5110).
#
# Verified property: a site in both sets is flagged.
# Expected verdict: SUCCESSFUL (Phase 1 and Phase 2).

def check_exclusivity_flags(in_A, in_B):
    """Cumulative-membership model: the site is flagged on its second claim."""
    in_list = 0
    flagged = 0
    if in_A == 1:                  # set A processed first
        if in_list == 1:
            flagged = 1
        else:
            in_list = 1
    if in_B == 1:                  # set B: overlap checked against site_list
        if in_list == 1:
            flagged = 1
        else:
            in_list = 1
    return flagged


def main():
    in_A = nondet_int()  # noqa: F821  site claimed by set A?
    in_B = nondet_int()  # noqa: F821  site claimed by set B?
    __ESBMC_assume(in_A == 0 or in_A == 1)  # noqa: F821
    __ESBMC_assume(in_B == 0 or in_B == 1)  # noqa: F821

    flagged = check_exclusivity_flags(in_A, in_B)

    # Exclusivity: a site claimed by both sets must be flagged (never silently
    # accepted into two related website sets).
    if in_A == 1 and in_B == 1:
        assert flagged == 1


main()
