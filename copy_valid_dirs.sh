#!/bin/bash

# Create the new_data directory if it doesn't exist
mkdir -p new_data

# Use find to search for directories containing 'valid' at any depth
find . -type d -name "*valid*" | while read dir; do
    # Remove the './' prefix and spaces from the directory path
    clean_name=$(echo "$dir" | sed 's|^\./||' | tr -d '[:space:]')
    
    # Create the necessary parent directories inside new_data
    mkdir -p "new_data/$(dirname "$clean_name")"
    
    # Copy the directory to new_data with the cleaned name
    cp -r "$dir" "new_data/$clean_name"
done

echo "Operation completed. All directories containing 'valid' have been copied to 'new_data' and renamed."
