# Release

- Set `dev` version to `None`
- Push commit `Bump version to X.X.X`
- Create PR `dev` -> `main`
- Merge pull request (no squash!)
- Create new release and tag `vX.X.X`
  + Attach distributions
- Check release to `PyPI`
- Git commands
```bash
git fetch
git checkout dev
git merge origin/main
git push
```
- Bump version + set `dev` to `1`
- Push commit `Bump version to X.X.X.dev1`

- Optionally: Update version for home-assistant/core
