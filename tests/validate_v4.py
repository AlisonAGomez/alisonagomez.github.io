"""Valida arquivos, links, navegação e conteúdo da prévia V4 sem rede."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse, unquote
import re

ROOT=Path(__file__).resolve().parents[1]
class Parser(HTMLParser):
 def __init__(self):super().__init__();self.refs=[];self.idents=set();self.nav=[];self.text=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if 'id' in a:
   if a['id'] in self.idents:raise AssertionError(f'ID duplicado: {a["id"]}')
   self.idents.add(a['id'])
  for attr in ('href','src'):
   if a.get(attr):self.refs.append(a[attr])
 def handle_data(self,text):self.text.append(text)
files=list(ROOT.rglob('*.html'))
assert len(files)==11,(len(files),files)
errors=[]
for path in files:
 p=Parser();p.feed(path.read_text(encoding='utf-8'))
 for ref in p.refs:
  q=urlparse(ref)
  if q.scheme in ('https','http','mailto','tel','data'):continue
  if not q.path:
   if q.fragment and q.fragment not in p.idents:errors.append(f'{path.name}: fragmento inexistente {ref}')
   continue
  if q.path.startswith('/'):
   errors.append(f'{path.name}: referência absoluta {ref}')
   continue
  target=(path.parent/unquote(q.path)).resolve()
  if not target.is_relative_to(ROOT):errors.append(f'{path.name}: caminho fora do pacote {ref}')
  elif not target.exists():errors.append(f'{path.name}: não existe {ref}')
  elif q.fragment:
   tp=Parser();tp.feed(target.read_text(encoding='utf-8'))
   if q.fragment not in tp.idents:errors.append(f'{path.name}: ancora inexistente {ref}')
 assert '<html lang="pt-BR">' in path.read_text(encoding='utf-8')
 assert 'aria-label="Navegação principal"' in path.read_text(encoding='utf-8')
 assert 'Casos</a>' not in path.read_text(encoding='utf-8'),'Link de caso no menu'
 assert 'https://alisonagomez.github.io/cases/' not in path.read_text(encoding='utf-8'),'Case link não revisado'
 assert 'projeto.html?p=' not in path.read_text(encoding='utf-8'),'Link antigo da ficha'
 assert 'href="#projetos"' not in path.read_text(encoding='utf-8'),'Âncora antiga de projetos'
assert not errors, '\n'.join(errors)
base=(ROOT/'index.html').read_text(encoding='utf-8');assert 'Bem vindo ao' in base and 'meu portfolio' in base
assert 'EXPLORAR PROJETOS' not in base
cont=(ROOT/'contato.html').read_text(encoding='utf-8');assert '99905-1896' not in cont and 'tel:+5519999051896' not in cont
assert 'mailto:almeidaalison@hotmail.com' in cont
assert cont.count('ENVIAR EMAIL')==1
assert 'contact-line"><span>GITHUB' not in cont
for p in ['hard-skills','soft-skills','formacao','projetos','laboratorio','experiencia','contato']:
 assert (ROOT/f'{p}.html').exists()
for proj in ['sinalyx','pendrivao','nukkio']:
 content=(ROOT/f'projetos/{proj}.html').read_text(encoding='utf-8')
 assert content.count('class="detail-section"')>=4
print(f'PASS: {len(files)} páginas HTML; links internos e conteúdo verificados.')

# Regras de navegação da nova Home
assert base.count('href="https://github.com/AlisonAGomez"') == 1, 'GitHub duplicado na Home'
assert '<a class="btn btn-ghost" href="contato.html">' not in base, 'Contato duplicado na Home'
assert 'Conheça <span>meu trabalho.' not in base, 'Seção antiga repetitiva presente'
assert 'id="sobreTitle"' in base and 'id="motivoTitle"' in base and 'id="hobbiesTitle"' in base and 'id="futuroTitle"' in base
assert base.count('href="projetos.html"') == 2, 'Projeto deve aparecer no menu e apenas uma vez no final'
assert base.count('href="hard-skills.html"') == 2, 'Hard Skills deve aparecer no submenu e apenas uma vez no final'
assert base.count('href="soft-skills.html"') == 2, 'Soft Skills deve aparecer no submenu e apenas uma vez no final'

# Validação complementar do conteúdo pessoal de 15/11/2026.
from bs4 import BeautifulSoup
soup = BeautifulSoup(base, 'html.parser')
labels = [x.get_text(' ',strip=True) for x in soup.select('main .kicker')]
for label in ['00 / SOBRE MIM','01 / MINHA VOCAÇÃO NA ÁREA DE TI','02 / MINHA FORMA DE TRABALHAR','03 / FORA DO TRABALHO','04 / OBJETIVO']:
 assert label in labels,(label,labels)
assert len(soup.select('.personal-hobby-grid .hobby-panel'))==5
assert not soup.select('details.workflow-step')
assert len(soup.select('.workflow-step-static'))==3
assert 'Documentar o que descobri' in base
assert '2007' in base and '56 KBps' in base and 'Semp Toshiba' in base
assert 'Meu próprio livro' in base and 'Carros' in base
assert 'Minha vocação é a área' in base
assert 'Texto-base para sua revisão' not in base
for path in files:
 page = path.read_text('utf-8')
 assert 'Alison Guilherme de Almeida Gomez - 2026' in page, path
 assert 'AG<span>.</span> / PORTFOLIO' not in page, path
 assert 'Portfólio V4 · Prévia local · Sem publicação' not in page,path
print('PASS: seções 00–04, foto, três etapas fixas, cards de hobbies e rodapés.')
assert not soup.select('.system-panel')
assert not soup.select('.personal-ascii')
assert soup.select_one('.personal-portrait img')
for filename in ['index.html','projetos.html','experiencia.html','laboratorio.html','formacao.html','contato.html','hard-skills.html','soft-skills.html','projetos/sinalyx.html','projetos/pendrivao.html','projetos/nukkio.html']:
  page=(ROOT/filename).read_text('utf-8')
  assert 'class="brand-icon"' not in page,filename
  assert 'Ilustração para a prévia' not in page,filename
  assert 'As artes são ilustrativas' not in page,filename
  assert 'class="evidence-note"' not in page,filename
assert 'Sem notas ou porcentagens' not in (ROOT/'soft-skills.html').read_text('utf-8')
print('PASS: notas de protótipo removidas; telefone excluído e imagens de marca aplicadas.')
