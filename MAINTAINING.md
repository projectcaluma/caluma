# Maintainer's Handbook

## Make a new release

We use `python-semantic-release` to generate a changelog and suggest the next version. Ensure it is installed before following the steps below:

    poetry install

**Note**: For the following instructions, we assume that the main Caluma repository is the `origin` remote and `main` is set up to track that remote's `main` branch. Please adapt the commands as necessary if your local setup differs.

1. Check out the latest `main` branch and ensure you have all the tags:
   ```
   git checkout main
   git pull origin --tags
   ```
2. Determine the next version:
   ```
   poetry run semantic-release version --noop
   ```
3. Generate the changelog entries:
   ```
   poetry run semantic-release changelog --noop --unreleased
   ```
4. Update `CHANGELOG.md` and `pyproject.toml` with the information determined above.
5. Create a GitHub Pull Request with the changes.
6. After the PR is merged, pull from the remote, tag the merge commit, and push it back to GitHub:
   ```
   git pull origin
   git tag vXX.X.X
   git push --tags
   ```
7. Create a new release on GitHub (*Releases* › *Draft a new release*), and reuse the changelog text generated above for the release description.
    - Note: If you want a review of the release notes, you may save the release as a draft, to be published later.
