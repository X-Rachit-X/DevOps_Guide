# Chapter 5 — Git & GitHub Deep Dive

> **Source:** Response 5 of the original conversation (`source-archive/src-05.txt`, lines 1–1644) · **Part I — Core curriculum (Responses 1–24)**  
> **Study aids:** [Revision sheet](../../revision/ch05-revision.md) · [Contents](../../CONTENTS.md) · [Glossary](../../GLOSSARY.md)

<!-- SOURCE-BEGIN -->

We're now entering the **DevOps workflow** itself.

You've probably used Git before, so I won't waste time teaching `git add` as if it's your first day. Instead, we'll build the mental model from **how Git works → everyday workflow → branches → merging/rebasing → conflicts → recovery → collaboration → professional workflows**.

The goal is that in an interview you can explain not only *what command to run*, but **what Git is actually doing**.

---

## 1. Why Do We Need Git?

Imagine you're building your TypeScript backend.

Monday:

```text
server.ts
```

Tuesday:

```text
server-v2.ts
```

Wednesday:

```text
server-final.ts
```

Thursday:

```text
server-final-final.ts
```

😄

This becomes impossible to manage.

Git solves this by tracking changes over time.

```text
Version 1
   ↓
Version 2
   ↓
Version 3
   ↓
Version 4
```

You can:

- see what changed
- identify who changed it
- revert changes
- create branches
- collaborate
- merge work
- recover previous versions

---

## 2. Git vs GitHub

This distinction is extremely important.

#### Git

A **distributed version-control system**.

It runs locally.

```text
Your computer
    ↓
Git
```

#### GitHub

A hosted platform for Git repositories and collaboration.

```text
Your computer
      ↓
     Git
      ↓
   GitHub
```

Git can work without GitHub.

You could use Git with another remote hosting provider or even just locally.

---

## 3. The Git Mental Model

This is the most important concept.

Git broadly works with:

```text
Working Directory
       ↓
    Staging Area
       ↓
    Repository
```

Think:

```text
Your files
   ↓
git add
   ↓
Staging area
   ↓
git commit
   ↓
Git repository
```

---

## 4. Working Directory

This is your actual project.

Example:

```text
my-api/
├── src/
├── package.json
├── tsconfig.json
└── README.md
```

You modify:

```typescript
const port = 3000;
```

Git sees that the working directory differs from the last committed version.

Check:

```bash
git status
```

---

## 5. Staging Area

Suppose you changed:

```text
server.ts
database.ts
README.md
```

But you only want to commit:

```text
server.ts
database.ts
```

You stage them:

```bash
git add server.ts database.ts
```

Now:

```text
Working Directory
       │
       ├── server.ts      → staged
       ├── database.ts    → staged
       └── README.md      → unstaged
```

The staging area lets you construct **exactly what you want the next commit to contain**.

---

## 6. Commit

Now:

```bash
git commit -m "Add database connection"
```

Git creates a commit.

Conceptually:

```text
Working Directory
       ↓
Staging Area
       ↓
Commit
```

A commit represents a snapshot of your project state, together with metadata and relationships to previous commits.

---

## 7. What Is Actually Inside a Commit?

A commit contains information such as:

```text
Commit ID
Author
Timestamp
Message
Parent commit(s)
Reference to project snapshot/tree
```

Example:

```text
a83f91c
```

The identifier is based on Git's object hashing mechanisms.

Modern Git uses SHA-1 for many object IDs, with support for SHA-256 repositories as well.

For interviews, understand:

> **A commit is an immutable object identified by a hash and linked to its parent commit(s).**

---

## 8. Git Is a Graph

This is a powerful mental model.

Suppose:

```text
A → B → C → D
```

Each commit points backward toward its parent.

When branches exist:

```text
        B → C
       /
A → B
       \
        D → E
```

Git is therefore naturally modeled as a **directed acyclic graph of commits**.

This makes branches extremely cheap.

---

## 9. Branches

Suppose your production code is:

```text
main
```

You want to develop authentication.

Create:

```bash
git switch -c feature/auth
```

Now:

```text
main
   │
   A
   │
   B
   │
   C ← feature/auth
```

You can make changes without disturbing `main`.

---

## 10. What Is a Branch Really?

A common beginner misconception:

> "A branch is a copy of the entire project."

Not quite.

A branch is essentially a **movable reference/pointer to a commit**.

For example:

```text
A → B → C

main ────────→ C
```

Create another branch:

```text
A → B → C
          ↑
        main
          ↑
     feature/auth
```

Initially both references point to C.

After a new commit:

```text
          → D
         /
A → B → C
         \
          main → C
```

Actually, more clearly:

```text
A → B → C → D
         ↑   ↑
        main feature/auth
```

The feature branch moves to D while `main` remains at C.

This is why branches are lightweight.

---

## 11. Switching Branches

```bash
git switch main
```

Then:

```bash
git switch feature/auth
```

Older Git syntax:

```bash
git checkout feature/auth
```

`git switch` is clearer for branch switching.

---

## 12. Creating a Branch

Modern:

```bash
git switch -c feature/payment
```

Equivalent conceptually:

```bash
create branch
+
switch to it
```

---

## 13. Merge

Suppose:

```text
A → B → C
         \
          D → E
```

`feature/auth` contains:

```text
D → E
```

and you want it in `main`.

Switch to main:

```bash
git switch main
```

Then:

```bash
git merge feature/auth
```

Git combines the histories.

---

## 14. Fast-Forward Merge

Suppose:

```text
A → B → C
         ↑
        main
         \
          D → E
              ↑
         feature
```

If `main` hasn't advanced, Git can simply move the `main` pointer:

```text
A → B → C → D → E
                  ↑
              main, feature
```

This is a **fast-forward merge**.

No merge commit is required.

---

## 15. Three-Way Merge

Now suppose both branches moved:

```text
          C → D
         /     \
A → B ──        M
         \     /
          E → F
```

Git has:

- common ancestor
- changes on one branch
- changes on the other branch

It performs a **three-way merge**.

Often this creates a merge commit:

```text
        C → D
       /     \
A → B         M
       \     /
        E → F
```

---

## 16. Merge Conflicts

Suppose `main` changes:

```text
const port = 3000;
```

Your feature branch changes the same line:

```text
const port = 8080;
```

Git doesn't know which one you want.

You may see:

```text
<<<<<<< HEAD
const port = 3000;
=======
const port = 8080;
>>>>>>> feature/auth
```

You resolve it manually.

For example:

```typescript
const port = 8080;
```

Then:

```bash
git add server.ts
git commit
```

Or continue the appropriate merge operation.

---

## 17. Rebase

This is one of the most frequently asked Git interview topics.

Suppose:

```text
      C → D
     /
A → B
     \
      E → F
```

You are working on a feature based on B.

Meanwhile `main` moved:

```text
A → B → C → D
     \
      E → F
```

You can rebase your feature onto D:

```bash
git switch feature
git rebase main
```

Git essentially takes your feature commits:

```text
E
F
```

and replays their changes on top of D.

Result conceptually:

```text
A → B → C → D → E' → F'
```

---

## 18. Merge vs Rebase

#### Merge

Preserves the branching history.

```text
A → B → C ──→ M
     \       /
      D → E
```

#### Rebase

Creates a more linear history:

```text
A → B → C → D' → E'
```

Important:

> **Rebase rewrites commit history.**

Therefore, be careful rebasing commits that other people are already depending on.

---

## 19. Golden Rule of Rebase

A useful rule:

> **Don't casually rebase shared/public history.**

If you've pushed commits and teammates are building on them, rewriting those commits can cause unnecessary problems.

Rebase is particularly useful for keeping your **private feature branch** up to date with `main`.

---

## 20. `git pull`

A common command:

```bash
git pull
```

Conceptually, it retrieves remote changes and integrates them into your current branch.

Traditionally, this is roughly:

```text
git fetch
+
git merge
```

Depending on configuration, `git pull` can also use rebase.

You should understand what happens instead of treating `pull` as magic.

---

## 21. `git fetch`

```bash
git fetch origin
```

This downloads information from the remote repository **without integrating those changes into your current working branch**.

Think:

```text
Remote
  ↓
fetch
  ↓
Your knowledge of remote branches
```

Then you can inspect the changes before merging/rebasing.

This is often safer when you want to understand what changed first.

---

## 22. `git push`

```bash
git push origin feature/auth
```

This sends your local commits to the remote repository.

```text
Local Git
   ↓
push
   ↓
GitHub
```

---

## 23. Remote

A remote is a reference to another Git repository.

Check:

```bash
git remote -v
```

You might see:

```text
origin  git@github.com:user/project.git
```

`origin` is simply a conventional name.

It isn't a special Git keyword.

You could have:

```text
origin
upstream
company
```

---

## 24. Forks and Upstream

In open-source development, you may have:

```text
Original repository
       ↓
      fork
       ↓
Your GitHub repository
```

Your local repository might have:

```text
origin   → your fork
upstream → original project
```

Then:

```bash
git fetch upstream
```

allows you to retrieve changes from the original project.

---

## 25. `git clone`

Clone a remote repository:

```bash
git clone https://github.com/example/project.git
```

This creates a local Git repository containing the project's history and working tree.

---

## 26. `git log`

See history:

```bash
git log
```

Compact:

```bash
git log --oneline
```

Graph:

```bash
git log --oneline --graph --decorate --all
```

This is extremely useful for understanding branch history.

---

## 27. `git diff`

See changes that haven't been staged:

```bash
git diff
```

See staged changes:

```bash
git diff --staged
```

This should become a habit before committing.

Think:

```text
Changed something
      ↓
git diff
      ↓
Understand what you're committing
```

---

## 28. `git stash`

Suppose you're working on:

```text
feature/payment
```

but suddenly need to switch branches.

Your working directory has unfinished changes.

You can temporarily store them:

```bash
git stash
```

Switch branches:

```bash
git switch main
```

Later:

```bash
git switch feature/payment
git stash pop
```

Your changes return.

---

## 29. `git restore`

Suppose you modified a file but don't want those changes.

```bash
git restore server.ts
```

This discards the unstaged changes to that file.

Be careful.

Once discarded, recovery may be difficult unless Git has another copy/reference.

---

## 30. Reset vs Revert — VERY Important

Interviewers love this.

### `git reset`

Moves the current branch reference and can change the staging/working state depending on the mode.

Examples:

```bash
git reset --soft HEAD~1
```

```bash
git reset --mixed HEAD~1
```

```bash
git reset --hard HEAD~1
```

Conceptually:

#### Soft

Move HEAD/branch pointer, keep changes staged.

#### Mixed

Move HEAD and unstage changes, keeping working-tree changes.

#### Hard

Move HEAD and make index/worktree match it.

**`--hard` can destroy uncommitted work.**

---

## 31. `git revert`

Instead of rewriting history, create a new commit that reverses an earlier commit.

```bash
git revert <commit>
```

Suppose:

```text
A → B → C → D
```

D is bad.

Revert D:

```text
A → B → C → D → R
```

`R` undoes D's changes.

This is usually safer for shared branches.

---

## 32. Reset vs Revert

Remember:

```text
reset
↓
rewrite/move history

revert
↓
add a new commit that undoes an old commit
```

For public/shared history:

> **Revert is generally the safer conceptual choice.**

---

## 33. Cherry-Pick

Suppose you have:

```text
main:
A → B → C

feature:
A → B → D → E
```

You only want commit D in `main`.

You can:

```bash
git cherry-pick <D>
```

Result:

```text
main:
A → B → C → D'
```

The change from D is applied as a new commit.

Useful for:

- backporting fixes
- selectively moving changes
- release branches

But excessive cherry-picking can make histories complicated.

---

## 34. Tags

Tags mark important points.

For example:

```bash
git tag v1.0.0
```

Then:

```bash
git push origin v1.0.0
```

Tags are useful for:

- releases
- versioning
- deployment references

Example:

```text
v1.0.0
   ↓
Production release
```

---

## 35. `.gitignore`

You don't want to commit:

```text
node_modules/
.env
dist/
*.log
```

Example:

```gitignore
node_modules/
.env
dist/
*.log
```

Important:

> `.gitignore` prevents untracked matching files from being automatically included; it does not remove a file that is already tracked.

If `.env` has already been committed, simply adding it to `.gitignore` doesn't erase it from Git history.

That's an important practical detail.

---

## 36. Git Security

Never commit:

```text
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
DATABASE_PASSWORD
JWT_SECRET
API_KEY
```

For example:

```typescript
const password = "mySuperSecretPassword";
```

is a security problem if committed.

Use:

```text
Environment variables
Secret managers
CI/CD secrets
```

Later we'll connect this to AWS Secrets Manager and Kubernetes Secrets.

---

## 37. GitHub Pull Requests

Typical professional workflow:

```text
main
 │
 └── feature/auth
        ↓
      commits
        ↓
      push
        ↓
     GitHub
        ↓
   Pull Request
        ↓
 Code Review
        ↓
    CI tests
        ↓
     Merge
```

A Pull Request is not a Git feature itself.

It's a **GitHub collaboration/review mechanism** built around Git branches and commits.

---

## 38. Code Review

A reviewer might examine:

```text
Correctness
Security
Performance
Readability
Tests
Architecture
Maintainability
```

CI can automatically check:

```text
Lint
Tests
Build
Type checking
Security scans
```

This connects Git directly to **CI/CD**, which is our next major phase.

---

## 39. Branching Strategies

There isn't one universally correct strategy.

Two important approaches:

### Feature branches

```text
main
 ├── feature/auth
 ├── feature/payments
 └── bugfix/login
```

Developers work independently and merge through PRs.

---

### Trunk-based development

Developers integrate small changes into the main/trunk frequently, often using short-lived branches or direct integration depending on team policy.

```text
main
 ↑ ↑ ↑ ↑
small changes
```

Advantages can include smaller integration conflicts and faster feedback.

---

## 40. Git Flow

You may encounter Git Flow:

```text
main
develop
feature/*
release/*
hotfix/*
```

It's useful to recognize, but don't assume every modern company uses it.

For many software teams, **trunk-based development or lightweight feature-branch workflows** are common.

---

## 41. A Professional Workflow

Imagine you're implementing authentication.

```bash
git switch main
git pull --ff-only
git switch -c feature/auth
```

Develop.

Then:

```bash
git status
git diff
```

Stage:

```bash
git add src/auth
```

Review:

```bash
git diff --staged
```

Commit:

```bash
git commit -m "Add authentication flow"
```

Push:

```bash
git push -u origin feature/auth
```

Then:

```text
GitHub
 ↓
Pull Request
 ↓
CI
 ↓
Code Review
 ↓
Merge
```

That's a professional development workflow.

---

## 42. What Happens When You Push?

Suppose:

```bash
git push origin feature/auth
```

Conceptually:

```text
Local repository
       ↓
Git determines missing objects
       ↓
Transfers required objects
       ↓
Remote repository updates branch reference
```

Git doesn't simply upload "the whole project every time."

Git stores objects and transfers what the remote needs.

This is part of why Git can efficiently synchronize repositories.

---

## 43. Git Objects

At a deeper level, Git stores objects such as:

```text
Blob
Tree
Commit
Tag
```

#### Blob

Stores file contents.

#### Tree

Represents directory structure and references blobs/other trees.

#### Commit

Points to a tree and parent commit(s), with metadata.

Conceptually:

```text
Commit
   │
   ↓
 Tree
 ├── Blob
 ├── Blob
 └── Tree
       └── Blob
```

This is useful when someone asks:

> "How does Git store versions?"

You can give a much stronger answer than:

> "Git stores copies of files."

---

## 44. HEAD

`HEAD` represents what you're currently checked out at.

For example:

```text
A → B → C
        ↑
       HEAD
```

Usually:

```text
HEAD → current branch → current commit
```

You can inspect:

```bash
git status
```

and:

```bash
git log --oneline
```

---

## 45. Detached HEAD

You can checkout a specific commit:

```bash
git switch --detach <commit>
```

Now:

```text
A → B → C → D
        ↑
      HEAD
```

but you're not on a branch.

This is called **detached HEAD**.

It's useful for inspecting old states, but if you make commits there and don't create a branch/reference, those commits can eventually become difficult to find.

---

## 46. Reflog — Your Git Safety Net

One of the most useful advanced Git concepts.

```bash
git reflog
```

It records updates to references such as where `HEAD` and branches pointed.

Suppose you accidentally run:

```bash
git reset --hard HEAD~3
```

and panic.

The reflog may allow you to locate the previous commit reference and recover it.

This is one reason Git mistakes aren't always permanently catastrophic.

---

## 47. Interview Scenario

#### Question:

> You accidentally committed a password and pushed it to GitHub. What do you do?

A strong answer isn't simply:

> "Delete the commit."

You need to think:

```text
1. Rotate/revoke the exposed credential immediately.
2. Remove the secret from the repository/history as appropriate.
3. Investigate whether it was accessed.
4. Prevent recurrence with secret scanning / CI checks.
5. Store secrets using proper secret management.
```

Why rotate first?

Because deleting it from Git history **doesn't guarantee the secret was never copied**.

This is an important DevOps/security mindset.

---

## 48. Git Commands You Should Know

#### Daily use

```bash
git status
git add
git commit
git pull
git push
git fetch
git switch
git log
git diff
```

#### Branching

```bash
git branch
git switch -c feature/x
git merge
git rebase
```

#### Recovery

```bash
git restore
git stash
git reset
git revert
git reflog
```

#### Advanced

```bash
git cherry-pick
git tag
git remote
```

---

## 🧠 The Git Mental Model

Remember this:

```text
             Git
              │
       ┌──────┴──────┐
       ↓             ↓
 Working Tree     Repository
       │
       ↓
    git add
       ↓
   Staging Area
       │
       ↓
   git commit
       ↓
    Commit
       │
       ↓
    Branch
       │
       ↓
    git push
       │
       ↓
    GitHub
       │
       ↓
 Pull Request
       │
       ↓
 Code Review
       │
       ↓
     CI/CD
```

That's the bridge from **Git → DevOps**.

---

## 🎯 Interview Questions

You should now be able to reason about:

#### Fundamentals

1. Git vs GitHub?
2. Working tree vs staging area vs repository?
3. What is a commit?
4. What is a branch?
5. Why are Git branches lightweight?
6. What is HEAD?
7. What is a remote?

#### Branching

8. Merge vs rebase?
9. Fast-forward vs three-way merge?
10. What causes a merge conflict?
11. How do you resolve a conflict?
12. When should you avoid rebasing?

#### Recovery

13. `reset` vs `revert`?
14. `restore` vs `reset`?
15. What is `stash`?
16. What is `reflog`?
17. What is detached HEAD?

#### Collaboration

18. `fetch` vs `pull`?
19. What happens during `git push`?
20. What is a Pull Request?
21. Feature branches vs trunk-based development?
22. What is Git Flow?

#### Practical scenario

> **You have committed three changes locally. Your teammate has pushed changes to `main`. You need to update your feature branch without losing your work. What would you do?**

You should be able to reason through:

```text
git fetch
      ↓
update feature branch
      ↓
merge OR rebase
      ↓
resolve conflicts if needed
      ↓
test
      ↓
push
```

---

## 🧪 Practical Git Lab

Take one of your own small projects.

```bash
git init
git status
git add .
git commit -m "Initial commit"
```

Create a feature:

```bash
git switch -c feature/test
```

Change something and commit:

```bash
git add .
git commit -m "Add test feature"
```

Return:

```bash
git switch main
```

Make another change.

Then inspect:

```bash
git log --oneline --graph --decorate --all
```

Practice:

```text
merge
rebase
stash
restore
revert
reset
cherry-pick
```

**Do this on a throwaway repository**, especially for `reset --hard`, so you can safely see what each operation does.
<!-- SOURCE-END -->

---

**Navigation:** ← [Chapter 4: Networking for Cloud & DevOps](ch04-networking.md) · [Chapter 6: CI/CD + GitHub Actions](../03-cicd-gitops/ch06-cicd-github-actions.md) → · [Revision sheet](../../revision/ch05-revision.md)
