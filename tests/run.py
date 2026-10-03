from pathlib import Path
import subprocess, hashlib, json, sys
sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(__file__).resolve().parents[1]
jar = ROOT / 'dist/ManaMetal-Chess-Auto-1.7.10-1.0.1.jar'
classes = ROOT / 'build/engine-tests'
classes.mkdir(parents=True, exist_ok=True)
subprocess.run(['javac', '--release', '8', '-Xlint:-options', '-encoding', 'UTF-8', '-cp', str(jar),
                '-d', str(classes), str(ROOT / 'tests/EngineCheck.java')], check=True)
import os
result = subprocess.run(['java', '-Dfile.encoding=UTF-8', '-cp', os.pathsep.join([str(jar), str(classes)]), 'local.manametalchess.EngineCheck'],
                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding='utf-8', errors='replace')
(ROOT / 'build/engine-tests.txt').write_text(result.stdout, encoding='utf-8')
print(result.stdout)
result.check_returncode()
(ROOT / 'build/engine-verification.json').write_text(json.dumps({'status':'PASS', 'sha256':hashlib.sha256(jar.read_bytes()).hexdigest()}, indent=2), encoding='utf-8')
