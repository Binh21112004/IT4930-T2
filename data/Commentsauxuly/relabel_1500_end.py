import pandas as pd
import sys

sys.stdout.reconfigure(encoding='utf-8')
file_path = r"C:\Users\admin\Desktop\KHDL\IT4930-T2\data\Commentsauxuly\comments_data_ncds_preprocessed_toy.csv"

# Read the csv
df = pd.read_csv(file_path)

# Smart heuristic function to classify the comments based on user's exact requirements
# Quality: defects, material, model, taste, date, authenticity
# Service: CSKH, false ads, missing promos/gifts, attitude, price, wrong item (giao sai mẫu/màu)
# Shipping: Speed, behavior, wrong/missing delivery
# Packing: Damaged boxes, insufficient protection, leaky packaging
def classify(text):
    text = str(text).lower()
    q, se, sh, p = 0, 0, 0, 0
    
    # PACKING
    packing_keywords = ['đóng gói', 'hộp', 'bao bì', 'móp', 'mé', 'bẹp', 'thùng', 'nắp', 'tem', 'niêm phong', 'băng keo', 'tràn', 'đổ', 'chảy', 'lót']
    if any(k in text for k in packing_keywords):
        p = 1
        
    # SHIPPING
    shipping_keywords = ['giao', 'shipper', 'vận chuyển', 'nhận hàng', 'chậm', 'nhanh', 'trễ', 'đợi', 'ninja van', 'ghn', 'j&t']
    if any(k in text for k in shipping_keywords):
        sh = 1
        
    # SERVICE
    service_keywords = ['cskh', 'chăm sóc', 'thái độ', 'giá', 'mắc', 'rẻ', 'đắt', 'tiền', 'quà', 'khuyến mãi', 'tặng', 'voucher', 'hỗ trợ', 'shop', 'cửa hàng', 'tiki', 'làm ăn', 'phản hồi', 'hoàn tiền', 'đổi trả', 'trả lại', 'lừa', 'treo đầu dê', 'niềm tin', 'uy tín', 'nhầm', 'thiếu', 'sai']
    if any(k in text for k in service_keywords):
        se = 1
        
    # QUALITY
    quality_keywords = ['chất lượng', 'tốt', 'kém', 'gãy', 'hỏng', 'mỏng', 'rách', 'mùi', 'hôi', 'ngọt', 'nhạt', 'nhỏ', 'to', 'chật', 'rộng', 'giống', 'fake', 'giả', 'date', 'hạn sử dụng', 'xước', 'cũ', 'bẩn', 'đẹp', 'xấu', 'sử dụng', 'dùng', 'xài', 'thấm', 'mềm', 'cứng', 'ngứa', 'vỡ', 'bể', 'thủng', 'ngon', 'dở', 'lỏng', 'đặc', 'hao', 'chắc chắn', 'ọp ẹp', 'lung lay', 'lỗi', 'đứt', 'bong', 'sản phẩm', 'ổn', 'chính hãng', 'không đáng', 'phí']
    if any(k in text for k in quality_keywords):
        q = 1
        
    # Overrides based on combinations and nuances
    if 'giao nhầm' in text or 'giao sai' in text or 'giao thiếu' in text or 'không đúng' in text:
        sh = 1 # Shipping
        se = 1 # Service (missing/wrong)

    if 'không giống hình' in text or 'khác hình' in text or 'như quảng cáo' in text or 'treo đầu dê' in text:
        q = 1
        se = 1 # False ads
        
    if 'bể' in text or 'vỡ' in text or 'gãy' in text or 'móp' in text:
        q = 1 # Quality defect
        if 'hộp' in text or 'thùng' in text or 'bao bì' in text:
            p = 1
            
    if 'thái độ' in text or 'nhân viên' in text or 'gọi' in text or 'tổng đài' in text:
        se = 1
        
    if q == 0 and se == 0 and sh == 0 and p == 0:
        q = 1 # Default to quality if it's about the item generally
        
    return q, se, sh, p

# Apply classification to rows 1500 to 2012
start_idx = 1500
end_idx = min(2013, len(df))

for idx in range(start_idx, end_idx):
    text = df.loc[idx, 'content']
    q, se, sh, p = classify(text)
    
    df.loc[idx, 'Quality'] = q
    df.loc[idx, 'Service'] = se
    df.loc[idx, 'Shipping'] = sh
    df.loc[idx, 'Packing'] = p

# Save the updated dataframe
df.to_csv(file_path, index=False)

# Calculate statistics
total_new = end_idx - start_idx
q_new = df.loc[start_idx:end_idx-1, 'Quality'].sum()
se_new = df.loc[start_idx:end_idx-1, 'Service'].sum()
sh_new = df.loc[start_idx:end_idx-1, 'Shipping'].sum()
p_new = df.loc[start_idx:end_idx-1, 'Packing'].sum()

print(f"Hoan thanh label {total_new} dong cuoi cung (index {start_idx}-{end_idx-1})!")
print("\n=== THONG KE RIENG CHO BATCH NAY ===")
print(f"  Quality: {q_new}/{total_new} dong co nhan 1 ({q_new/total_new*100:.1f}%)")
print(f"  Service: {se_new}/{total_new} dong co nhan 1 ({se_new/total_new*100:.1f}%)")
print(f"  Shipping: {sh_new}/{total_new} dong co nhan 1 ({sh_new/total_new*100:.1f}%)")
print(f"  Packing: {p_new}/{total_new} dong co nhan 1 ({p_new/total_new*100:.1f}%)")

print("\n=== THONG KE TOAN BO FILE DATASET ===")
q_total = df['Quality'].sum()
se_total = df['Service'].sum()
sh_total = df['Shipping'].sum()
p_total = df['Packing'].sum()
total_rows = len(df)

print(f"  Quality: {q_total}/{total_rows} ({q_total/total_rows*100:.1f}%)")
print(f"  Service: {se_total}/{total_rows} ({se_total/total_rows*100:.1f}%)")
print(f"  Shipping: {sh_total}/{total_rows} ({sh_total/total_rows*100:.1f}%)")
print(f"  Packing: {p_total}/{total_rows} ({p_total/total_rows*100:.1f}%)")
