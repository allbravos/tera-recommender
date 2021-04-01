import psycopg
import random
import streamlit as st
# To make things easier later, we're also importing numpy and pandas for
# working with sample data.
import numpy as np
import pandas as pd

QUANTIDADE_DE_TEMAS = 25

# Set up a connection to the postgres server
conn_string = "host=179.188.16.131 port=5432 dbname=recommender user=recommender password=Tera2021"
conn = psycopg.connect(conn_string)
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
        usuario.load(df['id'][0], df['id_perfil'][0], df['email'][0], df['nome'][0])
        usuarios.append(usuario)
    return usuarios


# INICIA O FLUXO PRINCIPAL DA APLICAÇÃO STREAMLIT

st.title("I'm Edu")
st.header('Educational Recommender and Guru')
st.text('Recomendação de Trilha para Data Science')

# Inicia o questionario de perfil no sidebar
st.subheader('Quem é você?')
usuarios = load_usuarios()
usuario_selecionado = st.selectbox('', usuarios)

# if len(df) == 0:
#
#     # Avalia o perfil do usuário
#     nome = st.sidebar.text_input('Nome', key='nome')
#     profissao = st.sidebar.radio('Qual desses perfis profissionais te descreve melhor?',
#                          ('1 - Pessoa desenvolvedora',
#                           '2 - Da Matemática ou Estatística',
#                           '3 - Sou de uma outra área',
#                           '4 - Não tenho profissão ainda'),
#                          key='profissao')
#     enviar_respostas = st.sidebar.button('Enviar Respostas', key='enviar_respostas')
#
# else:
#     usuario.load(df['id'][0], df['id_perfil'][0], df['email'][0], df['nome'][0])
#
#     df = pd.DataFrame({
#         'nome': usuario.nome,
#         'usuario': usuario
#     }, index={0})
#     option = st.sidebar.selectbox('Bem-vind@ ', df)
