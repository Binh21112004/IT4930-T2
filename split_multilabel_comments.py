#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tách mệnh đề từ các bình luận đa nhãn (Multi-label) để trích xuất thêm dữ liệu đơn nhãn (Single-label)
cho các lớp thiểu số: Service, Shipping, Packing.

Script này thực hiện:
1. Quét tất cả các file CSV tiền xử lý gốc trong thư mục data/Commentsauxuly/.
2. Đọc toàn bộ dữ liệu (bao gồm cả dòng đa nhãn).
3. Lọc ra các dòng đa nhãn (tổng số nhãn >= 2).
4. Sử dụng Regex để chặt nhỏ câu thành các mệnh đề.
5. Chỉ giữ lại các mệnh đề có chứa từ khóa liên quan đến Service, Shipping, Packing (loại bỏ Quality).
6. Ghép các mệnh đề này lại thành một câu hoàn chỉnh mới.
7. Gán lại nhãn dựa trên các mệnh đề được chọn (nhãn Quality mặc định = 0).
8. Nếu câu mới tạo ra là đơn nhãn (chỉ có đúng 1 nhãn bằng 1), ta sẽ lưu lại và gộp vào comments_merged_single_label.csv.
9. Tự động chạy lại quy trình tăng cường dữ liệu augment_data.py để đồng bộ hóa.
"""

import os
import re
import shutil
import subprocess
import pandas as pd

# Định nghĩa các liên từ và dấu câu để tách câu
CONJUNCTIONS = [
    r'\bnhưng mà\b', r'\bnhưng\b', r'\btuy nhiên\b', r'\bmỗi tội\b', 
    r'\bchỉ có điều\b', r'\bchỉ mỗi tội\b', r'\bcó điều\b', r'\bcơ mà\b',
    r'\bbù lại\b', r'\bvới lại\b', r'\bhơn nữa\b', r'\bđồng thời\b'
]
PUNCTUATION_PATTERN = r'[,.;!?\n()\-]+|\s+(?:' + '|'.join(CONJUNCTIONS) + r')\s+'

# Từ khóa nhận diện nhóm Shipping (Vận chuyển)
SHIPPING_KEYWORDS = [
    r'ship', r'giao hàng', r'giao hang', r'vận chuyển', r'van chuyen', 
    r'giao nhận', r'giao nhan', r'gửi hàng', r'gui hang', r'shipper', r'shiper', 
    r'giao tới', r'giao toi', r'giao đến', r'giao den', r'giao lâu', r'giao lau', 
    r'giao nhanh', r'giao chậm', r'giao cham', r'giao muộn', r'giao muon', 
    r'giao trễ', r'giao tre', r'nhận hàng', r'nhan hang', r'giao hàng nhanh',
    r'giao hàng chậm', r'ship nhanh', r'ship chậm', r'bên giao', r'ben giao',
    r'gửi lâu', r'gui lau', r'nhận trễ', r'nhan tre', r'chuyển hàng', r'chuyen hang',
    # Các mẫu linh hoạt hơn
    r'giao\s+(?:\w+\s+){0,3}(?:nhanh|chậm|cham|lâu|lau|trễ|tre|sớm|som|muộn|muon|lẹ|le)',
    r'ship\s+(?:\w+\s+){0,3}(?:nhanh|chậm|cham|lâu|lau|trễ|tre|sớm|som|muộn|muon|lẹ|le)',
    r'giao\s+(?:sản phẩm|sp|hàng|hang|đồ|do|sách|sach|máy|may|cốc|cọc|dây|giày|áo|quần)'
]

# Từ khóa nhận diện nhóm Packing (Đóng gói)
PACKING_KEYWORDS = [
    r'đóng gói', r'dong goi', r'gói hàng', r'goi hang', r'bọc hàng', r'boc hang', 
    r'đóng hàng', r'dong hang', r'bao bọc', r'bao boc', r'hộp carton', r'vỏ hộp', 
    r'vo hop', r'bọc chống sốc', r'chong soc', r'bọc bóng khí', r'quấn bong bóng', 
    r'quấn xốp', r'quấn kỹ', r'quấn kĩ', r'hộp méo', r'móp hộp', r'hộp rách', 
    r'rách hộp', r'hộp bẹp', r'đóng ẩu', r'đóng cẩu thả', r'đóng sơ sài', 
    r'gói ẩu', r'gói sơ sài', r'gói cẩu thả', r'đóng hộp', r'bọc kĩ', r'bọc kỹ',
    r'móp méo hộp', r'thùng carton', r'chống va đập', r'bọc túi', r'quấn băng keo',
    # Các mẫu linh hoạt hơn
    r'đóng gói\s+(?:\w+\s+){0,3}(?:cẩn thận|kỹ|kĩ|đẹp|ẩu|sơ sài|tệ|kém|chắc chắn|cẩu thả|qua loa)',
    r'gói\s+(?:sản phẩm|sp|hàng|hang|đồ|do|sách|sach|máy|may|cốc|cọc|dây|giày|áo|quần)\s+(?:\w+\s+){0,3}(?:cẩn thận|kỹ|kĩ|đẹp|ẩu|sơ sài|tệ|kém|chắc chắn|cẩu thả|qua loa)'
]

# Từ khóa nhận diện nhóm Service (Dịch vụ)
SERVICE_KEYWORDS = [
    r'tư vấn', r'tu van', r'chăm sóc', r'cham soc', r'hỗ trợ', r'ho tro', 
    r'giải đáp', r'giai dap', r'phản hồi', r'phan hoi', r'trả lời', r'tra loi', 
    r'inbox', r'nhắn tin', r'nhan tin', r'chat', r'thái độ', r'thai do', 
    r'phục vụ', r'phuc vu', r'nhiệt tình', r'nhiet tinh', r'đổi trả', r'doi tra', 
    r'hoàn tiền', r'hoan tien', r'trả hàng', r'tra hang', r'lừa đảo', r'lua dao', 
    r'giải quyết', r'giai quyet', r'quà tặng', r'qua tang', r'tặng kèm', r'tang kem', 
    r'phục vụ khách', r'phuc vu khach', r'rep tin', r'rep ib', r'rep chậm', 
    r'rep nhanh', r'tư vấn nhiệt tình', r'shop thái độ', r'cửa hàng tư vấn',
    r'thân thiện', r'than thien', r'chủ shop', r'chu shop', r'gọi điện', r'goi dien',
    r'alo', r'liên hệ', r'lien he', r'đền', r'den bù', r'den bu', r'hỗ trợ khách',
    # Các mẫu linh hoạt hơn
    r'(?:tư vấn|hỗ trợ|chăm sóc|phục vụ)\s+(?:\w+\s+){0,3}(?:nhiệt tình|tốt|tệ|kém|chu đáo|thân thiện|nhanh|chậm|tận tình|tận tâm)',
    r'thái độ\s+(?:\w+\s+){0,3}(?:tệ|lồi lõm|kém|tốt|lịch sự|nhã nhặn|ko tốt|không tốt|khó chịu)'
]

# Biên dịch trước các regex
SHIPPING_PATTERN = re.compile("|".join(SHIPPING_KEYWORDS), re.IGNORECASE)
PACKING_PATTERN = re.compile("|".join(PACKING_KEYWORDS), re.IGNORECASE)
SERVICE_PATTERN = re.compile("|".join(SERVICE_KEYWORDS), re.IGNORECASE)


def load_raw_csv_robustly(file_path):
    """
    Đọc robust một file dữ liệu CSV gốc, giữ lại toàn bộ dữ liệu bao gồm cả đa nhãn.
    """
    record_pattern = re.compile(r',\s*([01])\s*,\s*([01])\s*,\s*([01])\s*,\s*([01])\s*$')
    records = []
    current_content = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        header_line = f.readline()
        if not header_line:
            return pd.DataFrame(columns=['content', 'Quality', 'Service', 'Shipping', 'Packing'])
        
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


def split_into_clauses(text):
    """
    Tách nội dung thành các mệnh đề nhỏ hơn.
    """
    if not isinstance(text, str):
        return []
    
    parts = re.split(PUNCTUATION_PATTERN, text, flags=re.IGNORECASE)
    clauses = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        # Loại bỏ các từ nối thừa ở đầu câu sau khi chặt câu
        part = re.sub(r'^(?:mà|còn|thì|là|và|nhưng|tuy nhiên|có điều|mỗi tội)\s+', '', part, flags=re.IGNORECASE).strip()
        # Chỉ giữ lại các mệnh đề có độ dài hợp lý
        if len(part.split()) >= 1 and len(part) >= 3:
            clauses.append(part)
    return clauses


def classify_clause(clause):
    """
    Phân loại mệnh đề thuộc nhóm Service, Shipping hoặc Packing dựa trên từ khóa.
    """
    is_shipping = bool(SHIPPING_PATTERN.search(clause))
    is_packing = bool(PACKING_PATTERN.search(clause))
    is_service = bool(SERVICE_PATTERN.search(clause))
    return is_shipping, is_packing, is_service


def process_multilabel_comment(text):
    """
    Tách câu, chỉ giữ lại phần liên quan đến Shipping, Packing, Service 
    và dựng lại thành một câu hoàn chỉnh mới với nhãn tương ứng.
    """
    clauses = split_into_clauses(text)
    kept_clauses = []
    
    has_shipping = False
    has_packing = False
    has_service = False
    
    for clause in clauses:
        is_sh, is_pk, is_sv = classify_clause(clause)
        if is_sh or is_pk or is_sv:
            kept_clauses.append(clause)
            if is_sh:
                has_shipping = True
            if is_pk:
                has_packing = True
            if is_sv:
                has_service = True
                
    if kept_clauses:
        # Gộp các mệnh đề được giữ lại
        new_text = ", ".join(kept_clauses)
        # Viết hoa chữ cái đầu cho câu hoàn chỉnh
        new_text = new_text[0].upper() + new_text[1:] if new_text else ""
        return new_text, 0, int(has_service), int(has_shipping), int(has_packing)
        
    return "", 0, 0, 0, 0


def main():
    data_dir = r"data/Commentsauxuly"
    master_csv_path = os.path.join(data_dir, "comments_merged_single_label.csv")
    
    if not os.path.exists(data_dir):
        print(f"[-] Thư mục không tồn tại: {data_dir}")
        return

    # Quét các file CSV danh mục gốc
    all_files = os.listdir(data_dir)
    target_files = []
    for f in all_files:
        if f.startswith("comments_data_ncds_preprocessed_") and f.endswith(".csv"):
            if "_filtered" not in f and "_merged" not in f and "_split" not in f:
                target_files.append(f)

    if not target_files:
        print("[-] Không tìm thấy file dữ liệu gốc để xử lý!")
        return

    print(f"\n{'='*70}")
    print(f"[*] Bắt đầu đọc dữ liệu thô và tìm các comment đa nhãn...")
    print(f"{'='*70}")

    all_raw_dfs = []
    for file_name in sorted(target_files):
        file_path = os.path.join(data_dir, file_name)
        df_file = load_raw_csv_robustly(file_path)
        all_raw_dfs.append(df_file)
        print(f"   + Đã đọc file '{file_name}': {len(df_file)} dòng")

    df_all = pd.concat(all_raw_dfs, ignore_index=True)
    total_raw_rows = len(df_all)
    print(f"\n[+] Tổng số dòng dữ liệu thô tích lũy: {total_raw_rows}")

    # Lọc ra các dòng đa nhãn (tổng nhãn >= 2)
    label_cols = ['Quality', 'Service', 'Shipping', 'Packing']
    for col in label_cols:
        df_all[col] = df_all[col].fillna(0).astype(int)
        
    df_multilabel = df_all[df_all[label_cols].sum(axis=1) >= 2].copy()
    print(f"[+] Số dòng đa nhãn (Labels >= 2): {len(df_multilabel)} ({len(df_multilabel)/total_raw_rows*100:.2f}%)")

    # Tiến hành tách câu và lọc mệnh đề
    print(f"\n[*] Đang thực hiện thuật toán tách mệnh đề và lọc các lớp thiểu số...")
    split_records = []
    
    for idx, row in df_multilabel.iterrows():
        original_content = row['content']
        new_content, q, sv, sh, pk = process_multilabel_comment(original_content)
        
        if new_content:
            # Kiểm tra xem có phải là câu đơn nhãn sạch của lớp thiểu số hay không
            # Nghĩa là tổng nhãn sau khi lọc bằng 1 và nhãn Quality = 0
            if (q == 0) and (sv + sh + pk == 1):
                split_records.append({
                    'original_content': original_content,
                    'content': new_content,
                    'Quality': q,
                    'Service': sv,
                    'Shipping': sh,
                    'Packing': pk
                })

    df_split = pd.DataFrame(split_records)
    print(f"[+] Trích xuất thành công {len(df_split)} câu đơn nhãn sạch từ dữ liệu đa nhãn!")

    if len(df_split) == 0:
        print("[-] Không trích xuất được câu đơn nhãn nào từ các bình luận đa nhãn. Dừng chương trình.")
        return

    # Thống kê phân bố nhãn sau khi tách
    print("\n[+] Phân bố nhãn các câu được trích xuất mới:")
    for col in ['Service', 'Shipping', 'Packing']:
        count = len(df_split[df_split[col] == 1])
        print(f"   - {col:10}: {count} dòng")

    # In ra một số ví dụ Before -> After
    print("\n[*] Ví dụ một số câu đã được chặt và tách thành công:")
    sample_df = df_split.sample(n=min(10, len(df_split)), random_state=42)
    for idx, row in sample_df.iterrows():
        label_name = ""
        for col in ['Service', 'Shipping', 'Packing']:
            if row[col] == 1:
                label_name = col
        print(f"   - Trước: \"{row['original_content'][:120]}...\"")
        print(f"   - Sau:   \"{row['content']}\" -> [{label_name}]")
        print()

    # Lưu lại file kết quả tách riêng biệt để theo dõi
    split_output_path = os.path.join(data_dir, "comments_split_from_multilabel.csv")
    df_split_to_save = df_split[['content', 'Quality', 'Service', 'Shipping', 'Packing']]
    df_split_to_save.to_csv(split_output_path, index=False, encoding='utf-8')
    print(f"✅ Đã lưu dữ liệu tách tại: {os.path.abspath(split_output_path)}")

    # GỘP VÀO MASTER SINGLE LABEL DATASET
    if os.path.exists(master_csv_path):
        # Khôi phục từ bản sao lưu nếu có để dữ liệu bắt đầu sạch sẽ
        backup_path = master_csv_path + ".bak"
        if os.path.exists(backup_path):
            print(f"[*] Khôi phục file Master gốc từ bản sao lưu: {backup_path}")
            shutil.copyfile(backup_path, master_csv_path)
        else:
            # Tạo bản sao lưu lần đầu tiên
            shutil.copyfile(master_csv_path, backup_path)
            print(f"   + Đã tạo bản sao lưu tại: {backup_path}")
            
        print(f"\n[*] Đang tiến hành gộp {len(df_split_to_save)} dòng mới vào file Master: {master_csv_path}")
        
        # Đọc dữ liệu Master hiện tại
        df_master = pd.read_csv(master_csv_path)
        print(f"   + Số dòng Master hiện tại: {len(df_master)}")
        
        # Ghép thêm dữ liệu mới
        df_master_combined = pd.concat([df_master, df_split_to_save], ignore_index=True)
        
        # Loại bỏ các dòng trùng lặp hoàn toàn nếu có
        len_before_drop = len(df_master_combined)
        df_master_combined = df_master_combined.drop_duplicates(subset=['content']).reset_index(drop=True)
        dropped_count = len_before_drop - len(df_master_combined)
        if dropped_count > 0:
            print(f"   + Đã loại bỏ {dropped_count} dòng trùng lặp nội dung.")
            
        # Ghi đè lại Master
        df_master_combined.to_csv(master_csv_path, index=False, encoding='utf-8')
        print(f"✅ Gộp thành công! Số dòng Master mới: {len(df_master_combined)}")
        
        # Thống kê phân bố nhãn Master mới
        print("\n[+] Phân bố nhãn Master sau khi gộp:")
        for col in label_cols:
            count = len(df_master_combined[df_master_combined[col] == 1])
            print(f"   - {col:10}: {count} dòng")

        # TỰ ĐỘNG CHẠY LẠI AUGMENT_DATA.PY ĐỂ ĐỒNG BỘ TẬP DỮ LIỆU TĂNG CƯỜNG
        print("\n[*] Đang tự động chạy lại augment_data.py để đồng bộ tập dữ liệu tăng cường...")
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
    else:
        print(f"[-] Không tìm thấy file Master '{master_csv_path}', vui lòng tạo file Master trước.")


if __name__ == '__main__':
    main()
