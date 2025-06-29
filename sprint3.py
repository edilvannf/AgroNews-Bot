import os
import requests
from bs4 import BeautifulSoup
import csv
import re

arquivo_csv = 'noticias_agronews.csv'

def salvar_csv(fonte, titulo, link):
    precisa_cabecalho = not os.path.exists(arquivo_csv) or os.stat(arquivo_csv).st_size == 0
    with open(arquivo_csv, 'a', newline='', encoding='utf-8') as csvfile:
        escritor = csv.writer(csvfile, delimiter=';')
        if precisa_cabecalho:
            escritor.writerow(['Fonte', 'Título', 'Link'])
        escritor.writerow([fonte, titulo, link])

pagina = requests.get('https://globorural.globo.com/ultimas-noticias/')
canalrural = requests.get('https://www.canalrural.com.br/ultimas-noticias/')
agrolink = requests.get('https://www.agrolink.com.br/noticias/')

dados_pagina = BeautifulSoup(pagina.text, 'html.parser')
dados_canalrural = BeautifulSoup(canalrural.text, 'html.parser')
dados_agrolink = BeautifulSoup(agrolink.text, 'html.parser')

noticias_globorural = dados_pagina.find_all('div', class_='feed-post-body')
noticias_canalrural = dados_canalrural.find_all('article')
noticias_agrolink = dados_agrolink.select('a.block-news-main-general-title')

mensagem1 = '📰 *Últimas notícias do Globo Rural:*\n\n'
mensagem2 = '📰 *Últimas notícias do Canal Rural:*\n\n'
mensagem3 = '📰 *Últimas notícias do Agro Link:*\n\n'

def globo_rural():
    print(f'{mensagem1.upper()}')
    for div in noticias_globorural:
        h2 = div.find('h2', class_='feed-post-link gui-color-primary gui-color-hover')
        if h2:
            link_noticia = h2.find('a')
            if link_noticia:
                texto = re.sub(r'\s+', ' ', link_noticia.text).strip()
                link = link_noticia['href']
                print(f'👉 *{texto}*\n🔗 {link}\n\n')
                salvar_csv('Globo Rural', texto, link)
#oi edilvan

def canalrural():
    print(f'{mensagem2.upper()}')
    for artigo in noticias_canalrural[:5]:
        link_noticia = artigo.find('a', href=True)
        if link_noticia and link_noticia.text.strip():
            texto = re.sub(r'\s+', ' ', link_noticia.text).strip()
            link = link_noticia['href']
            print(f'👉 *{texto}*\n🔗 {link}\n\n')
            salvar_csv('Canal Rural', texto, link)

def agrolink():
    print(f'{mensagem3.upper()}')
    for link_noticia in noticias_agrolink[:5]:
        texto = re.sub(r'\s+', ' ', link_noticia.get_text(strip=True)).strip()
        link = link_noticia['href']
        if link.startswith('/'):
            link = f'https://www.agrolink.com.br{link}'
        print(f'👉 *{texto}*\n🔗 {link}\n\n')
        salvar_csv('AgroLink', texto, link)

def sites_noticias():
    while True:
        print('''
1 - Globo Rural
2 - Canal Rural
3 - Agro Link
4 - Voltar ao menu principal
            ''')
        escolha = input('Escolha uma opção: ')
        if escolha == '1':
            globo_rural()
        elif escolha == '2':
            canalrural()
        elif escolha == '3':
            agrolink()
        elif escolha == '4':
            break

def sobre():
    print(f'''🤖 Bot criado por Edilvan, Ketlhin e Ana Paula. Este projeto foi desenvolvido como parte da disciplina
Projeto Integrador à Programação, no curso de Big Data no Agronegócio da UNICENTRO, com o objetivo de aplicar conhecimentos
de web scraping, automação e manipulação dedados com Python.\n\nFontes: Globo Rural, Canal Rural e AgroLink.''')

def ajuda():
    print('''
ℹ️ *Guia de Ajuda do Bot de Notícias Agrícolas*
git
Este bot foi desenvolvido para te manter atualizado com as últimas notícias do agronegócio, coletando informações dos principais portais.

*Funcionalidades Principais:*
1. *Sites de Notícias:* Selecione esta opção para escolher entre os sites disponíveis (Globo Rural, Canal Rural, AgroLink) e ver as notícias mais recentes. 
2. *Sobre:* Conheça mais sobre os criadores e o propósito deste projeto.
3. *Sair:* Encerra a sessão do bot
    ''')


def menu():
    while True:
        print(f'''\nAgro News Bot
1 - Sites de Notícias
2 - Ajuda
3 - Sobre
4 - Sair''')
        opcao = input('Escolha uma opção: ')
        if opcao == '1':
            sites_noticias()
        elif opcao == '2':
            ajuda()
        elif opcao == '3':
            sobre()
        elif opcao == '4':
            print('Programa finalizado com sucesso!')
            break

menu()
