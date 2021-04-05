from bs4 import BeautifulSoup
from bs4.element import Comment
import pandas as pd
import requests


# Processa o sitemap principal, para encontrar os sitemaps internos (organizados po dia)
sitemap_url = 'https://towardsdatascience.com/sitemap/sitemap.xml'
xml = requests.get(sitemap_url).content
soup = BeautifulSoup(xml, "xml")
sitemaps = soup.find_all('sitemap')

# Cria as listas que serão as colunas do dataframe
c_titulo = list()
c_url = list()
c_data = list()
c_ano = list()
c_mes = list()
c_dia = list()
c_dia_semana = list()
c_ultima_atualizacao = list()
c_frequencia_atualizacao = list()
c_prioridade = list()

for sitemap_inter in sitemaps:

    # Processa as features de 1 sitemap interno (url, ano, data)
    loc = sitemap_inter.find('loc').text
    xml_data = requests.get(loc).content
    soup = BeautifulSoup(xml_data, "xml")

    # Extrai a data e o tipo de sitemap (posts ou tags)
    sitemap_url_split = loc.split('/')
    sitemap_url_end = sitemap_url_split[-1]
    if not sitemap_url_end.startswith('posts'):
        continue

    # Obtem a data do sitemap, a partir da url
    date = sitemap_url_end.replace('posts-', '').replace('.xml', '')
    sitemap_date_split = date.split('-')
    year = sitemap_date_split[0]
    month = sitemap_date_split[1]
    day = sitemap_date_split[2]
    day_of_week = pd.Timestamp(date).day_name()

    print('Processando o sitemap: ' + sitemap_url_end)

    # Processa as urls de 1 sitemap interno, contendo o cabaçalho dos artigos
    urlset = soup.find_all('url')
    for item in urlset:

        loc = item.find('loc').text
        print('...Extraindo dados do artigo: ' + loc)

        # Extrai o titulo da url
        loc_end = loc.split('/')[-1]
        loc_split = loc_end.split('-')
        title = ''
        for i in range(len(loc_split) - 1):
            title += ' ' + loc_split[i]
        title = title.strip()

        c_titulo.append(title)
        c_url.append(loc)
        c_data.append(date)
        c_ano.append(year)
        c_mes.append(month)
        c_dia.append(day)
        c_dia_semana.append(day_of_week)
        c_ultima_atualizacao.append(item.find('lastmod').text)
        c_frequencia_atualizacao.append(item.find('changefreq').text)
        c_prioridade.append(item.find('priority').text)

# Cria o dataframe para salvar em .csv
dict = {
    'titulo': c_titulo,
    'url': c_url,
    'data': c_data,
    'ano': c_ano,
    'mes': c_mes,
    'dia': c_dia,
    'diaSemana': c_dia_semana,
    'ultimaAtualizacao': c_ultima_atualizacao,
    'frequenciaAtualizacao': c_frequencia_atualizacao,
    'prioridade': c_prioridade}

df = pd.DataFrame(dict)
df.to_csv('C:/temp/tera/towardsdatascience.csv', encoding='UTF-8', index=False)
