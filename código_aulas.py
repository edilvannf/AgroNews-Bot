import requests
from bs4 import BeautifulSoup
import csv

with open('noticias_agronegocio.csv', 'w', newline='', encoding='utf-8') as csvfile:
    escritor = csv.writer(csvfile)
    escritor.writerow(['Fonte', 'Título', 'Link'])

    pagina = requests.get('https://globorural.globo.com/ultimas-noticias/')
    canalrural = requests.get('https://www.canalrural.com.br/ultimas-noticias/')
    agrolink = requests.get('https://www.agrolink.com.br/noticias/')
    dados_pagina = BeautifulSoup(pagina.text, 'html.parser')
    dados_canalrural = BeautifulSoup(canalrural.text, 'html.parser')
    dados_agrolink = BeautifulSoup(agrolink.text, 'html.parser')

    noticias_globorural = dados_pagina.find_all('div', class_='feed-post-body')
    noticias_canalrural = dados_canalrural.find_all('article')
    noticias_agrolink =  dados_agrolink.select('a.block-news-main-general-title')

    mensagem1 = '📰 *Últimas notícias do Globo Rural:*\n\n'
    mensagem2 = '📰 *Últimas notícias do Canal Rural:*\n\n'
    mensagem3 = '📰 *Últimas notícias do Agro Link:*\n\n'

    print(f'{mensagem1.upper()}')

    for div in noticias_globorural:
        h2 = div.find('h2', class_='feed-post-link gui-color-primary gui-color-hover')
        if h2:
            link_noticia = h2.find('a')
            if link_noticia:
                texto = link_noticia.text.strip()
                link = link_noticia['href']
                print(f'👉 *{texto}*\n🔗 {link}\n\n')
                escritor.writerow(['Globo Rural', texto, link])
    #oi edilvan

    print(f'{mensagem2.upper()}')

    for artigo in noticias_canalrural[:5]:
        link_noticia = artigo.find('a', href=True)
        if link_noticia and link_noticia.text.strip():
            texto = link_noticia.text.strip()
            link = link_noticia['href']
            print(f'👉 *{texto}*\n🔗 {link}\n\n')
            escritor.writerow(['Canal Rural', texto, link])

    print(f'{mensagem3.upper()}')

    for link_noticia in noticias_agrolink[:5]:
        texto = link_noticia.get_text(strip=True)
        link = link_noticia['href']
        if link.startswith('/'):
            link = f'https://www.agrolink.com.br{link}'
        print(f'👉 *{texto}*\n🔗 {link}\n\n')
        escritor.writerow(['AgroLink', texto, link])
