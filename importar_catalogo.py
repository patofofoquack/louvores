#!/usr/bin/env python3
"""Importa metadados públicos (categoria, número e nome) das coleções do Louvando.
Não baixa nem reproduz letras/cifras. Preserva o catálogo anterior em falhas.
"""
from pathlib import Path
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import requests, json, re, time

BASE='https://louvando.app/colecoes/'
COLLECTIONS=[
 ('Coletânea','58906058-58c6-4a85-a642-9db518a52891',795),
 ('Avulsos','f0b80fec-07b2-4482-b23e-6312060670c6',480),
 ('CIA','014259b3-1584-487a-bb73-631c71fe5329',255),
]
session=requests.Session()
retry=Retry(total=4,backoff_factor=1,status_forcelist=(429,500,502,503,504))
session.mount('https://',HTTPAdapter(max_retries=retry))
session.headers.update({'User-Agent':'LouvoresRepertorio/1.0 (catalog title metadata only)'})


def parse(html,category):
 soup=BeautifulSoup(html,'html.parser')
 table=soup.find('table')
 if not table: raise ValueError('Tabela de louvores não encontrada')
 result=[]
 for tr in table.select('tr'):
  cols=tr.find_all('td',recursive=False)
  if len(cols)<2:continue
  rawnum=cols[0].get_text(' ',strip=True)
  anchor=cols[1].find('a',href=re.compile('/louvores/'))
  if not anchor: continue
  title=anchor.get_text(' ',strip=True)
  if not title:continue
  number=re.search(r'\d+',rawnum)
  if category=='Avulsos': label='AVULSO' if not number else number.group().zfill(3)
  elif category=='CIA':label='CIA '+number.group().zfill(3) if number else 'CIA'
  else:label=number.group().zfill(3) if number else 'AVULSO'
  result.append({'id':label,'name':title,'cat':category,'key':'l:'+anchor['href'].rstrip('/').split('/')[-1]})
 return result


def fetch(category,ident,pages):
 songs=[]
 for page in range(1,pages+1):
  url=f'{BASE}{ident}?page={page}'
  r=session.get(url,timeout=30)
  r.raise_for_status()
  rows=parse(r.text,category)
  if not rows:raise RuntimeError(f'Página sem louvores: {url}')
  songs.extend(rows)
  print(category,page,len(rows),flush=True)
  time.sleep(0.16)
 return songs


def main():
 all_songs=[]
 for category,ident,expected in COLLECTIONS:
  pages=(expected+24)//25
  songs=fetch(category,ident,pages)
  if len(songs)!=expected:
   raise RuntimeError(f'{category}: esperados {expected}, encontrados {len(songs)}; não sobrescrevemos arquivo com dados incompletos')
  all_songs.extend(songs)
 if len(all_songs)!=1530:raise RuntimeError('Total inesperado')
 out=Path(__file__).resolve().parents[1]/'catalogo.json'
 out.write_text(json.dumps({'source':'Louvando','songs':all_songs,'status':'completo'},ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
 print(f'Catálogo completo escrito: {len(all_songs)} louvores')

if __name__=='__main__':main()
