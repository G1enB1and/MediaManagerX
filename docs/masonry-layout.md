# Masonry layout (container-first)

## Goal
MediaManager’s gallery should avoid visible layout jumping during asset load.

We want a layout pass that depends only on:
- The **container width** (known at render time)
- A target **column count** (or computed from min column width)
- A **gutter** spacing
- Each item’s **estimated height**
  - Prefer aspect ratio when known (from metadata / file probe)
  - Otherwise use a fallback height

The UI can later reconcile to true decoded dimensions (e.g., after image decode)
without reflowing the entire page.

## Contract
Given:
- `container_width_px`
- `columns`
- `gutter_px`
- a list of items `{ key, aspect_ratio?, fallback_height_px }`

Compute:
- placements `{ key, column, x, y, width, height }`
- total content height

See implementation: `app/mediamanager/layout/masonry.py`.

## Algorithm
Greedy “shortest column” assignment:
1. Compute `col_width = floor((container_width - gutter*(columns-1)) / columns)`
2. Track `col_heights[]` (starting at 0)
3. For each item in order:
   - pick `col = argmin(col_heights)` (stable tie-break to lowest index)
   - `x = col * (col_width + gutter)`
   - `y = col_heights[col]`
   - compute `height`:
     - if `aspect_ratio > 0`: `height = round(col_width / aspect_ratio)`
     - else: `height = fallback_height_px`
   - emit placement
   - update `col_heights[col] += height + gutter`
4. `total_height = max(col_heights) - gutter` (or 0 if no items)

## Notes / future work
- Column count selection policy (responsive): helper added in
  `app/mediamanager/layout/columns.py` (`choose_columns`). UI may still apply
  explicit breakpoints.
- Stabilization: maintain consistent ordering; keep stable tie-breaks.
- Reconciliation: if an item’s decoded aspect ratio differs from estimate, adjust
  that column below the item; avoid global reflow.
- Pagination: apply layout within each page and virtualize rendering.
