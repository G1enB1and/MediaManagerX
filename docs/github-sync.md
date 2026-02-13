# GitHub Sync Notes

## Why pushes to `main` may fail
If the GitHub repo `main` history was created from a different snapshot than the history produced by:

```bash
git subtree split --prefix MediaManager
```

…then pushes to `main` will be rejected as non-fast-forward.

## Recommended workflow (safe)
1. Push to a new branch.
2. Open a PR.
3. Merge the PR on GitHub.

After the first merge, future pushes should fast-forward normally (as long as we keep using the same history line).

## Helper script
From the workspace root (the repo that contains the `MediaManager/` folder):

```bash
chmod +x MediaManager/scripts/push_subtree_branch.sh
MediaManager/scripts/push_subtree_branch.sh
```

This pushes the current subtree split to a new branch like `workspace-sync-YYYYMMDD-HHMMSS`.
