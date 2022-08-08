import pandas as pd

df = pd.read_csv("data/HIST_PAINEL_COVIDBR_13mai2021.csv", sep=";")
df_states = df[(~df["estado"].isna()) & (df["codmun"].isna())]
df_brasil = df[df["regiao"] == "Brasil"]
df_states.to_csv("data/df_states.csv")
df_brasil.to_csv("data/df_brasil.csv")