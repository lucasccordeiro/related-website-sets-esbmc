#!/usr/bin/env python3
"""
Empirical reproducer — Finding RWS-1
  RwsCheck.check_well_known_list (RwsCheck.py:336-358) reports a spurious
  mismatch error when the PR and well-known lists are set-equal but differ in
  order or duplicates — because it gates the no-error path on exact LIST
  equality while computing (and ignoring) the symmetric diff.

Source (verbatim, GoogleChrome/related-website-sets):
  def check_well_known_list(self, field, list1, list2):
      # "returns an empty list if the 2 fields are symmetric"
      if list1 == list2:
          return []
      diff = sorted(set(list1) ^ set(list2))
      return [f"... Diff was: {diff}."]

Dependencies: none (pure Python stdlib).
"""

def check_well_known_list(field, list1, list2):
    """Verbatim logic from RwsCheck.check_well_known_list."""
    if list1 == list2:
        return []
    diff = sorted(set(list1) ^ set(list2))
    return [f"Inequality in {field}; Diff was: {diff}."]


# Same sites, different order — set-symmetric, so the documented contract says
# this should produce NO error.
pr = ["https://a.example", "https://b.example"]
wk = ["https://b.example", "https://a.example"]

errs = check_well_known_list("associatedSites", pr, wk)
print(f"PR:        {pr}")
print(f"well-known:{wk}")
print(f"symmetric diff: {sorted(set(pr) ^ set(wk))}   (empty -> sets are equal)")
print(f"errors returned: {errs}")
print()

assert errs, "expected the current code to (wrongly) report an error"
assert "Diff was: []" in errs[0], "the error embeds an empty diff -- the tell"
print("CONFIRMED: check_well_known_list reports a false-positive mismatch")
print('  ("Diff was: []") for set-equal lists that differ only in order.')
print()

# A duplicate triggers the same false positive.
errs_dup = check_well_known_list("associatedSites",
                                 ["https://a.example", "https://a.example"],
                                 ["https://a.example"])
print(f"duplicate case errors: {errs_dup}")
assert errs_dup and "Diff was: []" in errs_dup[0]
print()

# Contrast — the fix (gate on the symmetric diff) returns no error.
def check_well_known_list_fixed(field, list1, list2):
    diff = sorted(set(list1) ^ set(list2))
    if not diff:
        return []
    return [f"Inequality in {field}; Diff was: {diff}."]


print(f"fixed (set-equal, reordered): {check_well_known_list_fixed('associatedSites', pr, wk)}")
assert check_well_known_list_fixed("associatedSites", pr, wk) == []
print()
print("Proposed fix: return [] if not diff else [error]  (gate on the symmetric")
print("diff, per the docstring; associatedSites order is not significant).")
