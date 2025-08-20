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
