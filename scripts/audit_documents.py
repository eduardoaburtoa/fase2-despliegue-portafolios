"""Audita estructura y duplicación Markdown sin modificar entregables binarios."""
import difflib
import json
import re
import subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
FILES = ['documentos/Manual_despliegue.md', 'documentos/Validacion_pruebas.md']
def metrics(a, b):
    blocks = difflib.SequenceMatcher(None, a.splitlines(), b.splitlines(), autojunk=False).get_matching_blocks()
    return {'manual_lines': len(a.splitlines()), 'validation_lines': len(b.splitlines()),
            'matching_lines_including_blanks': sum(x.size for x in blocks),
            'longest_identical_block': max(x.size for x in blocks)}
def main():
    current = [(ROOT / f).read_text() for f in FILES]
    before = [subprocess.check_output(['git', '-C', str(ROOT), 'show', '625aaf9:' + f], text=True) for f in FILES]
    result = {'baseline_commit': '625aaf9', 'method': 'SequenceMatcher, autojunk=False; incluye líneas vacías',
              'before': metrics(*before), 'after': metrics(*current)}
    assert result['after']['longest_identical_block'] <= 10
    for name, content in zip(FILES, current):
        assert len(re.findall(r'^## Referencias$', content, re.M)) == 1, name
        assert len(re.findall(r'^## Conclusiones$', content, re.M)) == 1, name
        assert 'ánimo' in content, name
    original_block = before[1].split('## Arquitectura e integración')[1].split('## Modelo y datos conservados')[0]
    result['architecture_block_preserved_in_manual'] = original_block in current[0]
    assert result['architecture_block_preserved_in_manual']
    result['structure_checks'] = 'passed'
    result['pagination'] = 'Secciones trazadas; páginas se recalculan en exportación final.'
    (ROOT / 'evidencias/deduplicacion.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))
if __name__ == '__main__':
    main()
