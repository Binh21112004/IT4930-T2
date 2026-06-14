#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gộp tất cả các file dữ liệu comment sau khi chạy bộ lọc filter_single_label.
Script sẽ quét thư mục data/Commentsauxuly/, tự động đọc robust và lọc từng file 
(chỉ giữ lại các tổ hợp nhãn single-label 1,0,0,0; 0,1,0,0; 0,0,1,0; 0,0,0,1),
sau đó gộp tất cả lại thành một file CSV duy nhất phục vụ huấn luyện mô hình.

Đồng thời, script thêm cột 'category' để theo dõi nguồn gốc của từng comment.
"""

import os
import re
import pandas as pd


def load_and_filter_robustly(file_path):
    record_pattern = re.compile(r',\s*([01])\s*,\s*([01])\s*,\s*([01])\s*,\s*([01])\s*$')
    
    records = []
    current_content = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        header_line = f.readline()
        if not header_line:
            return None
        
        for line in f:
            stripped_line = line.rstrip('\r\n')
            match = record_pattern.search(stripped_line)
            if match:
                end_idx = match.start()
                line_content = stripped_line[:end_idx]
                
                if current_content:
                    current_content.append(line_content)
                    content_str = "\n".join(current_content)
                    current_content = []
                else:
                    content_str = line_content
                    
                if content_str.startswith('"'):
                    content_str = content_str[1:]
                if content_str.endswith('"'):
                    content_str = content_str[:-1]
                content_str = content_str.replace('""', '"')
                
                labels = [int(x) for x in match.groups()]
                records.append([content_str] + labels)
            else:
                current_content.append(stripped_line)
                
        if current_content:
            content_str = "\n".join(current_content)
            if content_str.startswith('"'):
                content_str = content_str[1:]
            if content_str.endswith('"'):
                content_str = content_str[:-1]
            content_str = content_str.replace('""', '"')
            records.append([content_str, 0, 0, 0, 0])
            
    df = pd.DataFrame(records, columns=['content', 'Quality', 'Service', 'Shipping', 'Packing'])
    
    # Lọc chỉ giữ lại single-label
    mask = (
        ((df['Quality'] == 1) & (df['Service'] == 0) & (df['Shipping'] == 0) & (df['Packing'] == 0)) |
        ((df['Quality'] == 0) & (df['Service'] == 1) & (df['Shipping'] == 0) & (df['Packing'] == 0)) |
        ((df['Quality'] == 0) & (df['Service'] == 0) & (df['Shipping'] == 1) & (df['Packing'] == 0)) |
        ((df['Quality'] == 0) & (df['Service'] == 0) & (df['Shipping'] == 0) & (df['Packing'] == 1))
    )
    
    df_filtered = df[mask].copy()
    return df, df_filtered


def main():
    data_dir = r"data/Commentsauxuly"
    if not os.path.exists(data_dir):
        print(f"[-] Thu muc khong ton tai: {data_dir}")
        return

    # Tìm các file CSV gốc (bỏ qua các file đã lọc _filtered.csv hoặc file gộp _merged.csv)
    all_files = os.listdir(data_dir)
    target_files = []
    for f in all_files:
        if f.startswith("comments_data_ncds_preprocessed_") and f.endswith(".csv"):
            if "_filtered" not in f and "_merged" not in f:
                target_files.append(f)

    if not target_files:
        print("[-] Khong tim thay file du lieu goc nao de gop!")
        return

    print(f"\n{'='*70}")
    print(f"[*] Bat dau xu ly va gop {len(target_files)} file CSV...")
    print(f"{'='*70}")

    merged_dfs = []
    total_raw_rows = 0
    total_filtered_rows = 0

    for file_name in sorted(target_files):
        file_path = os.path.join(data_dir, file_name)
        
        # Trích xuất tên danh mục từ tên file
        # Ví dụ: comments_data_ncds_preprocessed_Book.csv -> Book
        category = file_name.replace("comments_data_ncds_preprocessed_", "").replace(".csv", "")
        
        try:
            df_raw, df_filtered = load_and_filter_robustly(file_path)
            
            # Thêm cột danh mục nguồn
            df_filtered['category'] = category
            
            raw_len = len(df_raw)
            filt_len = len(df_filtered)
            
            total_raw_rows += raw_len
            total_filtered_rows += filt_len
            
            print(f"   + Category '{category:12}': Goc {raw_len:5} dong -> Con {filt_len:5} dong ({(filt_len/raw_len)*100:5.2f}%)")
            
            merged_dfs.append(df_filtered)
        except Exception as e:
            print(f"   [-] Loi khi xu ly file {file_name}: {e}")

    if not merged_dfs:
        print("[-] Khong co du lieu nao duoc loc thanh cong de gop!")
        return

    # Gộp tất cả các DataFrame
    final_df = pd.concat(merged_dfs, ignore_index=True)
    
    # Sắp xếp lại thứ tự cột cho đẹp mắt (loại bỏ category)
    cols = ['content', 'Quality', 'Service', 'Shipping', 'Packing']
    final_df = final_df[cols]

    # Lưu kết quả
    output_path = os.path.join(data_dir, "comments_merged_single_label.csv")
    try:
        final_df.to_csv(output_path, index=False, encoding='utf-8')
        print(f"\n{'='*70}")
        print(f"[+] GOP DU LIEU THANH CONG!")
        print(f"{'='*70}")
        print(f"   - Tong so dong truoc khi loc:  {total_raw_rows}")
        print(f"   - Tong so dong sau khi loc:    {total_filtered_rows} ({(total_filtered_rows/total_raw_rows)*100:.2f}%)")
        print(f"   - Luu file gop tai:            {os.path.abspath(output_path)}")
        
        # Thống kê phân bố nhãn sau khi gộp
        print("\n[+] Phan bo cac to hop nhan sau khi gop:")
        label_cols = ['Quality', 'Service', 'Shipping', 'Packing']
        combinations = final_df.groupby(label_cols).size().reset_index(name='count')
        for idx, row in combinations.iterrows():
            combo_str = ",".join(str(row[col]) for col in label_cols)
            print(f"     * To hop [{combo_str}]: {row['count']} dong")
            
    except Exception as e:
        print(f"[-] Loi khi ghi file gop: {e}")


if __name__ == '__main__':
    main()
