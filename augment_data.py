#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tăng cường dữ liệu (Data Augmentation) bằng phương pháp thay thế từ đồng nghĩa (Synonym Replacement).
Script này đọc từ file dữ liệu đã gộp 'comments_merged_single_label.csv',
thực hiện thay thế từ đồng nghĩa đối với các nhóm nhãn thiểu số (Service, Shipping, Packing)
để cân bằng dữ liệu với nhóm đa số (Quality).

Kết quả được lưu thành một file mới: 'comments_merged_single_label_augmented.csv'.
"""

import os
import random
import re
import pandas as pd

# Từ điển từ đồng nghĩa e-commerce tiếng Việt
SYNONYMS_DICT = {
    # Nhóm Shipping (Vận chuyển)
    "giao hàng": ["vận chuyển", "ship", "giao nhận", "gửi hàng"],
    "giao": ["ship", "gửi", "chuyển"],
    "chậm": ["trễ", "lâu", "muộn", "quá trễ", "quá lâu"],
    "nhanh": ["tốc hành", "siêu tốc", "thần tốc", "lẹ"],
    "shipper": ["người giao hàng", "bạn giao hàng", "nhân viên giao hàng", "anh ship"],
    
    # Nhóm Packing (Đóng gói)
    "đóng gói": ["bao bọc", "gói hàng", "bọc hàng", "đóng hàng"],
    "móp": ["méo", "dập", "móp méo", "bẹp"],
    "hộp": ["thùng", "vỏ hộp", "box"],
    "rách": ["thủng", "nát", "hỏng"],
    
    # Nhóm Service (Dịch vụ)
    "hỗ trợ": ["tư vấn", "chăm sóc", "phản hồi", "giải đáp"],
    "cửa hàng": ["shop", "nhà bán", "gian hàng", "seller"],
    "nhân viên": ["nv", "người hỗ trợ", "đội ngũ chăm sóc"],
    "lừa đảo": ["gian dối", "dối trá", "lừa gạt"],
}


def replace_synonyms(text, p=0.4):
    """
    Thay thế ngẫu nhiên các từ khóa xuất hiện trong text bằng từ đồng nghĩa
    với xác suất p cho mỗi từ khóa tìm thấy.
    """
    if not isinstance(text, str):
        return text
        
    new_text = text
    # Duyệt qua các cụm từ đồng nghĩa để thay thế
    for key, values in SYNONYMS_DICT.items():
        # Sử dụng capture groups (^|\s) và ($|\s|[.,!?;]) để tránh lỗi look-behind không cố định độ dài
        pattern = re.compile(rf'(^|\s){re.escape(key)}($|\s|[.,!?;])', re.IGNORECASE)
        
        if pattern.search(new_text):
            if random.random() < p:
                replacement = random.choice(values)
                # Thay thế bằng cách giữ lại các ký tự ở group 1 và group 2
                new_text = pattern.sub(rf'\1{replacement}\2', new_text, count=1)
                
    return new_text


def augment_class(df_class, target_count, existing_contents):
    """
    Tăng cường dữ liệu cho một nhóm nhãn cụ thể bằng cách lấy mẫu ngẫu nhiên
    và thực hiện Synonym Replacement cho đến khi đạt target_count.
    Tránh trùng lặp nội dung với tập existing_contents.
    """
    current_count = len(df_class)
    if current_count >= target_count:
        return df_class
        
    augmented_records = []
    needed_count = target_count - current_count
    
    # Tạo một bản sao của df_class để lấy mẫu
    source_pool = df_class.copy()
    
    # Để tránh lặp vô hạn, giới hạn số lần thử tối đa
    max_attempts = needed_count * 10
    attempts = 0
    generated_count = 0
    
    while generated_count < needed_count and attempts < max_attempts:
        attempts += 1
        # Lấy ngẫu nhiên 1 dòng từ source_pool
        row = source_pool.sample(n=1).iloc[0]
        original_text = row['content']
        
        # Thử thay thế từ đồng nghĩa tối đa 5 lần với p cao để tăng tỷ lệ đổi từ
        new_text = original_text
        for _ in range(5):
            mutated = replace_synonyms(original_text, p=0.6)
            if mutated != original_text and mutated not in existing_contents:
                new_text = mutated
                break
                
        if new_text != original_text and new_text not in existing_contents:
            new_row = row.copy()
            new_row['content'] = new_text
            augmented_records.append(new_row)
            existing_contents.add(new_text)
            generated_count += 1
            
    # Lấy bù phần còn thiếu nếu không tạo đủ các câu độc nhất
    if generated_count < needed_count:
        print(f"      [!] Canh bao: Chi tao duoc {generated_count}/{needed_count} dong doc nhat cho nhan nay do gioi han tu dong nghia.")
        remaining = needed_count - generated_count
        choices = source_pool.sample(n=remaining, replace=True)
        for _, row in choices.iterrows():
            new_row = row.copy()
            new_text = replace_synonyms(row['content'], p=0.8)
            new_row['content'] = new_text
            augmented_records.append(new_row)
            
    df_augmented = pd.DataFrame(augmented_records)
    return pd.concat([df_class, df_augmented], ignore_index=True)


def main():
    input_path = r"data/Commentsauxuly/comments_merged_single_label.csv"
    output_path = r"data/Commentsauxuly/comments_merged_single_label_augmented.csv"
    
    if not os.path.exists(input_path):
        print(f"[-] File du lieu chua gop hoac khong ton tai: {input_path}")
        print("    Vui lòng chạy script merge_filtered_data.py trước!")
        return

    # Đọc file dữ liệu đã gộp
    try:
        df = pd.read_csv(input_path)
        # Loại bỏ các dòng trùng lặp nội dung nếu có từ tệp đầu vào
        df = df.drop_duplicates(subset=['content']).reset_index(drop=True)
    except Exception as e:
        print(f"[-] Loi khi doc file: {e}")
        return

    # Khởi tạo tập hợp chứa tất cả nội dung hiện tại để kiểm tra trùng lặp
    existing_contents = set(df['content'].dropna().tolist())

    print(f"\n{'='*70}")
    print(f"[*] Bat dau qua trinh Tang cuong du lieu (Data Augmentation)...")
    print(f"{'='*70}")
    
    # Đếm số lượng mẫu hiện tại
    print("[+] Phan bo nhan truoc khi tang cuong:")
    label_cols = ['Quality', 'Service', 'Shipping', 'Packing']
    for col in label_cols:
        count = len(df[df[col] == 1])
        print(f"   - {col:10}: {count} dong")

    # Xác định số lượng mục tiêu cho các nhãn thiểu số
    # Ta có thể đặt mục tiêu cân bằng hoàn toàn với Quality (11,136 dòng) 
    # Hoặc đặt một ngưỡng trung bình hợp lý (ví dụ: 5,000 dòng) để tránh bị lặp cấu trúc câu quá nhiều.
    # Ở đây chúng ta đặt mục tiêu là 5,000 dòng cho mỗi lớp thiểu số.
    target_count = 5000
    print(f"\n[*] Dat muc tieu tang cuong cac nhan thieu so len toi thieu: {target_count} dong/nhan")

    augmented_dfs = []
    
    # Tách và xử lý từng nhãn
    # Nhóm Quality giữ nguyên (vì đã có 11,136 dòng)
    df_quality = df[(df['Quality'] == 1) & (df['Service'] == 0) & (df['Shipping'] == 0) & (df['Packing'] == 0)].copy()
    augmented_dfs.append(df_quality)
    
    # Các nhóm thiểu số cần tăng cường
    for col in ['Service', 'Shipping', 'Packing']:
        # Lọc ra tập con của nhãn này
        if col == 'Service':
            df_sub = df[(df['Quality'] == 0) & (df['Service'] == 1) & (df['Shipping'] == 0) & (df['Packing'] == 0)].copy()
        elif col == 'Shipping':
            df_sub = df[(df['Quality'] == 0) & (df['Service'] == 0) & (df['Shipping'] == 1) & (df['Packing'] == 0)].copy()
        else: # Packing
            df_sub = df[(df['Quality'] == 0) & (df['Service'] == 0) & (df['Shipping'] == 0) & (df['Packing'] == 1)].copy()
            
        print(f"   -> Dang tang cuong nhan '{col}' tu {len(df_sub)} len {target_count} dòng...")
        df_augmented = augment_class(df_sub, target_count, existing_contents)
        augmented_dfs.append(df_augmented)

    # Gộp lại thành tập dữ liệu cuối cùng
    df_final = pd.concat(augmented_dfs, ignore_index=True)
    
    # Xáo trộn dữ liệu ngẫu nhiên (shuffle)
    df_final = df_final.sample(frac=1, random_state=42).reset_index(drop=True)

    # Lưu file kết quả
    try:
        df_final.to_csv(output_path, index=False, encoding='utf-8')
        print(f"\n{'='*70}")
        print(f"[+] TANG CUONG DU LIEU THANH CONG!")
        print(f"{'='*70}")
        print(f"   - Tong so dong truoc tang cuong: {len(df)}")
        print(f"   - Tong so dong sau tang cuong:  {len(df_final)}")
        print(f"   - Luu tai:                       {os.path.abspath(output_path)}")
        
        # In phân bố nhãn sau tăng cường
        print("\n[+] Phan bo nhan sau khi tang cuong:")
        for col in label_cols:
            count = len(df_final[df_final[col] == 1])
            print(f"   - {col:10}: {count} dong")
            
    except Exception as e:
        print(f"[-] Loi khi ghi file output: {e}")


if __name__ == '__main__':
    main()
