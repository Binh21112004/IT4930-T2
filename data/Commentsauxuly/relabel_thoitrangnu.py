import pandas as pd
import re

FILE_PATH = r"C:\Users\admin\Desktop\KHDL\IT4930-T2\data\Commentsauxuly\comments_data_ncds_preprocessed_thoitrangnu.csv"

SHIPPING_PATTERNS = [
    r'giao\s+(nhanh|chậm|đúng|sai|nhầm|thiếu|không đúng)',
    r'giao hàng',
    r'đặt.{1,30}(nhưng|lại).{1,30}(giao|nhận|gửi)',
    r'(nhưng|lại).{1,20}giao.{1,20}(size|màu|sản phẩm|áo|quần)',
    r'chưa nhận được',
    r'không nhận được',
    r'nhận hàng',
    r'nhận sản phẩm',
    r'nhận về',
    r'vận chuyển',
    r'\bship\b',
    r'giao (về|đến|tới)',
    r'giao (đúng|sai|nhầm)',
    r'(đặt|order).{1,20}(giao|nhận)',
]

QUALITY_PATTERNS = [
    r'chất (vải|lượng|liệu)',
    r'\bvải\b',
    r'co dãn',
    r'\b(mỏng|dày|cứng|mềm|thô)\b',
    r'size.{0,20}(chật|rộng|nhỏ|lớn|vừa|không mặc)',
    r'mặc.{0,20}(không|thoải|chật|rộng|vừa|hằn)',
    r'\bhằn\b',
    r'không giống (mẫu|hình|ảnh)',
    r'không (như|giống).{0,20}(quảng cáo|giới thiệu|mô tả|hình)',
    r'treo đầu dê',
    r'đường may',
    r'\brách\b',
    r'\bgiãn\b',
    r'\bphai\b',
    r'form (áo|quần)',
    r'màu.{0,20}(xấu|ghê|chói|không đẹp|sặc sỡ|rẻ tiền|tệ)',
    r'\bcó mùi\b',
    r'\b(nhái|đểu)\b',
    r'mắc.{0,20}(xấu|kém)',
    r'không đáng (giá|tiền)',
    r'chất lượng',
    r'sản phẩm.{0,20}(xấu|kém|tệ|đểu|không đẹp)',
    r'(xấu|kém).{0,20}(chất|vải)',
    r'không như (mong đợi|kỳ vọng)',
    r'thất vọng.{0,30}(chất|sản phẩm|vải)',
    r'(sản phẩm|hàng).{0,20}không (như|giống)',
    r'quảng cáo.{0,30}(nẻo|khác|không đúng)',
    r'mặc (không|chật|rộng)',
    r'(áo|quần).{0,30}(xấu|kém|tệ|không đẹp)',
    r'(chất|vải).{0,20}(kém|tệ|xấu|thô|mỏng|không mềm)',
    r'(size|cỡ).{0,20}(lớn nhất|nhỏ nhất)',
    r'không co dãn',
    r'\bgiá cao\b',
    r'(tốn tiền|uổng tiền)',
]

SERVICE_PATTERNS = [
    r'tư vấn',
    r'cửa (hàng|sản phẩm)',
    r'(thiên vị|ưu tiên).{0,20}(màu|khách)',
    r'đổi (trả|size|hàng)',
    r'\bhỗ trợ\b',
    r'chính sách',
    r'liên hệ.{0,20}(tôi|shop|cửa)',
    r'shop.{0,20}(tệ|kém|không)',
]

PACKING_PATTERNS = [
    r'đóng gói',
    r'\bbao bì\b',
    r'(hộp|túi|bao).{0,20}(bẩn|cũ|hỏng|dơ|rách)',
    r'gói hàng',
    r'niêm phong',
]

def classify(text):
    t = str(text).lower()
    shipping = int(any(re.search(p, t) for p in SHIPPING_PATTERNS))
    quality  = int(any(re.search(p, t) for p in QUALITY_PATTERNS))
    service  = int(any(re.search(p, t) for p in SERVICE_PATTERNS))
    packing  = int(any(re.search(p, t) for p in PACKING_PATTERNS))
    return quality, service, shipping, packing

def main():
    df = pd.read_csv(FILE_PATH)
    print(f"Loaded {len(df)} rows")
    print("Label distribution before:")
    print(df[['Quality','Service','Shipping','Packing']].apply(pd.Series.value_counts))

    results = df['content'].apply(classify)
    df['Quality']  = [r[0] for r in results]
    df['Service']  = [r[1] for r in results]
    df['Shipping'] = [r[2] for r in results]
    df['Packing']  = [r[3] for r in results]

    print("\nLabel distribution after:")
    print(df[['Quality','Service','Shipping','Packing']].apply(pd.Series.value_counts))

    # Sample 15 rows for review
    print("\n--- SAMPLE 15 ROWS (first 15) ---")
    for _, row in df.head(15).iterrows():
        label = f"Q={row['Quality']} Sv={row['Service']} Sh={row['Shipping']} P={row['Packing']}"
        content = str(row['content'])[:80].encode('ascii', errors='replace').decode('ascii')
        print(f"{label} | {content}")

    df.to_csv(FILE_PATH, index=False)
    print(f"\nDone. Saved to {FILE_PATH}")

if __name__ == "__main__":
    main()
