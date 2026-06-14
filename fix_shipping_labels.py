#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sửa lỗi gán nhãn trong tệp comments_merged_single_label.csv.
Chuyển các bình luận bị hỏng hóc do vận chuyển/giao hàng từ nhãn 'Quality' (Chất lượng) 
sang nhãn 'Shipping' (Vận chuyển).

Đồng thời tự động chạy lại augment_data.py để đồng bộ hóa dữ liệu tập huấn luyện.
"""

import os
import re
import pandas as pd


def load_csv_robustly(input_path):
    # Pattern khớp với 4 nhãn nhị phân ở cuối dòng
    record_pattern = re.compile(r',\s*([01])\s*,\s*([01])\s*,\s*([01])\s*,\s*([01])\s*$')
    
    records = []
    current_content = []
    
    with open(input_path, 'r', encoding='utf-8') as f:
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
    return df


def main():
    csv_path = "data/Commentsauxuly/comments_merged_single_label.csv"
    if not os.path.exists(csv_path):
        print(f"[-] Tệp không tồn tại: {csv_path}")
        return

    print(f"\n{'='*70}")
    print(f"[*] Đang đọc và phân tích dữ liệu: {csv_path}")
    print(f"{'='*70}")
    
    df = load_csv_robustly(csv_path)
    total_rows = len(df)
    
    # Định nghĩa các mẫu regex nhận diện hư hỏng do vận chuyển
    shipping_damage_patterns = [
        # 1. Hư hại + do/vì/tại + bên vận chuyển
        r'(?:hỏng|hư|vỡ|bể|nát|móp|méo|trầy|xước|dập|cong|gãy|nứt|bẹp|rách|sứt|móp méo|hư hỏng|bể vỡ|nát bét)\s+(?:do|tại|vì|trong quá trình|bởi|từ|do bên|tại bên)\s+(?:bên\s+|đơn vị\s+|nhà\s+|cách\s+)?(?:vận chuyển|van chuyen|shipper|giao hàng|ship|giao nhận|giao hang)',
        # 2. Vận chuyển/shipper làm hỏng/vỡ
        r'(?:vận chuyển|van chuyen|shipper|bên giao|giao hàng|ship)\s+(?:làm|quăng|ném|vứt|làm hỏng|làm vỡ|làm rách|làm móp|lam)\s+(?:hư|hỏng|vỡ|bể|nát|móp|méo|trầy|xước|bẹp|dập|gãy|rách|sứt|hư hỏng)',
        # 3. Giao đến bị hư/hỏng
        r'giao\s+(?:đến|tới|hành|sản phẩm|hang|sp)\s+(?:thì|bị|đã|da)\s+(?:hỏng|hư|vỡ|bể|nát|móp|méo|trầy|xước|dập|cong|gãy|nứt|bẹp|rách|sứt|hư hỏng|bể vỡ)',
        # 4. Shipper cẩu thả làm hỏng
        r'shipper\s+(?:cẩu thả|bất cẩn|ném|quăng|vứt|làm mất|làm hỏng|làm vỡ)',
        # 5. Hư hỏng do quá trình vận chuyển
        r'(?:móp|méo|bể|vỡ|rách|hỏng|trầy|xước|hư|hư hỏng)\s+(?:do\s+)?(?:quá trình|qua trinh|khâu|khau)\s+(?:vận chuyển|van chuyen|giao hàng|ship)'
    ]
    
    # Định nghĩa các mẫu nhận diện hư hỏng do đóng gói ẩu, sơ sài
    packing_damage_patterns = [
        # 1. Hư hại + do/vì/tại + đóng gói/bọc hàng ẩu, sơ sài
        r'(?:hỏng|hư|vỡ|bể|nát|móp|méo|trầy|xước|dập|cong|gãy|nứt|bẹp|rách|sứt|móp méo|hư hỏng|bể vỡ|nát bét)\s+(?:do|tại|vì|bởi|do cách|vì cách|tại cách)\s+(?:bên\s+|đơn vị\s+|nhà\s+|cách\s+)?(?:đóng gói|gói hàng|bọc hàng|đóng hàng|gói cẩu thả|đóng cẩu thả|gói ẩu|đóng ẩu|bao bọc|đóng hộp)',
        # 2. Đóng gói ẩu/sơ sài làm hư hỏng sản phẩm
        r'(?:đóng gói|gói hàng|bọc hàng|đóng hàng|gói|đóng|bao bọc)\s+(?:ẩu|kém|tệ|sơ sài|cẩu thả|không cẩn thận|lỏng lẻo|không kĩ|không kỹ)\s+(?:làm|gây|khiến|lam)\s+(?:hư|hỏng|vỡ|bể|nát|móp|méo|trầy|xước|bẹp|dập|gãy|rách|sứt|hư hỏng)',
        # 3. Móp méo/bể vỡ do khâu đóng gói
        r'(?:móp|méo|bể|vỡ|rách|hỏng|trầy|xước|hư|hư hỏng)\s+(?:do\s+)?(?:khâu|khau|cách|khâu đóng gói)\s+(?:đóng gói|gói hàng|bọc hàng|gói)',
        # 4. Đóng gói quá cẩu thả làm rách/móp
        r'(?:đóng gói|gói hàng|bọc hàng)\s+quá\s+(?:ẩu|sơ sài|kém|tệ|lỏng lẻo|cẩu thả|sơ sài|hời hợt)'
    ]
    
    shipping_pattern = re.compile("|".join(shipping_damage_patterns), re.IGNORECASE)
    packing_pattern = re.compile("|".join(packing_damage_patterns), re.IGNORECASE)
    
    corrected_count = 0
    corrected_examples = []
    
    for idx, row in df.iterrows():
        content = str(row['content'])
        
        # 1. Kiểm tra lỗi vận chuyển trước
        if shipping_pattern.search(content):
            if row['Shipping'] != 1:
                prev_labels = f"Q={row.Quality} Sv={row.Service} Sh={row.Shipping} P={row.Packing}"
                df.at[idx, 'Quality'] = 0
                df.at[idx, 'Service'] = 0
                df.at[idx, 'Shipping'] = 1
                df.at[idx, 'Packing'] = 0
                corrected_count += 1
                corrected_examples.append((content, prev_labels, "Shipping"))
                
        # 2. Kiểm tra lỗi đóng gói ẩu làm hỏng đồ
        elif packing_pattern.search(content):
            if row['Packing'] != 1:
                prev_labels = f"Q={row.Quality} Sv={row.Service} Sh={row.Shipping} P={row.Packing}"
                df.at[idx, 'Quality'] = 0
                df.at[idx, 'Service'] = 0
                df.at[idx, 'Shipping'] = 0
                df.at[idx, 'Packing'] = 1
                corrected_count += 1
                corrected_examples.append((content, prev_labels, "Packing"))

    print(f"\n[+] ĐÃ PHÁT HIỆN VÀ SỬA ĐỔI: {corrected_count} dòng dữ liệu.")
    
    if corrected_count > 0:
        print("\n[*] Danh sách một số dòng được sửa đổi nhãn:")
        for content, prev, new_label in corrected_examples[:15]:
            print(f"   - Trước sửa: [{prev}] -> Sau sửa: [{new_label}=1, các nhãn còn lại=0]")
            print(f"     Nội dung:  \"{content[:150]}...\"\n")
            
        # Lưu đè lại file comments_merged_single_label.csv
        try:
            df.to_csv(csv_path, index=False, encoding='utf-8')
            print(f"✅ Đã cập nhật và ghi đè file: {csv_path}")
            
            # Chạy lại augment_data.py để đồng bộ hóa dữ liệu tăng cường
            print("\n[*] Đang tự động chạy lại augment_data.py để đồng bộ hóa tập huấn luyện...")
            import subprocess
            result = subprocess.run(
                ["python", "augment_data.py"],
                capture_output=True,
                text=True,
                env=dict(os.environ, PYTHONIOENCODING="utf-8")
            )
            print(result.stdout)
            if result.returncode == 0:
                print("✅ Đã đồng bộ thành công tập dữ liệu tăng cường augmented.csv!")
            else:
                print("❌ Lỗi khi chạy augment_data.py:")
                print(result.stderr)
                
        except Exception as e:
            print(f"❌ Lỗi khi lưu file: {e}")
    else:
        print("💡 Không phát hiện dòng nào cần sửa đổi thêm nhãn.")


if __name__ == '__main__':
    main()
