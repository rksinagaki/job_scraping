import pandas as pd
import os
from sqlalchemy import create_engine
from local_dashboard import df_filtered

# ------------------
# 接続情報を設定
# ------------------
user = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')
host = os.getenv('DB_HOST')
port = os.getenv('DB_PORT')
dbname = os.getenv('DB_NAME')

# --------------------------------
# DataFrameをPostgreSQLに書き出す
# --------------------------------
conn_string = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}"
engine = create_engine(conn_string)

df_filtered.to_sql('job_offers', con=engine, if_exists='replace', index=False)

print("DataFrameが正常にPostgreSQLに書き出されました。")