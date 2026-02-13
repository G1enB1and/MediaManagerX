#!/usr/bin/env bash
set -euo pipefail

# Push the current workspace's MediaManager subtree split to a *new branch* on GitHub.
# This avoids non-fast-forward issues when the GitHub repo main history diverges.
#
# Usage:
#   ./scripts/push_subtree_branch.sh [branch-name]
#
# Requirements:
# - `gh auth login` completed
# - run from inside the MediaManager workspace root (repo has MediaManager/ prefix)

BRANCH_NAME=${1:-"workspace-sync-$(date +%Y%m%d-%H%M%S)"}
REPO_URL=${REPO_URL:-"https://github.com/G1enB1and/MediaManager.git"}
PREFIX=${PREFIX:-"MediaManager"}

ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
cd "$ROOT_DIR"

SPLIT_SHA=$(git subtree split --prefix "$PREFIX")
TOKEN=$(gh auth token)
B64=$(printf 'x-access-token:%s' "$TOKEN" | base64 -w0)

export GIT_TERMINAL_PROMPT=0

git -c credential.helper= -c http.extraHeader="Authorization: Basic $B64" \
  push "$REPO_URL" "$SPLIT_SHA:refs/heads/$BRANCH_NAME"

echo "Pushed subtree split $SPLIT_SHA to branch: $BRANCH_NAME"
