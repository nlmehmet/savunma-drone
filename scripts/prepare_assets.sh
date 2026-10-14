#!/usr/bin/env bash
# Copies the sample photo shipped with Ultralytics into the target billboard texture.
# (The photo is not committed to the repository: it is generated here.)
set -e
cd "$(dirname "$0")/.."
python3 - << 'PY'
import shutil
from ultralytics.utils import ASSETS

dest = 'models/target_billboard/materials/textures/target.jpg'
shutil.copy(ASSETS / 'bus.jpg', dest)
print(f'Texture ready: {dest}')
PY
