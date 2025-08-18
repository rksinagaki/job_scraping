import requests
import json
import pandas as pd
import os
import ast

# APIのURLとヘッダー情報
api_url = "https://www.green-japan.com/api/v2/user/search_job_offers"
headers = {
    'Content-Type': 'application/json',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
}

# 求人情報リスト
all_job_offers = []

# 取得条件（複数タグ）
job_tag_ids = [60, 61, 62]

# ページネーション（offset）で全件取得
offset = 0
while True:
    payload = {
        "offset": offset,
        "user_search": {
            "job_tag_ids": job_tag_ids
        }
    }
    try:
        response = requests.post(api_url, data=json.dumps(payload), headers=headers)
        response.raise_for_status()
        data = response.json()

        job_offers_list = data.get("job_offers", [])
        if not job_offers_list:
            print("これ以上の求人情報はありません。")
            break

        all_job_offers.extend(job_offers_list)
        print(f"オフセット {offset} の求人情報を取得しました（{len(job_offers_list)}件）。")
        offset += len(job_offers_list)

    except requests.exceptions.RequestException as e:
        print(f"APIリクエスト中にエラーが発生しました: {e}")
        break

# 取得した全データをDataFrameに変換
df = pd.DataFrame(all_job_offers)

# CSVファイルに出力
output_directory = "data"
if not os.path.exists(output_directory):
    os.makedirs(output_directory)
csv_file_path = os.path.join(output_directory, "first_page.csv")
df.to_csv(csv_file_path, index=False, encoding='utf-8-sig')

print(f"\n合計 {len(all_job_offers)} 件の求人情報を'{csv_file_path}'に保存しました。")

df = pd.read_csv('./data/first_page.csv')

columns_to_keep = [
    'job_offer_id',
    'job_offer_name',
    'client',
    'job_offer_areas',
    'job_offer_min_salary',
    'job_offer_max_salary',
    'job_offer_skill_names'
]

df_filtered = df[columns_to_keep]

df_filtered['client_name'] = df_filtered['client'].apply(
    lambda x: ast.literal_eval(x)['name'] if pd.notna(x) else None
)
df_filtered['employee_count'] = df_filtered['client'].apply(
    lambda x: ast.literal_eval(x)['employee_count'] if pd.notna(x) else None
)
df_filtered = df_filtered.drop('client', axis = 1)

df_filtered['job_offer_skill_names'] = df_filtered['job_offer_skill_names'].apply(ast.literal_eval)

print("\n必要な情報のみに絞り込みました:")

df_filtered.to_csv('filtered.csv')