#!/usr/bin/env python3
"""
Script to rename files containing VAM/vam to SST/sst
Preserves case: VAM -> SST, vam -> sst, Vam -> Sst
"""
import os
import re
from pathlib import Path

def rename_vam_to_sst(root_dir):
    """Rename all files containing VAM/vam to SST/sst"""
    renamed_count = 0
    errors = []
    
    # Walk through all files
    for root, dirs, files in os.walk(root_dir):
        # Skip certain directories
        skip_dirs = ['.git', '__pycache__', 'build', 'cmake-build-debug-mingw', 'extern']
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        
        for filename in files:
            # Check if filename contains VAM or vam (case-insensitive)
            if 'vam' in filename.lower():
                old_path = os.path.join(root, filename)
                
                # Replace VAM/vam with SST/sst, preserving case
                new_filename = re.sub(r'VAM', 'SST', filename)
                new_filename = re.sub(r'vam', 'sst', new_filename)
                new_filename = re.sub(r'Vam', 'Sst', new_filename)
                
                # Only rename if the name actually changed
                if new_filename != filename:
                    new_path = os.path.join(root, new_filename)
                    
                    try:
                        # Check if target already exists
                        if os.path.exists(new_path):
                            errors.append(f"SKIP: {old_path} -> {new_path} (target exists)")
                            continue
                        
                        os.rename(old_path, new_path)
                        print(f"Renamed: {filename} -> {new_filename}")
                        renamed_count += 1
                    except Exception as e:
                        errors.append(f"ERROR: {old_path} -> {new_path}: {str(e)}")
    
    print(f"\nTotal files renamed: {renamed_count}")
    if errors:
        print(f"\nErrors/Skips ({len(errors)}):")
        for error in errors:
            print(f"  {error}")
    
    return renamed_count, errors

if __name__ == "__main__":
    # Start from VAMcore directory
    root = Path(__file__).parent
    print(f"Renaming files in: {root}")
    print("=" * 60)
    rename_vam_to_sst(root)

