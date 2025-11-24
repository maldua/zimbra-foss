# Zimbra FOSS - Downloads Github Action

## About

**MALDUA'S Zimbra FOSS** brought to you by [BTACTIC, open source & cloud solutions](https://www.btactic.com).

## Introduction

This project aims to ease the build of Zimbra FOSS.

This part is about how to automate Zimbra FOSS downloads page thanks to Github Actions.

You are supposed to use these instructions if you want to clone this repo and manage to automate Zimbra FOSS builds onto your own Github repo.

## Requisites

### Build Github Action

You are supposed to test and setup [BUILD-GITHUB-ACTION](BUILD-GITHUB-ACTION.md) before this Github Action.

### maldua.github.io Initial setup

- Visit zimbra-foss repo
- Settings
- Code and automation
- Pages
  - Build and deployment.
      - Source: Deploy from a branch
      - Branch:
        - `publish-downloads-dev` (Branch)
        - `/download-pages` (Directory)
        - Save

## Rename your organisation in yml files

Find the workflow yml files such as:

- `.github/workflows/generate-downloads-page.yml`

and then make sure to replace the maldua Github organisation with your own Github organisation.

## Rename your organisation in generate-downloads-page.py

Edit `download-pages/generate-downloads-page.py` and then make sure to replace the maldua Github organisation with your own Github organisation.

## First steps

### Build Docker and Zimbra

It makes no sense to make a downloads page without any releases to read from.
So you are supossed to build at least a Docker image and Zimbra release according to: [BUILD-GITHUB-ACTION](BUILD-GITHUB-ACTION.md) which you should have already done.

### Build downloads page

You just make sure to push a new tag in the form of `generate-downloads/v0.0.1` where that specific tag does not exist in the project yet.

```
git tag -a 'generate-downloads/v0.0.1' -m 'generate-downloads/v0.0.1'
git push origin 'generate-downloads/v0.0.1'
```

This will add a commit to the `publish-downloads-dev` branch which, in turn, will generate the **maldua.github.io/zimbra-foss** page as we have setup earlier in Settings. Page. section of the repo.

If everything went you should be able to visit: [https://maldua.github.io/zimbra-foss/downloads.html](https://maldua.github.io/zimbra-foss/downloads.html) with your own organisation, of course.

## Similar projects

- [ianw1974's zimbra-build-scripts](https://github.com/ianw1974/zimbra-build-scripts)
- [KontextWork's zimbra-builder](https://github.com/KontextWork/zimbra-builder)

## Extra documentation

- [aschmelyun.com - Using Docker Run inside of GitHub Actions](https://aschmelyun.com/blog/using-docker-run-inside-of-github-actions/)
- [Docker Run Action - Actions - GitHub Marketplace](https://github.com/marketplace/actions/docker-run-action)
- [Superuser - Read Only access to GitHub repo via SSH key](https://superuser.com/questions/1314064/read-only-access-to-github-repo-via-ssh-key)
