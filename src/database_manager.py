import pandas as pd
from sqlalchemy import create_engine
from dashboard import df_filtered

# ------------------
# 接続情報を設定
# ------------------
user = 'postgres'
password = 'takuma1815T!'
host = 'localhost'
port = '5432'
dbname = 'inagaki_test'

# --------------------------------
# DataFrameをPostgreSQLに書き出す
# --------------------------------
conn_string = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}"
engine = create_engine(conn_string)

df_filtered.to_sql('job_offers', con=engine, if_exists='replace', index=False)

print("DataFrameが正常にPostgreSQLに書き出されました。")