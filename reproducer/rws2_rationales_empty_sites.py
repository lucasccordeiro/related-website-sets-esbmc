#!/usr/bin/env python3
"""
Empirical reproducer — Finding RWS-2
  RwsCheck.has_all_rationales (RwsCheck.py:111-127) flags "rationaleBySite is
  required" for a set with NO associated/service sites, because
  `sites = associatedSites + serviceSites` is always a list (never None), making
  the guard `if sites is not None and rationales is None` vacuously true.

Source (verbatim, GoogleChrome/related-website-sets):
  sites = rwset.get("associatedSites", []) + rwset.get("serviceSites", [])
  rationales = rwset.get("rationaleBySite", None)
  if sites and rationales is not None:
      for site in sites:
          if site not in rationales.keys():
              error("There is no provided rationale for {site}")
  if sites is not None and rationales is None:        # always-true guard
      error("A rationaleBySite field is required ... none is provided.")

Dependencies: none (pure Python stdlib).
"""

def has_all_rationales_errors(rwset):
    """Verbatim logic from RwsCheck.has_all_rationales for one set."""
    errs = []
    sites = rwset.get("associatedSites", []) + rwset.get("serviceSites", [])
    rationales = rwset.get("rationaleBySite", None)
    if sites and rationales is not None:
        for site in sites:
            if site not in rationales.keys():
                errs.append(f"There is no provided rationale for {site}")
    if sites is not None and rationales is None:
        errs.append("A rationaleBySite field is required for this set, "
                    "but none is provided.")
    return errs


# A valid set: a primary plus ccTLD variants, but no associated/service sites and
# (correctly) no rationaleBySite — there is nothing to rationalise.
primary_only = {
    "primary": "https://a.example",
    "ccTLDs": {"https://a.example": ["https://a.example.co.uk"]},
}

errs = has_all_rationales_errors(primary_only)
print(f"sites = associatedSites + serviceSites = "
      f"{primary_only.get('associatedSites', []) + primary_only.get('serviceSites', [])}")
print(f"errors returned: {errs}")
print()

assert errs and "rationaleBySite field is required" in errs[0]
print("CONFIRMED: has_all_rationales flags 'rationaleBySite required' for a set")
print("  with no associated/service sites (nothing needs a rationale).")
print()

# Contrast — the fix (require only when there ARE sites) returns no error.
def has_all_rationales_fixed(rwset):
    errs = []
    sites = rwset.get("associatedSites", []) + rwset.get("serviceSites", [])
    rationales = rwset.get("rationaleBySite", None)
    if sites and rationales is not None:
        for site in sites:
            if site not in rationales.keys():
                errs.append(f"There is no provided rationale for {site}")
    if sites and rationales is None:        # FIX: `sites` (non-empty), not `sites is not None`
        errs.append("A rationaleBySite field is required ... none is provided.")
    return errs


print(f"fixed (primary-only set): {has_all_rationales_fixed(primary_only)}")
assert has_all_rationales_fixed(primary_only) == []
print()
print("Proposed fix: gate on `if sites and rationales is None:` (truthiness of the")
print("non-empty list) instead of `if sites is not None ...` (always true).")
