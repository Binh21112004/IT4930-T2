import pandas as pd
import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

# --------------- KEYWORD DICTIONARIES ---------------

# Quality: complaints about product quality, defects, not as described
QUALITY_NEG = [
    # Direct quality complaints
    r'chất lượng\s*(kém|tệ|xấu|thấp|không tốt|quá kém|quá tệ|rất kém|rất tệ|thật tệ|tồi|dở)',
    r'kém chất lượng', r'hàng (kém|lỗi|hỏng|tệ|xấu|giả|nhái|fake)',
    r'sản phẩm (kém|lỗi|hỏng|tệ|xấu|giả|nhái|fake|bị hỏng|bị lỗi)',
    # Defects
    r'\blỗi\b', r'\bhỏng\b', r'\bbị hư\b', r'bị hỏng', r'bị lỗi',
    r'\bvỡ\b', r'\bbể\b', r'\bnứt\b', r'\bthủng\b', r'\btrầy\b', r'\bxước\b',
    r'linh kiện\s*(lỏng|vỡ|hỏng)', r'tiếng kêu', r'kêu lạ',
    # Performance issues
    r'\blag\b', r'\btreo\b', r'\bđơ\b', r'\bnhiễu\b',
    r'tự động\s*(tắt|khởi động lại|reset)',
    r'pin\s*(yếu|kém|nhanh hết|mau hết|chết nhanh)',
    r'màn hình\s*(mờ|vỡ|nứt|đen|tối|nhòe|xước)',
    r'hình\s*(mờ|ảnh mờ)', r'không nét',
    r'không\s*(hoạt động|dùng được|sài được|chạy được|nhận|kết nối được)',
    r'không\s*(bắt được|nhận được)\s*wifi',
    r'không\s*(đúng|như|giống)\s*(mô tả|hình|quảng cáo|ảnh|mẫu)',
    r'không đúng như', r'không như mô tả', r'không giống hình', r'không giống mô tả',
    r'không đúng mô tả', r'khác (với|so với) mô tả',
    # Fake / counterfeit
    r'\bfake\b', r'\bgiả\b', r'\bnhái\b', r'hàng nhái', r'hàng giả',
    # General dissatisfaction
    r'thất vọng', r'tệ quá', r'kém quá', r'rất tệ', r'rất kém',
    r'không xài được', r'không sử dụng được', r'không dùng được',
    r'không hoạt động', r'không dùng được',
    r'mua phải cái (lỗi|hỏng|tệ)', r'nhanh hỏng', r'mau hỏng',
    r'yếu quá', r'rất yếu',
    r'cài đặt mãi (nhưng )?không', r'khó cài đặt',
    r'không nhận wifi', r'không bắt được wifi', r'disconnected', r'disconected',
    r'tốc độ\s*(chậm|thấp|kém)',
    r'không\s*hỗ trợ\s*(wifi|5ghz|5g|chuẩn)',
    r'thiếu\s*(driver)',  # missing driver only for quality
    r'bị\s*(lỏng|vỡ|hỏng|lỗi)',
    r'hàng\s*(không đúng|sai)',
]

# General disappointment patterns that imply ALL categories are bad
GENERAL_NEG = [
    r'tất cả\s*(đều|đều là|đều rất)\s*(tệ|kém|xấu|tồi)',
    r'mọi\s*thứ\s*(đều|đều là)\s*(tệ|kém|xấu)',
    r'toàn\s*bộ\s*(đều|đều là)\s*(tệ|kém|xấu)',
    r'tất cả\s*đều tệ', r'tất cả đều kém',
]

# Service: complaints about customer service, support, warranty
SERVICE_NEG = [
    r'dịch vụ\s*(kém|tệ|xấu|không tốt)',
    r'hỗ trợ\s*(kém|tệ|xấu|không|tồi)',
    r'không\s*(hỗ trợ|phản hồi|trả lời|giải quyết|xử lý)',
    r'cửa (hàng|sản phẩm|shop)\s*(thái độ|tệ|kém|không hỗ trợ|không trả|chiếm)',
    r'shop\s*(thái độ|tệ|kém|không phản hồi|không hỗ trợ|lừa)',
    r'nhân viên\s*(thái độ|kém|tệ|xấu)',
    r'tư vấn\s*(kém|tệ|sai|không đúng)',
    r'bảo hành\s*(kém|khó|không|không được|tệ)',
    r'đổi trả\s*(khó|không được|không cho|bị từ chối)',
    r'không\s*(?:cho\s*)?(?:đổi|trả)',
    r'không trả\s*(tiền|lại|hàng)',
    r'chiếm\s*(lấy\s*)?sản phẩm',
    r'lừa\s*(đảo|gạt|khách)',
    r'gian\s*(lận|dối)',
    r'tiki\s*(tệ|kém|không hỗ trợ|không giải quyết)',
    r'seller\s*(tệ|kém|không)',
    r'không\s*giải quyết',
    r'không\s*xử lý',
    r'khiếu nại\s*(không|mà không)',
    r'phản ánh\s*(không|mà không)',
    r'đề nghị\s*(tiki|cửa hàng|shop)',  # escalation signals
    r'bị\s*(lừa|gian|lừa đảo)',
    r'không\s*(tư vấn|hỗ trợ đổi|phản hồi|trả lời)',
    r'cửa sản phẩm không\s*(hỗ trợ|trả|giải quyết)',
]

# Shipping: complaints about delivery
SHIPPING_NEG = [
    r'ship\s*(chậm|trễ|lâu|muộn|quá chậm|quá lâu)',
    r'giao\s*(chậm|trễ|lâu|muộn|hàng chậm|hàng trễ|hàng lâu)',
    r'giao hàng\s*(chậm|trễ|lâu|muộn|không|tệ|kém)',
    r'vận chuyển\s*(chậm|trễ|lâu)',
    r'shipper\s*(thái độ|tệ|kém|không|ném|quăng)',
    r'hàng\s*(bị\s*?(móp|dập|vỡ|hỏng|trầy|xước)\s*(?:khi|lúc)\s*giao)',
    r'giao\s*(sai|nhầm|thiếu)',
    r'không\s*(?:được\s*)?giao', r'chưa\s*giao',
    r'mất\s*hàng',
    r'đợi\s*(lâu|quá lâu|mãi)',
    r'chờ\s*(lâu|quá lâu|mãi)',
    r'hàng đến\s*(muộn|trễ|chậm)',
    r'giao\s*không\s*(đúng|đủ)',
    r'giao\s*hàng\s*không\s*(cẩn thận|an toàn)',
]

# Packing: complaints about packaging
PACKING_NEG = [
    r'đóng gói\s*(kém|tệ|xấu|sơ sài|không cẩn thận|lỏng lẻo|bừa bãi)',
    r'bao bì\s*(hỏng|rách|bẹp|móp|ướt|tệ|kém)',
    r'hộp\s*(hỏng|rách|bẹp|móp|ướt|tệ|cũ|không|dập)',
    r'thùng\s*(hỏng|rách|bẹp|móp|ướt|tệ)',
    r'gói\s*(hàng\s*)?(sơ sài|kém|tệ|không cẩn thận)',
    r'thiếu\s*(phụ kiện|linh kiện|cáp|dây|adapter|sạc|tai nghe|chuột|bàn phím|usb)',
    r'trong\s*hộp\s*(thiếu|không có|lại thiếu)',
    r'không\s*(có|kèm)\s*(phụ kiện|cáp|dây|adapter|sạc)',
    r'bị\s*(móp|dập|bẹp)\s*(khi|lúc|do|vì)',
    r'hàng\s*(bị\s*)?(móp|dập|bẹp|vỡ|hỏng)\s*(do\s*(?:đóng gói|vận chuyển|ship))',
    r'đóng gói\s*không\s*cẩn thận',
    r'gói\s*hàng\s*(kém|tệ|sơ sài)',
    r'sản phẩm\s*(bị\s*)?(móp|dập|bẹp)\s*(trong|do|khi)',
    r'hộp\s*(cũ|tái sử dụng|đã qua sử dụng)',
]


def compile_patterns(patterns):
    return [re.compile(p, re.IGNORECASE) for p in patterns]

Q_PATTERNS  = compile_patterns(QUALITY_NEG)
SV_PATTERNS = compile_patterns(SERVICE_NEG)
SH_PATTERNS = compile_patterns(SHIPPING_NEG)
P_PATTERNS  = compile_patterns(PACKING_NEG)
GEN_PATTERNS = compile_patterns(GENERAL_NEG)


def label_comment(text):
    if pd.isna(text) or str(text).strip() == '':
        return 0, 0, 0, 0

    t = str(text).lower()

    # Global complaint → all categories are flagged
    if any(p.search(t) for p in GEN_PATTERNS):
        return 1, 1, 1, 1

    quality  = int(any(p.search(t) for p in Q_PATTERNS))
    service  = int(any(p.search(t) for p in SV_PATTERNS))
    shipping = int(any(p.search(t) for p in SH_PATTERNS))
    packing  = int(any(p.search(t) for p in P_PATTERNS))

    return quality, service, shipping, packing


# --------------- MAIN ---------------

df = pd.read_csv(r'd:\New folder\data\Laptop_full.csv')
print(f'Total rows: {len(df)}')

# Work on first 3000 rows (index 0..2999)
df_huy = df.iloc[:3000].copy()

results = df_huy['content'].apply(label_comment)
df_huy[['Quality', 'Service', 'Shipping', 'Packing']] = pd.DataFrame(
    results.tolist(), index=df_huy.index
)

# Save result
out_path = r'd:\New folder\data\Laptop_HuyDQ_3000.csv'
df_huy.to_csv(out_path, index=False, encoding='utf-8-sig')
print(f'Saved {len(df_huy)} rows to {out_path}')

# Stats
print('\nLabel distribution (first 3000):')
for col in ['Quality', 'Service', 'Shipping', 'Packing']:
    c = df_huy[col].sum()
    print(f'  {col}: {c} positive ({100*c/len(df_huy):.1f}%)')

# Spot check
print('\n--- Spot check (first 10 rows) ---')
for _, row in df_huy.head(10).iterrows():
    print(f'Q={row.Quality} Sv={row.Service} Sh={row.Shipping} P={row.Packing} | {str(row.content)[:90]}')
