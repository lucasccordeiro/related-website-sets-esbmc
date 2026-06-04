# related-website-sets / ESBMC-Python PoC — roadmap

Forward-looking plan. Companion to [`REPORT.md`](./REPORT.md).

## Context

`GoogleChrome/related-website-sets` ships `RwsCheck.py` — a validation engine for
RWS submissions: domain rules (eTLD+1, https), ccTLD-alias rules, well-known-file
consistency, exclusivity, and rationale presence. It is **archived** (read-only),
so this PoC is a verification demonstration; findings are not fileable upstream.

## Method

Same two-phase scheme as the chromium-dashboard PoC: Phase 1 (functional
contract via `assert`), Phase 2 (`--overflow-check`). Each target has a "good"
harness (SUCCESSFUL) and, where a defect exists, a paired witness (FAILED);
positive controls carry a buggy non-vacuity control.

## The string-modelling blocker (esbmc/esbmc#5110)

Most `RwsCheck` checks parse **symbolic domain strings** with `split(".")` /
`replace()` (`find_invalid_alias_eSLDs`, `is_eTLD_Plus1`, `find_non_https_urls`,
`check_list_sites`). ESBMC currently mis-models `str.split()` on a
**symbolic/runtime receiver** — it returns a 1-element list, which makes any such
harness vacuous (a buggy control wrongly verifies). Filed as
**esbmc/esbmc#5110** (the constant-receiver cases were already fixed in #5090 /
#5100). Until #5110 lands:

- Targets use **integer/boolean abstractions** of the domain attributes (sound,
  but one step removed from the source text).
- Once symbolic-string `split` works, each abstraction is to be **upgraded** to a
  faithful string-level harness that runs the real `split(".")` logic over
  symbolic domains.

## Covered

| Area | Targets | Notes |
|---|---|---|
| `check_well_known_list` | `well_known_list_order_false_positive` (witness) + `well_known_list_setdiff_validated` (control) | Finding RWS-1: set-equal-but-reordered false positive |
| `has_all_rationales` | `rationales_empty_sites_false_positive` (witness) + `rationales_validated` (control) | Finding RWS-2: `rationaleBySite` required even with no sites (`sites is not None` always true) |
| `find_invalid_alias_eSLDs` | `alias_com_variant_rule` + `_buggy` | `.com`-variant rule proof of absence |
| `check_exclusivity` | `check_exclusivity_invariant` + `_buggy` | site-exclusivity invariant proof of absence |
| `load_sets` | `load_sets_duplicate_primary_detected` + `_buggy` | duplicate-primary detection proof of absence |

## Candidate next targets

1. **`is_eTLD_Plus1` / `find_invalid_eTLD_Plus1`** — string-level (split/
   removeprefix); **blocked by #5110**. Abstraction possible (model "is registrable
   label" as a boolean) for the higher-level rule.
2. **`find_invalid_eTLD_Plus1` / `url_is_https`** — per-field validation over the
   set; abstraction of "is registrable / is https" booleans works today.
3. **`check_exclusivity` — full-field string upgrade** of the cumulative
   site_list across primary/associated/service/ccTLD once #5110 is fixed.
4. **`find_invalid_alias_eSLDs` — string-level upgrade** of the `.com` rule once
   #5110 is fixed (real `split(".")` on symbolic domains).

## Out of scope

- Network I/O (`requests.get` for well-known pages, robots.txt) — stubbed/nondet.
- Full publicsuffixlist / ICANN data — abstracted to small symbolic sets.
