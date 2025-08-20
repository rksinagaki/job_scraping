import pandas as pd
import ast
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter

df = pd.read_csv('./data/all_pages.csv')

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
    df_filtered['job_offer_areas'] = df_filtered['job_offer_areas'].apply(to_list_if_needed)

if 'job_offer_name' in df_filtered.columns:
    df_filtered['job_tag'] = 'その他'
    df_filtered.loc[df_filtered['job_offer_name'].str.contains('データ基盤エンジニア|データエンジニア|データベースエンジニア'), 'job_tag'] = 'データエンジニア'
    df_filtered.loc[df_filtered['job_offer_name'].str.contains('データサイエンティスト|データアナリスト'), 'job_tag'] = 'データサイエンティスト'
    df_filtered.loc[df_filtered['job_offer_name'].str.contains('AIエンジニア|機械学習エンジニア|AI開発エンジニア'), 'job_tag'] = 'AIエンジニア'

df_filtered.to_csv('data/filtered.csv', index=False, encoding='utf-8-sig')

print("\n必要なデータ絞り込みました:")


#dashboard化-----------------------------------------------------
st.title('データ職種求人ダッシュボード')
st.sidebar.header('フィルタ')

# 職種
job_options = ['すべて','AIエンジニア','データサイエンティスト','データエンジニア','その他']
selected_job = st.sidebar.selectbox('職種を選択:', options=job_options)

# 勤務地
all_areas = []
for sublist in df_filtered['job_offer_areas'].dropna():
    for item in sublist:
        all_areas.append(item)
unique_areas = list(set(all_areas))
area_options = ['すべて'] + unique_areas
selected_area = st.sidebar.selectbox('勤務地:', options=area_options)

# 従業員数
employee_options = ['すべて', '〜100人', '101〜500人', '501〜1000人', '1001人〜']
selected_emp_range = st.sidebar.selectbox('従業員数:', options=employee_options)


# 職種フィルタリング
if selected_job != 'すべて':
    df_filtered_by_job = df_filtered[df_filtered['job_tag'] == selected_job]
else:
    df_filtered_by_job = df_filtered

# 勤務地フィルタリング
if selected_area != 'すべて':
    df_filtered_by_area = df_filtered_by_job[df_filtered_by_job['job_offer_areas'].apply(
        # ここからーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー
        lambda x: any(item in selected_area for item in x)
    )]
else:
    df_filtered_by_area = df_filtered_by_job

#給与フィルタリング


# 従業員数フィルタリング
if selected_emp_range == '〜100人':
    df_filtered_final = df_filtered_by_area[df_filtered_by_area['employee_count'] <= 100]
elif selected_emp_range == '101〜500人':
    df_filtered_final = df_filtered_by_area[(df_filtered_by_area['employee_count'] > 100) & (df_filtered_by_area['employee_count'] <= 500)]
elif selected_emp_range == '501〜1000人':
    df_filtered_final = df_filtered_by_area[(df_filtered_by_area['employee_count'] > 500) & (df_filtered_by_area['employee_count'] <= 1000)]
elif selected_emp_range == '1001人〜':
    df_filtered_final = df_filtered_by_area[df_filtered_by_area['employee_count'] > 1000]
else:
    df_filtered_final = df_filtered_by_area

st.write(f"合計 {df_filtered_final['job_offer_id'].count()} 件の求人情報")
st.dataframe(df_filtered_final)

# -----------------
# 3. グラフの可視化
# -----------------
st.header('主要な分析')

# 職種別の求人割合
job_counts = df_filtered_final['job_tag'].value_counts()
fig_job_pie = px.pie(
    job_counts,
    values=job_counts.values,
    names=job_counts.index,
    title='職種別求人割合'
)
st.plotly_chart(fig_job_pie)

# 職種ごとのスキルヒートマップ
all_skills = [skill for sublist in df_filtered_final['job_offer_skill_names'].dropna() for skill in sublist]
skill_counts = Counter(all_skills)
top_skills = [skill for skill, count in skill_counts.most_common(20)]

skill_matrix = pd.DataFrame(index=top_skills, columns=df_filtered_final['job_tag'].unique()).fillna(0)
for job_tag, skills in zip(df_filtered_final['job_tag'], df_filtered_final['job_offer_skill_names']):
    if isinstance(skills, list):
        for skill in skills:
            if skill in skill_matrix.index:
                skill_matrix.loc[skill, job_tag] += 1

fig_heatmap = px.imshow(
    skill_matrix,
    x=skill_matrix.columns,
    y=skill_matrix.index,
    color_continuous_scale='YlGnBu',
    labels=dict(x="職種", y="スキル", color="件数"),
    title="職種別スキルヒートマップ"
)
st.plotly_chart(fig_heatmap)

# 給与の中央値（箱ひげ図）
st.subheader('給与の中央値')
salary_df = df_filtered_final.copy()
salary_df['avg_salary'] = (salary_df['job_offer_min_salary'] + salary_df['job_offer_max_salary']) / 2
fig_salary = px.box(
    salary_df,
    x='job_tag',
    y='avg_salary',
    points='all',
    title='職種別給与分布'
)
st.plotly_chart(fig_salary)

# 企業の規模（従業員数）の分布
st.subheader('企業の規模')
fig_emp = px.histogram(
    df_filtered_final,
    x='employee_count',
    nbins=20,
    title='従業員数の分布'
)
st.plotly_chart(fig_emp)
