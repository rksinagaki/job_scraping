import subprocess
import os

print("========== データパイプラインを開始します ==========")
script_dir = os.path.dirname(__file__)
project_dir = os.path.dirname(script_dir)
os.chdir(project_dir)

# ----------------------------------------
# scraper.py を実行
# ----------------------------------------
try:
    subprocess.run(["python", "src/scraper.py"], check=True)
    print("... データ取得が完了しました。")
except subprocess.CalledProcessError as e:
    print(f"エラー: scraper.py の実行中に問題が発生しました。詳細: {e}")
    exit()

# ----------------------------------------
# dashboard.py を実行
# ----------------------------------------
try:
    subprocess.run(["streamlit", "run", "src/dashboard.py"])
except KeyboardInterrupt:
    print("\nダッシュボードの実行を停止しました。")

# ----------------------------------------
# database_manager.py を実行
# ----------------------------------------
try:
    subprocess.run(["python", "src/database_manager.py"], check=True)
    print("... PostgreSQLへの書き出しが完了しました。")
except subprocess.CalledProcessError as e:
    print(f"エラー: database_manager.py の実行中に問題が発生しました。詳細: {e}")
    exit()

print(f"========== データパイプラインが完了しました。) ==========")