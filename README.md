# related-website-sets Veribee ESBMC-Python verification PoC

A proof-of-concept applying [ESBMC](https://github.com/esbmc/esbmc)'s Python
frontend to [GoogleChrome/related-website-sets](https://github.com/GoogleChrome/related-website-sets)
(RWS) — the submission-validation tooling that checks Related Website Set entries
(domain rules, ccTLD aliases, well-known consistency) before they ship to Chrome.

Companion to the [chromium-dashboard PoC](https://github.com/lucasccordeiro/chromium-dashboard-esbmc).

> **Note:** `related-website-sets` is **archived** upstream (read-only), so
> findings here are a verification *demonstration*, not fileable bug reports.

## Status

**10 verification targets**, `make verify` (two phases) with 0 failures:

| Target | Verdict | What it checks |
|---|---|---|
| `well_known_list_order_false_positive` | **FAILED** (witness) | RWS-1: `check_well_known_list` reports a spurious mismatch for set-equal-but-reordered lists |
| `well_known_list_setdiff_validated` | SUCCESSFUL | the fix (gate on the symmetric diff) honors the documented contract |
| `rationales_empty_sites_false_positive` | **FAILED** (witness) | RWS-2: `has_all_rationales` requires `rationaleBySite` even for a set with no associated/service sites |
| `rationales_validated` | SUCCESSFUL | the fix (require only when sites exist) |
| `alias_com_variant_rule` | SUCCESSFUL | `find_invalid_alias_eSLDs`: a `.com` variant is accepted only if the aliased TLD is an ICANN country code (proof of absence) |
| `alias_com_variant_rule_buggy` | **FAILED** (control) | dropping the guard (always allow `.com`) violates the rule — caught |
| `check_exclusivity_invariant` | SUCCESSFUL | `check_exclusivity`: a site claimed by two sets is always flagged (proof of absence) |
| `check_exclusivity_invariant_buggy` | **FAILED** (control) | dropping the overlap check lets a cross-set duplicate through — caught |
| `load_sets_duplicate_primary_detected` | SUCCESSFUL | `load_sets`: a primary listed by two sets is flagged (proof of absence) |
| `load_sets_duplicate_primary_buggy` | **FAILED** (control) | dropping the `primary in check_sets` check lets a duplicate primary through — caught |

```bash
make verify ESBMC=/path/to/esbmc
```

## Finding RWS-1 — `check_well_known_list` false-positive (low severity)

`RwsCheck.check_well_known_list` (`RwsCheck.py:336-358`) documents that it
"returns an empty list if the 2 fields are symmetric", and even computes the
symmetric diff — but it gates the no-error path on **exact list equality** and
otherwise *always* returns an error:

```python
if list1 == list2:                      # order + multiplicity
    return []
diff = sorted(set(list1) ^ set(list2))  # computed…
return [f"…Diff was: {diff}."]           # …but error returned even when diff == []
```

So a PR/well-known pair that is **set-equal but reordered** (or contains a
duplicate) produces a false-positive mismatch error literally reading
`Diff was: []`. This is an over-strict validation defect (rejects a benign
submission), confirmed by `reproducer/rws1_well_known_set_equal.py` and the
`well_known_list_order_false_positive` ESBMC witness. **Fix:** `return [] if not
diff else [error]` (gate on the symmetric diff; `associatedSites` order is not
significant).

## Finding RWS-2 — `has_all_rationales` over-strict required-field check (low severity)

`RwsCheck.has_all_rationales` (`RwsCheck.py:111-127`) requires `rationaleBySite`
whenever it is absent — even for a set with **no** associated/service sites:

```python
sites = rwset.get("associatedSites", []) + rwset.get("serviceSites", [])  # always a list
rationales = rwset.get("rationaleBySite", None)
...
if sites is not None and rationales is None:          # sites is never None -> vacuously true
    error("A rationaleBySite field is required ... none is provided.")
```

`sites` is the concatenation of two `.get(..., [])` lists, so it is never `None`;
the guard should be `if sites` (non-empty), not `if sites is not None`. As written,
a valid primary-only set (just a primary + ccTLDs, nothing to rationalise) is
flagged as missing `rationaleBySite`. Confirmed by the
`rationales_empty_sites_false_positive` witness and
`reproducer/rws2_rationales_empty_sites.py`. **Fix:** gate on `if sites and
rationales is None:`. Low severity (over-strict; rejects a valid submission).

## Proofs of absence — `check_exclusivity` and `load_sets`

`check_exclusivity` (`RwsCheck.py:128-179`) accumulates a cumulative `site_list`
and flags any site re-used across sets. `check_exclusivity_invariant` proves the
exclusivity guarantee — a site claimed by two sets is always flagged — over a
cumulative-membership abstraction; the buggy control (overlap check dropped)
FAILS, confirming non-vacuity.

`load_sets` (`RwsCheck.py:66-95`) keys `check_sets` by primary and flags any
primary listed more than once ("already a primary of another site").
`load_sets_duplicate_primary_detected` proves a primary listed by two sets is
always flagged; the buggy control (the `primary in check_sets` check dropped)
FAILS.

## A note on modelling — string-level harnesses are blocked

RWS validation parses **symbolic domain strings** with `split(".")` / `replace()`
(e.g. `find_invalid_alias_eSLDs`, `is_eTLD_Plus1`). ESBMC currently mis-models
`str.split()` on a symbolic/runtime receiver (returns a 1-element list →
unsound), filed as [esbmc/esbmc#5110](https://github.com/esbmc/esbmc/issues/5110)
(after the related #5085 / #5096 were fixed for constant receivers). Until #5110
is fixed, the current targets use **integer/boolean abstractions** of the domain
attributes — sound today, and to be upgraded to faithful string-level harnesses
once symbolic-string `split` works. See [`ROADMAP.md`](./ROADMAP.md).

## Layout

```
harness/      ESBMC harnesses (good = SUCCESSFUL, buggy/witness = FAILED)
reproducer/   standalone CPython reproductions of findings
verify.py     target manifest + two-phase runner
Makefile      make verify / phase1 / phase2 / verify-only
REPORT.md     per-target results + finding traces
ROADMAP.md    plan, the #5110 blocker, and string-level targets to add
```

Pinned upstream: `GoogleChrome/related-website-sets` (archived). Verifier: ESBMC
built from `master` with #5090 + #5100 (str.split constant-receiver fixes).
