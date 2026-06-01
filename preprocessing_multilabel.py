"""
Tiền xử lý dữ liệu Comment cho Multi-label Classification
Quy trình 5 bước tối ưu cho phân loại đa khía cạnh (Vận chuyển, Dịch vụ, Giá cả, Chất lượng)
"""

import re
import regex
import pandas as pd
import unicodedata

# ==================== BƯỚC 1: FILTERING - Lọc bỏ comment rác ====================

def is_valid_comment(text):
    """
    Kiểm tra comment có giá trị phân loại không
    Loại bỏ:
    - Comment rỗng/chỉ khoảng trắng
    - Comment chỉ toàn ký tự lặp (hhhhh, .......)
    - Comment chỉ toàn emoji
    - Comment là gibberish/keyboard mashing (hhgvhjjkghjk)
    - Comment quá ngắn hoặc không có từ thực
    """
    if not text or text.strip() == '':
        return False
    
    text = text.strip()
    
    # Loại bỏ comment quá ngắn
    if len(text) < 3:
        return False
    
    # Loại bỏ comment chỉ toàn dấu/ký tự lặp
    if re.match(r'^[.\-_!?:,;*]+$', text):
        return False
    
    # Loại bỏ comment chỉ toàn emoji
    emoji_pattern = r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002702-\U000027B0\U000024C2-\U0001F251]'
    if re.sub(emoji_pattern, '', text, flags=re.UNICODE).strip() == '':
        return False
    
    # ========== Lọc Gibberish/Keyboard mashing ==========
    # Kiểm tra consonant clusters quá dài (e.g., "hgvhjkghjk")
    # Nếu có consonant liên tiếp quá dài, có thể là gibberish
    consonant_clusters = re.findall(r'[bcdfghjklmnpqrstvwxyz]{4,}', text.lower())
    
    # Nếu có 1+ cluster dài >=5 ký tự, hoặc 2+ clusters >=4 ký tự → gibberish
    if consonant_clusters:
        long_clusters = [c for c in consonant_clusters if len(c) >= 5]
        if long_clusters or (len(consonant_clusters) >= 2 and min(len(c) for c in consonant_clusters) >= 4):
            return False
    
    # Kiểm tra nếu comment chỉ toàn số và ký tự (không có chữ thực)
    # Sau khi loại bỏ khoảng trắng, nếu chỉ còn <30% ký tự chữ cái, là rác
    letters = sum(1 for c in text if c.isalpha())
    if len(text) > 5 and letters / len(text) < 0.3:
        return False
    
    # ========== Kiểm tra từ thực (Real Words) ==========
    # Danh sách các từ thực tiếng Việt phổ biến
    common_vietnamese_words = {
        'là', 'có', 'được', 'không', 'của', 'từ', 'đến', 'với', 'cho', 'tại',
        'sản', 'phẩm', 'tốt', 'xấu', 'tuyệt', 'vời', 'kém', 'giá', 'rẻ', 'đắt',
        'giao', 'hàng', 'nhanh', 'chậm', 'lâu', 'dịch', 'vụ', 'hỗ', 'trợ',
        'chất', 'lượng', 'bền', 'hư', 'hỏng', 'lỗi', 'vỡ', 'rách', 'móp',
        'khuyến', 'mãi', 'sale', 'mua', 'bán', 'hài', 'lòng', 'thất', 'vọng'
    }
    
    words = text.lower().split()
    real_word_count = sum(1 for word in words if any(vword in word for vword in common_vietnamese_words))
    
    # Nếu comment có ≥5 từ nhưng không có từ thực nào → rác
    if len(words) >= 5 and real_word_count == 0:
        return False
    
    # Nếu comment ngắn (2-4 từ) nhưng hoàn toàn không có từ thực → rác
    if len(words) <= 4 and real_word_count == 0 and len(text) < 15:
        return False
    
    return True

def step1_filtering(text):
    """Bước 1: Lọc bỏ comment rác"""
    if not is_valid_comment(text):
        return None
    return text.strip()


# ==================== BƯỚC 2: TEXT NORMALIZATION - Chuẩn hóa văn bản ====================

def chuan_hoa_unicode(text):
    """Chuẩn hóa Unicode NFC"""
    return unicodedata.normalize('NFC', text)

def remove_emoji(text):
    """Xóa emoji và emotional ASCII patterns từ text"""
    # Loại bỏ emoji Unicode
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"
                               u"\U0001F300-\U0001F5FF"
                               u"\U0001F680-\U0001F6FF"
                               u"\U0001F1E0-\U0001F1FF"
                               u"\U00002702-\U000027B0"
                               u"\U000024C2-\U0001F251"
                               "]+", flags=re.UNICODE)
    text = emoji_pattern.sub(r'', text)
    
    # Loại bỏ emotional ASCII expressions: :((((, :(((, :))), etc.
    text = re.sub(r'[:;=\-]\s*[\(\)\[\]DdPpOo]{2,}', ' ', text)  # :((( :))) :DDD, etc.
    text = re.sub(r'[\(\)\[\]]+', ' ', text)  # Tất cả (1+ lần)
    
    return text

def remove_special_chars(text):
    """
    Xóa ký tự đặc biệt nhưng giữ lại dấu câu quan trọng
    Giữ: dấu phẩy, dấu chấm, dấu hỏi, dấu chém (/) để ngữ pháp rõ ràng
    """
    # Loại bỏ URL
    text = re.sub(r'http\S+|www\S+', '', text)
    
    # Loại bỏ @, #, $, %, *, ** và ký tự đặc biệt khác nhưng giữ các dấu câu cơ bản
    text = re.sub(r'[@#$%&^~`|\\*]', ' ', text)
    
    # Xóa các ký tự lặp quá nhiều
    text = re.sub(r'([.?!,;]){2,}', r'\1', text)
    
    return text

def step2_normalization(text):
    """Bước 2: Chuẩn hóa văn bản cơ bản"""
    text = text.lower()
    text = chuan_hoa_unicode(text)
    text = remove_emoji(text)
    text = remove_special_chars(text)
    # Xóa khoảng trắng thừa
    text = re.sub(r'\s+', ' ', text).strip()
    return text


# ==================== BƯỚC 3: TEXT REPLACEMENT - Teen code & Sai chính tả ====================

# Dictionary chuẩn hóa toàn diện cho Multi-label Classification
replace_dict = {
    # === Vận chuyển ===
    'gh': 'giao hàng',
    'ship': 'giao hàng',
    'shipper': 'shipper',
    'giao hang': 'giao hàng',
    'giao hàng nhanh': 'giao hàng nhanh',
    'giao hang nhanh': 'giao hàng nhanh',
    'ship nhanh': 'giao hàng nhanh',
    'ship chậm': 'giao hàng chậm',
    'ship lâu': 'giao hàng lâu',
    'giao hang lâu': 'giao hàng lâu',
    'giao hàng lâu': 'giao hàng lâu',
    'giao sai': 'giao sai',
    'giao nhầm': 'giao nhầm',
    'chậm': 'chậm',
    'trễ': 'trễ',
    'nhanh': 'nhanh',
    
    # === Dịch vụ ===
    'dich vu': 'dịch vụ',
    'cskh': 'chăm sóc khách hàng',
    'hỗ trợ': 'hỗ trợ',
    'tư vấn': 'tư vấn',
    'đáp ứng': 'đáp ứng',
    'thái độ': 'thái độ',
    'tính chuyên nghiệp': 'chuyên nghiệp',
    
    # === Chất lượng ===
    'cl': 'chất lượng',
    'chất lg': 'chất lượng',
    'sp': 'sản phẩm',
    'hàng': 'sản phẩm',
    'sản phẩm tốt': 'chất lượng tốt',
    'sản phẩm xấu': 'chất lượng xấu',
    'sản phẩm kém': 'chất lượng kém',
    'sản phẩm hư': 'sản phẩm hư',
    'hàng hư': 'sản phẩm hư',
    'hàng lỗi': 'sản phẩm lỗi',
    'hư hỏng': 'hư hỏng',
    'bị vỡ': 'bị vỡ',
    'bị rách': 'bị rách',
    'bị móp': 'bị móp',
    'độ bền': 'độ bền',
    
    # === Giá cả ===
    'giá': 'giá',
    'giá cao': 'giá cao',
    'giá cả cao': 'giá cao',
    'đắt': 'giá cao',
    'đắt lắm': 'giá cao',
    'giá rẻ': 'giá rẻ',
    're': 'giá rẻ',
    'rẻ': 'giá rẻ',
    'km': 'khuyến mãi',
    'giảm giá': 'giảm giá',
    'sale': 'sale',
    
    # === Teen code / Viết tắt chung ===
    'k ': 'không ',
    'kh ': 'không ',
    'ko ': 'không ',
    'kp ': 'không phải ',
    'hok ': 'không ',
    'chưa': 'chưa',
    'kém': 'kém',
    'không tốt': 'kém',
    'dc': 'được',
    'đc': 'được',
    'dk': 'được',
    'đk': 'được',
    'j': 'gì',
    'gì': 'gì',
    'sao': 'sao',
    'tại sao': 'tại sao',
    'bít': 'biết',
    'biết': 'biết',
    'qa': 'quá',
    'quá': 'quá',
    'rất': 'rất',
    'quá là': 'quá',
    'cực': 'cực',
    'ok': 'tốt',
    'okie': 'tốt',
    'ổn': 'tốt',
    'tạm': 'tạm ổn',
    'được': 'được',
    'còn': 'nhưng',
    'mà': 'nhưng',
    'nhưng': 'nhưng',
    'm': 'mình',
    'mik': 'mình',
    'mình': 'mình',
    'shop': 'cửa hàng',
    'store': 'cửa hàng',
    'sp': 'sản phẩm',
    'trc': 'trước',
    'training':'đào tạo',
    'sl': 'số lượng',
    'sz': 'size',
    'sx': 'sản xuất',
    'auth': 'chuẩn chính hãng',
    
    # === Từ phủ định (KHÔNG XÓA) ===
    'không': 'không',
    'chưa': 'chưa',
    'chưa': 'chưa',
    'kém': 'kém',
    'tệ': 'tệ',
    'xấu': 'xấu',
}

def fix_repeated_chars(text, max_repeat=2):
    """Sửa ký tự lặp quá nhiều (e.g., 'mịnnnnnn' -> 'mịn')"""
    result = []
    prev_char = ''
    repeat_count = 0
    
    for char in text:
        if char == prev_char:
            repeat_count += 1
            if repeat_count <= max_repeat:
                result.append(char)
        else:
            result.append(char)
            prev_char = char
            repeat_count = 0
    
    return ''.join(result)

def step3_text_replacement(text):
    """Bước 3: Xử lý teen code, viết tắt, sai chính tả"""
    # Sửa ký tự lặp trước
    text = fix_repeated_chars(text, max_repeat=2)
    
    # ========== Xử lý ký tự đơn (k, j) đặc biệt ==========
    # Phải xử lý trước các từ lẻ để tránh xung đột với word boundary
    # "k" hoặc "k," hoặc "k." → "không"
    text = re.sub(r'\bk\b', 'không', text, flags=re.IGNORECASE)
    # "j" hoặc "j," hoặc "j." → "gì"
    text = re.sub(r'\bj\b', 'gì', text, flags=re.IGNORECASE)
    
    # Chuẩn hóa theo dictionary (bỏ đi 'j' và 'k ' vì đã xử lý trên)
    for old, new in replace_dict.items():
        # Bỏ qua 'j' và 'k ' vì đã xử lý
        if old in ('j', 'k '):
            continue
        # Dùng word boundary để tránh thay thế một phần của từ
        text = re.sub(r'\b' + re.escape(old) + r'\b', new, text, flags=re.IGNORECASE)
    
    # Xóa khoảng trắng thừa
    text = re.sub(r'\s+', ' ', text).strip()
    
    # ========== Kiểm tra chất lượng comment sau xử lý ==========
    # Nếu comment vẫn toàn khoảng trắng → rác
    if not text or text.strip() == '':
        return None
    
    # Đếm từ có độ dài hợp lý (không phải 1-2 ký tự vô nghĩa)
    words = text.split()
    meaningful_words = [w for w in words if len(w) >= 2]  # Loại bỏ "k", "j" v.v.
    
    # Nếu sau xử lý chỉ còn <30% từ có nghĩa → rác
    if len(meaningful_words) > 0 and len(meaningful_words) / len(words) < 0.3:
        return None
    
    # Nếu comment chỉ có 1-2 từ và toàn viết tắt → rác
    # Ví dụ: "k hop", "j gì", "ko co"
    if len(meaningful_words) <= 2 and len(words) <= 3:
        # Kiểm tra nếu có quá nhiều từ 1-2 ký tự
        short_words = [w for w in words if len(w) <= 2]
        if len(short_words) >= len(words) * 0.6:
            return None
    
    return text


# ==================== BƯỚC 4: CODE-SWITCHING - Xử lý tiếng Anh ====================

def detect_english_ratio(text):
    """Tính tỷ lệ từ tiếng Anh trong text"""
    words = text.split()
    english_words = 0
    
    # Danh sách từ tiếng Anh thường gặp trên TMĐT
    common_english = {
        'ok', 'good', 'bad', 'nice', 'great', 'terrible', 'fast', 'slow',
        'quality', 'service', 'delivery', 'price', 'shop', 'product',
        'buy', 'sell', 'order', 'payment', 'free', 'sale', 'hot'
    }
    
    for word in words:
        if word.lower() in common_english:
            english_words += 1
    
    if len(words) == 0:
        return 0
    
    return english_words / len(words)

def step4_code_switching(text):
    """Bước 4: Xử lý tiếng Anh / Code-switching"""
    # Nếu comment là None, trả về None
    if text is None:
        return None
    
    # Nếu comment có quá 50% tiếng Anh, lọc bỏ
    if detect_english_ratio(text) > 0.5:
        return None
    
    # Kiểm tra nếu comment chỉ toàn số, dấu câu
    if re.match(r'^[\d.,!?\s]+$', text):
        return None
    
    # Nếu không, giữ lại (Loanwords sẽ được xử lý ở Bước 3)
    return text


# ==================== BƯỚC 5: WORD SEGMENTATION - Tách từ tiếng Việt ====================

def segment_vietnamese(text):
    """
    Tách từ tiếng Việt dùng Underthesea
    Yêu cầu: pip install underthesea
    """
    try:
        from underthesea import word_tokenize
        tokens = word_tokenize(text, format="text")
        return tokens
    except:
        # Nếu không cài underthesea, trả về text gốc
        print("⚠️  Chưa cài underthesea. Hãy chạy: pip install underthesea")
        return text

def step5_word_segmentation(text):
    """Bước 5: Tách từ tiếng Việt"""
    try:
        return segment_vietnamese(text)
    except Exception as e:
        print(f"Lỗi khi tách từ: {e}")
        return text


# ==================== HÀM CHÍNH: PREPROCESSING ====================

def preprocess_comment_multilabel(text):
    """
    Tiền xử lý comment theo 5 bước cho Multi-label Classification
    
    Input: text (comment gốc)
    Output: text đã xử lý (hoặc None nếu comment rác)
    """
    
    # Bước 1: Filtering
    text = step1_filtering(text)
    if text is None:
        return None
    
    # Bước 2: Normalization
    text = step2_normalization(text)
    
    # Bước 3: Text Replacement
    text = step3_text_replacement(text)
    
    # Bước 4: Code-switching
    text = step4_code_switching(text)
    if text is None:
        return None
    
    # Bước 5: Word Segmentation (Optional - tuỳ theo yêu cầu)
    # text = step5_word_segmentation(text)
    
    return text


# ==================== HÀM ỨNG DỤNG BATCH ====================

def preprocess_dataframe(df, text_column='content', output_column='content_processed'):
    """
    Tiền xử lý toàn bộ DataFrame
    
    Args:
        df: DataFrame chứa dữ liệu
        text_column: Tên cột chứa text gốc
        output_column: Tên cột output
    
    Returns:
        DataFrame đã xử lý với cột mới
    """
    df = df.copy()
    df[output_column] = df[text_column].fillna('').apply(preprocess_comment_multilabel)
    
    # Loại bỏ dòng có text_processed = None
    df = df[df[output_column].notna()]
    
    print(f"Tổng comment gốc: {len(df)}")
    print(f"Tổng comment sau xử lý: {len(df[df[output_column].notna()])}")
    print(f"Comment bị loại bỏ: {len(df) - len(df[df[output_column].notna()])}")
    
    return df


# ==================== VÍ DỤ SỬ DỤNG ====================

if __name__ == "__main__":
    # Test các bước xử lý
    test_comments = [
        "sp xài ổn áp cl tốt, mỗi tội gh hơi lâu k nhanh như lần trc.",
        "giao hàng quá chậm 😞😞 nhưng sản phẩm thì ổn, giá hơi đắt",
        "⭐⭐⭐⭐⭐ 🥰🥰🥰",  # Chỉ emoji
        "ok",  # Quá ngắn
        "Service quá tệ, shipper thái độ xấu nhưng hàng ok",
        "Không hài lòng vì giao nhầm hàng, đc cái là ship nhanh...",
    ]
    
    print("="*70)
    print("VÍ DỤ XỬ LÝ COMMENT")
    print("="*70)
    
    for i, comment in enumerate(test_comments, 1):
        processed = preprocess_comment_multilabel(comment)
        print(f"\n[Comment {i}]")
        print(f"Gốc: {comment}")
        print(f"Xử lý: {processed}")
