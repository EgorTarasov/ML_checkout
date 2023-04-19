import pandas as pd


def update_table(url: str):
    df = pd.read_csv(url)
    df["ФИО"] = df["ФИО"].apply(lambda x: x.lower())
    # add new column with surname from fio
    df["Фамилия"] = df["ФИО"].apply(lambda x: x.split(" ")[0])
    return df
