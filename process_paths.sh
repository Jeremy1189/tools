#!/bin/bash
# This script is designed to process file paths for DeepMD distillation and fine-tuning.
# It reads paths from a selected text file, wraps each path in double quotes, adds a comma at the end,
# and saves the processed paths to a new file with the same name but '_new_path' appended.
# It also removes the trailing comma from the last line.
#
# Usage:
# 1. Save this script as `process_paths.sh`.
# 2. Make the script executable by running `chmod +x process_paths.sh`.
# 3. Run the script by typing `./process_paths.sh`.
# 4. The script will prompt you to select a `.txt` file containing paths in the current directory.
# 5. It will process the selected file and create a new file with '_new_path' added to the original filename.
#    For example, if the original file is `yourfile.txt`, the new file will be `yourfile_new_path.txt`.


# List all .txt files in the current directory and prompt the user to select one
echo "Please choose a text file to process:"
select original_file in *.txt; do
    if [[ -n "$original_file" ]]; then
        # If a valid file is selected, proceed with processing
        break
    else
        echo "Invalid selection. Please choose a valid .txt file."
    fi
done

# Create a new file name by appending '_new_path' to the original file name
new_file="${original_file%.txt}_new_path.txt"

# Initialize a flag to track if we're processing the last line
line_count=$(wc -l < "$original_file")
current_line=0

# Process each line of the selected file
while IFS= read -r line; do
    current_line=$((current_line + 1))
    # Add quotes around the path and append a comma, but handle the last line
    if [ "$current_line" -eq "$line_count" ]; then
        # For the last line, don't add a comma
        echo "\"$line\"" >> "$new_file"
    else
        # For all other lines, add a comma
        echo "\"$line\"," >> "$new_file"
    fi
done < "$original_file"

echo "Paths have been processed and saved to '$new_file'."
