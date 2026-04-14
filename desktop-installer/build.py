"""Build script for GLORB Desktop Installer.

Detects the current platform and runs PyInstaller with the appropriate
arguments to produce a standalone executable.

Usage:
    python build.py
"""

import os
import platform
import subprocess
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
APP_NAME = "GLORB Installer"
MAIN_SCRIPT = os.path.join(SCRIPT_DIR, "glorb_installer.py")
BIN_DIR = os.path.join(REPO_ROOT, "bin")
BANNER = os.path.join(REPO_ROOT, "banner.png")
ASSETS_DIR = os.path.join(SCRIPT_DIR, "assets")


def build():
    system = platform.system()
    sep = ":" if system != "Windows" else ";"

    # macOS .app bundles are directories, so use --onedir there.
    # Windows uses --onefile for a single .exe.
    onefile_flag = "--onedir" if system == "Darwin" else "--onefile"

    cmd = [
        sys.executable, "-m", "PyInstaller",
        onefile_flag,
        "--windowed",
        "--noconfirm",
        "--name", APP_NAME,
        f"--add-data={BIN_DIR}{sep}bin",
    ]

    # Include banner image if it exists
    if os.path.isfile(BANNER):
        cmd.append(f"--add-data={BANNER}{sep}assets")

    # Platform-specific icon
    if system == "Darwin":
        icon = os.path.join(ASSETS_DIR, "icon.icns")
        if os.path.isfile(icon):
            cmd.extend(["--icon", icon])
        cmd.extend(["--osx-bundle-identifier", "me.glorb.installer"])
    elif system == "Windows":
        icon = os.path.join(ASSETS_DIR, "icon.ico")
        if os.path.isfile(icon):
            cmd.extend(["--icon", icon])

    # Hidden imports that PyInstaller may miss
    cmd.extend([
        "--hidden-import", "esptool",
        "--hidden-import", "esptool.cmds",
        "--hidden-import", "esptool.targets",
        "--hidden-import", "esptool.targets.esp32s3",
        "--hidden-import", "serial.tools.list_ports",
    ])

    cmd.append(MAIN_SCRIPT)

    print(f"Building for {system}...")
    print(f"Command: {' '.join(cmd)}")
    subprocess.run(cmd, check=True, cwd=SCRIPT_DIR)

    dist_dir = os.path.join(SCRIPT_DIR, "dist")
    print(f"\nBuild complete! Output in: {dist_dir}")

    if system == "Darwin":
        print(f"  macOS app: {dist_dir}/{APP_NAME}")
        print("\nTo create a DMG for distribution:")
        print(f'  hdiutil create -volname "{APP_NAME}" -srcfolder "{dist_dir}/{APP_NAME}" '
              f'-ov -format UDZO "{dist_dir}/{APP_NAME}.dmg"')
    elif system == "Windows":
        print(f"  Windows exe: {dist_dir}\\{APP_NAME}.exe")


if __name__ == "__main__":
    build()
