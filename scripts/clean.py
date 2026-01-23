"""
Clean script for the RegressionLab project.

This script removes all __pycache__ directories from the project,
which contain compiled Python bytecode files (.pyc).

Virtual environment directories (.venv, venv, env, virtualenv) are
automatically excluded to preserve installed packages' performance.

Usage:
    python scripts/clean.py

This is equivalent to 'make clean' in C projects - it removes
build artifacts without affecting source code.
"""

import os
import shutil
from pathlib import Path
from typing import List


def find_pycache_dirs(root_dir: Path) -> List[Path]:
    """
    Search for all __pycache__ directories recursively.
    
    Walks through the directory tree starting from root_dir and
    collects paths to all __pycache__ directories found, excluding
    those inside virtual environment directories.
    
    Args:
        root_dir: Root directory where search begins
        
    Returns:
        List of paths to found __pycache__ directories
        
    Note:
        __pycache__ directories are created by Python 3 to store
        compiled bytecode files (.pyc) for faster module loading.
        Virtual environments (.venv, venv, env, virtualenv) are
        excluded to preserve installed packages' performance.
    """
    # Common virtual environment directory names to exclude
    venv_names = {'.venv', 'venv', 'env', 'virtualenv', '.virtualenv'}
    
    pycache_dirs = []
    # Walk the directory tree
    for dirpath, dirnames, _ in os.walk(root_dir):
        # Skip virtual environment directories (modify dirnames in-place)
        dirnames[:] = [d for d in dirnames if d not in venv_names]
        
        if '__pycache__' in dirnames:
            pycache_path = Path(dirpath) / '__pycache__'
            pycache_dirs.append(pycache_path)
    return pycache_dirs


def remove_pycache_dirs(root_dir: Path = None) -> None:
    """
    Remove all found __pycache__ directories.
    
    This function searches for __pycache__ directories in the project
    and removes them along with their contents. Useful for cleaning
    up before version control commits or when troubleshooting import issues.
    
    Args:
        root_dir: Root directory to search. If None, uses project root
                  (parent directory of scripts/).
                  
    Example:
        >>> remove_pycache_dirs()  # Cleans entire project
        >>> remove_pycache_dirs(Path('/path/to/specific/dir'))  # Cleans specific directory
    """
    if root_dir is None:
        # Automatically determine project root (parent of scripts/)
        root_dir = Path(__file__).parent.parent
    
    print(f"Searching for __pycache__ directories in: {root_dir}")
    pycache_dirs = find_pycache_dirs(root_dir)
    
    # Early exit if nothing to clean
    if not pycache_dirs:
        print("No __pycache__ directories found")
        return
    
    # Report what was found
    print(f"\nFound {len(pycache_dirs)} __pycache__ directories:")
    for pycache_dir in pycache_dirs:
        print(f"  - {pycache_dir.relative_to(root_dir)}")
    
    # Remove each directory
    print("\nRemoving directories...")
    for pycache_dir in pycache_dirs:
        try:
            # shutil.rmtree removes directory and all its contents
            shutil.rmtree(pycache_dir)
            print(f" Removed: {pycache_dir.relative_to(root_dir)}")
        except Exception as e:
            # Report errors but continue with other directories
            print(f" Error removing {pycache_dir.relative_to(root_dir)}: {e}")
    
    print("\nCleanup completed!")


if __name__ == "__main__":
    remove_pycache_dirs()
