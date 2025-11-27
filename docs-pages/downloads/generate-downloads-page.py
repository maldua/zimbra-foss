#!/usr/bin/env python3

import os
import shutil
import re
import requests
from subprocess import run, PIPE

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

# Resolve output directory: we are running from docs-pages/downloads
PARENT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
GRAND_PARENT_DIR = os.path.abspath(os.path.join(PARENT_DIR, ".."))
DOCS_DIR = os.path.join(GRAND_PARENT_DIR, "docs")
DOWNLOADS_OUTPUT_DIR = os.path.join(DOCS_DIR, "downloads")
os.makedirs(DOWNLOADS_OUTPUT_DIR, exist_ok=True)

# Write output into docs/
simple_downloads_md = os.path.join(DOWNLOADS_OUTPUT_DIR, "README.md")
downloads_md = os.path.join(DOWNLOADS_OUTPUT_DIR, "advanced.md")

# templates/ and images/ remain relative to current folder
templatesDir = 'templates'
imagesDir = "images"

repoReleasesApiUrl="https://api.github.com/repos/maldua/zimbra-foss/releases"

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')

# Other functions
def sizeof_fmt(num, suffix="B"):
    for unit in ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
        if abs(num) < 1024.0:
            return f"{num:3.0f} {unit}{suffix}"
        num /= 1024.0
    return f"{num:f} Yi{suffix}"

# Download markdown functions
def getIconField(prefixTag):
  if ("ubuntu" in prefixTag):
    iconField = f"![Ubuntu icon]({imagesDir}/ubuntu.png)"
  elif ("rhel" in prefixTag):
    iconField = f"![RedHat icon]({imagesDir}/redhat.png)"
  elif ("oracle" in prefixTag):
    iconField = f"![Oracle icon]({imagesDir}/oracle.png)"
  elif ("rocky" in prefixTag):
    iconField = f"![Rocky icon]({imagesDir}/rocky.png)"
  elif ("centos" in prefixTag):
    iconField = f"![Centos icon]({imagesDir}/centos.png)"
  else:
    iconField = ""

  return (iconField)

def get_download_table_top_simple (versionTag, shortName):
  return (
    f"### {versionTag} ({shortName})\n"
    '\n'
    f'| {IMAGE_ICON} | {COMPUTER_ICON} PLATFORM | {PACKAGE_ICON} DOWNLOAD 64-BIT | {MEMO_ICON} +INFO |\n'
    '| --- | --- | --- | --- |'
  )

def get_download_table_top (versionTag, shortName):
  return (
    f"### {versionTag} ({shortName})\n"
    '\n'
    f"| {IMAGE_ICON} | {COMPUTER_ICON} Platform | {PACKAGE_ICON} Download 64-BIT | {CALENDAR_ICON} Build Date | {RULER_ICON} Size | {LINK_ICON} +Info | {MEMO_ICON} Comment |\n"
    '| --- | --- | --- | --- | --- | --- | --- |'
  )

def get_download_row (prefixTag, versionTag, distroLongName, tgzDownloadUrl, buildDate, size, moreInformationUrl, comment):
  icon = getIconField(prefixTag)
  md5DownloadUrl = tgzDownloadUrl + ".md5"
  sha256DownloadUrl = tgzDownloadUrl + ".sha256"
  humanSize = sizeof_fmt(size)
  # TODO: Use the release url directly instead of crafting it ourselves.
  download_row = f"|{icon} | {distroLongName} | [64bit x86]({tgzDownloadUrl}) - [MD5]({md5DownloadUrl}) - [SHA256]({sha256DownloadUrl}) | {buildDate} | {humanSize} | [+Info]({moreInformationUrl}) | {comment} |"
  return (download_row)

def get_download_row_simple (prefixTag, versionTag, distroLongName, tgzDownloadUrl, buildDate, size, moreInformationUrl, comment):
  icon = getIconField(prefixTag)
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

def outputSection(downloads_md, versionTags, releasesMatrix, shortName):
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
      download_row = get_download_row (prefixTag=nRelease['prefixTag'], versionTag=nRelease['versionTag'], distroLongName=nRelease['distroLongName'], tgzDownloadUrl=nRelease['tgzDownloadUrl'], buildDate=nRelease['buildDate'], size=nRelease['size'] , moreInformationUrl=nRelease['html_url'], comment=nRelease['comment'])
      with open(downloads_md, 'a') as outfile:
        outfile.write(download_row + '\n')

def outputSectionSimple(downloads_md, versionTags, releasesMatrix, shortName):
  for nTagVersion in versionTags:
    filteredMatrix = filterByVersionTag(releasesMatrix, nTagVersion)
    orderedFilteredMatrix = sorted(filteredMatrix, key=lambda d: d['distroLongName'])

    download_table_top = get_download_table_top_simple (versionTag=nTagVersion, shortName=shortName)
    with open(downloads_md, 'a') as outfile:
      outfile.write('\n' + download_table_top + '\n')

    for nRelease in orderedFilteredMatrix:
      download_row = get_download_row_simple (prefixTag=nRelease['prefixTag'], versionTag=nRelease['versionTag'], distroLongName=nRelease['distroLongName'], tgzDownloadUrl=nRelease['tgzDownloadUrl'], buildDate=nRelease['buildDate'], size=nRelease['size'] , moreInformationUrl=nRelease['html_url'], comment=nRelease['comment'])
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

def writeAdvancedDownloadsPage(downloads_md):
  # Empty our output file
  if (os.path.isfile(downloads_md)):
    os.remove(downloads_md)

  # Write the different sections as needed

  append_files(templatesDir + "/" + "downloads-top.md", downloads_md)
  append_files(templatesDir + "/" + "downloads-index.md", downloads_md)

  outputNewLine(downloads_md)
  append_files(templatesDir + "/" + "stable-releases-top.md", downloads_md)
  append_files(templatesDir + "/" + "section-top-disclaimers.md", downloads_md)
  append_files(templatesDir + "/" + "downloads-subscribe.md", downloads_md)
  outputSection(downloads_md=downloads_md, versionTags=stableVersionTags, releasesMatrix=stableReleasesMatrix, shortName=f"{STABLE_ICON} Stable {STABLE_ICON}")

  outputNewLine(downloads_md)
  append_files(templatesDir + "/" + "recent-releases-top.md", downloads_md)
  append_files(templatesDir + "/" + "section-top-disclaimers.md", downloads_md)
  append_files(templatesDir + "/" + "downloads-subscribe.md", downloads_md)
  outputSection(downloads_md=downloads_md, versionTags=recentVersionTags, releasesMatrix=recentReleasesMatrix, shortName=f"{RECENT_ICON} Recent {RECENT_ICON}")

  outputNewLine(downloads_md)
  append_files(templatesDir + "/" + "experimental-releases-top.md", downloads_md)
  append_files(templatesDir + "/" + "section-top-disclaimers.md", downloads_md)
  append_files(templatesDir + "/" + "downloads-subscribe.md", downloads_md)
  outputSection(downloads_md=downloads_md, versionTags=experimentalVersionTags, releasesMatrix=experimentalReleasesMatrix, shortName=f"{EXPERIMENTAL_ICON} Experimental {EXPERIMENTAL_ICON}")

  outputNewLine(downloads_md)
  append_files(templatesDir + "/" + "other-releases-top.md", downloads_md)
  append_files(templatesDir + "/" + "section-top-disclaimers.md", downloads_md)
  append_files(templatesDir + "/" + "downloads-subscribe.md", downloads_md)
  outputSection(downloads_md=downloads_md, versionTags=otherVersionTags, releasesMatrix=otherReleasesMatrix, shortName=f"{OTHER_ICON} Recent {OTHER_ICON}")

  outputNewLine(downloads_md)
  append_files(templatesDir + "/" + "downloads-index.md", downloads_md)

def writeSimpleDownloadsPage(downloads_md):
  # Empty our output file
  if (os.path.isfile(downloads_md)):
    os.remove(downloads_md)

  # Write the different sections as needed

  append_files(templatesDir + "/" + "simple-title.md", downloads_md)
  append_files(templatesDir + "/" + "simple-top.md", downloads_md)
  outputSectionSimple(downloads_md=downloads_md, versionTags=simple1VersionTags, releasesMatrix=simpleReleasesMatrix, shortName=f"10.1.x {STABLE_ICON} Stable {STABLE_ICON}")
  outputNewHLine(downloads_md)
  outputSectionSimple(downloads_md=downloads_md, versionTags=simple2VersionTags, releasesMatrix=simpleReleasesMatrix, shortName=f"10.0.x {STABLE_ICON} Stable {STABLE_ICON}")
  outputNewHLine(downloads_md)
  append_files(templatesDir + "/" + "simple-top.md", downloads_md)

writeAdvancedDownloadsPage(downloads_md)
writeSimpleDownloadsPage(simple_downloads_md)

# Copy images/ folder into docs/
src_images = os.path.join(os.path.dirname(__file__), "images")
dst_images = os.path.join(DOWNLOADS_OUTPUT_DIR, "images")

if os.path.isdir(dst_images):
    shutil.rmtree(dst_images)

shutil.copytree(src_images, dst_images)
