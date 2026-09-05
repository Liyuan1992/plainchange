# Git policy baseline

Before changing a Git project, inspect and report its branch and working-tree state. Preserve unrelated changes.

Recommended for a serious/shared repository after owner confirmation:

- Work on a named branch or isolated worktree.
- Use focused commits with evidence-backed messages.
- Require reviewed pull requests and relevant CI before merging to the protected mainline.
- Never put secrets, private data, generated caches, virtual environments, or `node_modules` in Git.

This document is a project policy, not an automatic GitHub configuration. Branch protection, remote changes, commits, pushes, and CI changes require their own explicit authorization.
