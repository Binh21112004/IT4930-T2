#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tiền xử lý Comment với 5-step pipeline cho Multi-label Classification
Sử dụng: python preprocess_comments.py <đường_dẫn_file_csv>

Ví dụ:
  python preprocess_comments.py data/4-toys-tiki/result/comments_data_ncds.csv
  python preprocess_comments.py data/bachhoa-thoitrangnam-thethao/comments_data_ncds_cleaned.csv
"""

import pandas as pd
import os
import sys
import argparse
from preprocessing_multilabel import preprocess_comment_multilabel


def process_comment_file(input_path):
    """
    Xử lý file CSV comment bất kỳ
    
    Args:
        input_path: Đường dẫn file CSV cần xử lý
    
    Returns:
        Dict với thống kê: {before, after, removed_trash, removed_duplicates}
    """
    
    # Kiểm tra file tồn tại
    if not os.path.exists(input_path):
        print(f"❌ File không tồn tại: {input_path}")
        return None
    
    # Tạo tên file output - GHI ĐÈ TRỰC TIẾP LÊN FILE GỐC
    output_path = input_path
    
    # Kiểm tra file output đã tồn tại - tạo backup nếu cần
    if os.path.exists(output_path):
        backup_path = output_path.replace('.csv', '_backup.csv')
        try:
            import shutil
            shutil.copy(output_path, backup_path)
            print(f"📦 Backup file: {backup_path}")
        except:
            pass
    
    print(f"\n{'='*70}")
    print(f"📖 Đang xử lý: {input_path}")
    print(f"{'='*70}")
    
    # Đọc file CSV
    try:
        df = pd.read_csv(input_path)
    except Exception as e:
        print(f"❌ Lỗi khi đọc file: {e}")
        return None
    
    total_before = len(df)
    print(f"📊 Tổng dòng: {total_before}")
    
    # Kiểm tra cột 'content' tồn tại
    if 'content' not in df.columns:
        print(f"❌ Cột 'content' không tồn tại!")
        print(f"   Các cột có sẵn: {df.columns.tolist()}")
        return None
    
    # Áp dụng preprocessing
    print(f"⚙️  Đang tiền xử lý (5 bước)...")
    df['content_processed'] = df['content'].fillna('').apply(preprocess_comment_multilabel)
    
    # Loại bỏ dòng có content_processed = None (comment rác)
    df_cleaned = df[df['content_processed'].notna()].copy()
    total_after_trash = len(df_cleaned)
    removed_trash = total_before - total_after_trash
    
    # ========== DEDUPLICATION: Loại bỏ comment trùng ==========
    df_deduplicated = df_cleaned.drop_duplicates(subset=['content_processed'], keep='first')
    removed_dupes = total_after_trash - len(df_deduplicated)
    total_after_dedup = len(df_deduplicated)
    
    # ========== LỌC RATING: Chỉ giữ rating <= 3 sao ==========
    removed_low_rating = 0
    if 'rating' in df_deduplicated.columns:
        total_before_rating_filter = len(df_deduplicated)
        df_deduplicated = df_deduplicated[df_deduplicated['rating'] <= 3].copy()
        removed_low_rating = total_before_rating_filter - len(df_deduplicated)
    
    total_after = len(df_deduplicated)
    
    # In thống kê
    print(f"\n📊 THỐNG KÊ:")
    print(f"   Trước xử lý:        {total_before}")
    print(f"   Loại bỏ (rác):      {removed_trash} ({removed_trash/total_before*100:.1f}%)")
    print(f"   Loại bỏ (trùng):    {removed_dupes}")
    print(f"   Loại bỏ (rating>3): {removed_low_rating}")
    print(f"   Sau xử lý:          {total_after}")
    print(f"   Giữ lại:            {(total_after/total_before)*100:.1f}%")
    
    # Ghi đè cột content bằng content_processed, xóa content_processed
    df_deduplicated['content'] = df_deduplicated['content_processed']
    df_deduplicated = df_deduplicated.drop('content_processed', axis=1)
    
    # ========== TẠO NHÃN MULTI-LABEL (Quality, Service, Shipping, Packing) ==========
    # Rating 1-2 sao = 1 (Có khiếu nại), Rating 3 sao = 0 (Không có khiếu nại)
    if 'rating' in df_deduplicated.columns:
        # Xác định nhãn chính dựa trên rating
        complaint_label = df_deduplicated['rating'].apply(lambda x: 1 if x <= 2 else 0)
        
        # Gán nhãn cho 4 cột theo quy tắc:
        # - Nếu rating <= 2: Khiếu nại (1)
        # - Nếu rating == 3: Không khiếu nại (0)
        # Tất cả comments hiện tại đều chỉ được gán nhãn mặc định (chưa phân loại chi tiết)
        df_deduplicated['Quality'] = complaint_label
        df_deduplicated['Service'] = complaint_label
        df_deduplicated['Shipping'] = complaint_label
        df_deduplicated['Packing'] = complaint_label
    else:
        # Nếu không có rating column, mặc định là 0
        df_deduplicated['Quality'] = 0
        df_deduplicated['Service'] = 0
        df_deduplicated['Shipping'] = 0
        df_deduplicated['Packing'] = 0
    
    # Sắp xếp lại cột (giữ thứ tự: id, title, content, rating, Quality, Service, Shipping, Packing)
    if 'id' in df_deduplicated.columns:
        cols = ['id', 'title', 'content', 'rating', 'Quality', 'Service', 'Shipping', 'Packing']
    else:
        cols = ['title', 'content', 'rating', 'Quality', 'Service', 'Shipping', 'Packing']
    
    # Giữ các cột đó nếu tồn tại
    cols = [c for c in cols if c in df_deduplicated.columns]
    df_deduplicated = df_deduplicated[cols]
    
    # Lưu file
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df_deduplicated.to_csv(output_path, index=False, encoding='utf-8')
        print(f"\n✅ File đã được lưu: {output_path}")
    except Exception as e:
        print(f"❌ Lỗi khi lưu file: {e}")
        return None
    
    return {
        'input': input_path,
        'output': output_path,
        'before': total_before,
        'after': total_after,
        'removed_trash': removed_trash,
        'removed_duplicates': removed_dupes,
        'removed_low_rating': removed_low_rating
    }


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Tiền xử lý Comment với 5-step pipeline cho Multi-label Classification',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ví dụ sử dụng:
  python preprocess_comments.py data/4-toys-tiki/result/comments_data_ncds.csv
  python preprocess_comments.py data/bachhoa-thoitrangnam-thethao/comments_data_ncds_cleaned.csv
  python preprocess_comments.py data/nhacua-tiki/result/comments_data_ncds.csv
        """
    )
    
    parser.add_argument(
        'file',
        nargs='?',
        default=None,
        help='Đường dẫn đến file CSV cần xử lý (bỏ qua nếu dùng --batch)'
    )
    
    parser.add_argument(
        '--batch',
        nargs='+',
        help='Xử lý nhiều file cùng lúc (ví dụ: --batch file1.csv file2.csv file3.csv)'
    )
    
    args = parser.parse_args()
    
    # Kiểm tra: phải cung cấp file hoặc --batch
    if not args.file and not args.batch:
        parser.error("Phải cung cấp FILE hoặc dùng --batch")
    
    # Xử lý single file hoặc batch
    files_to_process = []
    
    if args.batch:
        files_to_process = args.batch
    elif args.file:
        files_to_process = [args.file]
    
    print("\n" + "="*70)
    print("TIỀN XỬ LÝ COMMENT - Multi-label Classification")
    print("="*70)
    
    results = []
    for file_path in files_to_process:
        result = process_comment_file(file_path)
        if result:
            results.append(result)
    
    # Hiển thị tổng kết
    if results:
        print("\n" + "="*70)
        print("TỔNG KẾT")
        print("="*70)
        
        total_before_all = 0
        total_after_all = 0
        total_trash_all = 0
        total_dupes_all = 0
        
        for result in results:
            print(f"\n📁 {result['input']}")
            print(f"   Trước: {result['before']} | Trash: {result['removed_trash']} | Trùng: {result['removed_duplicates']} | Rating>3: {result['removed_low_rating']} | Sau: {result['after']}")
            print(f"   ➜ {result['output']}")
            
            total_before_all += result['before']
            total_after_all += result['after']
            total_trash_all += result['removed_trash']
            total_dupes_all += result['removed_duplicates']
        
        print(f"\n{'TỔNG CỘNG':}")
        print(f"   Trước: {total_before_all} | Trash: {total_trash_all} | Trùng: {total_dupes_all} | Sau: {total_after_all}")
        print("="*70)
        
        print(f"\n✅ Hoàn thành xử lý {len(results)} file!")
    else:
        print("\n❌ Không có file nào được xử lý thành công")
        sys.exit(1)


if __name__ == "__main__":
    main()
