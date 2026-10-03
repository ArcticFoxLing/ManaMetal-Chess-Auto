from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import zipfile

sys.stdout.reconfigure(encoding='utf-8')
ROOT = Path(__file__).resolve().parent
WORKSPACE = Path(os.environ.get('CHESS_WORKSPACE', os.environ.get('FOXFOX_WORKSPACE', ROOT.parent))).resolve()
BUILD, DIST = ROOT / 'build', ROOT / 'dist'
BUILD.mkdir(exist_ok=True)
DIST.mkdir(exist_ok=True)
DEPS = [Path(os.environ.get('FORGE_SRG_JAR', WORKSPACE / 'FoxFoxAccessories/tools/forge-1.7.10-srg.jar')),
        Path(os.environ.get('MANAMETAL_JAR', WORKSPACE / '.minecraft/mods/manametalmod-8.0.7.jar')),
        WORKSPACE / '.minecraft/libraries/org/lwjgl/lwjgl/lwjgl/2.9.1/lwjgl-2.9.1.jar']
for path in DEPS:
    if not path.is_file():
        raise SystemExit('Missing build dependency: ' + str(path))
artifact = DIST / 'ManaMetal-Chess-Auto-1.7.10-1.0.1.jar'
with tempfile.TemporaryDirectory(prefix='compile-', dir=BUILD) as folder:
    classes = Path(folder)
    result = subprocess.run(['javac', '--release', '8', '-encoding', 'UTF-8', '-cp',
                             os.pathsep.join(map(str, DEPS)), '-d', str(classes),
                             *map(str, sorted((ROOT / 'src').rglob('*.java')))],
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            encoding='utf-8', errors='replace')
    (BUILD / 'compile.log').write_text(result.stdout, encoding='utf-8')
    print(result.stdout, end='')
    result.check_returncode()
    with zipfile.ZipFile(artifact, 'w', zipfile.ZIP_DEFLATED) as out:
        out.write(ROOT / 'LICENSE', 'META-INF/LICENSE')
        def put(name, data):
            info = zipfile.ZipInfo(name, (2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            out.writestr(info, data)
        put('META-INF/MANIFEST.MF', b'Manifest-Version: 1.0\r\nImplementation-Version: 1.0.1\r\n\r\n')
        for path in sorted(classes.rglob('*.class')):
            data = path.read_bytes()
            assert int.from_bytes(data[6:8], 'big') == 52
            put(path.relative_to(classes).as_posix(), data)
        for path in sorted((ROOT / 'src').rglob('*')):
            if path.is_file() and path.suffix != '.java':
                put(path.relative_to(ROOT / 'src').as_posix(), path.read_bytes())
report = {'artifact': artifact.name, 'sha256': hashlib.sha256(artifact.read_bytes()).hexdigest(),
          'minecraft': '1.7.10', 'manametal': '8.0.7', 'javaTarget': 8, 'clientOnly': True,
          'dependencies': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in DEPS}}
(BUILD / 'build.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
print(artifact)
