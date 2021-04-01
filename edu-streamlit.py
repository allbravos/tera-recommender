import psycopg2
import random
import streamlit as st
# To make things easier later, we're also importing numpy and pandas for
# working with sample data.
import numpy as np
import pandas as pd

QUANTIDADE_DE_TEMAS = 25

# Set up a connection to the postgres server
conn_string = "host=179.188.16.131 port=5432 dbname=recommender user=recommender password=Tera2021"
conn = psycopg2.connect(conn_string)
print("Connected!")

# Create a cursor to connect in the database
cursor = conn.cursor()


# Define a classe de Usuario
class Usuario:
    id = 0
    id_perfil = 0
    id_preferencia_idioma = 0
    email = ''
    nome = ''

    def load(self, id, perfil, email, nome):
        self.id = int(id)
        self.id_perfil = int(perfil)
        self.email = email
        self.nome = nome

    def __str__(self):
        return self.nome

# Define a classe Artigo
class Artigo:
    id = 0
    id_tema = 0
    titulo = ''
    url = ''
    nps = 0

    def load(self, id_artigo, id_tema, titulo, url, nps=0):
        self.id = int(id_artigo)
        self.id_tema = int(id_tema)
        self.titulo = titulo
        self.url = url
        self.nps = int(nps)
        return self


# Funcao de consulta simples na base de dados
def select(schema, table, where=''):
    sql_command = "SELECT * FROM {}.{}".format(str(schema), str(table))
    if where != '':
        sql_command += ' WHERE ' + where

    sql_command += ';'

    data = pd.read_sql(sql_command, conn)
    return data


# Funcao de consulta customizada na base de dados
def query(sql):
    data = pd.read_sql(sql, conn)
    return data


# Funcao de escrita na base de dados
def insert(schema, table, columns, values):
    parameters = '%s'
    for i in range(1, len(values)):
        parameters += ', %s'

    sql = 'INSERT INTO {}.{} ({}) VALUES ({}) RETURNING ID;'.format(schema, table, columns, parameters)
    # INCLUIR UMA QUANTIDADE VARIAVEL DE PARAMETROS
    cursor.execute(sql, values)
    conn.commit()
    new_id = cursor.fetchone()[0]

    return new_id


# Funcao de update na base de dados
def update(schema, table, columns, where):
    # sql = 'UPDATE {}.{} SET {} WHERE {};'.format(schema, table, columns, where)
    sql = 'DELETE FROM feedbacks WHERE nps = 0;'
    cursor.execute('DELETE FROM feedbacks WHERE nps = 0;')
    conn.commit()

    return cursor.rowcount


def load_usuarios():
    df = select('public', 'usuarios')
    usuarios = list()
    for index, row in df.iterrows():
        usuario = Usuario()
        usuario.load(df['id'][index], df['id_perfil'][index], df['email'][index], df['nome'][index])
        usuarios.append(usuario)
    return usuarios


def recommend_artigo(usuario):
    # Verifica qual o ultimo tema que o usuario deu feedback
    sql = 'SELECT max(id_tema) as ultimo_tema FROM public.feedbacks WHERE id_usuario = {};'.format(usuario.id)
    df_ultimo_tema = query(sql)

    id_tema = 1
    if df_ultimo_tema['ultimo_tema'][0] != None:
        id_tema = int(df_ultimo_tema['ultimo_tema'][0]) + 1

    # Consulta os artigos que ainda não receberam feedback do perfil selecionado
    sql = 'SELECT a.id, a.id_tema, a.titulo, a.url, f.nps FROM public.artigos as a ' \
    'LEFT JOIN public.feedbacks as f on a.id = f.id_artigo AND f.id_perfil = {}' \
    'WHERE a.id_tema = {} AND f.nps IS NULL;'.format(usuario.id_perfil, id_tema)
    df = query(sql)

    artigo = Artigo()
    # Se ha artigos ainda nao avaliados, escolhe um deles
    if len(df) > 0:
        artigos = list()
        for index, row in df.iterrows():
            artigo = Artigo().load(row['id'], row['id_tema'], row['titulo'], row['url'])
            artigos.append(artigo)

        # Escolhe um artigo randomico para recomendar
        index_artigo_escolhido = random.randint(0, len(artigos) - 1)
        artigo = artigos[index_artigo_escolhido]
    else:
        # Seleciona o artigo com maior Score local
        sql = 'SELECT a.id, a.id_tema, a.titulo, a.url, ac.score FROM public.artigos as a ' \
              'INNER JOIN public.artigos_score as ac on a.id = ac.id_artigo AND ac.id_perfil = {} ' \
              'WHERE id_tema = {} ORDER BY ac.score DESC;'.format(usuario.id_perfil, id_tema)
        df = query(sql)

        # Se não tem artigos para este tema, retorna vazio
        if len(df) == 0:
            return None

        artigo = Artigo().load(df['id'][0], df['id_tema'][0], df['titulo'][0], df['url'][0])

    return artigo


def save_feedback(usuario, artigo, nps):

    values = [usuario.id, usuario.id_perfil, usuario.id_preferencia_idioma, artigo.id, artigo.id_tema, nps]
    insert('public', 'feedbacks', 'id_usuario, id_perfil, id_preferencia_idioma, id_artigo, id_tema, nps', values)

    # Atualiza o score local (por perfil) do artigo
    sql = 'SELECT avg(f.nps) as score FROM public.artigos as a ' \
          'LEFT JOIN public.feedbacks as f on a.id = f.id_artigo AND f.id_perfil = {}' \
          'WHERE a.id = {} AND f.nps IS NOT NULL;'.format(usuario.id_perfil, artigo.id)
    df_average = query(sql)
    score = int(df_average['score'][0])
    values = [artigo.id, usuario.id_perfil, score]

    # Verifica se o artigo ja possuia um score para o perfil
    df_score = select('public', 'artigos_score', 'id_artigo = {} AND id_perfil = {}'.
                      format(artigo.id, usuario.id_perfil))

    if len(df_score) == 0:
        insert('public', 'artigos_score', 'id_artigo, id_perfil,score', values)
    else:
        update('public', 'artigos_score', 'score = ' + str(score), 'id_artigo = {} AND id_perfil = {}'.
               format(artigo.id, usuario.id_perfil))


# INICIA O FLUXO PRINCIPAL DA APLICAÇÃO STREAMLIT

st.title("I'm Edu")
st.header('Educational Recommender and Guru')
st.text('Recomendação de Trilha para Data Science')

# Monta o combo com as opções de usuários
st.subheader('Quem é você?')
usuarios = load_usuarios()
usuario_selecionado = st.selectbox('', usuarios)

# Recomenda o próximo artigo para o usuário
artigo = recommend_artigo(usuario_selecionado)
st.subheader('Sua próxima recomendação de artigo é:')
st.text(artigo.titulo)
st.write('[{}]({})'.format(artigo.url, artigo.url))

st.subheader('Deixe seu Feedback sobre o artigo:')
nps = st.slider('Qual a chance de você recomendar esse artigo para um amigo interessado em Data Science?',
                min_value=0, max_value=10, value=5)

if nps:
    if st.button('Enviar Feedback'):
        save_feedback(usuario_selecionado, artigo, nps)
