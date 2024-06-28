#!/bin/bash



echo "devc project files"
echo "Timestamp: $(date "+%Y-%m-%d %H:%M:%S")"

echo "File index:"
find * -type f | sort
echo
echo

find * -type f | sort | while read -r file; do
    echo "File: $file"
    echo "----------------------------------------"
    cat "$file"
    echo "<EOF>"
    echo
done