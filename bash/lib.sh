#!/bin/bash
# lib.sh
# Brian Dunbar
# bash library

# USAGE
# file_exists "/path/to/file.txt"
# log_info "File exists"
# log_error "File shouldn't exist"
# log_warn "DANGER WILL ROBINSON FILE EXISTS"
#

# exit on fail
set -e

# Prettify output
print_separator() {
  printf '%*s\n' "$(tput cols)" '' | tr ' ' '-'
}

print_blank_line() {
    echo " "
}


# Time function.  Because we like to measure things.
time_function() {
    local func_to_time="$1"
    local start_time=$(date +%s)

    # call
    $func_to_time

    local end_time=$(date +%s)
    local elapsed_time=$((end_time - start_time))
    echo "Elapsed time for $func_to_time: $elapsed_time seconds"
}

# Functions

## application check
function check_tmux() {
    if ! command -v tmux &> /dev/null; then
	echo "Error: tmux is not installed."
	exit 1
    fi
}


## GIT Stuff

# are we at the root

check_git_root() {
  git_root=$(git rev-parse --show-toplevel 2> /dev/null)
  if [ "$?" != "0" ]; then
    echo "Not in a Git repository. Exiting."
    return 1
  fi

  current_dir=$(pwd)
  if [ "$git_root" != "$current_dir" ]; then
    echo "Not at the root of the Git repository. Please navigate to the root directory. Exiting."
    return 1
  fi

  return 0
}


## Log

log_info() {
    local message="$1"
    echo "[INFO] $message"
}


log_error() {
    local message="$1"
    echo "[ERROR] $message" >&2
}


log.warn() {
    local message="$1"
    echo "[WARNING] $message"
}


# ERROR HANDLING
handle_error() {
    echo "Error: $1"
#    log_error $message
    exit 1
}

# ERROR CHECKING

check_command_success() {
    local last_exit_code="$?"
    local message="$1"

    if [ "$last_exit_code" -ne 0]; then
	log_error "$message"
	exit $last_exit_code
    fi
}

require_input() {
    local input="$1"
    local message="$2"

    if [[ -z "$input" ]]; then
	log_error "${message:-"Input is required!"}"
	exit 1
    fi
}

# FILE EXIST
file_exists() {
    local filename="$1"

    if [[ ! -f "$filename" ]]; then
	log_error "File $filename does not exist."
	exit 1
    fi
}

# FILE EXECUTABLE
file_exec() {
    local filename="$1"

    if [[ ! -f "$filename" ]]; then
	log_error "File $filename is not executable."
	exit 1
    fi
}


check_file_path() {
    local filename="$1"
    
    if ! command -v $filename &> /dev/null; then
	echo "Error: $filename is not installed or not in path."
	exit 1
    fi
}

# DIRECTORY EXIST
directory_exists() {
    local dirname="$1"

    if [[ ! -d "$dirname" ]]; then
	log_error "Directory $dirname does not exist."
	exit 1
    fi
}
