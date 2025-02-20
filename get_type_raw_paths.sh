#!/bin/bash

# Print help message
function print_help() {
    echo "Usage Instructions:"
    echo "This script is used to find directories containing a 'type.raw' file in the specified folder and save their relative paths to a text file."
    echo ""
    echo "Usage:"
    echo "./get_type_raw_paths.sh <folder_path>"
    echo "  <folder_path>: The path to the target folder where data directories are located."
    echo "  If no folder path is provided, the script will prompt you to select a folder, defaulting to the current directory."
    echo ""
    echo "Example:"
    echo "./get_type_raw_paths.sh ./data_folder"
    echo ""
}

# Check if any arguments are passed, if not, ask the user to select a folder
if [ $# -eq 0 ]; then
    echo "No folder path provided, the script will prompt you to select a folder."
    # Prompt the user to select a folder
    folder_path=$(zenity --file-selection --directory --title="Select Folder" --filename="./")
    if [ -z "$folder_path" ]; then
        echo "No folder selected, exiting the script."
        exit 1
    fi
else
    folder_path=$1
fi

# Check if the provided path is a valid directory
if [ ! -d "$folder_path" ]; then
    echo "The specified path is not a valid directory: $folder_path"
    exit 1
fi

# Get the current working directory
current_dir=$(pwd)

# Generate the output file name
output_file="${folder_path}_path.txt"

# Find directories containing 'type.raw' file and output their relative paths to the output file
echo "Searching for directories containing 'type.raw' and saving their relative paths to the file $output_file..."

# Use the find command to search for 'type.raw' and output the relative directory paths
find "$folder_path" -type f -name "type.raw" -exec dirname {} \; | sed "s|^$current_dir/||" | sed 's|^|\"|' | sed 's|$|\",|' > "$output_file"

# Format the output file (remove the last comma and add a newline)
sed -i '$ s/,$//' "$output_file"
sed -i 's/$/\n/' "$output_file"

echo "Paths have been saved to $output_file"
echo "Script execution completed."
