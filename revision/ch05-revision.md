# Chapter 5 — Revision Sheet: Git & GitHub

> Supplements [the full chapter](../docs/01-foundations/ch05-git-github.md).

## Mental model

```text
Working Directory --git add--> Staging Area (index) --git commit--> Repository --git push--> GitHub --> Pull Request --> Review + CI --> Merge
```

- **Git** = distributed version-control system, runs locally. **GitHub** = hosted platform for Git repos + collaboration (PRs, reviews, Actions). **A Pull Request is a GitHub mechanism, not a Git feature.**
- **Staging area** lets you build exactly what the next commit contains (`git add server.ts database.ts`, leave `README.md` unstaged).
- **Commit** = immutable snapshot + metadata (commit ID/hash, author, timestamp, message, parent commit(s), reference to the project tree). Git uses SHA-1 object IDs (SHA-256 repos are supported).
- **Git is a DAG of commits** (each commit points to its parent(s)); this is why branching is cheap.
- **Branch = a movable pointer to a commit**, not a copy of the project. `HEAD` → current branch → current commit.
- **Objects:** blob (file contents), tree (directory → blobs/trees), commit (tree + parents + metadata), tag. Strong answer to "how does Git store versions": *as content-addressed objects/snapshots, not copies of files per version*.

## Command groups

| Group | Commands |
|---|---|
| Daily | `git status`, `add`, `commit -m`, `pull`, `push`, `fetch`, `switch`, `log`, `diff` |
| Inspect | `git log --oneline --graph --decorate --all`, `git diff` (unstaged), `git diff --staged` |
| Branching | `git branch`, `git switch -c feature/x`, `git switch main` (older: `git checkout`), `merge`, `rebase` |
| Recovery | `restore`, `stash` / `stash pop`, `reset`, `revert`, `reflog` |
| Advanced | `cherry-pick`, `tag`, `remote -v`, `clone` |
| Pro workflow | `git switch main` → `git pull --ff-only` → `git switch -c feature/auth` → `status`/`diff` → `add src/auth` → `diff --staged` → `commit -m` → `push -u origin feature/auth` → PR → CI → review → merge |

## Merge vs rebase

| | Merge | Rebase |
|---|---|---|
| History | Preserves branch structure; may create a merge commit | Replays your commits on top of another base → linear history (E′, F′) |
| Rewrites history? | No | **Yes** (new commits) |
| Use for | Integrating branches, shared history | Updating a **private** feature branch on latest `main` |

- **Fast-forward merge:** target branch hasn't moved → Git just moves the pointer, no merge commit.
- **Three-way merge:** both branches moved → uses common ancestor + both tips → typically a merge commit.
- **Golden rule:** don't casually rebase shared/public history.
- **Conflict markers:** `<<<<<<< HEAD` … `=======` … `>>>>>>> feature/auth`. Edit → `git add file` → `git commit` (or continue the merge/rebase).

## Fetch / pull / push / remote

- `git fetch` downloads remote info **without** integrating (safe; inspect first). `git pull` ≈ `fetch + merge` (can be configured to rebase).
- `git push` sends missing objects and updates the remote branch ref — it doesn't upload the whole project each time.
- A **remote** is a reference to another repo; `origin` is only a convention. Fork workflow: `origin` = your fork, `upstream` = original; `git fetch upstream`.

## Undo cheat sheet

| Situation | Tool |
|---|---|
| Discard unstaged edits to a file | `git restore server.ts` (irrecoverable!) |
| Park unfinished work | `git stash` → switch → `git stash pop` |
| `reset --soft HEAD~1` | Move branch back; **keep changes staged** |
| `reset --mixed HEAD~1` (default) | Move back; **unstage**, keep working-tree changes |
| `reset --hard HEAD~1` | Move back; index + working tree match → **destroys uncommitted work** |
| Undo a commit already shared | `git revert <commit>` → new commit R that undoes D (A→B→C→D→R) — safer for shared branches |
| Lost commits after reset | `git reflog` — log of where HEAD/branches pointed; usually lets you recover |
| Take one commit from another branch | `git cherry-pick <D>` → D′ on current branch (backports, release branches; overuse complicates history) |

**reset = move/rewrite history; revert = add a new commit that undoes an old one.**

## Other concepts

- **Detached HEAD:** `git switch --detach <commit>` — HEAD points at a commit not a branch; commits made here can get lost unless you create a branch.
- **Tags:** `git tag v1.0.0`, `git push origin v1.0.0` — releases/versioning/deployment refs.
- **.gitignore:** `node_modules/`, `.env`, `dist/`, `*.log`. ⚠ It does **not** untrack a file already committed, nor erase it from history.
- **Security:** never commit `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `DATABASE_PASSWORD`, `JWT_SECRET`, `API_KEY`. Use env vars, secret managers, CI/CD secrets.
- **Branching strategies:** feature branches (merge via PR) · trunk-based development (small, frequent integration to main, short-lived branches; fewer conflicts, faster feedback) · Git Flow (`main`, `develop`, `feature/*`, `release/*`, `hotfix/*`) — recognise it, don't assume every company uses it.
- **Code review looks at:** correctness, security, performance, readability, tests, architecture, maintainability. CI checks lint, tests, build, type-checking, security scans.

## Scenarios

1. **Password pushed to GitHub:** (1) **rotate/revoke the credential first** (deleting history doesn't undo copying), (2) remove it from repo/history as appropriate, (3) investigate use, (4) add secret scanning/CI checks, (5) use proper secret management.
2. **Update feature branch after teammate pushed to main:** `git fetch` → update branch (merge **or** rebase) → resolve conflicts → test → push.

## Added precision (not in source)

- After rebasing a branch you already pushed, a plain push is rejected; teams use `git push --force-with-lease` on **private** branches only.
- `git restore --staged <file>` unstages a file (the source covers `restore` only for discarding working-tree edits).
- `git push -u origin feature/auth` sets the upstream so later `git push` / `git pull` know the remote branch.
- Reverting a **merge commit** needs `-m <parent-number>`.
- Removing a secret from history is done with tools such as `git filter-repo` or BFG; the credential must still be rotated.
- Annotated tags are real tag objects; lightweight tags are just refs.

## Interview questions (22) — pointers

Git vs GitHub; working tree/staging/repo; commit; branch (and why lightweight); HEAD; remote; merge vs rebase; FF vs 3-way; what causes/resolves conflicts; when to avoid rebase; reset vs revert; restore vs reset; stash; reflog; detached HEAD; fetch vs pull; what push does; what a PR is; feature branches vs trunk-based; Git Flow; plus the scenarios above.

<!-- NAV -->

---

← [Sheet 4](ch04-revision.md) · [Full chapter 5](../docs/01-foundations/ch05-git-github.md) · [All revision material](README.md) · [Sheet 6](ch06-revision.md) →
