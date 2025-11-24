# Zimbra FOSS - Maintainer release

## About

**MALDUA'S Zimbra FOSS** brought to you by [BTACTIC, open source & cloud solutions](https://www.btactic.com).

## Introduction

This project aims to ease the build of Zimbra FOSS.

This part is about the maintainer is supposed to be releasing new tgz downloads.

## Requisites

### Build Github Action

You are supposed to test and setup:

- [BUILD-GITHUB-ACTION](BUILD-GITHUB-ACTION.md)
- [DOWNLOADS-GITHUB-ACTION](DOWNLOADS-GITHUB-ACTION.md)

before this makes any sense.

## Check for new versions

You might already know that there is a new version of Zimbra which might affect two or three major versions of Zimbra. If it's not the case you should check the [Zimbra Releases page](https://wiki.zimbra.com/wiki/Zimbra_Releases) in the Zimbra Wiki.

E.g.:
- 10.0.0 gets its Patch Level updated to: **Patch 10.0.8**. This means: **10.0.8** git tag.
- 9.0.0 gets its Patch Level updated to: Patch 40. This means: **9.0.0.p40** git tag.
.

Not so quick,... let's double-check thanks to our zimbra-tag-helper tool.

```
git clone https://github.com/maldua/zimbra-tag-helper.git
cd zimbra-tag-helper


./zm-build-filter-tags.sh 10.0.0 > tags_for_10.txt
./zm-build-filter-tags.sh 9.0.0 > tags_for_9.txt

cat tags_for_10.txt | grep '10.0.8'
10.0.8

cat tags_for_10.txt | grep '9.0.0.p40'
9.0.0.p40
```

Ok, so we have found out that those tags are still there.

Let's also check 8.8.x branch just for fun.
```
./zm-build-filter-tags.sh 8.8.15 > tags_for_8.txt

cat tags_for_8.txt | grep '8.8.15.p47'
8.8.15.p47
```

Be careful because they won't be pushing 8.8.x patches always.

So we have managed to find out that we can build these tags:

- 8.8.15.p47
- 9.0.0.p40
- 10.0.8
.

## Option A: Push build tags (Without Pimbra)

Versions to build are: 8.8.15.p47, 9.0.0.p40 and 10.0.8.

We also know that our system right now is only be able to build RHEL 7, RHEL 8, Ubuntu 18.04 and Ubuntu 20.04 builds.

So we have 3 versions that need to be built in 4 different platforms. 3 times 4 makes 12.

Let's build all of these builds in Github thanks to Github actions in one go. It usually takes 13 minutes. So we will wait for 20 minutes before going on.
Let's craft a real quick script.

```
for nplatform in rhel-7 rhel-8 ubuntu-18.04 ubuntu-20.04 ; do
  for nversion in 8.8.15.p47 9.0.0.p40 10.0.8 ; do
    ntag="builds-${nplatform}/${nversion}"
    git tag -a $ntag -m $ntag
    git push origin $ntag
  done
done
sleep 20m
```
.

You might want to check the Github Repo Actions tab to see if every build went ok.

## Option B: Push build tags (With Pimbra)

First of all we make sure that the [Pimbra's maldua-pimbra-config](https://github.com/maldua-pimbra/maldua-pimbra-config) repo has the proper tag which links to the proper patched repos.
Please notice that **if the tag is non-existant** in Github Zimbra repos (E.g.: 10.1.7p1) then it needs to be **added** in the modified repos from Pimbra organisation not only as 10.1.7p1-maldua but also as **10.1.7p1**, both of those tags pointing to the same tag.

Versions to build are: 8.8.15.p47, 9.0.0.p40 and 10.0.8.

We also know that our system right now is only be able to build RHEL 7, RHEL 8, Ubuntu 18.04 and Ubuntu 20.04 builds.

So we have 3 versions that need to be built in 4 different platforms. 3 times 4 makes 12.

Let's build all of these builds in Github thanks to Github actions in one go. It usually takes 13 minutes. So we will wait for 20 minutes before going on.
Let's craft a real quick script.

```
for nplatform in rhel-7 rhel-8 ubuntu-18.04 ubuntu-20.04 ; do
  for nversion in 8.8.15.p47 9.0.0.p40 10.0.8 ; do
    ntag="builds-with-pimbra-${nplatform}/${nversion}"
    git tag -a $ntag -m $ntag
    git push origin $ntag
  done
done
sleep 20m
```
.

You might want to check the Github Repo Actions tab to see if every build went ok.

## Optional category change

The builds are set to be **recent** releases by default. If those were not recent releases we might want to edit them in the Github Repo Releases page to change them into another category.

Once everything is built you are ready to update the downloads page.

## Push Generate Downloads tag

First of all we get the latest tag related to generate downloads and we just increase from there.

```
git tag | grep '^generate-downloads' | sort -V | tail -n 1
```
returns us: `generate-downloads/v0.0.23` so we will go with 24 instead.

```
git tag -a 'generate-downloads/v0.0.24' -m 'generate-downloads/v0.0.24'
git push origin 'generate-downloads/v0.0.24'
```

You might want to check the Github Repo Actions tab while the webpages are being rebuilt.

Finally you might want to check the real thing here: [Zimbra FOSS Downloads / Zimbra OSE Downloads page](https://maldua.github.io/zimbra-foss/downloads.html).

## Similar projects

- [ianw1974's zimbra-build-scripts](https://github.com/ianw1974/zimbra-build-scripts)
- [KontextWork's zimbra-builder](https://github.com/KontextWork/zimbra-builder)

## Extra documentation

- [aschmelyun.com - Using Docker Run inside of GitHub Actions](https://aschmelyun.com/blog/using-docker-run-inside-of-github-actions/)
- [Docker Run Action - Actions - GitHub Marketplace](https://github.com/marketplace/actions/docker-run-action)
- [Superuser - Read Only access to GitHub repo via SSH key](https://superuser.com/questions/1314064/read-only-access-to-github-repo-via-ssh-key)
