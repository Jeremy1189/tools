#!/bin/bash

# Create the new_data directory if it doesn't exist
mkdir -p new_data

# Iterate through all directories in the current folder
for dir in */; do
    # Check if the directory name contains the word "valid"
    if [[ "$dir" == *valid* ]]; then
        # Remove spaces from the directory path and use it as the folder name
        clean_name=$(echo "$dir" | tr -d '[:space:]')
        # Copy the directory to new_data with the cleaned name
        cp -r "$dir" "new_data/$clean_name"
    fi
done

echo "Operation completed. All directories containing 'valid' have been copied to 'new_data'."
