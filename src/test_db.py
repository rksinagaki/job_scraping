import os
import sqlalchemy
from dotenv import load_dotenv

# .envファイルを読み込む
load_dotenv() 

# -----------------
# データベース接続情報を環境変数から取得
# -----------------
DB_HOST = os.environ.get("DB_HOST")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_PORT = 5432

# データベース接続文字列を作成
db_url = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# 接続と切断を管理するオブジェクトを初期化
engine = None
connection = None

try:
    # データベースエンジンを作成
    engine = sqlalchemy.create_engine(db_url)
    # 接続を確立
    connection = engine.connect()

    print("データベースに接続しました。")

    # データの読み書きなど）を記述します。
    # バージョン情報を取得
    result = connection.execute(sqlalchemy.text("SELECT version();")).scalar()
    print(f"PostgreSQLのバージョン情報: {result}")
    
except Exception as e:
    print("データベース操作中にエラーが発生しました。")
    print(f"エラー内容: {e}")

finally:
    # 接続とエンジンの解放
    if connection:
        connection.close()
        print("データベース接続を閉じました。")
    if engine:
        engine.dispose()
        print("データベースエンジンを解放しました。")