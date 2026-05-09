import pandas as pd
import xlsxwriter

data_files = [
    'data/dth-tiki/result/comments_data_ncds.csv',
    'data/nhacua-tiki/result/comments_data_ncds.csv',
    'data/laptop-tiki/result/comments_data_ncds.csv',
    'data/book-tiki/result/comments_data_ncds.csv'
]

dfs = []
sample_size = 5000

for file in data_files:
    df = pd.read_csv(file)
    df_negative = df[(df['rating'] <= 3) & df['content'].notnull()]
    if len(df_negative) > sample_size:
        df_negative = df_negative.sample(sample_size, random_state=42)
    dfs.append(df_negative)

merged_df = pd.concat(dfs)
merged_df = merged_df.sample(frac=1, random_state=42) 


merged_df.reset_index(drop=True, inplace=True)

merged_df.drop('id', axis=1, inplace=True)

merged_df.drop('customer_id', axis=1, inplace=True)

num_files = 6
split_sizes = [2500, 2500, 2500, 1000, 1000, 1000]

start_index = 0
for i in range(num_files):
    end_index = start_index + split_sizes[i]
    file_name = f'data/data_split_{i+1}.xlsx'
    subset_df = merged_df[start_index:end_index]
    subset_df.to_excel(file_name, engine='xlsxwriter')
    start_index = end_index