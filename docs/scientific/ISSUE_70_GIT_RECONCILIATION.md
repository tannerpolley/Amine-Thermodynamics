# Issue 70 Git reconciliation

Date: 2026-08-25

## Selected base

| Ref | Commit |
|---|---|
| Dirty topic `codex/model-hierarchy-literature-review` | `e00f1daba78c120af9c3f5981373ae6374597c57` |
| Local default `main` | `5ec1c550e01392b2970672c4d6aa1cf7e84d0107` |
| Remote default `origin/main` | `838f5a5a068ea10f620c57f0cab83d789374608d` |
| Integration base | `838f5a5a068ea10f620c57f0cab83d789374608d` |

The local-default and remote-default commits contain the same `.codex/environments/setup.sh`
change. `git range-diff d23ce51..main d23ce51..origin/main` reports only commit
metadata differences. The remote commit is the merged Issue 69 history and is
therefore the integration base. A nonmutating
`git merge-tree --write-tree e00f1da 838f5a5` completed without conflict and
produced tree `24e5724b7e60f965c4db6f793ca04e73d3e0c26c`.

## Dirty-state inventory

The preserved pre-integration checkout contained 413 paths: 64 tracked
changes, 349 untracked files, and 39 tracked deletions. For each inventory
below, records are sorted by path and encoded as
`status<TAB>sha256-or-deleted<TAB>path<LF>` before hashing.

| Inventory | Paths | SHA-256 |
|---|---:|---|
| Complete dirty state | 413 | `630db5a919b8f706dc9cc8973becfaacc092a244a2c56998f32ec51e1b46b041` |
| Scientific inputs and configurations | 60 | `df536c4272ee25130d50427c6ca4a888a067f3a91237e73ea528895261f5f210` |
| Calculated results and figures | 280 | `5d5d7d769f49d2a3e9cc4d57331be83d6002599a770843dd53320cb81ca23544` |
| Executable Python sources | 55 | `830f4e597c88a48c1453b6ff242bce4b3c60e4e6ae2ef0da67ab829c635d521b` |
| Authority and notebook sources | 14 | `685f65ce966a12f5ad4bc1ec5170641ec9fb7d0b4e2dd002fc8ebb35b2d0920c` |

The issue-owned slices are observation provenance (#62), neutral-binary
qualification (#63), electrostatic selection (#64), induced association
(#65), fixed-configuration assembly (#67), reactive fitting (#13),
multiple-property comparison (#14), and Issue 70 aggregation/cleanup. Their
exact path inventories are the path lists of the corresponding commits; no
dirty path is assigned to more than one commit.

| Slice | Source commit |
|---|---|
| Observation provenance (#62) | `f5be5cc` |
| Neutral-binary qualification (#63) | `7f1ac24` |
| Induced association (#65) | `e376025` |
| Electrostatic selection (#64) | `aa4f6d9` |
| Fixed configuration (#67) | `49a436c` |
| Reactive fitting (#13) | `130f42a` |
| Multiple-property comparison (#14) | `15fb655` |
| Issue 70 aggregation and cleanup | this commit |

## Bülow exclusion

The separately active Bülow work is outside this repository at
`$HOME/.codex/worktrees/4ccc/ePC-SAFT-project` on
`codex/bulow-2021-fit-reproduction`, commit
`891a23bea9428f9ce49e9bfcc158636ae51fda6c`, tracking the identical remote
commit. Its owned campaign is `validation/campaigns/2021-bulow-sour-gas/`.
That worktree was clean at reconciliation and no file in it was staged,
modified, copied, or absorbed by Issue 70.
