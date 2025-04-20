import PyInstaller.__main__
from pathlib import Path
import zipfile
import toml
import argparse
import os
import random
import string

# Keep the original path resolution
HERE = Path(__file__).parent.parent.absolute()
path_to_main = str(HERE / "auto_muter" / "main.py")

def generate_key():
    """Generate a random encryption key for PyInstaller"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=16))

def install(use_key=False):
    """Original build function that Poetry calls with 'poetry run build'"""
    cmd = [
        path_to_main,
        '--noconfirm',
        '--clean',
        '--onefile',       # Crucial!
        '--windowed',
        '--noupx',
        '--name=AutoMuter',
        '--distpath=dist',  # Output only in dist/
        '--workpath=build', # Temp build files
        '--specpath=build', # Optional
    ]
    
    # Add encryption key to help bypass antivirus false positives
    if use_key:
        encryption_key = generate_key()
        cmd.append(f'--key={encryption_key}')
        print(f"Using encryption key: {encryption_key}")
    
    PyInstaller.__main__.run(cmd)
    print("Build completed successfully!")

def get_version():
    """Get the version from pyproject.toml"""
    pyproject = toml.load(HERE / "pyproject.toml")
    return pyproject["project"]["version"]

def package_exe():
    """Original package function that Poetry calls with 'poetry run package'"""
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Package AutoMuter executable.")
    parser.add_argument(
        '--path', 
        type=str, 
        default="G:/My Drive/AutoMuter/versions",  # Default Google Drive path
        help="The path to store the packaged .zip (default is Google Drive folder)"
    )
    parser.add_argument(
        '--use-key',
        action='store_true',
        help="Use encryption key with PyInstaller when building"
    )
    parser.add_argument(
        '--build',
        action='store_true',
        help="Build before packaging"
    )
    parser.add_argument(
        '--github',
        action='store_true',
        help="Set outputs for GitHub Actions"
    )
    
    args = parser.parse_args()
    
    # Build if requested
    if args.build:
        install(use_key=args.use_key)
    
    # Get the custom output path (default is Google Drive)
    output_dir = Path(args.path)

    # Default path to dist if not provided
    dist_dir = Path("dist")
    exe_path = dist_dir / "AutoMuter.exe"  # Default exe path

    version = get_version()
    output_dir.mkdir(parents=True, exist_ok=True)

    zip_path = output_dir / f"AutoMuter-v{version}.zip"

    if exe_path.exists():
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Store just the .exe inside zip, no folder
            zipf.write(exe_path, arcname="AutoMuter.exe")
        print(f"Packaged: {zip_path}")
        
        # For GitHub Actions, set the output variable for the file path
        if args.github and os.environ.get('GITHUB_ACTIONS') == 'true':
            with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
                f.write(f"package_path={zip_path}\n")
                f.write(f"version={version}\n")
    else:
        print(f"Executable not found at {exe_path}!")
        exit(1)
    
    return zip_path

# Add a new function that combines build and package for GitHub Actions
def build_and_package():
    """Combined function for GitHub Actions workflow"""
    install(use_key=True)
    return package_exe()