#!/bin/bash

# Get the original file name (without the path)
original_file="yourfile.txt"
new_file="${original_file%.txt}_new_path.txt"  # Append 'new_path' to the original filename

# Open the original file and process each line
while IFS= read -r line; do
    # Add quotes around the path and append a comma
    echo "\"$line\"," >> "$new_file"
done < "$original_file"

echo "Paths have been processed and saved to '$new_file'."
