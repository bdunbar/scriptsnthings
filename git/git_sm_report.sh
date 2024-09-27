#!/bin/bash
set -e  # Exit on error

# git_sm_report.sh
# BDunba
# reports on git submodule state

echo "Submodule Status Report" 
echo "-----------------------"

# Fetch the latest data from all remotes
git submodule update --init --recursive
git submodule foreach --recursive 'git fetch'

# Report on each submodule
git submodule foreach --recursive '
    echo "Submodule: $path"
    current_commit=$(git rev-parse HEAD)
    echo "Current Commit: $current_commit"

    # Default to development, fall back to main
    branch_to_compare="development"
    if ! git show-ref --verify --quiet "refs/remotes/origin/development"; then
        if git show-ref --verify --quiet "refs/remotes/origin/main"; then
            branch_to_compare="main"
        else
            echo "Neither development nor main branches found"
            echo "-----------------------"
            exit 0
        fi
    fi

    echo "Comparing with branch: $branch_to_compare"
    latest_commit=$(git rev-parse origin/$branch_to_compare 2>/dev/null || echo "N/A")
    echo "Latest Commit on $branch_to_compare: $latest_commit"

    if [ "$latest_commit" == "N/A" ]; then
        echo "Cannot determine the latest commit on remote branch"
    elif [ "$current_commit" == "$latest_commit" ]; then
        echo "Status: UP TO DATE"
    else
        echo "Status: BEHIND or DIVERGED"
        commits_behind=$(git rev-list --count $current_commit..origin/$branch_to_compare 2>/dev/null || echo "N/A")
        echo "Commits Behind: $commits_behind"
    fi
    echo "-----------------------"
'
