from pathlib import Path
import hashlib, json, shutil, zipfile, sys

sys.stdout.reconfigure(encoding='utf-8')
ROOT = Path(__file__).resolve().parent
artifact = ROOT / 'dist/ManaMetal-Chess-Auto-1.7.10-1.0.1.jar'
digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
for name in ('build.json', 'engine-verification.json', 'client-verification.json'):
    report = json.loads((ROOT / 'build' / name).read_text('utf-8'))
    assert report['sha256'] == digest, 'Test current JAR before packaging: ' + name
    if name != 'build.json': assert report['status'] == 'PASS'
fixture = Path(report['fixture']).resolve()
assert fixture.is_relative_to((ROOT / 'build').resolve())
assert 'status=PASS' in (fixture / 'result.txt').read_text('utf-8')
with zipfile.ZipFile(artifact) as jar:
    assert jar.testzip() is None
    assert not any(n.startswith('project/') or 'test' in n.lower() for n in jar.namelist())
    assert json.loads(jar.read('mcmod.info'))[0]['modid'] == 'manametalchessauto'
    assert 'local/manametalchess/ChessCommand.class' not in jar.namelist()
bundle = artifact.with_name(artifact.stem + '-with-source.zip')
with zipfile.ZipFile(bundle, 'w', zipfile.ZIP_DEFLATED) as out:
    out.write(ROOT / 'LICENSE', 'LICENSE')
    out.write(ROOT / 'README.md', 'README.md')
    out.write(ROOT / 'LICENSE', 'source/LICENSE')
    out.write(ROOT / 'README.md', 'source/README.md')
    out.write(ROOT / '.gitignore', 'source/.gitignore')
    out.write(ROOT / '.gitattributes', 'source/.gitattributes')
    out.write(artifact, artifact.name)
    out.write(ROOT / '使用说明.md', '使用说明.md')
    for folder in ('src', 'tests', 'client-tests'):
        for p in sorted((ROOT / folder).rglob('*')):
            if p.is_file() and p.suffix in ('.java', '.py', '.lang', '.info'):
                out.write(p, 'source/' + p.relative_to(ROOT).as_posix())
    for name in ('build.py', 'package.py', '使用说明.md'):
        out.write(ROOT / name, 'source/' + name)
    for name in ('build.json', 'engine-verification.json', 'client-verification.json', 'engine-tests.txt', 'compile.log'):
        out.write(ROOT / 'build' / name, 'validation/' + name)
    out.write(fixture / 'result.txt', 'validation/client-result.txt')
shutil.copy2(ROOT / '使用说明.md', ROOT / 'dist/使用说明.md')
shutil.copy2(fixture / 'result.txt', ROOT / 'dist/测试结果.txt')
(ROOT / 'dist/SHA256SUMS.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n'
                                               for p in (artifact, bundle)), encoding='ascii')
print(bundle)
print('Verified release, source archive and checksums: PASS')
