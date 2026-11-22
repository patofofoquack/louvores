#!/usr/bin/env python3
"""Gera TXT de conferência a partir do catálogo usado pelo aplicativo.
Não busca dados externos e não modifica catalogo.json.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
source = ROOT / 'catalogo.json'
dest = ROOT / 'catalogo-referencia.txt'
data = json.loads(source.read_text(encoding='utf-8'))
songs = data.get('songs', [])
if not isinstance(songs, list) or not songs:
    raise SystemExit('Catálogo sem músicas; nenhum TXT foi criado.')

def cell(s):
    return str(s if s is not None else '').replace('\t', ' ').replace('\r', ' ').replace('\n', ' ').strip()

lines = ['# Referência gerada automaticamente a partir de catalogo.json',
         '# A chave do aplicativo é a chave explícita do JSON ou c + posição (começando em 0).',
         'chave_aplicativo\tcategoria\tnumero\tnome_original\ttom\treferencia_original']
for i, song in enumerate(songs):
    if not isinstance(song, dict):
        raise SystemExit(f'Música inválida na posição {i}')
    cat, number, name = cell(song.get('cat')), cell(song.get('id')), cell(song.get('name'))
    key = cell(song.get('key')) or f'c{i}'
    ref = f'{cat}|{number}|{name}'
    lines.append('\t'.join(map(cell,[key,cat,number,name,song.get('tom',''),ref])))
dest.write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(f'{len(songs)} músicas -> {dest}')
