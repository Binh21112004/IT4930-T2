import pandas as pd

FILE_PATH = r"C:\Users\admin\Desktop\KHDL\IT4930-T2\data\Commentsauxuly\comments_data_ncds_preprocessed_thoitrangnu.csv"

# (Quality, Service, Shipping, Packing) — keyed by 0-based row index (= csv line - 2)
# Only rows currently labeled 0,0,0,0 will be updated.
MANUAL_LABELS = {
    19:  (1, 0, 0, 0),  # "rất tốt. mua giảm xuống 1 size" → Q
    31:  (0, 0, 1, 0),  # "đặc size mình lại giao en l" → Sh
    40:  (0, 1, 1, 0),  # "combo 5 cái nhưng giao có 4...chưa xử lí" → Sh+Sv
    41:  (1, 0, 0, 0),  # "quần ghi nylon nhưng tiki ghi cotton" → Q
    49:  (0, 0, 1, 0),  # "giao sản phẩm không đúng size" → Sh
    50:  (0, 0, 1, 0),  # "giao không đúng cỡ đã chọn cỡ s" → Sh
    51:  (0, 0, 1, 0),  # "đặc bộ người lớn nhưng ra trẻ em" → Sh
    52:  (0, 0, 1, 0),  # "không đúng cỡ đã chọn là cỡ s" → Sh
    53:  (1, 0, 0, 0),  # "đúng size nhưng cổ hơi rộng" → Q
    54:  (1, 0, 0, 0),  # "màu tối hơn trên hình, gần như màu đen" → Q
    55:  (1, 0, 0, 0),  # "áo ra màu hơn sản phẩm chợ" → Q
    56:  (1, 0, 1, 0),  # "không đúng mẫu mã, chưa cắt chỉ" → Sh+Q
    57:  (0, 0, 1, 0),  # "sản phẩm không đúng màu đã đặt" → Sh
    69:  (0, 1, 1, 0),  # "đặt hồng nhưng đưa màu này...iu cầu đổi" → Sh+Sv
    72:  (1, 0, 0, 0),  # "đường chỉ may xấu, chỉ chưa cắt" → Q
    80:  (1, 1, 0, 0),  # "không vừa, co đổi được ko" → Q+Sv
    81:  (0, 0, 1, 0),  # "đặt bộ hồng, mẫu hoàn toàn khác" → Sh
    83:  (0, 1, 0, 0),  # "làm ăn yêu cầu mẫu gửi mẫu giá như đi xin" → Sv
    87:  (0, 0, 1, 0),  # "sản phẩm giao khác mô tả và hình" → Sh
    88:  (0, 0, 1, 0),  # "hình quảng cáo quần dài mà giao quần đùi" → Sh
    98:  (1, 0, 0, 0),  # "dán 8 tiếng bị phồng rộp da" → Q
    101: (0, 1, 1, 0),  # "không đúng như quảng cáo...yêu cầu trả" → Sh+Sv
    106: (0, 0, 1, 0),  # "gửi sản phẩm sai quảng cáo, sai size" → Sh
    116: (1, 0, 0, 0),  # "chat luong kem, khong nen mua" → Q
    117: (1, 0, 0, 0),  # "cai tot cai xau tra tron vo" → Q
    119: (1, 0, 0, 0),  # "chat luong qua chan" → Q
    127: (1, 0, 0, 0),  # "tiền nào của nấy, đúng giá trị thực" → Q
    132: (1, 1, 0, 0),  # "2 mẫu 1 bự 1 xíu, muốn đổi ko ai tl" → Q+Sv
    133: (0, 0, 1, 0),  # "đặt combo 10 giao 5, tính tiền 10" → Sh
    146: (1, 0, 0, 0),  # "váy ngắn hơn hình ảnh" → Q
    148: (1, 0, 0, 0),  # "sản phẩm như hình" → Q
    152: (1, 0, 0, 0),  # "áo giặt 1 lần co rúm đến rốn" → Q
    154: (1, 0, 0, 0),  # "sản phẩm kg có một chút nào là như hình" → Q
    160: (1, 0, 1, 0),  # "giao không đúng size, váy ngắn hơn hình" → Sh+Q
    166: (1, 0, 0, 0),  # "bình thường. size hơi to." → Q
    168: (0, 0, 1, 1),  # "gói kỹ. giao nhanh" → Sh+P
    169: (1, 0, 0, 0),  # "bình thường. không đẹp như mô tả" → Q
    171: (1, 0, 0, 0),  # "quan mac tot, thoang, chat lieu thoai mai" → Q
    174: (0, 0, 1, 0),  # "nhầm mẫu, không đẹp" → Sh
    180: (1, 0, 0, 0),  # "không đúng với hình ảnh quảng cáo" → Q
    181: (0, 0, 1, 0),  # "chọn 1 size giao nhiều size" → Sh
    202: (1, 0, 0, 0),  # "tốt nhưng chon size vừa quá, không thoải mái" → Q
    204: (1, 0, 0, 0),  # "xxl nhưng nhỏ bằng l" → Q
    222: (1, 0, 1, 0),  # "không giống màu chọn...chất áo tạm ổn" → Sh+Q
    238: (1, 0, 0, 0),  # "kiểu đẹp nhưng bị ra màu" → Q
    239: (0, 1, 0, 0),  # "tìm cách xả sản phẩm đi hết" → Sv
    240: (0, 0, 1, 0),  # "đặt áo đỏ đũi giao ghẻ lau" → Sh
    244: (0, 1, 0, 0),  # "cs quả lag nhiều điều bất ngờ" → Sv
    249: (0, 1, 0, 0),  # "buôn bán không đàng hoàng hoài" → Sv
    252: (1, 0, 0, 0),  # "áo rộng so với size, dáng tay dơi" → Q
    253: (0, 0, 1, 0),  # "không đúng màu đỏ mong muốn" → Sh
    255: (1, 0, 0, 0),  # "tệ wa không giong sản pham đang" → Q
    257: (1, 1, 0, 0),  # "muốn đổi vì quần rúm, chỉ thừa, kg như quảng cáo" → Q+Sv
    262: (1, 0, 0, 0),  # "rất kém tệ hại" → Q
    266: (0, 0, 1, 0),  # "giao sản phẩm không đúng hình đăng bán" → Sh
    271: (1, 0, 0, 0),  # "phù hợp giá tiền, xài tốt" → Q
    276: (0, 1, 1, 0),  # "mua 10 gửi 9, làm ăn kiểu trẻ con" → Sh+Sv
    281: (1, 0, 0, 0),  # "quá to so với kg" → Q
    284: (0, 1, 0, 0),  # "tiki nâng giá lên rồi giảm sâu" → Sv
    292: (0, 0, 1, 0),  # "mua 2 hộp giao có 1 hộp" → Sh
    293: (1, 0, 0, 0),  # "bình thường, trùng màu, không giúp hình chụp" → Q
    298: (1, 0, 0, 0),  # "đường chỉ nhăn nhúm, màu sắc khác hình" → Q
    306: (0, 1, 0, 0),  # "bọn đảo, đẩy giá" → Sv
    309: (1, 0, 0, 0),  # "thun mỏng, màu nhạt, chữ in rạn sau lần giặt đầu" → Q
    319: (1, 0, 0, 0),  # "không có tem mác, bị lủng lỗ" → Q
    336: (1, 0, 1, 0),  # "không đúng mẫu, thun xấu như hàng chợ" → Sh+Q
    344: (1, 0, 0, 0),  # "muốn mua về làm giẻ lau" → Q
    345: (1, 0, 1, 0),  # "giao 3 size khác nhau, xấu hơn chợ" → Sh+Q
    350: (1, 0, 0, 0),  # "lưng không phải thun, vòng 3 to kéo không lên" → Q
    354: (1, 0, 0, 0),  # "bán 1 kiểu rao 1 kiểu, áo mùi hôi" → Q
    355: (0, 0, 1, 0),  # "giao không đúng mẫu" → Sh
    358: (1, 0, 1, 0),  # "giao nhanh nhưng áo không giống hình" → Sh+Q
    363: (1, 0, 0, 0),  # "sản phẩm màu không giống như hình" → Q
    368: (1, 0, 0, 0),  # "to như cái thúng" → Q
    370: (1, 0, 1, 0),  # "giao nhanh nhưng áo bự quá" → Sh+Q
    371: (1, 0, 0, 0),  # "sản phẩm quá vừa túi tiền" → Q
    372: (1, 0, 0, 0),  # "cotton nhưng giặt xong co rút" → Q
    374: (1, 0, 0, 0),  # "quá nhỏ so với mô tả không vừa" → Q
    375: (1, 1, 0, 0),  # "mua L bé xíu, xin đổi lại" → Q+Sv
    379: (1, 0, 0, 0),  # "mua S nhưng to quá" → Q
    380: (0, 0, 1, 0),  # "lấy màu cam sáng nhưng nhận màu cam đất tối" → Sh
    387: (1, 1, 1, 0),  # "không đúng mẫu, ống quần hẹp, yêu cầu trả" → Sh+Q+Sv
    388: (0, 0, 1, 0),  # "đặt đen 26 giao xám 28" → Sh
    392: (1, 0, 0, 0),  # "đẹp lắm mặc tôn dáng" → Q
    393: (1, 1, 0, 0),  # "quần chật, sh đổi cho mình" → Q+Sv
    395: (1, 0, 0, 0),  # "không có hợp như đã xem review" → Q
    399: (0, 0, 1, 0),  # "hình minh hoạ 1 đằng, mẫu giao 1 nẻo" → Sh
    403: (1, 0, 0, 0),  # "không đúng size theo mô tả" → Q
    405: (1, 0, 0, 0),  # "đồ bơi quá bé, L 48kg chẳng vào đâu" → Q
    409: (0, 0, 1, 0),  # "mua 60kg giao 30kg" → Sh
    410: (1, 0, 0, 0),  # "tương xứng giá tiền, nên mua lớn hơn 1 size" → Q
    411: (1, 1, 0, 0),  # "bị chật không biết có đổi được không" → Q+Sv
    418: (1, 0, 0, 0),  # "cũng được nhưng size không phù hợp cách tính" → Q
    425: (1, 0, 0, 0),  # "không hài lòng. màu không đúng" → Q
    430: (0, 0, 1, 1),  # "giáo sản phẩm nhanh. gói cẩn thận" → Sh+P
    434: (0, 0, 1, 0),  # "mua quần có túi nhưng giao không có túi" → Sh
    436: (1, 0, 0, 0),  # "chân váy ngắn hơn hình, không dài qua gối" → Q
    438: (1, 0, 0, 0),  # "quần bận rất thích, mua cái thứ 2" → Q
    442: (1, 0, 0, 0),  # "bình thường, không đẹp." → Q
    450: (0, 0, 1, 0),  # "mua 3 màu sáng giao 3 màu tối" → Sh
    451: (1, 0, 0, 0),  # "áo khá tốt nhưng chật, không như mong đợi" → Q
    452: (0, 0, 1, 0),  # "hình 1 đường áo giao 1 nẻo" → Sh
    455: (1, 0, 0, 0),  # "sản phẩm hoá đúng mô tả, hài lòng" → Q
    464: (0, 0, 1, 0),  # "giao sản phẩm khác giá rẻ hơn" → Sh
    465: (0, 1, 1, 0),  # "hết hàng không thông báo, tự đổi sản phẩm" → Sv+Sh
    468: (0, 0, 1, 0),  # "giao không đúng như hình, như đồ trẻ sơ sinh" → Sh
    469: (0, 0, 1, 0),  # "gửi sản phẩm vớ vẩn, không đúng sản phẩm" → Sh
    473: (1, 0, 0, 0),  # "không mặc được" → Q
    474: (1, 0, 0, 0),  # "qua te khg nen mua. phi tien" → Q
    475: (0, 0, 1, 0),  # "bỏ ra 29k nhận được sản phẩm 19k" → Sh
    481: (0, 0, 1, 0),  # "set 10 khi giao là set 5" → Sh
    485: (1, 0, 0, 0),  # "hình ảnh và thực tế không hề liên quan" → Q
    486: (1, 1, 0, 0),  # "không đúng mô tả và hình, muốn trả lại" → Q+Sv
    487: (0, 1, 1, 0),  # "hết hàng không thông báo, đổi sản phẩm khác" → Sv+Sh
    492: (1, 0, 0, 0),  # "mua đủ màu nhưng thiếu...thất vọng" → Q
    499: (1, 0, 0, 0),  # "chỉ 4 cúc, vạt áo ngắn không bỏ vào quần được" → Q
    500: (1, 0, 0, 0),  # "khuy áo bị lỗi, cài không được" → Q
    507: (1, 0, 0, 0),  # "nhìn như áo bà ba, được cái chất đẹp" → Q
    514: (1, 0, 0, 0),  # "vừa nhưng hai vạt áo không kép vào nhau" → Q
    518: (1, 0, 1, 0),  # "váy đẹp, dây lưng không có cây...nhân viên vui vẻ" → Q+Sh
    519: (1, 0, 0, 0),  # "chân váy dầy ổn nhưng xoè quá" → Q
    523: (1, 0, 0, 0),  # "bình thuong, không đẹp như thấy trên ảnh" → Q
    524: (1, 0, 0, 0),  # "quá nhỏ so với kg trên bảng size" → Q
    525: (0, 0, 1, 0),  # "shipper quá hỗn" → Sh
    528: (1, 0, 0, 0),  # "bình thường, nút khâu sơ xài" → Q
    530: (1, 0, 0, 0),  # "mới mặc đã bung chỉ viền bụng" → Q
    534: (1, 0, 0, 0),  # "áo quá rộng so với size" → Q
    535: (1, 0, 0, 0),  # "không nhu hinh, vai qua mong" → Q
    543: (1, 0, 0, 0),  # "đệm lót lỏng nên bơi không được" → Q
    548: (1, 0, 0, 0),  # "nhỏ so với dự kiến" → Q
    552: (0, 1, 1, 0),  # "mua nịt bụng giao băng keo...tiki ẩu tả" → Sh+Sv
    554: (1, 1, 0, 0),  # "hơi rộng cho mình đổi lại sai s" → Q+Sv
    556: (1, 0, 0, 0),  # "kém và không chắc chắn" → Q
    557: (1, 0, 0, 0),  # "xấu hơn trên ảnh nhiều" → Q
    558: (0, 0, 1, 0),  # "đặt đồ dài nhưng nhận bộ ngắn" → Sh
    559: (0, 1, 1, 0),  # "giao không đúng, đề nghị tiki trả lời gấp" → Sh+Sv
    560: (0, 0, 1, 0),  # "giao không đúng size như yêu cầu" → Sh
    567: (1, 0, 0, 0),  # "may bị lỗi, mắt tiền" → Q
    571: (0, 0, 1, 0),  # "quần dài mà giao quần ngắn" → Sh
    574: (1, 1, 0, 0),  # "xl bé quá so với loại khác, muốn đổi" → Q+Sv
    577: (1, 0, 0, 0),  # "áo hơi nóng so với tưởng tượng" → Q
    584: (1, 0, 0, 0),  # "chất đẹp, nên có nhiều màu hơn" → Q
    591: (1, 0, 0, 0),  # "mặc bị lằn dù mua xl" → Q
    593: (1, 0, 0, 0),  # "quần mặc mát, thấm hút tốt" → Q
    594: (0, 0, 1, 0),  # "combo 5 quần nhưng nhận được 4" → Sh
    601: (1, 0, 0, 0),  # "siza l không vừa dù bảng ghi 60kg" → Q
    609: (1, 0, 0, 0),  # "đẹp, chấp nhận được, phù hợp giá tiền" → Q
    615: (0, 0, 1, 0),  # "dạo này đặt gì cũng lâu" → Sh
    617: (0, 0, 1, 0),  # "mua 2 set giao có 1 set" → Sh
    619: (0, 0, 1, 0),  # "giao không đúng màu sắc trong hình" → Sh
    626: (1, 0, 0, 0),  # "đẹp nhưng ôm người quá" → Q
    627: (0, 1, 0, 0),  # "muốn đổi số lớn phải làm sao?" → Sv
    629: (1, 0, 0, 1),  # "đẹp như hình, đóng gói đẹp" → Q+P
    634: (1, 0, 0, 0),  # "đúng quảng cáo nhưng size to, nhăn khi ngồi" → Q
    639: (1, 0, 0, 0),  # "xxl lần này nhỏ như l lần trước" → Q
    649: (1, 0, 0, 0),  # "bình thường so với giá tiền" → Q
    656: (0, 0, 1, 0),  # "giao không đúng mẫu" → Sh
    660: (0, 1, 0, 0),  # "đã trả hàng nhưng chưa được hoàn tiền" → Sv
    665: (0, 0, 1, 0),  # "hình lụa hồng nhưng giao lụa đỏ bóng" → Sh
    666: (1, 0, 0, 0),  # "mua cho mẹ nhưng con mặc được, khác hình" → Q
    679: (1, 0, 0, 0),  # "áo tốt nhưng form rộng quá" → Q
    683: (1, 0, 0, 0),  # "phù hợp giá tiền nên chất bình thường" → Q
    687: (1, 0, 0, 0),  # "sản phẩm không lung linh như hình. xấu." → Q
    692: (1, 0, 0, 0),  # "mặc vô bị bung chỉ" → Q
    694: (1, 0, 0, 0),  # "sản phẩm không đúng như ảnh" → Q
    695: (1, 0, 1, 0),  # "65kg nhưng đồ nhỏ, không đúng màu đã chọn" → Q+Sh
    697: (0, 1, 1, 0),  # "đặt màu da giao màu xám, không liên hệ hỏi" → Sh+Sv
    699: (1, 0, 0, 0),  # "đầm không đẹp rất xấu" → Q
    701: (0, 0, 1, 0),  # "sản phẩm không đúng mẫu" → Sh
    703: (1, 0, 0, 0),  # "nóng lắm, mặc cả bộ chỉ ngồi điều hoà được" → Q
    709: (0, 0, 1, 0),  # "nhận mẫu trơn không có ren như hình" → Sh
    719: (1, 0, 0, 0),  # "size không đúng kích thước, 5 cái chỉ 1 đúng" → Q
    729: (1, 0, 0, 0),  # "form xấu, mút ngực lỏng lẻo" → Q
    736: (1, 0, 0, 0),  # "áo ngắn, dưới 1m50 vẫn ngắn" → Q
    737: (1, 1, 0, 0),  # "áo chật chưa mặc không cho đổi" → Q+Sv
    743: (1, 0, 0, 0),  # "2 áo cùng xxl: 1 vàng vừa, 1 xám chật" → Q
    747: (0, 0, 1, 0),  # "người giao thái độ kém" → Sh
    750: (1, 0, 0, 0),  # "tạm ổn, dùng hơi nhàu, phải ủi" → Q
    760: (1, 0, 0, 0),  # "dây áo sau lưng dễ bị lật" → Q
    761: (1, 0, 0, 0),  # "giặt máy bay hết tấm đệm ra ngoài" → Q
    764: (0, 0, 1, 0),  # "giao sản phẩm nhanh chóng tốt" → Sh
    765: (1, 0, 0, 0),  # "không mặc được quá nhỏ dù đã xem size" → Q
    766: (1, 0, 0, 0),  # "may ẩu, bung chỉ" → Q
    767: (1, 0, 0, 0),  # "chật, thích hợp tuổi teen" → Q
    768: (1, 0, 0, 0),  # "không có miếng lót" → Q
    773: (1, 0, 0, 0),  # "vừa giá tiền, không đẹp nhưng không tới nỗi" → Q
    777: (1, 0, 0, 0),  # "áo chất dáng đẹp như quảng cáo" → Q
    778: (1, 0, 0, 0),  # "giặt xong xù hết lông" → Q
    781: (1, 0, 0, 0),  # "cũng đẹp và tốt sương sương" → Q
    782: (1, 0, 0, 0),  # "không mặc dừa buồn quá" → Q
    793: (1, 0, 0, 0),  # "vải mịn mặc rất mát, rất thích" → Q
}


def main():
    df = pd.read_csv(FILE_PATH)
    print(f"Loaded {len(df)} rows")

    before_zeros = ((df['Quality'] == 0) & (df['Service'] == 0) &
                    (df['Shipping'] == 0) & (df['Packing'] == 0)).sum()
    print(f"Rows with 0,0,0,0 before: {before_zeros}")

    updated = 0
    for idx, (q, sv, sh, p) in MANUAL_LABELS.items():
        row = df.iloc[idx]
        if (row['Quality'] == 0 and row['Service'] == 0 and
                row['Shipping'] == 0 and row['Packing'] == 0):
            df.at[idx, 'Quality'] = q
            df.at[idx, 'Service'] = sv
            df.at[idx, 'Shipping'] = sh
            df.at[idx, 'Packing'] = p
            updated += 1

    after_zeros = ((df['Quality'] == 0) & (df['Service'] == 0) &
                   (df['Shipping'] == 0) & (df['Packing'] == 0)).sum()
    print(f"Updated: {updated} rows")
    print(f"Rows with 0,0,0,0 after: {after_zeros}")
    print("\nLabel distribution after:")
    print(df[['Quality', 'Service', 'Shipping', 'Packing']].apply(pd.Series.value_counts))

    # Spot-check
    checks = {
        116: ("chat luong kem", (1, 0, 0, 0)),
        168: ("goi san pham ky / giao nhanh", (0, 0, 1, 1)),
        629: ("dep nhu hinh, dong goi dep", (1, 0, 0, 1)),
    }
    print("\n--- Spot checks ---")
    for idx, (desc, expected) in checks.items():
        row = df.iloc[idx]
        actual = (row['Quality'], row['Service'], row['Shipping'], row['Packing'])
        status = "OK" if actual == expected else "FAIL"
        print(f"[{status}] idx={idx} ({desc}): {actual}")

    df.to_csv(FILE_PATH, index=False)
    print(f"\nSaved to {FILE_PATH}")


if __name__ == "__main__":
    main()
