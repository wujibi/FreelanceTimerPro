#!/usr/bin/env python3
"""
Time Tracker App Launcher
Cross-platform launcher with enhanced error handling
"""

import sys
import os
import subprocess
from pathlib import Path


def print_banner():
    """Print application banner"""
    print("=" * 50)
    print("          Time Tracker App Launcher")
    print("=" * 50)
    print()


def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 6):
        print(f"ERROR: Python 3.6+ required. Current version: {sys.version}")
        return False
    print(f"✓ Python version: {sys.version.split()[0]}")
    return True


def check_requirements():
    """Check if all required packages are installed"""
    required_modules = ['tkinter', 'sqlite3', 'json', 'datetime', 'pathlib']
    missing_modules = []

    for module in required_modules:
        try:
            __import__(module)
            print(f"✓ {module}")
        except ImportError:
            missing_modules.append(module)
            print(f"✗ {module} (missing)")

    if missing_modules:
        print(f"\nERROR: Missing required modules: {', '.join(missing_modules)}")
        return False

    return True


def check_project_files():
    """Check if required project files exist"""
    script_dir = Path(__file__).parent
    required_files = ['main.py']
    missing_files = []

    for file in required_files:
        file_path = script_dir / file
        if file_path.exists():
            print(f"✓ {file}")
        else:
            missing_files.append(file)
            print(f"✗ {file} (missing)")

    if missing_files:
        print(f"\nERROR: Missing required files: {', '.join(missing_files)}")
        return False

    return True


def create_data_directory():
    """Create data directory if it doesn't exist"""
    data_dir = Path("data")
    try:
        data_dir.mkdir(exist_ok=True)
        print(f"✓ Data directory: {data_dir.absolute()}")
        return True
    except Exception as e:
        print(f"✗ Error creating data directory: {e}")
        return False


def launch_app():
    """Launch the main application"""
    print_banner()

    print("Performing pre-flight checks...")
    print()

    # Check Python version
    if not check_python_version():
        return False

    # Check required modules
    if not check_requirements():
        return False

    # Check project files
    if not check_project_files():
        return False

    # Create data directory
    if not create_data_directory():
        return False

    print("\n" + "=" * 50)
    print("All checks passed! Launching Time Tracker App...")
    print("=" * 50)
    print()
    print(f"Database location: {os.path.abspath('data/time_tracker.db')}")

    try:
        # Launch main application
        from main import main
        main()
        return True
    except ImportError as e:
        print(f"ERROR: Could not import main module: {e}")
        return False
    except Exception as e:
        print(f"ERROR: Application error: {e}")
        return False


def main():
    """Main launcher function"""
    try:
        success = launch_app()
        if not success:
            input("\nPress Enter to exit...")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nApplication interrupted by user")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        input("Press Enter to exit...")
        sys.exit(1)


if __name__ == "__main__":
    main()
