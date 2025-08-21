import pandas as pd
from sqlalchemy import create_engine
from dashboard import df_filtered

# ------------------
# 接続情報を設定
# ------------------
# ご自身のPostgreSQLの情報を入力してください
user = 'postgres'
password = 'takuma1815T!'
host = 'localhost'  # ローカルPCなら 'localhost'
port = '5432'
dbname = 'inagaki_test'

# --------------------------------
# DataFrameをPostgreSQLに書き出す
# --------------------------------
# df_finalは、整形済みのDataFrameを想定

# PostgreSQLへの接続文字列を作成
conn_string = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}"
engine = create_engine(conn_string)

# DataFrameを'job_offers'というテーブル名でデータベースに保存
# if_exists='replace'で、もしテーブルが既に存在したら上書き
df_filtered.to_sql('job_offers', con=engine, if_exists='replace', index=False)

print("DataFrameが正常にPostgreSQLに書き出されました。")