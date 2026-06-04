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
| `find_invalid_alias_eSLDs` | `alias_com_variant_rule` + `_buggy` | `.com`-variant rule proof of absence |

## Candidate next targets

1. **`check_exclusivity`** (`RwsCheck.py:69-119`) — a site (primary/associated/
   service/ccTLD) must not appear in more than one set. Model set membership over
   a small symbolic domain; assert no site is accepted into two sets. Integer-set
   abstraction works today.
2. **`is_eTLD_Plus1` / `find_invalid_eTLD_Plus1`** — string-level (split/
   removeprefix); **blocked by #5110**. Abstraction possible (model "is registrable
   label" as a boolean) for the higher-level rule.
3. **`has_all_rationales`** (`RwsCheck.py:38-66`) — every associated/service site
   must have a `rationaleBySite` entry; model presence over a symbolic site set.
4. **`find_invalid_alias_eSLDs` — string-level upgrade** of the `.com` rule once
   #5110 is fixed (real `split(".")` on symbolic domains).

## Out of scope

- Network I/O (`requests.get` for well-known pages, robots.txt) — stubbed/nondet.
- Full publicsuffixlist / ICANN data — abstracted to small symbolic sets.
