#!/bin/bash

function get_generate_tag() {
	LAST_GENERATE_TAG=$(git tag | grep '^generate-downloads' | sort -V | tail -n 1)
	TAG_VERSION=$(echo ${LAST_GENERATE_TAG} | awk -F '.' '{print $3}')
	TAG_VERSION=$((TAG_VERSION+1))
	NEW_GENERATE_TAG=$(echo -e -n ${LAST_GENERATE_TAG} | awk -F '.' '{print $1 "." $2 "."}')$(echo -e -n "${TAG_VERSION}")
	echo ${NEW_GENERATE_TAG}
}


ZIMBRA_10_0_X_VERSIONS="10.0.11"
ZIMBRA_10_1_X_VERSIONS="10.1.3"

ZIMBRA_10_0_X_PLATFORMS="rhel-7 rhel-8 ubuntu-18.04 ubuntu-20.04"
ZIMBRA_10_1_X_PLATFORMS="rhel-7 rhel-8 rhel-9 ubuntu-18.04 ubuntu-20.04 ubuntu-22.04"

RELEASE_BUILD_TIME="20m"

for nplatform in ${ZIMBRA_10_0_X_PLATFORMS} ; do
  for nversion in ${ZIMBRA_10_0_X_VERSIONS} ; do
    ntag="builds-${nplatform}/${nversion}"
    git tag -a $ntag -m $ntag
    git push origin $ntag
  done
done
for nplatform in ${ZIMBRA_10_1_X_PLATFORMS} ; do
  for nversion in ${ZIMBRA_10_1_X_VERSIONS} ; do
    ntag="builds-${nplatform}/${nversion}"
    git tag -a $ntag -m $ntag
    git push origin $ntag
  done
done

sleep ${RELEASE_BUILD_TIME}

NEW_GENERATE_TAG=$(get_generate_tag)

git tag -a "${NEW_GENERATE_TAG}" -m "${NEW_GENERATE_TAG}"
git push origin "${NEW_GENERATE_TAG}"

