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

# ページネーション
offset = 0

def process_page_response(data, offset, list):
    job_offers_list = data.get("job_offers")
    list.extend(job_offers_list)
    print(f"[page={offset}] 取得（{len(job_offers_list)}件）。")
    next_offset_value = data.get("next_offset")
    return (next_offset_value if isinstance(next_offset_value, int) else None), False


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

        result = process_page_response(data, offset, all_job_offers)
        next_offset_value = result[0]
        is_last = result[1]
        if is_last:
            break
        if next_offset_value is not None:
            offset = next_offset_value
        else:
            offset += 1

        time.sleep(0.5)

    except requests.exceptions.RequestException as e:
        try:
            # status_codeの取得
            if hasattr(e, 'response') and e.response is not None:
                status_code = e.response.status_code
            else:
                status_code = None

            # bodyの取得
            if hasattr(e, 'response') and e.response is not None:
                body = e.response.text[:500]
            else:
                body = ""

            print(f"APIリクエスト中にエラーが発生しました: {e} | status={status_code} | body={body}")
        
        except Exception:
            print(f"APIリクエスト中にエラーが発生しました: {e}")
        
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

# コラム厳選
columns_to_keep = [
    'job_offer_id',
    'job_offer_name',
    'client',
    'job_offer_areas',
    'job_offer_min_salary',
    'job_offer_max_salary',
    'job_offer_skill_names'
]

df_filtered = df.loc[:, columns_to_keep].copy()

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

#データの整形
if 'client' in df_filtered.columns:
    df_filtered['client_dict'] = df_filtered['client'].apply(to_dict_if_needed)
    df_filtered['client_name'] = df_filtered['client_dict'].apply(lambda d: d.get('name') if isinstance(d, dict) else None)
    df_filtered['employee_count'] = df_filtered['client_dict'].apply(lambda d: d.get('employee_count') if isinstance(d, dict) else None)
    df_filtered['established'] = df_filtered['client_dict'].apply(lambda d: d.get('established_at') if isinstance(d, dict) else None)
    # df_filtered['established'] = df_filtered.to_datetime('established', unit='s')
    df_filtered['established'] = pd.to_datetime(df_filtered['established'], unit='s')
    df_filtered = df_filtered.drop(['client', 'client_dict'], axis=1, errors='ignore')

if 'job_offer_skill_names' in df_filtered.columns:
    df_filtered['job_offer_skill_names'] = df_filtered['job_offer_skill_names'].apply(to_list_if_needed)

if 'job_offer_areas' in df_filtered.columns:
    df_filtered['job_offer_areas'] = df_filtered['job_offer_skill_names'].apply(to_list_if_needed)

if 'job_offer_name' in df_filtered.columns:
    df_filtered['job_tag'] = 'その他'
    df_filtered.loc[df_filtered['job_offer_name'].str.contains('データ基盤エンジニア|データエンジニア|データベースエンジニア'), 'job_tag'] = 'データエンジニア'
    df_filtered.loc[df_filtered['job_offer_name'].str.contains('データサイエンティスト|データアナリスト'), 'job_tag'] = 'データサイエンティスト'
    df_filtered.loc[df_filtered['job_offer_name'].str.contains('AIエンジニア|機械学習エンジニア|AI開発エンジニア'), 'job_tag'] = 'AIエンジニア'

print("\n必要なに絞り込みました:")

df_filtered.to_csv('data/filtered.csv', index=False, encoding='utf-8-sig')
