import requests
import json
import pandas as pd
import os

# APIのURLを設定
api_url = "https://www.green-japan.com/api/v2/user/search_job_offers"

# 全ての求人情報を格納するリスト
all_job_offers = []

# 取得したいページのオフセットをリストに設定
offsets_to_get = [0, 20] 



# 正しいペイロードを定義
payload = {
    "offset": 0,
    "order_type": "jobOfferScore",
    "user_search": {
        "area_ids": [],
        "company_feature_ids": [],
        "job_feature_ids": [],
        "job_tag_ids": [60],
        "keyword": "",
        "new_flg": False,
        "over_employees": 0,
        "over_establish_yyyy": 0,
        "salary_bottom_id": 0,
        "under_employees": 0,
        "under_establish_yyyy": 0
    }
}


# ヘッダー情報を設定
headers = {
    'Content-Type': 'application/json',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
}


response = requests.post(api_url, data=json.dumps(payload), headers=headers)
response.raise_for_status()

data = response.json()
    
# データを整形して表示
job_offers_list = json.dumps(data, indent=2, ensure_ascii=False)

print(job_offers_list)

# if len(job_offers_list) > 0:
#     # 最初の項目だけを取得
#     first_job_offer = job_offers_list[0]
    
#     # 整形して表示
#     print(json.dumps(first_job_offer, indent=2, ensure_ascii=False))
# else:
#     print("求人情報が取得できませんでした。")