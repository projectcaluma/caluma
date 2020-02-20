# Maintainer's Handbook

## Release Management

The release procedure was recently changed from automatic to manual, due to too
many problems with it.

Here is a rough outline / checklist for the release (explained further below):

1. Checkout `master` branch, ensure you have all tags
2. Prepare changelog
3. Figure out the next version
4. Update code (CHANGELOG, version info)
5. Pull Request with the version bump.
6. Create tag on the merge commit
7. Upload / edit change log
8. If new deprecations have been introduced, make sure they are listed in the
   `Deprecations` issue, and ensure the deprecations are explicitly mentioned in the release notes as well.

Here's how this works in detail:

### Get release information

The `semantic-release` tool can help you with the first few tasks of the above
checklist:

```bash
# Ensure you're on the current master and have all release tags
git checkout master
git pull origin --tags

# Prepare changelog
semantic-release changelog --noop --unreleased -D version_source=tag

# Figure out the next version
semantic-release version --noop -D version_source=tag
```

You should verify that the version proposed by `semantic-release` is actually
correct. At the time of writing (2020-01-22), it didn't detect some "BREAKING
CHANGES" labels, for example. Adjust the version to what you think is correct.

### Update version, changelog in source

The version is also put in code. Update the file
`caluma/caluma_metadata.py`.

Put the changelog on top of the `CHANGELOG.md` file along with the proposed date
of release. If needed, amend it with some informative text about the release

### Create a Pull request for the proposed version bump

Put the changelog in the commit message or in the PR discussion somewhere, so
it won't be forgotten once the release actually happens.

Note: If other PRs are merged after you create the version bump PR, you may need
to revisit the changelog, and potentially even the version number to be created.
It is thus important to create and merge the version bump in a timely,
coordinated manner.

### Create Release

Once the version bump PR has been merged, take the corresponding merge commit,
and tag it with the version. Note that the tag needs to be prefixed with `v`,
so for example version 5.0.0 will need a tag named exactly `v5.0.0`.

You should then edit the release on Github and paste the changelog there as well.

Docker Hub will automatically trigger a build for the new tag, and publish it.

The `pypi` github workflow will automatically build a source package and a wheel and
publish them on [PyPI](https://pypi.org/project/caluma/).
