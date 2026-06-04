# related-website-sets / ESBMC-Python PoC — verification record

Per-target results. See [`ROADMAP.md`](./ROADMAP.md) for the plan and blockers.

Pinned upstream: `GoogleChrome/related-website-sets` (archived, read-only).
Verifier: ESBMC built from `master` (incl. esbmc/esbmc#5090 + #5100).

---

## Target index

| Name | Entry | Phase 1 | VCCs | Phase 2 | VCCs | Notes |
|---|---|---|---|---|---|---|
| `well_known_list_order_false_positive` | `well_known_list_order_false_positive.py` | **FAILED** | 1 | skipped | — | **Finding RWS-1 — witness** |
| `well_known_list_setdiff_validated` | `well_known_list_setdiff_validated.py` | SUCCESSFUL | 1 | SUCCESSFUL | 1 | positive control: diff-based check |
| `alias_com_variant_rule` | `alias_com_variant_rule.py` | SUCCESSFUL | 1 | SUCCESSFUL | 1 | security invariant: `.com`-variant rule |
| `alias_com_variant_rule_buggy` | `alias_com_variant_rule_buggy.py` | **FAILED** | 1 | skipped | — | non-vacuity: dropped ccTLD guard caught |
| `rationales_empty_sites_false_positive` | `rationales_empty_sites_false_positive.py` | **FAILED** | 1 | skipped | — | **Finding RWS-2 — witness** |
| `rationales_validated` | `rationales_validated.py` | SUCCESSFUL | 1 | SUCCESSFUL | 1 | positive control: required only when sites exist |
| `check_exclusivity_invariant` | `check_exclusivity_invariant.py` | SUCCESSFUL | 1 | SUCCESSFUL | 1 | exclusivity invariant: site in two sets is flagged |
| `check_exclusivity_invariant_buggy` | `check_exclusivity_invariant_buggy.py` | **FAILED** | 1 | skipped | — | non-vacuity: dropped overlap check caught |

**Total targets: 8 (4 SUCCESSFUL + 4 FAILED). Every target matches its expected
verdict; 0 deviations.**

All current targets are integer/boolean abstractions (see ROADMAP — string-level
harnesses are blocked by esbmc/esbmc#5110).

---

## Finding RWS-1 — `check_well_known_list` false-positive (over-strict)

**Source**: `RwsCheck.py:336-358`

```python
def check_well_known_list(self, field, list1, list2):
    # "returns an empty list if the 2 fields are symmetric"
    if list1 == list2:                      # exact LIST equality (order + dups)
        return []
    diff = sorted(set(list1) ^ set(list2))  # symmetric diff computed…
    return [f"…Diff was: {diff}."]           # …but error returned even if diff == []
```

The docstring promises no error when the fields are "symmetric" (= symmetric diff
empty = set-equal), but the code only short-circuits on exact list equality and
otherwise always errors. A set-equal pair that differs in order or has a
duplicate therefore triggers a spurious mismatch error reading `Diff was: []`.

**ESBMC witness** (`well_known_list_order_false_positive.py`, Phase 1 FAILED,
1 VCC): with `sets_equal = 1`, `lists_equal = 0` the modelled check returns an
error, violating the documented contract `sets_equal ⟹ no error`. The paired
`well_known_list_setdiff_validated.py` models the fix (gate on the symmetric
diff) and is SUCCESSFUL. Confirmed under CPython
(`reproducer/rws1_well_known_set_equal.py`): `["a","b"]` vs `["b","a"]` →
`['…Diff was: [].']`.

**Severity**: LOW — over-strict validation (rejects a benign, set-equal
submission with a confusing empty-diff message). Not a security issue.

**Proposed fix**: `return [] if not diff else [error]`.

**Disposition**: not filed — upstream repo is archived.

---

## find_invalid_alias_eSLDs — ccTLD `.com`-variant rule (proof of absence)

**Source**: `RwsCheck.py:455-498`

Documented rule: "A site may list a variant with 'com' as its eTLD IFF the site
being aliased has an eTLD on ICANN's list of country codes." Encoded as
`icann_check = icanns ∪ {"com"}` only when `aliased_tld in icanns`.

`alias_com_variant_rule.py` models the accept logic over symbolic domain
attributes (booleans for *is-ccTLD* / *is-com* / *eSLD-match*) and proves the
derived invariant: **an accepted alias whose TLD is `"com"` implies the aliased
site's TLD is an ICANN country code.** Phase 1 + Phase 2 SUCCESSFUL. The buggy
control (`alias_com_variant_rule_buggy.py`, drops the `aliased_tld in icanns`
guard) FAILS, confirming non-vacuity.

This is a proof of absence (the rule holds); the naive `split(".")[0]` eSLD
extraction in the source is compensated by eTLD+1 enforcement elsewhere, so no
bypass exists. A faithful string-level model is blocked by esbmc/esbmc#5110.

---

## Finding RWS-2 — `has_all_rationales` over-strict required-field check

**Source**: `RwsCheck.py:111-127`

```python
sites = rwset.get("associatedSites", []) + rwset.get("serviceSites", [])  # always a list
rationales = rwset.get("rationaleBySite", None)
if sites and rationales is not None:
    for site in sites:
        if site not in rationales.keys():
            error(f"There is no provided rationale for {site}")
if sites is not None and rationales is None:    # sites is never None -> always true
    error("A rationaleBySite field is required ... none is provided.")
```

`sites` is a concatenation of two `.get(..., [])` lists, so it is never `None`,
making the second guard vacuously true: `rationaleBySite` is reported as required
whenever the field is absent, even for a primary-only set with no associated/
service sites (nothing to rationalise). The guard should be `if sites` (non-empty).

**ESBMC witness** (`rationales_empty_sites_false_positive.py`, Phase 1 FAILED,
1 VCC): with `has_sites = 0`, `has_rationales = 0` the modelled check raises the
required-field error, violating the contract `error ⟹ has_sites`. The paired
`rationales_validated.py` models the fix (`if sites and rationales is None`) and
is SUCCESSFUL. Confirmed under CPython
(`reproducer/rws2_rationales_empty_sites.py`): a primary-only set yields
`["A rationaleBySite field is required ..."]`.

**Severity**: LOW — over-strict (rejects a valid submission). Not a security issue.

**Proposed fix**: `if sites and rationales is None:`.

**Disposition**: not filed — upstream repo is archived.

---

## check_exclusivity — site-exclusivity invariant (proof of absence)

**Source**: `RwsCheck.py:128-179`

`check_exclusivity` accumulates a cumulative `site_list` over all sets and reports
an overlap whenever a later set re-uses a site already registered by an earlier
one (across primary / associated / service / ccTLD fields).

`check_exclusivity_invariant.py` models the cumulative-membership core for one
symbolic site claimed by set A (first) and/or set B, and proves the invariant: **a
site claimed by both sets is flagged** (never silently registered in two sets).
Phase 1 + Phase 2 SUCCESSFUL. The buggy control
(`check_exclusivity_invariant_buggy.py`, drops set B's overlap check) FAILS,
confirming the invariant is non-vacuous. A faithful string-set model over the full
field set is deferred (esbmc/esbmc#5110).
