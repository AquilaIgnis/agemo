#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$repo_root"

if [[ "$(uname -m)" != x86_64 ]]; then
    printf 'This build currently supports x86_64 Linux.\n' >&2
    exit 1
fi

build_dir="$repo_root/build/appimage"
appdir="$build_dir/Agemo.AppDir"
output_dir="$repo_root/dist"
mkdir -p "$build_dir" "$output_dir"

python -m PyInstaller \
    --noconfirm --clean --onedir --noupx \
    --name agemo \
    --paths "$repo_root/src" \
    --distpath "$appdir/usr/lib" \
    --workpath "$build_dir/pyinstaller" \
    --specpath "$build_dir" \
    --add-data "$repo_root/assets:assets" \
    --add-data "$repo_root/src/style.qss:." \
    "$repo_root/src/agemo.py"

# Keep the PyInstaller directory intact, including its relative symlinks.
mkdir -p "$appdir/usr/bin"
ln -sfn ../lib/agemo/agemo "$appdir/usr/bin/agemo"
install -m 755 packaging/appimage/AppRun "$appdir/AppRun"
install -m 644 packaging/appimage/agemo.desktop "$appdir/agemo.desktop"
install -m 644 assets/agemo.png "$appdir/agemo.png"
install -Dm 644 LICENSE "$appdir/usr/share/licenses/agemo/LICENSE"
ln -sfn agemo.png "$appdir/.DirIcon"
desktop-file-validate "$appdir/agemo.desktop"

appimagetool="$build_dir/appimagetool-x86_64.AppImage"
curl --fail --location --retry 3 \
    'https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-x86_64.AppImage' \
    --output "$appimagetool"
chmod +x "$appimagetool"

repository="${GITHUB_REPOSITORY:-acidburnmonkey/agemo}"
update_info="gh-releases-zsync|${repository%/*}|${repository#*/}|latest|Agemo-x86_64.AppImage.zsync"
app_version="$(python -c 'import pathlib, tomllib; print(tomllib.loads(pathlib.Path("pyproject.toml").read_text())["project"]["version"])')"

# appimagetool writes the zsync file in its working directory.
cd "$output_dir"
ARCH=x86_64 VERSION="$app_version" APPIMAGE_EXTRACT_AND_RUN=1 \
    "$appimagetool" --no-appstream --updateinformation "$update_info" \
    "$appdir" "$output_dir/Agemo-x86_64.AppImage"

test -s "$output_dir/Agemo-x86_64.AppImage"
test -s "$output_dir/Agemo-x86_64.AppImage.zsync"
