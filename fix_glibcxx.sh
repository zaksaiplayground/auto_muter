#!/bin/bash

# Create a backup directory for your current libstdc++
mkdir -p ~/lib_backup

# Backup the current libstdc++
cp ~/miniconda3/envs/auto_muter/lib/libstdc++.so.6 ~/lib_backup/

# Find the system libstdc++
SYSTEM_LIBSTDCXX=$(find /usr/lib -name "libstdc++.so.6" | grep -v conda | head -1)

# If found, create a symbolic link
if [ -n "$SYSTEM_LIBSTDCXX" ]; then
    echo "Found system libstdc++ at $SYSTEM_LIBSTDCXX"
    ln -sf $SYSTEM_LIBSTDCXX ~/miniconda3/envs/auto_muter/lib/libstdc++.so.6
    echo "Created symbolic link to system libstdc++"
else
    echo "System libstdc++ not found"
fi

# Check if the issue is resolved
echo "Checking for GLIBCXX_3.4.32..."
strings ~/miniconda3/envs/auto_muter/lib/libstdc++.so.6 | grep GLIBCXX_3.4.32

echo "If GLIBCXX_3.4.32 is found above, the issue should be resolved."