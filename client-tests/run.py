from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
import argparse

sys.stdout.reconfigure(encoding='utf-8')
parser = argparse.ArgumentParser()
parser.add_argument('--controls', action='store_true', help='Verify key controls and one complete client/server turn')
options_args = parser.parse_args()
ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = Path(os.environ.get('CHESS_WORKSPACE', os.environ.get('FOXFOX_WORKSPACE', ROOT.parent))).resolve()
artifact = ROOT / 'dist/ManaMetal-Chess-Auto-1.7.10-1.0.1.jar'
if not artifact.is_file():
    raise SystemExit('Run build.py first')
fixture = Path(tempfile.mkdtemp(prefix='client-', dir=ROOT / 'build'))
game = fixture / 'client'
mods = game / 'mods'
mods.mkdir(parents=True)
for name in ('config', 'falsepattern'):
    source = WORKSPACE / 'FoxFoxAccessories/test-server' / name
    if source.exists():
        shutil.copytree(source, game / name, dirs_exist_ok=True)
(game / 'config').mkdir(exist_ok=True)
(game / 'config/splash.properties').write_text('enabled=false\n', encoding='ascii')
sound = ['master', 'music', 'record', 'weather', 'block', 'hostile', 'neutral', 'player', 'ambient']
options = 'fullscreen:false\nlang:zh_CN\nguiScale:2\npauseOnLostFocus:false\noverrideWidth:1280\noverrideHeight:720\n'
options += ''.join('soundCategory_' + c + ':0.0\n' for c in sound)
(game / 'options.txt').write_text(options, encoding='ascii')
assert all('soundCategory_' + c + ':0.0' in (game / 'options.txt').read_text() for c in sound)
for pattern in ['lwjgl3ify-*.jar', '+unimixins-*.jar', 'gtnhlib-*.jar', '*CodeChickenCore*.jar',
                'NotEnoughItems-*.jar', 'manametalmod-8.0.7.jar', '*Muya*.jar']:
    matches = list((WORKSPACE / '.minecraft/mods').glob(pattern))
    if len(matches) != 1:
        raise SystemExit('Expected one dependency for ' + pattern)
    path = matches[0]
    shutil.copy2(path, mods / path.name.split(']', 1)[-1])
(mods / '1.7.10').mkdir()
for path in (WORKSPACE / '.minecraft/mods/1.7.10').glob('*.jar'):
    shutil.copy2(path, mods / '1.7.10' / path.name)
shutil.copy2(artifact, mods / artifact.name)
classes = fixture / 'probe-classes'
classes.mkdir()
deps = [WORKSPACE / 'FoxFoxAccessories/tools/forge-1.7.10-srg.jar', artifact,
        *sorted(mods.glob('*.jar')), *sorted((WORKSPACE / '.minecraft/libraries').rglob('*.jar'))]
subprocess.run(['javac', '--release', '8', '-Xlint:-options', '-encoding', 'UTF-8', '-cp',
                os.pathsep.join(map(str, deps)), '-d', str(classes),
                str(ROOT / 'client-tests/ChessRuntimeCheck.java')], check=True)
with zipfile.ZipFile(mods / 'chess-test-probe.jar', 'w', zipfile.ZIP_DEFLATED) as jar:
    for path in sorted(classes.rglob('*.class')):
        jar.write(path, path.relative_to(classes).as_posix())
profile_dir = WORKSPACE / 'fcwqmmmserver/deployment/java21'
profile = json.loads((profile_dir / 'prepared-client-version.json').read_text('utf-8-sig'))
cp = os.pathsep.join(json.loads((profile_dir / 'client-classpath.json').read_text('utf-8-sig')))
natives = game / 'natives'
natives.mkdir()
args = ['-Xms256m', '-Xmx2G', '-XX:+UseG1GC', '-Dchessauto.test.root=' + str(fixture)]
if options_args.controls:
    args.append('-Dchessauto.test.controls=true')
args += [a.replace('${classpath}', cp).replace('${natives_directory}', str(natives))
         for a in profile['arguments']['jvm'] if isinstance(a, str)]
args += [profile['mainClass'], '--username', 'ChessTest', '--version', profile['id'],
         '--gameDir', str(game), '--assetsDir', str(WORKSPACE / '.minecraft/assets'), '--assetIndex', '1.7.10',
         '--uuid', '00000000000000000000000000000007', '--accessToken', '0', '--userProperties', '{}',
         '--userType', 'legacy', '--width', '1280', '--height', '720',
         '--tweakClass', 'cpw.mods.fml.common.launcher.FMLTweaker']
argfile = fixture / 'client.args'
argfile.write_text('\n'.join('"' + a.replace('\\', '\\\\').replace('"', '\\"') + '"' for a in args), encoding='utf-8')
report = fixture / 'result.txt'
report.write_text('RUNNING\n', encoding='utf-8')
with (fixture / 'console.log').open('w', encoding='utf-8') as log:
    process = subprocess.Popen(['java', '@' + str(argfile)], cwd=game, stdout=log, stderr=subprocess.STDOUT,
                               creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
    print('Isolated client:', fixture, 'PID', process.pid, flush=True)
    try:
        code = process.wait(timeout=900)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()
        raise SystemExit('Client timeout: ' + str(fixture / 'console.log'))
result = report.read_text('utf-8')
print(result, flush=True)
if code != 0 or 'status=PASS' not in result:
    raise SystemExit('Client verification failed: ' + str(fixture / 'console.log'))
record = {'status': 'PASS', 'fixture': str(fixture), 'manametal': '8.0.7', 'standalone': True,
          'scope': 'key controls and one complete turn' if options_args.controls else 'key controls and full game',
          'artifact': artifact.name, 'sha256': hashlib.sha256(artifact.read_bytes()).hexdigest(),
          'transport': 'isolated integrated server and real block-use packets', 'sound': 'all categories checked at runtime',
          'manametal_sha256': hashlib.sha256((mods / 'manametalmod-8.0.7.jar').read_bytes()).hexdigest()}
(ROOT / 'build/client-verification.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
