#!/usr/bin/env python3

import os
import shutil
import re
import requests
from subprocess import run, PIPE
from datetime import datetime

# Please run from docs folder

CALENDAR_ICON = "\U0001F4C5"
PACKAGE_ICON  = "\U0001F4E6"
LINK_ICON     = "\U0001F517"
MEMO_ICON     = "\U0001F4DD"
COMPUTER_ICON = "\U0001F5A5"
RULER_ICON = "\U0001F4CF"
IMAGE_ICON = "\U0001F5BC"
STABLE_ICON = "\U0001F7E2"
RECENT_ICON = "\U0001F9EA"
EXPERIMENTAL_ICON = "\U0001F9EC"
OTHER_ICON = "\U0001F5C2\ufe0f"
EMPTY_ICON = "\u2205"
ARCHIVE_ICON = "\U0001F5C4"
LATEST_ICON = "\U0001F195"
LATEST_PER_PLATFORM_ICON = "\U0001F4F0"
LATEST_PER_FAMILY_ICON = "\U0001F4CB"

MENU_GROUPS = {
    "Main": ["main"],
    "Categories": ["stable", "recent", "experimental", "other"],
    "Latest": ["latest", "latest_per_platform", "latest_per_family"],
    "Misc": ["archive"]
}

# Global variables
header_links_mapping = {
    "main": "README.md",
    "stable": "stable.md",
    "recent": "recent.md",
    "experimental": "experimental.md",
    "other": "other.md",
    "latest": "latest.md",
    "latest_per_platform": "latest-per-platform.md",
    "latest_per_family": "latest-per-zimbra-family.md",
    "archive": "archive.md"
}

shortNamesLabels = {
    "main": "Main",
    "stable": f"{STABLE_ICON} Stable {STABLE_ICON}",
    "recent": f"{RECENT_ICON} Recent {RECENT_ICON}",
    "experimental": f"{EXPERIMENTAL_ICON} Experimental {EXPERIMENTAL_ICON}",
    "other": f"{OTHER_ICON} Other {OTHER_ICON}",
    "archive": f"{ARCHIVE_ICON} Archive {ARCHIVE_ICON}",
    "latest": f"{LATEST_ICON} Latest {LATEST_ICON}",
    "latest_per_platform": f"{LATEST_PER_PLATFORM_ICON} Latest per Platform {LATEST_PER_PLATFORM_ICON}",
    "latest_per_family": f"{LATEST_PER_FAMILY_ICON} Latest per Zimbra Family {LATEST_PER_FAMILY_ICON}"
}

# Resolve output directory: we are running from docs-pages/downloads
PARENT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
GRAND_PARENT_DIR = os.path.abspath(os.path.join(PARENT_DIR, ".."))
DOCS_DIR = os.path.join(GRAND_PARENT_DIR, "docs")
DOWNLOADS_OUTPUT_DIR = os.path.join(DOCS_DIR, "downloads")
os.makedirs(DOWNLOADS_OUTPUT_DIR, exist_ok=True)
VERSION_DIR = os.path.join(DOWNLOADS_OUTPUT_DIR, "version")
os.makedirs(VERSION_DIR, exist_ok=True)

# Write output into docs/
main_downloads_md = os.path.join(DOWNLOADS_OUTPUT_DIR, "README.md")
archive_md = os.path.join(DOWNLOADS_OUTPUT_DIR, "archive.md")
stable_md = os.path.join(DOWNLOADS_OUTPUT_DIR, "stable.md")
recent_md = os.path.join(DOWNLOADS_OUTPUT_DIR, "recent.md")
experimental_md = os.path.join(DOWNLOADS_OUTPUT_DIR, "experimental.md")
other_md = os.path.join(DOWNLOADS_OUTPUT_DIR, "other.md")
latest_md = os.path.join(DOWNLOADS_OUTPUT_DIR, "latest.md")
latest_per_platform_md = os.path.join(DOWNLOADS_OUTPUT_DIR, "latest-per-platform.md")
latest_per_family_md = os.path.join(DOWNLOADS_OUTPUT_DIR, "latest-per-zimbra-family.md")

# templates/ and images/ remain relative to current folder
templatesDir = 'templates'
imagesDir = "images"

ZIMBRA_FOSS_ORG="maldua"
ZIMBRA_FOSS_REPO="zimbra-foss"
repoReleasesApiUrl=f"https://api.github.com/repos/{ZIMBRA_FOSS_ORG}/{ZIMBRA_FOSS_REPO}/releases"
versionDownloadUrlBase=f"https://{ZIMBRA_FOSS_ORG}.github.io/{ZIMBRA_FOSS_REPO}/downloads/version"

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')

# Other functions
def sizeof_fmt(num, suffix="B"):
    for unit in ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
        if abs(num) < 1024.0:
            return f"{num:3.0f} {unit}{suffix}"
        num /= 1024.0
    return f"{num:f} Yi{suffix}"

# Download markdown functions
def getIconField(prefixTag, url_prefix=""):
  if ("ubuntu" in prefixTag):
    iconField = f"![Ubuntu icon]({url_prefix}{imagesDir}/ubuntu.png)"
  elif ("rhel" in prefixTag):
    iconField = f"![RedHat icon]({url_prefix}{imagesDir}/redhat.png)"
  elif ("oracle" in prefixTag):
    iconField = f"![Oracle icon]({url_prefix}{imagesDir}/oracle.png)"
  elif ("rocky" in prefixTag):
    iconField = f"![Rocky icon]({url_prefix}{imagesDir}/rocky.png)"
  elif ("centos" in prefixTag):
    iconField = f"![Centos icon]({url_prefix}{imagesDir}/centos.png)"
  else:
    iconField = ""

  return (iconField)

def get_download_table_top_simple (versionTag, shortName):
  return (
    f"### [{versionTag}]({versionDownloadUrlBase}/{versionTag}) ({shortName})\n"
    '\n'
    f'| {IMAGE_ICON} | {COMPUTER_ICON} PLATFORM | {PACKAGE_ICON} DOWNLOAD 64-BIT | {MEMO_ICON} +INFO |\n'
    '| --- | --- | --- | --- |'
  )

def get_download_table_top (versionTag, shortName):
  return (
    f"### [{versionTag}]({versionDownloadUrlBase}/{versionTag}) ({shortName})\n"
    '\n'
    f"| {IMAGE_ICON} | {COMPUTER_ICON} Platform | {PACKAGE_ICON} Download 64-BIT | {CALENDAR_ICON} Build Date | {RULER_ICON} Size | {LINK_ICON} +Info | {MEMO_ICON} Comment |\n"
    '| --- | --- | --- | --- | --- | --- | --- |'
  )

def get_download_row (prefixTag, versionTag, distroLongName, tgzDownloadUrl, buildDate, size, moreInformationUrl, comment, url_prefix=""):
  icon = getIconField(prefixTag, url_prefix=url_prefix)
  md5DownloadUrl = tgzDownloadUrl + ".md5"
  sha256DownloadUrl = tgzDownloadUrl + ".sha256"
  humanSize = sizeof_fmt(size)
  # TODO: Use the release url directly instead of crafting it ourselves.
  download_row = f"|{icon} | {distroLongName} | [64bit x86]({tgzDownloadUrl}) - [MD5]({md5DownloadUrl}) - [SHA256]({sha256DownloadUrl}) | {buildDate} | {humanSize} | [+Info]({moreInformationUrl}) | {comment} |"
  return (download_row)

def get_download_row_simple (prefixTag, versionTag, distroLongName, tgzDownloadUrl, buildDate, size, moreInformationUrl, comment, url_prefix=""):
  icon = getIconField(prefixTag, url_prefix=url_prefix)
  md5DownloadUrl = tgzDownloadUrl + ".md5"
  sha256DownloadUrl = tgzDownloadUrl + ".sha256"
  humanSize = sizeof_fmt(size)
  # TODO: Use the release url directly instead of crafting it ourselves.
  download_row = f"|{icon} | {distroLongName} | [64bit x86]({tgzDownloadUrl}) ([MD5]({md5DownloadUrl})) ([SHA256]({sha256DownloadUrl})) | [+Info]({moreInformationUrl}) |"
  return (download_row)

def getCategoryFromBody (body):
  categoryRegex = re.compile('^category: (.*)$')
  allowedCategories = [ "stable", "recent", "experimental" ]

  defaultCategory = "other"
  category = defaultCategory

  bodyLines = body.splitlines()
  for nBodyLine in bodyLines:
    if re.match(categoryRegex, nBodyLine):
      categoryCandidate = re.findall(categoryRegex, nBodyLine)[0]
      if categoryCandidate in allowedCategories:
        category = categoryCandidate
        break
  return (category)

def getCommentFromBody (body):
  downloadCommentRegex = re.compile('^download_comment: (.*)$')

  defaultDownloadComment = ""
  downloadComment = defaultDownloadComment

  bodyLines = body.splitlines()
  for nBodyLine in bodyLines:
    if re.match(downloadCommentRegex, nBodyLine):
      downloadComment = re.findall(downloadCommentRegex, nBodyLine)[0]
  return (downloadComment)

# Releases Matrix functions
def getReleasesMatrix():
  # Get info from releases based on previous tag matrix (releasesMatrix)
  # Keep only tags that start with: 'zimbra-foss-build-'
  # - tag: zimbra-foss-build-ubuntu-20.04/9.0.0.p39
  # - buildDate
  # - prefixTag: zimbra-foss-build-ubuntu-20.04
  # - versionTag: 9.0.0.p39
  # - distroLongName: Ubuntu 20.04 based on release title
  # - tgzDownloadUrl: https://...tgz based on assets which start with 'zcs-' and end in 'tgz'
  # - category: 'stable, recent, experimental, other' based on draft, pre-release values (use a helper function)

  repoReleasesApiFirstPageUrl=repoReleasesApiUrl+'?simple=yes&per_page=100&page=1'
  response = requests.get(repoReleasesApiFirstPageUrl, headers={"Accept":"application/vnd.github+json", "Authorization":f"Bearer {GITHUB_TOKEN}", "X-GitHub-Api-Version":"2022-11-28"})
  responseJson = response.json()
  while 'next' in response.links.keys():
    response=requests.get(response.links['next']['url'],headers={"Accept":"application/vnd.github+json", "Authorization":f"Bearer {GITHUB_TOKEN}", "X-GitHub-Api-Version":"2022-11-28"})
    responseJson.extend(response.json())

  wantedTagRegex = re.compile('^zimbra-foss-build-.*$')
  prefixTagRegex = re.compile('(.*)/.*')
  versionTagRegex = re.compile('.*/(.*)')
  distroLongNameRegex =re.compile('.* \( (.*) \)')
  tgzRegex = re.compile('^zcs-.*tgz$')

  releasesMatrix = []

  for nJson in responseJson:
    tag = nJson["tag_name"]
    # print (nJson)
    # print ("")
    if re.match(wantedTagRegex, tag):

      prefixTag = re.findall(prefixTagRegex, tag)[0]
      versionTag = re.findall(versionTagRegex, tag)[0]
      distroLongName = re.findall(distroLongNameRegex, nJson["name"])[0]

      tagsItem = {}
      tagsItem["tag"] = tag
      tagsItem["buildDate"] = nJson["published_at"]
      tagsItem["prefixTag"] = prefixTag
      tagsItem["versionTag"] = versionTag
      tagsItem["distroLongName"] = distroLongName
      tagsItem["html_url"] = nJson["html_url"]

      tagsItem["category"] = getCategoryFromBody (nJson["body"])
      tagsItem["comment"] = getCommentFromBody (nJson["body"])

      for nAsset in nJson["assets"]:
        if re.match(tgzRegex, nAsset["name"]):
          tagsItem["tgzDownloadUrl"] = nAsset["browser_download_url"]
          tagsItem["size"] = nAsset["size"]
          break

      releasesMatrix.append(tagsItem)
  return (releasesMatrix)

from datetime import datetime

def getLatestVersionTagsByBuildDate(matrix, limit=5):
    """
    Returns the latest `limit` versionTag groups based on their newest buildDate.
    """
    buckets = {}

    for row in matrix:
        vt = row["versionTag"]
        buildDate = datetime.fromisoformat(row["buildDate"].replace("Z","+00:00"))
        if vt not in buckets:
            buckets[vt] = []
        buckets[vt].append(buildDate)

    # Pick the most recent build date per versionTag
    versionTag_with_latest_date = [
        (vt, max(dates)) for vt, dates in buckets.items()
    ]

    # Sort by date descending
    versionTag_sorted = sorted(
        versionTag_with_latest_date,
        key=lambda t: t[1],
        reverse=True
    )

    # Return only versionTag names
    return [t[0] for t in versionTag_sorted[:limit]]

def getShortNameForVersionTag(versionTag, releasesMatrix):
    """
    Given a versionTag, find its category and return the corresponding shortNamesLabels value.
    If multiple categories appear (should not happen), the first one wins.
    """
    for row in releasesMatrix:
        if row["versionTag"] == versionTag:
            category = row["category"]
            return shortNamesLabels.get(category, shortNamesLabels["other"])
    return shortNamesLabels["other"]

def getLatestVersionTagsByDistro(releasesMatrix, distroLongName, limit=2):
    filteredMatrix = [row for row in releasesMatrix if row["distroLongName"] == distroLongName]
    if not filteredMatrix:
        return []
    # Group by versionTag and pick the most recent buildDate
    versionBuckets = {}
    for row in filteredMatrix:
        vt = row["versionTag"]
        buildDate = datetime.fromisoformat(row["buildDate"].replace("Z","+00:00"))
        if vt not in versionBuckets:
            versionBuckets[vt] = []
        versionBuckets[vt].append(buildDate)
    # Take most recent build per version
    version_with_latest = [(vt, max(dates)) for vt, dates in versionBuckets.items()]
    # Sort by build date descending
    version_sorted = sorted(version_with_latest, key=lambda t: t[1], reverse=True)
    return [t[0] for t in version_sorted[:limit]]

def getZimbraFamily(versionTag):
    """
    Compute Zimbra family from versionTag.
    Examples:
        10.1.9 -> 10.1
        10.1.10.p6 -> 10.1
        10.0.5 -> 10.0
        9.0.0.p5 -> 9.0
        8.8.15.p46 -> 8.8
    """
    # Match major.minor
    match = re.match(r'^(\d+\.\d+)', versionTag)
    if match:
        return match.group(1)
    return versionTag

def family_to_label(family: str) -> str:
    """
    Convert a numeric family string to its display label.
    """
    if family == "9.0":
        return "9.0.0.pX"
    elif family == "8.8":
        return "8.8.15.pX"
    else:
        # Default fallback: keep family.x
        return f"{family}.x"

# Helper to convert version string to float for sorting (e.g., "20.04" -> 20.04)
def version_to_float(v):
    try:
        return float(v)
    except ValueError:
        return 0.0

def filterByCategory(matrix, category):
  newMatrix = []
  for nRow in matrix:
    if (nRow["category"] == category):
      newMatrix.append(nRow)
  return (newMatrix)

def filterNoRhel(matrix):
  rhelRegex = re.compile('^.*RHEL.*$')
  newMatrix = []
  for nRow in matrix:
    if not (re.match(rhelRegex, nRow['distroLongName'])):
      newMatrix.append(nRow)
  return (newMatrix)

def expandByRhel7(matrix):
  rhel7Regex = re.compile('^.*-rhel-7$')
  newMatrix = []
  for nRow in matrix:
    if re.match(rhel7Regex, nRow['prefixTag']):
      rhelRow = nRow.copy()
      rhelRow['distroLongName'] = "Red Hat Enterprise Linux 7"
      newMatrix.append(rhelRow)

      oracleRow = nRow.copy()
      oracleRow['prefixTag'] = nRow['prefixTag'].replace("rhel","oracle")
      oracleRow['distroLongName'] = "Oracle Linux 7"
      newMatrix.append(oracleRow)

      centosRow = nRow.copy()
      centosRow['prefixTag'] = nRow['prefixTag'].replace("rhel","centos")
      centosRow['distroLongName'] = "CentOS 7"
      newMatrix.append(centosRow)
    newMatrix.append(nRow)
  return (newMatrix)

def expandByRhel8(matrix):
  rhel8Regex = re.compile('^.*-rhel-8$')
  newMatrix = []
  for nRow in matrix:
    if re.match(rhel8Regex, nRow['prefixTag']):
      rhelRow = nRow.copy()
      rhelRow['distroLongName'] = "Red Hat Enterprise Linux 8"
      newMatrix.append(rhelRow)

      oracleRow = nRow.copy()
      oracleRow['prefixTag'] = nRow['prefixTag'].replace("rhel","oracle")
      oracleRow['distroLongName'] = "Oracle Linux 8"
      newMatrix.append(oracleRow)

      rockyRow = nRow.copy()
      rockyRow['prefixTag'] = nRow['prefixTag'].replace("rhel","rocky")
      rockyRow['distroLongName'] = "Rocky Linux 8"
      newMatrix.append(rockyRow)

      centosRow = nRow.copy()
      centosRow['prefixTag'] = nRow['prefixTag'].replace("rhel","centos")
      centosRow['distroLongName'] = "CentOS 8"
      newMatrix.append(centosRow)
    newMatrix.append(nRow)
  return (newMatrix)

def expandByRhel9(matrix):
  rhel9Regex = re.compile('^.*-rhel-9$')
  newMatrix = []
  for nRow in matrix:
    if re.match(rhel9Regex, nRow['prefixTag']):
      rhelRow = nRow.copy()
      rhelRow['distroLongName'] = "Red Hat Enterprise Linux 9"
      newMatrix.append(rhelRow)

      oracleRow = nRow.copy()
      oracleRow['prefixTag'] = nRow['prefixTag'].replace("rhel","oracle")
      oracleRow['distroLongName'] = "Oracle Linux 9"
      newMatrix.append(oracleRow)

      rockyRow = nRow.copy()
      rockyRow['prefixTag'] = nRow['prefixTag'].replace("rhel","rocky")
      rockyRow['distroLongName'] = "Rocky Linux 9"
      newMatrix.append(rockyRow)

    newMatrix.append(nRow)
  return (newMatrix)

# Tag functions
def getVersionTags(matrix):
  versionTags = []
  for nRow in matrix:
    versionTags.append(nRow["versionTag"])
  return (versionTags)

def getUniqueList(nonUniqueList):
  uniqueList = []
  for nItem in nonUniqueList:
    if nItem not in uniqueList:
      uniqueList.append(nItem)
  return (uniqueList)

def orderedAndUniqueVersionTags (versionTags):
  # StrictVersion and package.version.parse does not seem to like this tag versions
  # So let's use 'sort -V -r' from the command line instead
  versionTags = getUniqueList (versionTags)
  versionTagsInput = '\n'.join([str(item) for item in versionTags])
  sortVersionProcess = run(['sort', '-V', '-r'], stdout=PIPE, input=versionTagsInput, encoding='ascii')
  versionTagsOrdered=(sortVersionProcess.stdout).rstrip().split('\n')
  return (versionTagsOrdered)

def getFirstTagStartingWith (versionTags, prefix):
  tagStartingWithRegex = re.compile('^' + prefix + '.*$')
  newVersionTags = []
  for nVersionTag in versionTags:
    if re.match(tagStartingWithRegex, nVersionTag):
      newVersionTags.append(nVersionTag)
      break

  return (newVersionTags)

def filterByVersionTag(matrix, versionTag):
  newMatrix = []
  for nRow in matrix:
    if (nRow["versionTag"] == versionTag):
      newMatrix.append(nRow)
  return (newMatrix)

# File output functions
def append_files(file1_path, file2_path):
    with open(file1_path, 'r') as file1:
        with open(file2_path, 'a') as file2:
            shutil.copyfileobj(file1, file2)

def outputTitle(downloads_md, title="", description=""):
    with open(downloads_md, 'a') as outfile:
      outfile.write(f'''\
---
title: {title} - Zimbra Foss Downloads (from Maldua)
description: {title} - {description} - Zimbra Foss Downloads (from Maldua)
---

        ''')

def outputSection(downloads_md, versionTags, releasesMatrix, shortName, url_prefix=""):
  if not releasesMatrix:
    with open(downloads_md, 'a') as outfile:
      outfile.write(f'''
## {EMPTY_ICON} {EMPTY_ICON} {EMPTY_ICON} {EMPTY_ICON} {EMPTY_ICON} {EMPTY_ICON}

**Notice:** No releases found for **{shortName}** category.

## {EMPTY_ICON} {EMPTY_ICON} {EMPTY_ICON} {EMPTY_ICON} {EMPTY_ICON} {EMPTY_ICON}
        ''')
    return
  for nTagVersion in versionTags:
    filteredMatrix = filterByVersionTag(releasesMatrix, nTagVersion)
    orderedFilteredMatrix = sorted(filteredMatrix, key=lambda d: d['distroLongName'])

    download_table_top = get_download_table_top (versionTag=nTagVersion, shortName=shortName)
    with open(downloads_md, 'a') as outfile:
      outfile.write('\n' + download_table_top + '\n')

    for nRelease in orderedFilteredMatrix:
      download_row = get_download_row (prefixTag=nRelease['prefixTag'], versionTag=nRelease['versionTag'], distroLongName=nRelease['distroLongName'], tgzDownloadUrl=nRelease['tgzDownloadUrl'], buildDate=nRelease['buildDate'], size=nRelease['size'] , moreInformationUrl=nRelease['html_url'], comment=nRelease['comment'], url_prefix=url_prefix)
      with open(downloads_md, 'a') as outfile:
        outfile.write(download_row + '\n')

def outputSectionSimple(downloads_md, versionTags, releasesMatrix, shortName, url_prefix=""):
  for nTagVersion in versionTags:
    filteredMatrix = filterByVersionTag(releasesMatrix, nTagVersion)
    orderedFilteredMatrix = sorted(filteredMatrix, key=lambda d: d['distroLongName'])

    download_table_top = get_download_table_top_simple (versionTag=nTagVersion, shortName=shortName)
    with open(downloads_md, 'a') as outfile:
      outfile.write('\n' + download_table_top + '\n')

    for nRelease in orderedFilteredMatrix:
      download_row = get_download_row_simple (prefixTag=nRelease['prefixTag'], versionTag=nRelease['versionTag'], distroLongName=nRelease['distroLongName'], tgzDownloadUrl=nRelease['tgzDownloadUrl'], buildDate=nRelease['buildDate'], size=nRelease['size'] , moreInformationUrl=nRelease['html_url'], comment=nRelease['comment'], url_prefix=url_prefix)
      with open(downloads_md, 'a') as outfile:
        outfile.write(download_row + '\n')

def outputNewLine(downloads_md):
  with open(downloads_md, 'a') as outfile:
    outfile.write('\n')

def outputNewHLine(downloads_md):
  with open(downloads_md, 'a') as outfile:
    outfile.write('\n')
    outfile.write('---')
    outfile.write('\n')

def outputBlockNewLine(downloads_md, block):
  with open(downloads_md, 'a') as outfile:
    outfile.write(block)
    outfile.write('\n')

# Get the main releasesMatrix with all of the releases information
releasesMatrix = getReleasesMatrix()

releasesMatrix = expandByRhel7(releasesMatrix)
releasesMatrix = expandByRhel8(releasesMatrix)
releasesMatrix = expandByRhel9(releasesMatrix)

# Get our four main matrices
stableReleasesMatrix = filterByCategory(matrix=releasesMatrix, category="stable")
recentReleasesMatrix = filterByCategory(matrix=releasesMatrix, category="recent")
experimentalReleasesMatrix = filterByCategory(matrix=releasesMatrix, category="experimental")
otherReleasesMatrix = filterByCategory(matrix=releasesMatrix, category="other")
simpleReleasesMatrix = filterNoRhel(matrix=stableReleasesMatrix)

# Get ordered (and unique) tags
stableVersionTags = getVersionTags (stableReleasesMatrix)
stableVersionTags = orderedAndUniqueVersionTags (stableVersionTags)

# Get ordered (and unique) tags
simpleVersionTags = getVersionTags (simpleReleasesMatrix)
simpleVersionTags = orderedAndUniqueVersionTags (simpleVersionTags)

simple1VersionTags = getFirstTagStartingWith (simpleVersionTags, prefix='10.1.')
simple2VersionTags = getFirstTagStartingWith (simpleVersionTags, prefix='10.0.')

recentVersionTags = getVersionTags (recentReleasesMatrix)
recentVersionTags = orderedAndUniqueVersionTags (recentVersionTags)

experimentalVersionTags = getVersionTags (experimentalReleasesMatrix)
experimentalVersionTags = orderedAndUniqueVersionTags (experimentalVersionTags)

otherVersionTags = getVersionTags (otherReleasesMatrix)
otherVersionTags = orderedAndUniqueVersionTags (otherVersionTags)

latestVersionTags = getLatestVersionTagsByBuildDate(releasesMatrix, limit=5)

def generate_downloads_header(current_idCategory, url_prefix=""):
    """
    Generate a markdown header menu for Zimbra downloads with the current category highlighted,
    arranged in labeled rows.
    """

    if url_prefix is None:
        url_prefix = ""
    if url_prefix and not url_prefix.endswith("/"):
        url_prefix = url_prefix + "/"

    prefix = "Maldua's Zimbra Foss Downloads"
    postfix = f"\n( Learn more at: [Maldua's Zimbra Foss]({url_prefix}../) and [Maldua's Zimbra Foss Github repo](https://github.com/maldua/zimbra-foss). )"

    rows = []

    for group_label, ids in MENU_GROUPS.items():
        row_items = []
        for idCat in ids:
            file = header_links_mapping[idCat]
            label = shortNamesLabels.get(idCat, idCat.capitalize())
            item = f"[{label}]({url_prefix}{file})"
            if idCat == current_idCategory:
                item = f"**{item}**"
            row_items.append(item)

        row_md = f"- *{group_label}:* " + " \\| ".join(row_items)
        rows.append(row_md)

    # Combine into final markdown block
    return prefix + "\n" + "\n" + "\n".join(rows) + "\n" + postfix

def renderCategoryBlock(
    downloads_md,
    top_template,
    versionTags,
    releasesMatrix,
    shortName
):
    outputNewLine(downloads_md)
    append_files(templatesDir + "/" + top_template, downloads_md)
    append_files(templatesDir + "/" + "section-top-disclaimers.md", downloads_md)
    append_files(templatesDir + "/" + "downloads-subscribe.md", downloads_md)

    outputSection(
        downloads_md=downloads_md,
        versionTags=versionTags,
        releasesMatrix=releasesMatrix,
        shortName=shortName
    )

def writeAdvancedDownloadsPage(downloads_md):
    # Empty our output file
    if os.path.isfile(downloads_md):
        os.remove(downloads_md)

    title=f"Archive"
    description=f"Release historic archive."
    outputTitle(downloads_md, title=title, description=description)

    header = generate_downloads_header("archive")
    outputBlockNewLine(downloads_md, header)

    # Initial structure
    append_files(templatesDir + "/" + "downloads-top.md", downloads_md)
    append_files(templatesDir + "/" + "downloads-index.md", downloads_md)

    # Stable section
    renderCategoryBlock(
        downloads_md=downloads_md,
        top_template="stable-releases-top.md",
        versionTags=stableVersionTags,
        releasesMatrix=stableReleasesMatrix,
        shortName=f"{STABLE_ICON} Stable {STABLE_ICON}"
    )

    # Recent section
    renderCategoryBlock(
        downloads_md=downloads_md,
        top_template="recent-releases-top.md",
        versionTags=recentVersionTags,
        releasesMatrix=recentReleasesMatrix,
        shortName=f"{RECENT_ICON} Recent {RECENT_ICON}"
    )

    # Experimental section
    renderCategoryBlock(
        downloads_md=downloads_md,
        top_template="experimental-releases-top.md",
        versionTags=experimentalVersionTags,
        releasesMatrix=experimentalReleasesMatrix,
        shortName=f"{EXPERIMENTAL_ICON} Experimental {EXPERIMENTAL_ICON}"
    )

    # Other section
    renderCategoryBlock(
        downloads_md=downloads_md,
        top_template="other-releases-top.md",
        versionTags=otherVersionTags,
        releasesMatrix=otherReleasesMatrix,
        shortName=f"{OTHER_ICON} Recent {OTHER_ICON}"
    )

    outputNewLine(downloads_md)
    append_files(templatesDir + "/" + "downloads-index.md", downloads_md)

def writeSimpleDownloadsPage(downloads_md):
  # Empty our output file
  if (os.path.isfile(downloads_md)):
    os.remove(downloads_md)

  title=f"Main"
  description=f"Main page for downloading Maldua's releases."
  outputTitle(downloads_md, title=title, description=description)

  header = generate_downloads_header("main")
  outputBlockNewLine(downloads_md, header)

  # Write the different sections as needed

  append_files(templatesDir + "/" + "simple-title.md", downloads_md)
  append_files(templatesDir + "/" + "simple-top.md", downloads_md)
  outputSectionSimple(downloads_md=downloads_md, versionTags=simple1VersionTags, releasesMatrix=simpleReleasesMatrix, shortName=f"10.1.x {STABLE_ICON} Stable {STABLE_ICON}")
  outputNewHLine(downloads_md)
  outputSectionSimple(downloads_md=downloads_md, versionTags=simple2VersionTags, releasesMatrix=simpleReleasesMatrix, shortName=f"10.0.x {STABLE_ICON} Stable {STABLE_ICON}")
  outputNewHLine(downloads_md)
  append_files(templatesDir + "/" + "simple-top.md", downloads_md)

def writeCategoryDownloadsPage(
    downloads_md,
    top_template,
    versionTags,
    releasesMatrix,
    shortName,
    idCategory
):
    # Empty output file
    if os.path.isfile(downloads_md):
        os.remove(downloads_md)

    categoryTitle=idCategory.capitalize()
    title=f"{categoryTitle} Downloads"
    description=f"{categoryTitle} Downloads (Category)"
    outputTitle(downloads_md, title=title, description=description)

    # Common header for all category pages
    categoryHeader = generate_downloads_header(idCategory)
    outputBlockNewLine(downloads_md, categoryHeader)

    outputNewLine(downloads_md)

    # Category-specific header
    append_files(templatesDir + "/" + top_template, downloads_md)
    append_files(templatesDir + "/" + "section-top-disclaimers.md", downloads_md)
    append_files(templatesDir + "/" + f"category-{idCategory}-subscribe.md", downloads_md)

    # The actual section
    outputSection(
        downloads_md=downloads_md,
        versionTags=versionTags,
        releasesMatrix=releasesMatrix,
        shortName=shortName
    )

    outputNewHLine(downloads_md)
    categoryHeader = generate_downloads_header(idCategory)
    outputBlockNewLine(downloads_md, categoryHeader)

def writeStableDownloadsPage(downloads_md):
    writeCategoryDownloadsPage(
        downloads_md=downloads_md,
        top_template="stable-releases-top.md",
        versionTags=stableVersionTags,
        releasesMatrix=stableReleasesMatrix,
        shortName=shortNamesLabels.get("stable"),
        idCategory="stable"
    )

def writeRecentDownloadsPage(downloads_md):
    writeCategoryDownloadsPage(
        downloads_md=downloads_md,
        top_template="recent-releases-top.md",
        versionTags=recentVersionTags,
        releasesMatrix=recentReleasesMatrix,
        shortName=shortNamesLabels.get("recent"),
        idCategory="recent"
    )

def writeExperimentalDownloadsPage(downloads_md):
    writeCategoryDownloadsPage(
        downloads_md=downloads_md,
        top_template="experimental-releases-top.md",
        versionTags=experimentalVersionTags,
        releasesMatrix=experimentalReleasesMatrix,
        shortName=shortNamesLabels.get("experimental"),
        idCategory="experimental"
    )

def writeOtherDownloadsPage(downloads_md):
    writeCategoryDownloadsPage(
        downloads_md=downloads_md,
        top_template="other-releases-top.md",
        versionTags=otherVersionTags,
        releasesMatrix=otherReleasesMatrix,
        shortName=shortNamesLabels.get("other"),
        idCategory="other"
    )

def outputLatestSection(downloads_md, versionTag, releasesMatrix):
    versionTags = [versionTag]
    shortName = getShortNameForVersionTag(versionTag, releasesMatrix)

    outputSection(
        downloads_md=downloads_md,
        versionTags=versionTags,
        releasesMatrix=releasesMatrix,
        shortName=shortName
    )

def writeLatestDownloadsPage(downloads_md):
    # Remove old file
    if os.path.isfile(downloads_md):
        os.remove(downloads_md)

    title=f"Latest Downloads"
    description=f"The very latest downloads."
    outputTitle(downloads_md, title=title, description=description)

    header = generate_downloads_header("latest")
    outputBlockNewLine(downloads_md, header)

    append_files(templatesDir + "/" + "section-top-disclaimers.md", downloads_md)

    for versionTag in latestVersionTags:
        outputLatestSection(downloads_md, versionTag, releasesMatrix)

    outputNewLine(downloads_md)
    header = generate_downloads_header("latest")
    outputBlockNewLine(downloads_md, header)

def writeLatestPerPlatformDownloadsPage(downloads_md):
    """
    Generate the 'latest-per-platform.md' downloads page:
    - Shows all distro variants.
    - Ordered by family alphabetically and distro version descending.
    - Latest 2 releases per distro.
    - Adds index at top with links to each distro section.
    - Adds markdown section heading for each distro.
    """
    # Remove old file
    if os.path.isfile(downloads_md):
        os.remove(downloads_md)

    title=f"Latest Downloads per platform"
    description=f"The very latest downloads grouped by platforms."
    outputTitle(downloads_md, title=title, description=description)

    header = generate_downloads_header("latest_per_platform")
    outputBlockNewLine(downloads_md, header)

    append_files(templatesDir + "/" + "section-top-disclaimers.md", downloads_md)

    # Collect all distro variants with family and version info
    distroList = []
    for row in releasesMatrix:
        prefix_parts = row["prefixTag"].split("-")
        family = prefix_parts[-2].capitalize()  # e.g., "Ubuntu", "Rhel", "Rocky"
        distro_version = prefix_parts[-1]       # e.g., "20.04", "8", "9"
        distroList.append((family, version_to_float(distro_version), row["distroLongName"]))

    # Remove duplicates (keep order)
    seen = set()
    uniqueDistros = []
    for fam, ver, name in distroList:
        if name not in seen:
            seen.add(name)
            uniqueDistros.append((fam, ver, name))

    # Sort by family alphabetically, then version descending
    sortedDistros = sorted(uniqueDistros, key=lambda x: (x[0], -x[1]))

    # --- Generate index ---
    index_lines = ["## Index\n"]
    for family, version, distroName in sortedDistros:
        # Markdown anchor: lowercase, replace spaces and dots with hyphens
        anchor = distroName.lower().replace(" ", "-").replace(".", "")
        index_lines.append(f"- [{distroName}](#{anchor})")
    outputBlockNewLine(downloads_md, "\n".join(index_lines))
    outputNewLine(downloads_md)

    # --- Generate sections for each distro ---
    for family, version, distroName in sortedDistros:
        outputNewHLine(downloads_md)
        # Markdown section heading for the distro
        anchor = distroName.lower().replace(" ", "-").replace(".", "")
        distro_header = f"\n## {distroName} {{#{anchor}}}\n"
        outputBlockNewLine(downloads_md, distro_header)

        latestTags = getLatestVersionTagsByDistro(releasesMatrix, distroName, limit=2)
        for versionTag in latestTags:
            filteredMatrix = filterByVersionTag(releasesMatrix, versionTag)
            filteredMatrix = [row for row in filteredMatrix if row["distroLongName"] == distroName]
            if filteredMatrix:
                category = filteredMatrix[0]["category"]
                shortName = f"{shortNamesLabels.get(category, category)}"
                outputSection(downloads_md, [versionTag], filteredMatrix, shortName)

    outputNewLine(downloads_md)
    outputBlockNewLine(downloads_md, "\n".join(index_lines))
    outputNewLine(downloads_md)

    outputNewLine(downloads_md)
    # Repeat header at the bottom
    header = generate_downloads_header("latest_per_platform")
    outputBlockNewLine(downloads_md, header)

def writeLatestPerFamilyDownloadsPage(downloads_md):
    """
    Generate 'latest-per-zimbra-family.md':
    - Shows latest 2 versionTags per Zimbra family
    - Adds index at top with links to each family
    - Sorted by family descending
    """
    # Remove old file
    if os.path.isfile(downloads_md):
        os.remove(downloads_md)

    title=f"Latest Downloads per Zimbra family"
    description=f"The very latest downloads grouped by Zimbra family. E.g. Zimbra 10.0.x, Zimbra 10.1.x."
    outputTitle(downloads_md, title=title, description=description)

    header = generate_downloads_header("latest_per_family")
    outputBlockNewLine(downloads_md, header)

    append_files(templatesDir + "/" + "section-top-disclaimers.md", downloads_md)

    # Build mapping family -> list of versionTags
    familyBuckets = {}
    for row in releasesMatrix:
        family = getZimbraFamily(row["versionTag"])
        if family not in familyBuckets:
            familyBuckets[family] = set()
        familyBuckets[family].add(row["versionTag"])

    # Convert to sorted list (newest first)
    familyBucketsSorted = {}
    for family, tags in familyBuckets.items():
        orderedTags = orderedAndUniqueVersionTags(list(tags))
        familyBucketsSorted[family] = orderedTags[:2]  # latest 2 per family

    # Sort families descending
    sortedFamilies = sorted(
        familyBucketsSorted.keys(),
        key=lambda fam: float(fam),
        reverse=True
    )

    # --- Generate index ---
    index_lines = ["## Index\n"]
    for family in sortedFamilies:
        label = family_to_label(family)
        anchor = label.replace(".", "-").lower()
        index_lines.append(f"- [Zimbra {label}](#zimbra-{anchor})")
    outputBlockNewLine(downloads_md, "\n".join(index_lines))
    outputNewLine(downloads_md)

    # --- Generate sections ---
    for family in sortedFamilies:
        outputNewHLine(downloads_md)
        label = family_to_label(family)
        anchor = label.replace(".", "-").lower()
        outputBlockNewLine(downloads_md, f"\n## Zimbra {label} {{#zimbra-{anchor}}}\n")

        for versionTag in familyBucketsSorted[family]:
            filteredMatrix = filterByVersionTag(releasesMatrix, versionTag)
            category = filteredMatrix[0]["category"]
            shortName = f"{shortNamesLabels.get(category, category)}"
            outputSection(downloads_md, [versionTag], filteredMatrix, shortName)

    outputNewLine(downloads_md)
    outputBlockNewLine(downloads_md, "\n".join(index_lines))
    outputNewLine(downloads_md)

    outputNewLine(downloads_md)
    header = generate_downloads_header("latest_per_family")
    outputBlockNewLine(downloads_md, header)

def writeVersionPage(version_md, versionTag):

    url_prefix = "../"
    # Remove old file
    if os.path.isfile(version_md):
        os.remove(version_md)


    title=f"Zimbra Foss {versionTag}"
    description=f"Zimbra Foss {versionTag} different releases from Maldua for you to download."
    outputTitle(version_md, title=title, description=description)

    header = generate_downloads_header("", url_prefix=url_prefix)
    outputBlockNewLine(version_md, header)

    append_files(templatesDir + "/" + "section-top-disclaimers.md", version_md)

    filteredMatrix = filterByVersionTag(releasesMatrix, versionTag)

    shortName = ""
    if filteredMatrix:
        category = filteredMatrix[0]["category"]
        shortName = f"{shortNamesLabels.get(category, category)}"

    outputSection(
        downloads_md=version_md,
        versionTags=[versionTag],
        releasesMatrix=releasesMatrix,
        shortName=shortName,
        url_prefix=url_prefix
    )

    outputNewLine(version_md)

    header = generate_downloads_header("", url_prefix=url_prefix)
    outputBlockNewLine(version_md, header)

def writeVersionPages():
    """
    Generate one markdown file per unique versionTag using outputSectionSimple().
    Output files go to: docs/downloads/version/<versionTag>.md
    """

    version_tags = getUniqueList([row["versionTag"] for row in releasesMatrix])

    for vt in version_tags:
        version_md = os.path.join(VERSION_DIR, f"{vt}.md")
        writeVersionPage(version_md, vt)

writeAdvancedDownloadsPage(archive_md)
writeSimpleDownloadsPage(main_downloads_md)

writeStableDownloadsPage(stable_md)
writeRecentDownloadsPage(recent_md)
writeExperimentalDownloadsPage(experimental_md)
writeOtherDownloadsPage(other_md)
writeLatestDownloadsPage(latest_md)
writeLatestPerPlatformDownloadsPage(latest_per_platform_md)
writeLatestPerFamilyDownloadsPage(latest_per_family_md)

writeVersionPages()

# Copy images/ folder into docs/
src_images = os.path.join(os.path.dirname(__file__), "images")
dst_images = os.path.join(DOWNLOADS_OUTPUT_DIR, "images")

if os.path.isdir(dst_images):
    shutil.rmtree(dst_images)

shutil.copytree(src_images, dst_images)
