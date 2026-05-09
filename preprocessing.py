import re
import regex
import string
import unicodedata

with open('data/vietnamese-stopwords.txt', 'r', encoding='utf-8') as f:
    stopwords = f.read().splitlines()
    stopwords = [i for i in stopwords if i.find(" ") == -1]

bang_nguyen_am = [['a', 'à', 'á', 'ả', 'ã', 'ạ', 'a'],
                  ['ă', 'ằ', 'ắ', 'ẳ', 'ẵ', 'ặ', 'aw'],
                  ['â', 'ầ', 'ấ', 'ẩ', 'ẫ', 'ậ', 'aa'],
                  ['e', 'è', 'é', 'ẻ', 'ẽ', 'ẹ', 'e'],
                  ['ê', 'ề', 'ế', 'ể', 'ễ', 'ệ', 'ee'],
                  ['i', 'ì', 'í', 'ỉ', 'ĩ', 'ị', 'i'],
                  ['o', 'ò', 'ó', 'ỏ', 'õ', 'ọ', 'o'],
                  ['ô', 'ồ', 'ố', 'ổ', 'ỗ', 'ộ', 'oo'],
                  ['ơ', 'ờ', 'ớ', 'ở', 'ỡ', 'ợ', 'ow'],
                  ['u', 'ù', 'ú', 'ủ', 'ũ', 'ụ', 'u'],
                  ['ư', 'ừ', 'ứ', 'ử', 'ữ', 'ự', 'uw'],
                  ['y', 'ỳ', 'ý', 'ỷ', 'ỹ', 'ỵ', 'y']]

bang_ky_tu_dau = ['', 'f', 's', 'r', 'x', 'j']
nguyen_am_to_ids = {}

for i in range(len(bang_nguyen_am)):
    for j in range(len(bang_nguyen_am[i]) - 1):
        nguyen_am_to_ids[bang_nguyen_am[i][j]] = (i, j)

def chuan_hoa_unicode(text):
    return unicodedata.normalize('NFC', text)

def is_valid_vietnam_word(word):
    chars = list(word)
    nguyen_am_index = -1
    for index, char in enumerate(chars):
        x, y = nguyen_am_to_ids.get(char, (-1, -1))
        if x != -1:
            if nguyen_am_index == -1:
                nguyen_am_index = index
            else:
                if index - nguyen_am_index != 1:
                    return False
                nguyen_am_index = index
    return True

def chuan_hoa_dau_tu_tieng_viet(word):
    if not is_valid_vietnam_word(word):
        return word
    chars = list(word)
    dau_cau = 0
    nguyen_am_index = []
    qu_or_gi = False
    for index, char in enumerate(chars):
        x, y = nguyen_am_to_ids.get(char, (-1, -1))
        if x == -1:
            continue
        elif x == 9:  # check qu
            if index != 0 and chars[index - 1] == 'q':
                chars[index] = 'u'
                qu_or_gi = True
        elif x == 5:  # check gi
            if index != 0 and chars[index - 1] == 'g':
                chars[index] = 'i'
                qu_or_gi = True
        if y != 0:
            dau_cau = y
            chars[index] = bang_nguyen_am[x][0]
        if not qu_or_gi or index != 1:
            nguyen_am_index.append(index)
    if len(nguyen_am_index) < 2:
        if qu_or_gi:
            if len(chars) == 2:
                x, y = nguyen_am_to_ids.get(chars[1])
                chars[1] = bang_nguyen_am[x][dau_cau]
            else:
                x, y = nguyen_am_to_ids.get(chars[2], (-1, -1))
                if x != -1:
                    chars[2] = bang_nguyen_am[x][dau_cau]
                else:
                    chars[1] = bang_nguyen_am[5][dau_cau] if chars[1] == 'i' else bang_nguyen_am[9][dau_cau]
            return ''.join(chars)
        return word

    for index in nguyen_am_index:
        x, y = nguyen_am_to_ids[chars[index]]
        if x == 4 or x == 8:  # ê, ơ
            chars[index] = bang_nguyen_am[x][dau_cau]
            return ''.join(chars)

    if len(nguyen_am_index) == 2:
        if nguyen_am_index[-1] == len(chars) - 1:
            x, y = nguyen_am_to_ids[chars[nguyen_am_index[0]]]
            chars[nguyen_am_index[0]] = bang_nguyen_am[x][dau_cau]
        else:
            x, y = nguyen_am_to_ids[chars[nguyen_am_index[1]]]
            chars[nguyen_am_index[1]] = bang_nguyen_am[x][dau_cau]
    else:
        x, y = nguyen_am_to_ids[chars[nguyen_am_index[1]]]
        chars[nguyen_am_index[1]] = bang_nguyen_am[x][dau_cau]
    return ''.join(chars)

def chuan_hoa_dau_cau_tieng_viet(sentence):
    sentence = sentence.lower()
    words = sentence.split()
    for index, word in enumerate(words):
        cw = regex.sub(r'(^\p{P}*)([p{L}.]*\p{L}+)(\p{P}*$)', r'\1/\2/\3', word).split('/')
        if len(cw) == 3:
            cw[1] = chuan_hoa_dau_tu_tieng_viet(cw[1])
        words[index] = ''.join(cw)
    return ' '.join(words)

def get_lower(text):
    return text.lower().strip()

def chuan_hoa_cau(text):
    text = re.sub(r'[^\s\wáàảãạăắằẳẵặâấầẩẫậéèẻẽẹêếềểễệóòỏõọôốồổỗộơớờởỡợíìỉĩịúùủũụưứừửữựýỳỷỹỵđ_]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def remove_tag(text):
    pattern = re.compile('<.*?>')
    return pattern.sub(r'', text)

def remove_url(text):
    pattern = re.compile(r'http\S+')
    return pattern.sub(r'', text)

def remove_punc(text):
    exclude = string.punctuation
    for char in exclude:
        text = text.replace(char, '')
    return text

def remove_stopW(text):
    new_text = []
    for word in text.split():
        if word not in stopwords:
            new_text.append(word)
    return " ".join(new_text)

def remove_emoji(text):
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"
                               u"\U0001F300-\U0001F5FF"
                               u"\U0001F680-\U0001F6FF"
                               u"\U0001F1E0-\U0001F1FF"
                               u"\U00002702-\U000027B0"
                               u"\U000024C2-\U0001F251"
                               "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)

replace_list = {
    'ô kêi': ' ok ', 'okie': ' ok ', ' o kê ': ' ok ', 'okey': ' ok ', 'ôkê': ' ok ', 'oki': ' ok ', ' oke ': ' ok ', ' okay': ' ok ', 'okê': ' ok ',
    ' tks ': ' cám ơn ', 'thks': ' cám ơn ', 'thanks': ' cám ơn ', 'ths': ' cám ơn ', 'thank': ' cám ơn ',
    'kg ': ' không ', 'not': ' không ', ' kh ': ' không ', 'kô': ' không ', 'hok': ' không ', ' kp ': ' không phải ', ' kô ': ' không ', ' ko ': ' không ', ' k ': ' không ', 'khong': ' không ', ' hok ': ' không ',
    'he he': ' positive ', 'hehe': ' positive ', 'hihi': ' positive ', 'haha': ' positive ', 'hjhj': ' positive ',
    ' lol ': ' negative ', ' cc ': ' negative ', 'cute': ' dễ thương ', 'huhu': ' negative ', ' vs ': ' với ', 'wa': ' quá ', 'wá': ' quá', 'j': ' gì ', '“': ' ',
    ' sz ': ' cỡ ', 'size': ' cỡ ', ' đx ': ' được ', 'dk': ' được ', 'dc': ' được ', 'đk': ' được ',
    'đc': ' được ', 'authentic': ' chuẩn chính hãng ', ' aut ': ' chuẩn chính hãng ', ' auth ': ' chuẩn chính hãng ', 'thick': ' positive ', 'store': ' cửa hàng ',
    'shop': ' cửa hàng ', 'sp': ' sản phẩm ', 'gud': ' tốt ', 'god': ' tốt ', 'wel done': ' tốt ', 'good': ' tốt ', 'gút': ' tốt ',
    'sấu': ' xấu ', 'gut': ' tốt ', ' tot ': ' tốt ', ' nice ': ' tốt ', 'perfect': 'rất tốt', 'bt': ' bình thường ',
    'time': ' thời gian ', 'qá': ' quá ', ' ship ': ' giao hàng ', ' m ': ' mình ', ' mik ': ' mình ',
    'ể': 'ể', 'product': 'sản phẩm', 'quality': 'chất lượng', 'chat': ' chất ', 'excelent': 'hoàn hảo', 'bad': 'tệ', 'fresh': ' tươi ', 'sad': ' tệ ',
    'date': ' hạn sử dụng ', 'hsd': ' hạn sử dụng ', 'quickly': ' nhanh ', 'quick': ' nhanh ', 'fast': ' nhanh ', 'delivery': ' giao hàng ', ' síp ': ' giao hàng ',
    'beautiful': ' đẹp tuyệt vời ', ' tl ': ' trả lời ', ' r ': ' rồi ', ' shopE ': ' cửa hàng ', ' order ': ' đặt hàng ',
    'chất lg': ' chất lượng ', ' sd ': ' sử dụng ', ' dt ': ' điện thoại ', ' nt ': ' nhắn tin ', ' tl ': ' trả lời ', ' sài ': ' xài ', 'bjo': ' bao giờ ',
    'thik': ' thích ', ' sop ': ' cửa hàng ', ' fb ': ' facebook ', ' face ': ' facebook ', ' very ': ' rất ', 'quả ng ': ' quảng ',
    'dep': ' đẹp ', ' xau ': ' xấu ', 'delicious': ' ngon ', 'hàg': ' hàng ', 'qủa': ' quả ',
    'iu': ' yêu ', 'fake': ' giả mạo ', 'trl': 'trả lời', '><': ' positive ',
    ' por ': ' tệ ', ' poor ': ' tệ ', 'ib': ' nhắn tin ', 'rep': ' trả lời ', 'fback': ' feedback ', 'fedback': ' feedback ',
}

def xu_ly_tu_viet_tat(text):
    for key, value in replace_list.items():
        text = re.sub(r'(?i)\b{}\b'.format(key), value, text)
    return text

def clean_data(text):
    text = get_lower(text)
    text = remove_tag(text)
    text = remove_url(text)
    text = remove_stopW(text)
    text = remove_emoji(text)
    text = remove_punc(text)
    text = chuan_hoa_unicode(text)
    text = chuan_hoa_dau_cau_tieng_viet(text)
    text = chuan_hoa_cau(text)
    text = xu_ly_tu_viet_tat(text)
    return text

def preprocess_comment(comment):
    return clean_data(comment)
