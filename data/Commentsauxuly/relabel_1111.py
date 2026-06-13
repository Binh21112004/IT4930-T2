import pandas as pd
import sys

sys.stdout.reconfigure(encoding='utf-8')
file_path = r"C:\Users\admin\Desktop\KHDL\IT4930-T2\data\Commentsauxuly\comments_data_ncds_preprocessed_toy.csv"

df = pd.read_csv(file_path)

updates = {
    1503: [0, 1, 1, 0],
    1558: [0, 1, 1, 1],
    1590: [1, 1, 1, 0],
    1623: [0, 1, 1, 1],
    1698: [0, 1, 1, 0],
    1860: [0, 1, 1, 0],
    1869: [0, 1, 1, 0],
    1888: [0, 1, 1, 0],
    1896: [0, 1, 1, 1],
    1928: [0, 1, 1, 1],
    1945: [0, 1, 1, 0],
    1947: [0, 1, 1, 0],
    1956: [1, 1, 1, 0],
    1957: [0, 1, 1, 0],
    1961: [1, 1, 0, 0],
    1983: [0, 1, 1, 0],
    1985: [0, 1, 1, 0]
}

for idx, labels in updates.items():
    df.loc[idx, 'Quality'] = labels[0]
    df.loc[idx, 'Service'] = labels[1]
    df.loc[idx, 'Shipping'] = labels[2]
    df.loc[idx, 'Packing'] = labels[3]

df.to_csv(file_path, index=False)

r1111 = df[(df['Quality']==1) & (df['Service']==1) & (df['Shipping']==1) & (df['Packing']==1)]
print(f"Đã sửa các dòng sai sót. Hiện tại số lượng dòng 1,1,1,1 thực sự là: {len(r1111)}")
