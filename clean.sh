# delete all the __pycache__ folders in the current and the nested folders
find . -type d -name "__pycache__" -exec rm -rf {} \;