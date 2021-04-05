import pandas as pd
import numpy as np


# Cria um subset do dataframe de acordo com o filtro enviado
def subset(text):
    subdf = df[df['titulo'].str.contains(text)]
    subdf.to_csv('C:/temp/tera/pandas/{}.csv'.format(text), encoding='UTF-8', index=False)
    print('Tamanho e head do subset: ' + text)
    print(subdf.shape[0])
    print(subdf.head())

    subdf['titulo'] = subdf['titulo'].replace({text: ''}, regex=True)
    subdf['titulo'] = subdf['titulo'].replace({'  ': ' '}, regex=True)
    print(subdf.head())

    return subdf


# FLUXO PRINCIPAL

df = pd.read_csv('C:/temp/tera/towardsdatascience.csv')

# Filtra os artigos com
data_science = subset('data science')
career = subset('career')
machine_learning = subset('machine learning')
statistics = subset('statistics')
math = subset('mathematics')
python = subset('python')
pandas = subset('pandas')
data_vizualization = subset('data visualization')

