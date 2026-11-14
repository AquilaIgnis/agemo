"""Check update metadata and launch the packaged GUI without a display or FUSE."""

import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile

appimage = Path(sys.argv[1]).resolve()
zsync = Path(f"{appimage}.zsync")
header = zsync.read_bytes().split(b"\n\n", 1)[0].decode()
assert f"Filename: {appimage.name}" in header, header
assert f"SHA-1: {hashlib.sha1(appimage.read_bytes()).hexdigest()}" in header, header

repository = os.environ.get("GITHUB_REPOSITORY", "acidburnmonkey/agemo")
owner, name = repository.split("/")
expected = f"gh-releases-zsync|{owner}|{name}|latest|{appimage.name}.zsync"
actual = subprocess.check_output([str(appimage), "--appimage-updateinformation"], text=True)
assert actual.strip() == expected, actual

with tempfile.TemporaryDirectory(prefix="agemo-smoke-") as directory:
    # Hyprland is a host requirement; provide one monitor for this headless run.
    bin_dir = Path(directory) / "bin"
    bin_dir.mkdir()
    hyprctl = bin_dir / "hyprctl"
    hyprctl.write_text(
        '#!/bin/sh\n'
        'printf "%s" "${LD_LIBRARY_PATH-}" > "$AGEMO_SMOKE_LIBRARY_PATH"\n'
        'printf \'[{"name":"SMOKE-1"}]\\n\'\n'
    )
    hyprctl.chmod(0o755)
    host_library_path = Path(directory) / "host-library-path"
    env = os.environ.copy()
    env.update(
        APPIMAGE_EXTRACT_AND_RUN="1",
        QT_QPA_PLATFORM="offscreen",
        QT_STYLE_OVERRIDE="Fusion",
        XDG_DATA_HOME=directory,
        PATH=f"{bin_dir}{os.pathsep}{env.get('PATH', '')}",
        AGEMO_SMOKE_LIBRARY_PATH=str(host_library_path),
    )
    process = subprocess.Popen(
        [str(appimage)],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        start_new_session=True,
    )
    try:
        output, _ = process.communicate(timeout=15)
        raise RuntimeError(f"AppImage exited early ({process.returncode}):\n{output}")
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGTERM)
        output, _ = process.communicate(timeout=10)
        print(output)

    settings = Path(directory) / "agemo/src/agemo.json"
    assert settings.is_file(), "The packaged app did not create writable settings"
    assert json.loads(settings.read_text())["monitors"] == ["SMOKE-1"]
    assert host_library_path.read_text() == os.environ.get("LD_LIBRARY_PATH", "")
    assert "Traceback" not in output, output

print("AppImage startup and zsync metadata passed.")
