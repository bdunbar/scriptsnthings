#!/bin/bash
# chrome_select
# choose chrome prifle and url to launch
# TODO add profile names from Local State or Preferences within profile directory.  Friendly name should be in JSON

# Path to Chrome profiles
PROFILE_PATH="$HOME/Library/Application Support/Google/Chrome"

# List all profiles by checking folder names in the profile path
echo "Available Chrome profiles:"
profiles=()
for profile_dir in "$PROFILE_PATH"/Profile* "$PROFILE_PATH"/Default; do
    profile_name=$(basename "$profile_dir")
    profiles+=("$profile_name")
    echo "${#profiles[@]}. $profile_name"
done

# Prompt user to select a profile
read -p "Enter the number of the profile you want to use: " profile_choice
selected_profile="${profiles[$((profile_choice - 1))]}"

# Prompt for the URL
read -p "Enter the URL to open: " url

# Launch Chrome with the selected profile and URL
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --profile-directory="$selected_profile" "$url"