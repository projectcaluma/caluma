# Maintainer's Handbook

## Make a new release

We're using `python-semantic-release` to generate a changelog and suggest the next version.

1. Checkout `main` branch, ensure you have all tags
2. Figure out the next version
3. Update code (CHANGELOG, version info)
4. Pull Request with the version bump.
5. Create tag and release on the merge commit with the changelog

```bash
# Ensure you're on the current `main` branch and have all release tags
git checkout main
git pull origin --tags
# Figure out the next version
poetry run semantic-release version --noop
# Prepare changelog
poetry run semantic-release changelog --noop --unreleased
```
