# Building Standalone Executables

This project can be built into standalone executables for macOS, Windows, and Linux using PyInstaller.

## Local Build

### Prerequisites

- Python 3.11+
- pip

### Build Steps

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   pip install pyinstaller
   ```

2. Run the build script:

   ```bash
   python build.py
   ```

   Or manually:

   ```bash
   pyinstaller build.spec --clean --noconfirm
   ```

3. The executable will be in the `dist/` directory:
   - **macOS/Linux**: `dist/lg-remote-api`
   - **Windows**: `dist/lg-remote-api.exe`

## Automated Builds (GitHub Actions)

Binaries are automatically built for all three platforms on:
- Push to `init` or `main` branches
- Tagged releases (e.g., `v1.0.0`)
- Manual workflow dispatch

### Downloading Builds

1. Go to the **Actions** tab in GitHub
2. Select a completed workflow run
3. Download artifacts from the **Artifacts** section

### Release Builds

When you create a tag (e.g., `v1.0.0`), the workflow will:
- Build binaries for all platforms
- Create a GitHub Release
- Attach binaries to the release

## Usage

After building, run the executable:

```bash
# macOS/Linux
./dist/lg-remote-api

# Windows
dist\lg-remote-api.exe
```

The API will start on `http://localhost:8000`

### Environment Variables

You can set environment variables before running:

```bash
# macOS/Linux
export TV_IP=192.168.1.100
export TV_MAC=00-11-22-33-44-55
./dist/lg-remote-api

# Windows
set TV_IP=192.168.1.100
set TV_MAC=00-11-22-33-44-55
dist\lg-remote-api.exe
```

Or create a `.env` file in the same directory as the executable (if supported).

## Notes

- The executable includes all dependencies - no Python installation needed
- First run may be slower due to extraction
- `store.json` (WebOS auth) should be in the same directory as the executable
- File size: ~50-100 MB (includes Python runtime and dependencies)
