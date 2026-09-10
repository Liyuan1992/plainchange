# Implementation plan

## Regions in this round

1. Add strict profile data and a derived, labelled concept-map model.
2. Add the concept-map card before the static-code workspace and retain the old workspace as the second layer.
3. Add click-through from a mapped concept component to an existing static group.

## Files expected to change

- `src/change_passport/target_profile.py`
- target-profile JSON assets
- `src/change_passport/review_model.py`
- `src/change_passport/templates/review.html`, `review.css`, `review.js`
- focused tests and governance/UI validation records

## Things not to change

- Git collection, architecture delta extraction, baseline approval semantics, model bridge, or target repository access.

## Expected screenshot difference

The architecture tab opens with a readable left-to-right input → processing → output → human-gate diagram. The static import map appears below with an explicit implementation-layer heading.
