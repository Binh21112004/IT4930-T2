#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lọc dữ liệu comment để chỉ giữ lại các dòng có đúng một nhãn được gắn (Single-label).
Nghĩa là chỉ giữ lại các tổ hợp:
  - 1,0,0,0 (chỉ Quality)
  - 0,1,0,0 (chỉ Service)
  - 0,0,1,0 (chỉ Shipping)
  - 0,0,0,1 (chỉ Packing)
Loại bỏ tất cả các dòng có tổ hợp khác (ví dụ: 0,0,0,0 hoặc nhiều hơn một nhãn là 1).

Cách sử dụng:
  python filter_single_label.py <đường_dẫn_file_csv> [--output <đường_dẫn_file_output>]

Ví dụ:
  python filter_single_label.py data/Commentsauxuly/comments_data_ncds_preprocessed_nhacua.csv
"""

import os
import sys
import argparse
import pandas as pd


def filter_comments(input_path, output_path=None):
    # Kiểm tra file đầu vào tồn tại
    if not os.path.exists(input_path):
        print(f"[-] File khong ton tai: {input_path}")
        return False

    # Xác định đường dẫn file output mặc định nếu không truyền vào
    if not output_path:
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_filtered{ext}"

    print(f"\n{'='*70}")
    # Chuyển đổi sang đường dẫn tuyệt đối/chuẩn hóa để hiển thị đẹp hơn
    print(f"[*] Doc du lieu tu: {os.path.abspath(input_path)}")
    print(f"{'='*70}")

    # Đọc file CSV bằng phương thức robust tự xây dựng
    try:
        import re
        record_pattern = re.compile(r',\s*([01])\s*,\s*([01])\s*,\s*([01])\s*,\s*([01])\s*$')
        
        records = []
        current_content = []
        
        with open(input_path, 'r', encoding='utf-8') as f:
            header_line = f.readline()
            if not header_line:
                print("[-] File CSV trong!")
                return False
            
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
                        
                    # Loại bỏ dấu nháy kép bọc ngoài nội dung nếu có
                    if content_str.startswith('"'):
                        content_str = content_str[1:]
                    if content_str.endswith('"'):
                        content_str = content_str[:-1]
                    content_str = content_str.replace('""', '"')
                    
                    labels = [int(x) for x in match.groups()]
                    records.append([content_str] + labels)
                else:
                    current_content.append(stripped_line)
            
            # Xử lý phần nội dung còn sót lại ở cuối file nếu có
            if current_content:
                content_str = "\n".join(current_content)
                if content_str.startswith('"'):
                    content_str = content_str[1:]
                if content_str.endswith('"'):
                    content_str = content_str[:-1]
                content_str = content_str.replace('""', '"')
                records.append([content_str, 0, 0, 0, 0])
                
        df = pd.DataFrame(records, columns=['content', 'Quality', 'Service', 'Shipping', 'Packing'])
    except Exception as e:
        print(f"[-] Loi khi doc va phan tich file: {e}")
        return False

    total_before = len(df)
    print(f"[*] Tong so dong ban dau: {total_before}")

    # Danh sách các cột nhãn cần kiểm tra
    label_cols = ['Quality', 'Service', 'Shipping', 'Packing']

    # Chuyển đổi dữ liệu các cột nhãn sang kiểu int (điền NaN bằng 0)
    for col in label_cols:
        df[col] = df[col].fillna(0).astype(int)

    # Thống kê phân bố tổ hợp trước khi lọc
    print("\n[+] Phan bo cac to hop truoc khi loc:")
    combinations_before = df.groupby(label_cols, dropna=False).size().reset_index(name='count')
    # Sắp xếp theo số lượng giảm dần
    combinations_before = combinations_before.sort_values(by='count', ascending=False)
    for idx, row in combinations_before.iterrows():
        combo_str = ",".join(str(row[col]) for col in label_cols)
        print(f"   - To hop [{combo_str}]: {row['count']} dong")

    # Tạo mask lọc: Chỉ giữ các dòng có đúng một cột bằng 1 và các cột còn lại bằng 0
    mask = (
        ((df['Quality'] == 1) & (df['Service'] == 0) & (df['Shipping'] == 0) & (df['Packing'] == 0)) |
        ((df['Quality'] == 0) & (df['Service'] == 1) & (df['Shipping'] == 0) & (df['Packing'] == 0)) |
        ((df['Quality'] == 0) & (df['Service'] == 0) & (df['Shipping'] == 1) & (df['Packing'] == 0)) |
        ((df['Quality'] == 0) & (df['Service'] == 0) & (df['Shipping'] == 0) & (df['Packing'] == 1))
    )

    df_filtered = df[mask].copy()
    total_after = len(df_filtered)
    removed_rows = total_before - total_after

    # Thống kê phân bố tổ hợp sau khi lọc
    print("\n[+] Phan bo cac to hop sau khi loc:")
    combinations_after = df_filtered.groupby(label_cols).size().reset_index(name='count')
    for idx, row in combinations_after.iterrows():
        combo_str = ",".join(str(row[col]) for col in label_cols)
        print(f"   - To hop [{combo_str}]: {row['count']} dong")

    # Thống kê tổng quan
    print(f"\n[+] KET QUA LOC:")
    print(f"   - Tong so dong truoc khi loc: {total_before}")
    print(f"   - So dong giu lai:            {total_after} ({(total_after / total_before) * 100:.2f}%)")
    print(f"   - So dong da loai bo:         {removed_rows} ({(removed_rows / total_before) * 100:.2f}%)")

    # Lưu kết quả
    try:
        # Đảm bảo thư mục đầu ra tồn tại
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df_filtered.to_csv(output_path, index=False, encoding='utf-8')
        print(f"\n[+] Da luu file da loc tai: {os.path.abspath(output_path)}")
    except Exception as e:
        print(f"[-] Loi khi luu file output: {e}")
        return False

    return True


def main():
    parser = argparse.ArgumentParser(
        description="Lọc file CSV comment chỉ giữ lại các tổ hợp nhãn single-label (1,0,0,0; 0,1,0,0; 0,0,1,0; 0,0,0,1)."
    )
    parser.add_argument(
        'input_file',
        help='Đường dẫn đến file CSV cần lọc'
    )
    parser.add_argument(
        '-o', '--output',
        default=None,
        help='Đường dẫn đến file output (nếu không truyền, mặc định sẽ thêm "_filtered" vào tên file gốc)'
    )
    
    args = parser.parse_args()
    
    success = filter_comments(args.input_file, args.output)
    if not success:
        sys.exit(1)


if __name__ == '__main__':
    main()
