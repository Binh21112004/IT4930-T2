import pandas as pd

# Đọc file gốc
df = pd.read_csv(
    r"C:\Users\admin\Desktop\KHDL\IT4930-T2\data\Commentsauxuly\comments_data_ncds_preprocessed_toy.csv",
    dtype={"Quality": object, "Service": object, "Shipping": object, "Packing": object}
)

# -----------------------------------------------------------------------
# LABEL THỦ CÔNG 100 DÒNG ĐẦU (index 0 → 99)
# Format: (Quality, Service, Shipping, Packing)
# 1 = đề cập khía cạnh đó, 0 = không đề cập
# -----------------------------------------------------------------------
# Định nghĩa label:
# Quality  : chất lượng sản phẩm (sữa, tã, khăn...), mẫu mã, hương vị, thành phần, date, hàng giả/nhái
# Service  : dịch vụ khách hàng, tư vấn, hỗ trợ đổi trả, thái độ nhân viên CSKH, khuyến mãi/quà tặng
# Shipping : vận chuyển, thời gian giao hàng, shipper (thái độ, giao đúng/sai, giao trễ)
# Packing  : đóng gói (hộp/bao bì bị móp méo, sơ sài, không chống sốc, rách vỏ)

manual_labels = [
    # idx: (Quality, Service, Shipping, Packing)
    # 0: "tiki xử lý đơn... giao trễ... điện tổng đài... thiếu trách nhiệm"
    # → Shipping (giao trễ), Service (tổng đài, nhân viên không báo)
    (0, 1, 1, 0),

    # 1: "co giao sản phẩm đâu nhưng thấy giao thành công"
    # → Shipping (shipper báo giao thành công nhưng không giao)
    (0, 0, 1, 0),

    # 2: "giao mẫu dày, bé rất khó chịu khi sử dụng, sai mẫu"
    # → Quality (sai mẫu, bé khó chịu)
    (1, 0, 0, 0),

    # 3: "giao mẫu dày không giống mỗi khi mua, đã 2 lần mất niềm tin"
    # → Quality (sai mẫu)
    (1, 0, 0, 0),

    # 4: "sao đợt này tả dày quá, làm hoang mang"
    # → Quality (tã dày, chất lượng khác mẫu cũ)
    (1, 0, 0, 0),

    # 5: "giao sản phẩm sữa thì móp, được cái nồi quà tặng, bể cái lồng ở trong, nấu sao. giao sản phẩm quá tệ"
    # → Quality (sản phẩm bị hỏng - nồi bể), Shipping (giao tệ), Packing (hộp móp)
    (1, 0, 1, 1),

    # 6: "ghi mua 3 tặng nồi... ghi chữ nhỏ xíu... xoá app"
    # → Service (quảng cáo gây hiểu lầm, khuyến mãi không đúng)
    (0, 1, 0, 0),

    # 7: "hình ảnh đăng bán 1 vị, thêm giỏ 1 vị"
    # → Service (giao sai sản phẩm so với mô tả/quảng cáo)
    (0, 1, 0, 0),

    # 8: "đơn giao trễ vì shipper báo chỉ có mỗi đơn mình và xa quá nên hẹn lại"
    # → Shipping (giao trễ, shipper hẹn lại)
    (0, 0, 1, 0),

    # 9: "khui sữa ra bị móp méo tùm lum. không chấp nhận được"
    # → Packing (hộp sữa bị móp méo)
    (0, 0, 0, 1),

    # 10: "dạo này đóng gói sơ xài, tôi mua 4 hộp, 3 hộp bị móp, không đậy nắp được"
    # → Packing (đóng gói sơ sài, hộp móp)
    (0, 0, 0, 1),

    # 11: "cửa hàng giao sản phẩm móp sẵn chứ không phải do vận chuyển"
    # → Packing (hộp sữa móp - lỗi từ nguồn)
    (0, 0, 0, 1),

    # 12: "hộp bị móp nên hơi thất vọng. lần đầu mình mua thì tốt, rất tiếc cho lần này"
    # → Packing (hộp bị móp)
    (0, 0, 0, 1),

    # 13: "không gọi nhưng nhá máy, gọi lại thì thái độ kém"
    # → Shipping (shipper thái độ kém khi giao)
    (0, 0, 1, 0),

    # 14: "con mình không hợp tác với sữa này"
    # → Quality (bé không uống được, sữa không phù hợp)
    (1, 0, 0, 0),

    # 15: "cửa hàng đóng gói sản phẩm cực tệ, nhận lần nào cũng móp méo"
    # → Packing (đóng gói tệ, hộp móp)
    (0, 0, 0, 1),

    # 16: "sao không có tem phụ từ công ty... liệu có phải sản phẩm fake"
    # → Quality (nghi ngờ hàng giả, không có tem xác nhận nguồn gốc)
    (1, 0, 0, 0),

    # 17: "hộp bị móp với cái chỗ mở lắp bị bung nhưng vẫn gửi cho khách"
    # → Service (vẫn giao hàng lỗi), Packing (hộp móp, bung nắp)
    (0, 1, 0, 1),

    # 18: "sữa bị móp méo nhưng vẫn gửi kh"
    # → Service (vẫn giao hàng lỗi), Packing (sữa bị móp)
    (0, 1, 0, 1),

    # 19: "sao không thấy phần khuyến mãi như hình nhỉ?"
    # → Service (không nhận được khuyến mãi như quảng cáo)
    (0, 1, 0, 0),

    # 20: "giao sản phẩm quá chậm, bình thường đặt khuya giao chiều nhưng đợt này 4 ngày sau mới giao"
    # → Shipping (giao chậm)
    (0, 0, 1, 0),

    # 21: "sản phẩm mỏng và thấm hút kém bằng mẫu cũ"
    # → Quality (chất lượng tã kém hơn mẫu cũ)
    (1, 0, 0, 0),

    # 22: "mua combo 12 gói, tiki trading giao đúng 1 gói. shipper không chịu nhận lại... tổng đài không giải quyết"
    # → Service (tổng đài không giải quyết), Shipping (giao thiếu hàng, shipper từ chối)
    (0, 1, 1, 0),

    # 23: "mô tả không đúng, giao sai. combo 12 gói 1 kiện, giao thực tế 1 gói. sau 3 ngày vẫn chưa giao bù"
    # → Service (sản phẩm không đúng mô tả), Shipping (giao thiếu, chưa giao bù)
    (0, 1, 1, 0),

    # 24: "mình mua 4 combo... thanh toán đủ nhưng chỉ nhận 1 thùng và 4 gói"
    # → Shipping (giao thiếu hàng)
    (0, 0, 1, 0),

    # 25: "đặt hoa tốc giao sai ngày không đúng cam kết"
    # → Shipping (giao sai ngày, không đúng cam kết)
    (0, 0, 1, 0),

    # 26: "tôi thanh toán mua combo 12 gói - chỉ giao 1 gói khăn giấy ướt. đề nghị đổi lại"
    # → Shipping (giao thiếu hàng)
    (0, 0, 1, 0),

    # 27: "sản phẩm lỗi thuộc diện bị thu hồi. tiki không cho đổi trả hoàn tiền, không giải thích"
    # → Quality (sản phẩm lỗi bị thu hồi), Service (không cho đổi trả, không giải thích)
    (1, 1, 0, 0),

    # 28: "sữa méo mó. bật cả nắp hộp. không biết chất lượng sữa có bị ảnh hưởng không"
    # → Packing (hộp méo, bật nắp)
    (0, 0, 0, 1),

    # 29: "đặt 3 hộp nhưng bị móp hết 2 hộp mặc dù mỗi hộp đều được bọc xốp và thùng khá chắc chắn"
    # → Packing (hộp bị móp dù đóng gói cẩn thận - lỗi sản phẩm gốc)
    (0, 0, 0, 1),

    # 30: "sữa thì tốt, date xa... mình cho 3 sao vì shipper tiki quá tệ. y/c kiểm hàng nhưng shipper không cho"
    # → Quality (sữa tốt - tích cực), Shipping (shipper thái độ tệ, không cho kiểm hàng)
    (1, 0, 1, 0),

    # 31: "đóng gói rất không thân thiện với môi trường... 1 hộp sữa nhưng đóng thùng quá lớn... nhiều nilong"
    # → Packing (đóng gói không hợp lý, lãng phí)
    (0, 0, 0, 1),

    # 32: "bữa giờ mua đóng gói rất kỹ nhưng cái này chắc móp trước khi đóng gói"
    # → Packing (hộp bị móp từ trước khi đóng gói)
    (0, 0, 0, 1),

    # 33: "giao sản phẩm gì móp méo vậy, hộp méo nhiều hộp méo ít"
    # → Packing (hộp bị móp méo)
    (0, 0, 0, 1),

    # 34: "sản phẩm nằm trong nhóm thu hồi nhưng không thấy tiki ý kiến xử lý"
    # → Quality (sản phẩm bị thu hồi), Service (không xử lý, không phản hồi)
    (1, 1, 0, 0),

    # 35: "hộp ngoài nguyên vẹn, nhưng hộp sữa bên trong bị móp. móp sẵn nhưng vẫn đóng gói giao khách"
    # → Service (vẫn giao hàng lỗi), Packing (hộp sữa bên trong bị móp sẵn)
    (0, 1, 0, 1),

    # 36: "giao sản phẩm trễ lần nào cũng vậy"
    # → Shipping (giao trễ thường xuyên)
    (0, 0, 1, 0),

    # 37: "sữa có vị mặn bị hỏng tôi muốn hoàn trả liên hệ cho tôi"
    # → Quality (sữa hỏng, vị mặn), Service (muốn hoàn trả)
    (1, 1, 0, 0),

    # 38: "giao sản phẩm ẩu, đóng gói sơ xài"
    # → Shipping (giao ẩu), Packing (đóng gói sơ sài)
    (0, 0, 1, 1),

    # 39: "không biết do bên cửa hàng hay bên giao nhưng hộp bị méo"
    # → Packing (hộp bị méo)
    (0, 0, 0, 1),

    # 40: "lần này mình đặt sản phẩm chậm hơn so với dự kiến"
    # → Shipping (giao chậm)
    (0, 0, 1, 0),

    # 41: "tôi đề nghị tiki rà soát lại thái độ của shipper khu vực p14 quận 8. thái độ rất kém, nhiều lần"
    # → Shipping (shipper thái độ kém, nhiều lần)
    (0, 0, 1, 0),

    # 42: "sản phẩm bị móp méo hộp. hạn dùng"
    # → Packing (hộp bị móp)
    (0, 0, 0, 1),

    # 43: "mong bên nhà bán đóng sản phẩm có tâm xíu, sản phẩm nhận 10 đơn móp hết 9"
    # → Packing (đóng gói không tốt, hộp móp liên tục)
    (0, 0, 0, 1),

    # 44: "sau khi dùng sản phẩm, bé thường xuyên bị đầy hơi, nóng trong người, nấc cụt. sản phẩm không phù hợp với baby việt nam"
    # → Quality (sữa không phù hợp, gây phản ứng cho bé)
    (1, 0, 0, 0),

    # 45: "đóng gói cẩn thận nhưng hộp bị móp"
    # → Packing (đóng gói cẩn thận nhưng vẫn bị móp - nhận xét cả 2 chiều về Packing)
    (0, 0, 0, 1),

    # 46: "có chống sốc nhưng vẫn bị móp sữa"
    # → Packing (dù có chống sốc vẫn bị móp)
    (0, 0, 0, 1),

    # 47: "nắp hộp quá lỏng lẻo, không chặt như hộp 850gram"
    # → Quality (chất lượng hộp/nắp kém so với loại khác)
    (1, 0, 0, 0),

    # 48: "mình mua rất nhiều sữa nan ở đây, nhưng 3 lần hộp sữa bị móp... móp nhưng không đóng hộp được. tiki đóng gói tệ"
    # → Packing (đóng gói tệ, hộp móp nhiều lần, không đóng nắp được)
    (0, 0, 0, 1),

    # 49: "mình đặt mua 5. đóng gói rất sơ sài có tới 3 bị móp ngay miệng hở cả nắp gây khó khăn trong việc bảo quản"
    # → Packing (đóng gói sơ sài, hộp móp, hở nắp)
    (0, 0, 0, 1),

    # 50: "hộp bị méo. cả 2 lần mua đều bị vậy. thêm lần đầu 1 hộp có hơi rỉ sét bên hông"
    # → Quality (hộp bị rỉ sét - lỗi sản phẩm), Packing (hộp bị méo liên tục)
    (1, 0, 0, 1),

    # 51: "giao sản phẩm gì nhưng hộp biến dạng móp méo tùm lum... không biết có uy tín hay không"
    # → Packing (hộp bị móp méo)
    (0, 0, 0, 1),

    # 52: "tôi muốn trả sản phẩm vì ngay lô sản phẩm bị thu hồi của hãng"
    # → Quality (sản phẩm bị thu hồi), Service (muốn trả hàng)
    (1, 1, 0, 0),

    # 53: "cửa hàng dùm đổi lại sản phẩm nhe"
    # → Service (yêu cầu đổi sản phẩm)
    (0, 1, 0, 0),

    # 54: "sữa bị móp méo... cửa hàng cố tình gửi... móp ở phần nắp, mở ra không thể đóng nắp lại được"
    # → Service (cố tình giao hàng lỗi), Packing (hộp móp, không đóng nắp được)
    (0, 1, 0, 1),

    # 55: "sản phẩm giao toàn móp méo, cẩu thả, lỗi do bên đóng gói sản phẩm"
    # → Packing (đóng gói cẩu thả, hộp móp)
    (0, 0, 0, 1),

    # 56: "sữa vẫn bị hơi móp, giao trễ 2 ngày"
    # → Shipping (giao trễ), Packing (hộp bị móp)
    (0, 0, 1, 1),

    # 57: "giao sản phẩm 2 bị móp hết, quá tệ"
    # → Packing (hộp bị móp)
    (0, 0, 0, 1),

    # 58: "mua 1,2 lần giá rẻ hơn thị trường đến lần thứ 3 giá cao hơn thị trường"
    # → Service (giá cả không ổn định, tăng giá)
    (0, 1, 0, 0),

    # 59: "sản phẩm nhận khui ra thấy có hạt bụi đen trong sữa... màu sắc đậm hơn"
    # → Quality (sữa có bụi đen, màu sắc khác thường - nghi ngờ chất lượng)
    (1, 0, 0, 0),

    # 60: "mua 3 móp dẹp cả 3 lon"
    # → Packing (cả 3 lon đều bị móp)
    (0, 0, 0, 1),

    # 61: "mua 599k được tặng 1b tã... chốt đơn xong xem lại không thấy... thất vọng"
    # → Service (không nhận được quà tặng như cam kết)
    (0, 1, 0, 0),

    # 62: "tiki dạo này giao sản phẩm không đúng hẹn. mua giao trong ngày nhưng 2 ngày sau mới giao"
    # → Shipping (giao không đúng hẹn)
    (0, 0, 1, 0),

    # 63: "đánh giá không tính điểm shipper cực kì hách dịch. sáng sớm gọi nói giọng khó chịu... thái độ không thể chấp nhận được"
    # → Shipping (shipper thái độ rất kém)
    (0, 0, 1, 0),

    # 64: "hài lòng, giao nhanh. hi vọng nguồn chất lượng tốt định"
    # → Shipping (giao nhanh - tích cực)
    (0, 0, 1, 0),

    # 65: "tiki gói có cái thùng đẹp nhưng bọc chống sốc như không bọc, làm móp sữa"
    # → Packing (thùng có nhưng chống sốc không hiệu quả, sữa bị móp)
    (0, 0, 0, 1),

    # 66: "mua sản phẩm lần nào cũng thế giao sản phẩm trậm mấy ngày so với thông báo"
    # → Shipping (giao trễ thường xuyên)
    (0, 0, 1, 0),

    # 67: "sản phẩm không đảm bảo chất lượng, thuộc lô bị nhiễm vi khuẩn, chính sách trả hàng không thống nhất"
    # → Quality (sản phẩm nhiễm vi khuẩn, không đảm bảo), Service (chính sách trả hàng không nhất quán)
    (1, 1, 0, 0),

    # 68: "có lẽ là sản phẩm nhái hoặc sản phẩm tẩy date... không có vòng tròn xanh dương như hộp đang dùng"
    # → Quality (nghi ngờ hàng nhái/tẩy date)
    (1, 0, 0, 0),

    # 69: "nhận được sản phẩm vỏ hộp bị bóp méo"
    # → Packing (hộp bị móp)
    (0, 0, 0, 1),

    # 70: "sản phẩm bị móp méo nhiều"
    # → Packing (sản phẩm bị móp)
    (0, 0, 0, 1),

    # 71: "giao sản phẩm trễ và giao sản phẩm móp méo. quá thất vọng"
    # → Shipping (giao trễ), Packing (sản phẩm móp)
    (0, 0, 1, 1),

    # 72: "chất lượng cũng được, nhưng bên vận chuyển chất lượng quá tệ"
    # → Quality (chất lượng ổn), Shipping (vận chuyển tệ)
    (1, 0, 1, 0),

    # 73: "đánh giá không tính điểm chất lượng tốt bé nhà mình uống rất hợp, lần này mình đặt 2 hộp thì 1 hộp bị móp méo"
    # → Quality (sữa tốt, bé hợp), Packing (1 hộp bị móp)
    (1, 0, 0, 1),

    # 74: "đánh giá không tính điểm đóng gói cũng cẩn thận nhưng hộp sữa vẫn bị móp méo như bị móp méo trước khi đóng"
    # → Packing (đóng gói cẩn thận nhưng hộp bị móp sẵn từ trước)
    (0, 0, 0, 1),

    # 75: "tiki giao sản phẩm càng ngày càng ẩu, đóng gói sơ sài. hộp sữa móp méo, bung nắp ngoài"
    # → Packing (đóng gói sơ sài, hộp móp, bung nắp)
    (0, 0, 0, 1),

    # 76: "mình mua được mấy hôm nay... sữa không được thơm như cũ, màu sữa nhạt hơn, vị sữa không được đậm... con nôn hết sữa"
    # → Quality (chất lượng sữa kém hơn mẫu cũ, bé không hợp), Service (cần gặp CSKH)
    (1, 1, 0, 0),

    # 77: "sữa mới trắng, mịn hơn nhưng không thơm... tiki đóng gói sơ sài. thùng carton xô lệch bong băng dính"
    # → Quality (chất lượng sữa thay đổi), Packing (đóng gói sơ sài, thùng xô lệch)
    (1, 0, 0, 1),

    # 78: "không có muỗng mình đong bằng gì nhỉ?"
    # → Quality (thiếu phụ kiện - không có muỗng trong hộp)
    (1, 0, 0, 0),

    # 79: "bé nhà mình mấy hôm đầu uống bị đi ngoài... sữa loại mới không thơm và ngọt như loại cũ"
    # → Quality (bé phản ứng với sữa, chất lượng thay đổi so với mẫu cũ)
    (1, 0, 0, 0),

    # 80: "trong sữa có sạn đen. mình bị 3 hộp đều như vậy"
    # → Quality (sữa có tạp chất - sạn đen, nghiêm trọng)
    (1, 0, 0, 0),

    # 81: "đã 3 lần đặt sản phẩm, lần nào về cũng bị móp nặng. góp ý cũng như không"
    # → Service (góp ý không được lắng nghe), Packing (hộp bị móp liên tục)
    (0, 1, 0, 1),

    # 82: "mình mua con nhà mình uống bị đi ngoài"
    # → Quality (sữa gây tiêu chảy cho bé)
    (1, 0, 0, 0),

    # 83: "sản phẩm nhận bị móp, không biết có ảnh hưởng chất lượng sữa hay không. mong tiki đóng gói cẩn thận"
    # → Packing (hộp bị móp, lo ngại chất lượng sữa bên trong)
    (0, 0, 0, 1),

    # 84: "tôi chưa nhận được sản phẩm này. chỉ nhận được 2 hộp sữa giấy. nhưng tôi đã trả tiền đủ đơn"
    # → Shipping (giao thiếu hàng)
    (0, 0, 1, 0),

    # 85: "cửa hàng giao sản phẩm giả, không có mã pin, yêu cầu hoàn tiền"
    # → Quality (hàng giả), Service (yêu cầu hoàn tiền)
    (1, 1, 0, 0),

    # 86: "không được hài lòng; bao gói của hãng kém. đánh giá friso"
    # → Packing (bao gói kém)
    (0, 0, 0, 1),

    # 87: "sữa mẫu mới này sao khó tan hơn mẫu cũ. hạt sữa rời li ti khác mẫu cũ không biết là sữa chuẩn hay không"
    # → Quality (chất lượng sữa thay đổi, khó tan, nghi ngờ chuẩn)
    (1, 0, 0, 0),

    # 88: "giao sản phẩm thiếu rất nhiều, mong cửa hàng giải quyết hợp lý"
    # → Shipping (giao thiếu hàng), Service (yêu cầu giải quyết)
    (0, 1, 1, 0),

    # 89: "sao con mình từ hôm dùng sữa này lại bị tiêu chảy vậy... từ khi dùng sữa là bị"
    # → Quality (sữa gây tiêu chảy, không phù hợp)
    (1, 0, 0, 0),

    # 90: "đặt sản phẩm từ đầu tháng 9 gần hết tháng 10 mới giao. gói sản phẩm quá ẩu"
    # → Shipping (giao cực kỳ chậm), Packing (đóng gói ẩu)
    (0, 0, 1, 1),

    # 91: "giao sản phẩm quá lâu. không có niềm tin vào tiki nữa rồi"
    # → Shipping (giao quá chậm)
    (0, 0, 1, 0),

    # 92: "sản phẩm bị mớp méo không đảm bảo chất lượng"
    # → Packing (sản phẩm bị móp, lo chất lượng)
    (0, 0, 0, 1),

    # 93: "sản phẩm frisolac gold 3 sử dụng khá tốt"
    # → Quality (sản phẩm tốt - tích cực)
    (1, 0, 0, 0),

    # 94: "đóng gói tệ, hộp bị móp méo"
    # → Packing (đóng gói tệ, hộp móp)
    (0, 0, 0, 1),

    # 95: "sản phẩm và giá rất tốt sẻ ủng hộ tiếp"
    # → Quality (sản phẩm và giá tốt - tích cực)
    (1, 0, 0, 0),

    # 96: "không check được mã vạch. rất hoang mang"
    # → Quality (nghi ngờ hàng thật/giả vì không check được mã vạch)
    (1, 0, 0, 0),

    # 97: "không ngon bằng mẫu cũ. uống thấy kiểu gì ấy"
    # → Quality (chất lượng sữa thay đổi, kém hơn mẫu cũ)
    (1, 0, 0, 0),

    # 98: "kg tra được mã vạch nên kg hài lòng về sản phẩm"
    # → Quality (không xác minh được hàng thật qua mã vạch)
    (1, 0, 0, 0),

    # 99: "giao sản phẩm nhanh, hài lòng"
    # → Shipping (giao nhanh - tích cực)
    (0, 0, 1, 0),
]

# Áp dụng labels
for i, (q, s, sh, p) in enumerate(manual_labels):
    df.at[i, "Quality"] = q
    df.at[i, "Service"] = s
    df.at[i, "Shipping"] = sh
    df.at[i, "Packing"] = p

# Chuyển về int cho 100 dòng đầu
for col in ["Quality", "Service", "Shipping", "Packing"]:
    df[col] = pd.to_numeric(df[col], errors='coerce')
    df[col] = df[col].astype("Int64")  # Int64 hỗ trợ NaN

# Ghi lại file gốc
df.to_csv(
    r"C:\Users\admin\Desktop\KHDL\IT4930-T2\data\Commentsauxuly\comments_data_ncds_preprocessed_toy.csv",
    index=False
)

print("✅ Đã label lại 100 dòng đầu và ghi vào file gốc thành công!")

# Kiểm tra kết quả
print("\n=== KIỂM TRA 10 DÒNG ĐẦU ===")
print(df[["content", "Quality", "Service", "Shipping", "Packing"]].head(10).to_string())

# Thống kê phân phối label trong 100 dòng đầu
print("\n=== THỐNG KÊ 100 DÒNG ĐẦU ===")
first_100 = df.head(100)
for col in ["Quality", "Service", "Shipping", "Packing"]:
    count = first_100[col].sum()
    print(f"  {col}: {count}/100 dòng có nhãn 1 ({count}%)")
