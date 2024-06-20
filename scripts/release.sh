debug=echo
dbg_suffix=.dev7
# Assume this file is in the reporoot/scripts directory
reporoot=$(dirname $0)/..
cd $reporoot

# Make sure required env vars are set
if [ -z "$DPK_DOCKER_REGISTRY_USER" ]; then
    echo DPK_DOCKER_REGISTRY_USER env var must be set
    exit 1
elif [ -z "$DPK_DOCKER_REGISTRY_KEY" ]; then
    echo DPK_DOCKER_REGISTRY_KEY env var must be set
    exit 1
elif [ -z "$DPK_PYPI_USER" ]; then
    echo DPK_PYPI_USER env var must be set
    exit 1
elif [ -z "$DPK_PYPI_TOKEN" ]; then
    echo DPK_DPYP_TOKEN env var must be set
    exit 1
fi

if [ -z "$debug" ]; then
    DEFAULT_BRANCH=dev
else
    DEFAULT_BRANCH=releasing-copy
fi

# Make sure we're starting from the base branch
get fetch
git checkout $DEFAULT_BRANCH 

# Get the currently defined version w/o any suffix.  This is the next release version
version=$(make DPK_VERSION_SUFFIX= show-version)

if [ -z "$debug" ]; then
    tag=v$version
else
    tag=test$version
fi

# Create a new branch for this version and switch to it
release_branch=release/$tag
if [ ! -z "$debug" ]; then
    # delete local tag and branch
    git tag --delete $tag
    git branch --delete $release_branch
    # delete remote tag and branch
    git push --delete origin $tag
    git push --delete origin $release_branch
fi
git checkout -b $release_branch 


# Remove the release suffix in this branch
if [ -z "$debug" ]; then
    cat .make.versions | sed -e 's/^DPK_VERSION_SUFFIX.*/DPK_VERSION_SUFFIX=/' > tt
    mv tt .make.versions
else
    cat .make.versions | sed -e "s/^DPK_VERSION_SUFFIX.*/DPK_VERSION_SUFFIX=$dbg_suffix/" > tt
    mv tt .make.versions
fi

# Apply the unsuffixed version to the repo and check it into this release branch
make set-versions
git add -A
git commit -s -m "Cut release $version"
git push origin
git tag -a -s -m "Cut release $version" $tag 
git push --set-upstream origin $release_branch 
git push origin $tag 

# Now build with the updated version
# Requires quay credentials in the environment, DPL_DOCKER_REGISTRY_USER, DPK_DOCKER_REGISTRY_KEY
# Requires pypi credentials in the environment, DPK_PYPI_USER=, DPK_PYPI_TOKEN
if [ -z "$debug" ]; then
    make build publish
else
    echo make -C transforms/universal/noop build publish
fi

# Now go back to the default branch so we can bump the minor version number and reset the version suffix
git checkout $DEFAULT_BRANCH

# Change to the next development version (bumped minor version with suffix).
# Do we want to control major vs minor bump
minor=$(cat .make.versions | grep '^DPK_MINOR_VERSION=' | sed -e 's/DPK_MINOR_VERSION=\([0-9]*\).*/\1/') 
minor=$(($minor + 1))
cat .make.versions | sed -e "s/^DPK_MINOR_VERSION=.*/DPK_MINOR_VERSION=$minor/"  \
 			 -e "s/^DPK_VERSION_SUFFIX=.*/DPK_VERSION_SUFFIX=.dev0/"  > tt
mv tt .make.versions

# Push the version change back to the origin
# git add -A
# git commit -s -m "Bump minor version to $minor after cutting release $version"
# git push origin
