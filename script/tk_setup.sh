#!/bin/bash -e
# tk_setup.sh
# Brian Dunbar
# assumes work happens in ~/workspace/fsw
# - Change WORKSPACE to another value if desired
# tk_setup.sh xxxx
# - creates ~/workspace/xxxx
# - git clones
# - walks into cfs, updates modules
# now runs in paraallel


# include as many, or as few, repositories as desired.
# repos=("cfe" "cfs" "osal" "psp" "sbn")

repos=("cfs")

# The ticket number is passed as a command line argument
TICKET=$1

# The workspace is set as an environment variable
WORKSPACE=${WORKSPACE:-~/workspace/fsw}

# Check if ticket number is provided
if [ -z "$TICKET" ]; then
    echo "No ticket number provided. Please run the script with a ticket number." >&2
    exit 1
fi

# Create the directory for the ticket in the workspace
if ! mkdir -p ${WORKSPACE}/${TICKET}; then
    echo "Could not create the directory: ${WORKSPACE}/${TICKET}" >&2
    exit 1
fi

# Change into the new directory
cd ${WORKSPACE}/${TICKET}

# Clone the repositories into the directory in parallel
for repo in "${repos[@]}"; do
    git clone git@gitlab.maxar.com:irad/augustus/fsw/$repo.git & # This line is executed in the background
done

# Wait for all background jobs to finish
wait

# Check if all repositories were cloned successfully
for repo in "${repos[@]}"; do
    if [ ! -d "$repo" ]; then
        echo "Failed to clone repository: $repo" >&2
        exit 1
    fi
done

# Move into the cfs directory and update the submodules
cd cfs
if ! git submodule update --init --recursive; then
    echo "Failed to update one or more submodules" >&2
    exit 1
fi


echo "Setup completed successfully at ${WORKSPACE}/${TICKET}"
