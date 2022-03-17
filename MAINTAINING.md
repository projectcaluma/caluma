# Maintainer's Handbook

## Make a new release

We're using `python-semantic-release` to generate a changelog, update the
version and publish it to Github and PyPi.

To release a new version simply head over to [Github
Actions](https://github.com/projectcaluma/caluma/actions/workflows/release.yml)
and trigger the workflow dispatch event on the branch `main`. Optionally you
can check the "prerelease" checkbox when triggering the workflow to release a
beta version.
