# changelog.md
 Generate CHANGELOG.md from debian/changelog

[![Build Status](https://travis-ci.org/erikni/debian-changelog.md.svg?branch=develop)](https://travis-ci.org/erikni/debian-changelog.md)

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/fed757b5a2074617906ffca343e30978)](https://www.codacy.com/manual/erikni/debian-changelog.md?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=erikni/debian-changelog.md&amp;utm_campaign=Badge_Grade)

[![Maintainability](https://api.codeclimate.com/v1/badges/310ca4ea8facca60c1c4/maintainability)](https://codeclimate.com/github/erikni/debian-changelog.md/maintainability)


### How to install:
```
$ wget -O - https://raw.githubusercontent.com/erikni/debian-changelog.md/develop/setup.sh | bash
```

### Run:

```
$ export DEB_CHANGELOG_YML=changelog_md.yml 
$ python3 changelog_md.py
```
