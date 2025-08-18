import requests
import json
import pandas as pd
import os
import ast
import time

# APIのURLとヘッダー情報
api_url = "https://www.green-japan.com/api/v2/user/search_job_offers"
headers = {
    'Content-Type': 'application/json',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    'Referer': 'https://www.green-japan.com/search',
    'X-Requested-With': 'XMLHttpRequest',
}

# 求人情報リスト
all_job_offers = []

# 職種タグ
job_tag_ids = [60, 61, 62]

# ページネーション（offset は 0始まりのページ番号とみなす）
offset = 0

while True:
    payload = {
        "offset": offset,
        "order_type": "jobOfferScore",
        "user_search": {
            "job_tag_ids": job_tag_ids
        }
    }
    try:
        response = requests.post(api_url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        total_count = data.get("total_count") or data.get("total") or data.get("job_offers_total_count")
        job_offers_list = data.get("job_offers", [])
        if not job_offers_list:
            print("これ以上の求人情報はありません。")
            break

        all_job_offers.extend(job_offers_list)
        got = len(job_offers_list)
        if total_count is not None:
            print(f"[page={offset}] 取得（{got}件 / total={total_count}）。")
        else:
            print(f"[page={offset}] 取得（{got}件）。")

        next_offset = data.get("next_offset") or data.get("nextOffset")
        if isinstance(next_offset, int):
            offset = next_offset
        else:
            offset += 1

        time.sleep(1.0)

    except requests.exceptions.RequestException as e:
        # 可能ならレスポンス本文を出力
        try:
            status_code = e.response.status_code if hasattr(e, 'response') and e.response is not None else None
            body = e.response.text[:500] if hasattr(e, 'response') and e.response is not None else ""
            print(f"APIリクエスト中にエラーが発生しました: {e} | status={status_code} | body={body}")
        except Exception:
            print(f"APIリクエスト中にエラーが発生しました: {e}")
        # 軽いリトライ（1回）
        try:
            time.sleep(1.0)
            response = requests.post(api_url, json=payload, headers=headers, timeout=15)
            response.raise_for_status()
            data = response.json()
            job_offers_list = data.get("job_offers", [])
            if not job_offers_list:
                print("これ以上の求人情報はありません。（リトライ後空）")
                break
            all_job_offers.extend(job_offers_list)
            print(f"[Retry OK][page={offset}] 取得（{len(job_offers_list)}件）。")
            next_offset = data.get("next_offset") or data.get("nextOffset")
            if isinstance(next_offset, int):
                offset = next_offset
            else:
                offset += 1
            continue
        except Exception as e2:
            print(f"リトライでも失敗しました。処理を終了します: {e2}")
            break

# 取得した全データをDataFrameに変換
df = pd.DataFrame(all_job_offers)

# CSVファイルに出力
output_directory = "data"
if not os.path.exists(output_directory):
    os.makedirs(output_directory)
all_csv_path = os.path.join(output_directory, "all_pages.csv")
df.to_csv(all_csv_path, index=False, encoding='utf-8-sig')
print(f"\n合計 {len(all_job_offers)} 件の求人情報を'{all_csv_path}'に保存しました。")

# 後続処理: 必要カラムの抽出と整形
columns_to_keep = [
    'job_offer_id',
    'job_offer_name',
    'client',
    'job_offer_areas',
    'job_offer_min_salary',
    'job_offer_max_salary',
    'job_offer_skill_names'
]
existing_cols = [c for c in columns_to_keep if c in df.columns]
df_filtered = df.loc[:, existing_cols].copy()

# 文字列/辞書どちらでも扱えるようヘルパ

def to_dict_if_needed(value):
    if value is None:
        return None
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        try:
            return ast.literal_eval(value)
        except Exception:
            return None
    if isinstance(value, float) and pd.isna(value):
        return None
    return None


def to_list_if_needed(value):
    if value is None:
        return None
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        try:
            return ast.literal_eval(value)
        except Exception:
            return None
    if isinstance(value, float) and pd.isna(value):
        return None
    return None

if 'client' in df_filtered.columns:
    df_filtered.loc[:, 'client_dict'] = df_filtered['client'].apply(to_dict_if_needed)
    df_filtered.loc[:, 'client_name'] = df_filtered['client_dict'].apply(lambda d: d.get('name') if isinstance(d, dict) else None)
    df_filtered.loc[:, 'employee_count'] = df_filtered['client_dict'].apply(lambda d: d.get('employee_count') if isinstance(d, dict) else None)
    df_filtered = df_filtered.drop(['client', 'client_dict'], axis=1, errors='ignore')

if 'job_offer_skill_names' in df_filtered.columns:
    df_filtered.loc[:, 'job_offer_skill_names'] = df_filtered['job_offer_skill_names'].apply(to_list_if_needed)

print("\n必要な情報のみに絞り込みました:")

df_filtered.to_csv('filtered.csv', index=False, encoding='utf-8-sig')