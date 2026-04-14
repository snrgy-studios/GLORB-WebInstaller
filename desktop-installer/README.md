# GLORB Desktop Installer

A standalone desktop application for flashing firmware to GLORB devices (ESP32-S3). Unlike the web installer, this app can recover devices stuck in a boot loop by erasing the flash before reinstalling firmware.

## Prerequisites

- Python 3.9+
- pip

## Setup

```bash
cd desktop-installer
python -m venv venv
source venv/bin/activate   # macOS/Linux
# venv\Scripts\activate    # Windows
pip install -r requirements.txt
```

## Run in development

```bash
python glorb_installer.py
```

## Build standalone executable

```bash
python build.py
```

Output goes to `dist/`. On macOS this produces a bundled app, on Windows a `.exe`.

### macOS DMG

After building, create a DMG for distribution:

```bash
hdiutil create -volname "GLORB Installer" \
  -srcfolder "dist/GLORB Installer" \
  -ov -format UDZO "dist/GLORB Installer.dmg"
```

### Code signing

**macOS:** Without signing, users must right-click > Open to bypass Gatekeeper. For production, sign with an Apple Developer certificate and notarize with `xcrun notarytool`.

**Windows:** Without signing, SmartScreen shows a warning. Users click "More info" > "Run anyway". For production, sign with an EV code signing certificate.

## Adding a new firmware version

When a new firmware release is added to the web installer:

1. Add the firmware binaries to `bin/` as usual
2. Update the `<select>` dropdown in `index.htm`
3. Add a matching entry to `FIRMWARE_OPTIONS` in `glorb_installer.py`

## Icons

Place app icons in `assets/`:
- `icon.icns` — macOS (can convert from PNG using `iconutil` or `sips`)
- `icon.ico` — Windows (can convert from PNG using ImageMagick or an online tool)
