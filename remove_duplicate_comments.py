import pandas as pd

categories = [
    'lam-dep-suc-khoe-tiki',
    'thoi-trang-nu-tiki',
    'bach-hoa-online-tiki'
]

for category in categories:
    csv_path = f'data/{category}/result/comments_data_ncds.csv'
    print(f'\n=== Lọc trùng lặp cho {category} ===')
    
    try:
        df = pd.read_csv(csv_path)
        print(f'Số bình luận trước: {len(df)}')
        
        # Loại bỏ trùng lặp theo id (giữ lại bản ghi đầu tiên)
        df_unique = df.drop_duplicates(subset=['id'], keep='first')
        print(f'Số bình luận sau: {len(df_unique)}')
        print(f'Số bình luận bị loại bỏ: {len(df) - len(df_unique)}')
        
        # Lưu lại file
        df_unique.to_csv(csv_path, index=False)
        print(f'Đã lưu file: {csv_path}')
    except Exception as e:
        print(f'Lỗi khi xử lý {category}: {e}')

print('\n=== Hoàn tất lọc trùng lặp ===')
