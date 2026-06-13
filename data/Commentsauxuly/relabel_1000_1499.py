import pandas as pd, sys
sys.stdout.reconfigure(encoding='utf-8')

df = pd.read_csv(
    r"C:\Users\admin\Desktop\KHDL\IT4930-T2\data\Commentsauxuly\comments_data_ncds_preprocessed_toy.csv"
)

# -----------------------------------------------------------------------
# LABEL THỦ CÔNG DÒNG 1000 -> 1499 (index 1000-1499, file line 1002-1501)
# Quality  : chất lượng SP (hư hỏng, vị lạ, hàng giả/nhái, sai mẫu, date cận/hết hạn)
# Service  : CSKH, tư vấn, đổi trả, khuyến mãi/quà không đúng, giá cao/sai, hoàn tiền
# Shipping : giao trễ, giao nhầm/thiếu, shipper thái độ, xác nhận giao ảo
# Packing  : đóng gói sơ sài, hộp móp/rách, bao bì rách/bẩn, nắp bung, không chống sốc
# -----------------------------------------------------------------------

manual_labels = [
    # 1000: "sữa cảm nhận khi uống bình thường nhưng giá cao"
    # Quality (+), Service (giá cao)
    (1, 1, 0, 0),
    # 1001: "sữa giao có hộp bị hở chảy sữa, cảm thấy không yên tâm về chất lượng sữa"
    # Quality (sữa chảy - lo ngại chất lượng), Packing (hộp bị hở)
    (1, 0, 0, 1),
    # 1002: "hộp móp méo, không phải do vận chuyển vì tôi thấy nhà bán bọc rất kỹ. nhãn nắp rách. sản phẩm tặng kèm rỉ sét nắp hộp, cận date"
    # Quality (SP tặng rỉ sét, cận date), Service (bán SP tặng kém chất lượng), Packing (hộp móp méo, nhãn rách)
    (1, 1, 0, 1),
    # 1003: "sản phẩm bị vỡ đã gọi điện và email tiki 4-5 lần. kêu tôi giữ sản phẩm vỡ... mặt sản phẩm sữa nên kiến bu đầy... đã gần 1 tháng vẫn không thấy ai thu hồi. dịch vụ giải quyết vấn đề sau khi mua quá tệ"
    # Quality (SP vỡ, kiến bu vào), Service (xử lý khiếu nại cực kỳ chậm - 1 tháng)
    (1, 1, 0, 0),
    # 1004: "khi giao đến thì hộp bị cấn móp sữa văng ra tùm lum rồi... tiki có hỏi là đổi trả hoặc hoàn tiền không... thời gian giao hơn 1 tuần nên chấp nhận để lại dùng"
    # Service (tiki hỗ trợ đổi trả), Shipping (giao chậm 1 tuần), Packing (hộp bị cấn móp, sữa văng ra)
    (0, 1, 1, 1),
    # 1005: "sữa bột hơi bị khô và có mùi giống dầu á! date thì vẫn nhưng sao mùi hơi lạ"
    # Quality (sữa khô, mùi lạ - nghi chất lượng kém)
    (1, 0, 0, 0),
    # 1006: "mua cho mẹ mình uống mẹ mình nói đây như bột sắn vậy, mở ra không có thơm mùi gì và không có mịn. sữa rất ngọt hơn cần thiết"
    # Quality (sữa không thơm, không mịn, ngọt quá - chất lượng không đạt)
    (1, 0, 0, 0),
    # 1007: "ưu điểm giao sản phẩm nhanh nhưng chưa hài lòng về sản phẩm nắp thiếc bị bung ra hộp méo bị bẹp"
    # Shipping (+), Packing (nắp thiếc bung, hộp méo bẹp)
    (0, 0, 1, 1),
    # 1008: "nắp hộp sữa bị bung, sữa văng hết ra ngoài, chất lượng quá tệ"
    # Packing (nắp bung, sữa văng ra)
    (0, 0, 0, 1),
    # 1009: "chất lượng tốt, có thiệp cám ơn kèm theo, uy tín, đợi ông bà dùng phản hồi chất lượng sẽ mua tiếp"
    # Quality (+)
    (1, 0, 0, 0),
    # 1010: "mua 3 hộp sữa ensure to thì 2 hộp lỗi, 1 hộp bị bẹp, 1 hộp bị tung sữa ra ngoài, không dùng để biếu được"
    # Quality (SP lỗi), Packing (1 hộp bẹp, 1 hộp tung sữa ra)
    (1, 0, 0, 1),
    # 1011: "mua lần 1 tốt. lần 2 nắp thiếc bung lên hết. nhắn cho bên hỗ trợ thì không thấy hồi âm. chính sách hỗ trợ tệ!"
    # Service (hỗ trợ không phản hồi, chính sách tệ), Packing (nắp thiếc bung)
    (0, 1, 0, 1),
    # 1012: "đặt mua sữa bột ensure, cửa hàng lại giao sữa hiệu khác, yêu cầu giao lại đúng loại"
    # Shipping (giao sai nhãn hiệu)
    (0, 0, 1, 0),
    # 1013: "không có tem dán bảo đảm sản phẩm nguyên, chất lượng và chính hãng"
    # Quality (không có tem bảo đảm - nghi hàng giả)
    (1, 0, 0, 0),
    # 1014: "giao chất lượng tốt. nhanh. đóng gói không chèn"
    # Quality (+), Shipping (+), Packing (không có lớp chèn)
    (1, 0, 1, 1),
    # 1015: "cửa hàng đóng gói sản phẩm như thế nào, nhưng bung 2 nắp nhôm lên hết và đổ sữa ra ngoài nhiều, lon móp méo hết, cửa hàng nên rút kinh nghiệm"
    # Packing (nắp nhôm bung, sữa đổ ra, lon móp méo)
    (0, 0, 0, 1),
    # 1016: "1 hộp sữa hơn 600k, đóng gói mấy lớp nhưng móp méo nặng thế này chứng tỏ cửa hàng cố tình bán sữa bị móp hộp cho khách online"
    # Quality (bán SP bị móp cố tình), Service (cố tình bán SP kém), Packing (móp nặng dù nhiều lớp)
    (1, 1, 0, 1),
    # 1017: "quá thất vọng về chính sách khuyến mãi của tiki, lúc đặt sản phẩm web để mua 3 sản phẩm tặng 1 vali khi nhận không có quà khuyến mãi. nhận sản phẩm thì nắp bị bung. mình muốn trả lại sản phẩm"
    # Service (không nhận được quà, muốn trả hàng), Packing (nắp bị bung)
    (0, 1, 0, 1),
    # 1018: "thấy đăng mua 2 hộp được tặng bộ mền gối, hôm nay nhận sản phẩm không có mền gối"
    # Service (không nhận được quà mền gối)
    (0, 1, 0, 0),
    # 1019: "mua từ 19/8 nhưng hỏi không ai phản hồi lại thời gian giao... 2 tháng mới có sữa để uống"
    # Service (không phản hồi), Shipping (giao cực kỳ chậm - 2 tháng)
    (0, 1, 1, 0),
    # 1020: "khi mua hàng thì thấy báo mua 2 hộp tặng chăn nhưng nhận hàng thì không thấy có"
    # Service (không nhận được quà chăn)
    (0, 1, 0, 0),
    # 1021: "giao sản phẩm chậm rãi quá không đúng thời hạn dự định tệ quá luôn"
    # Shipping (giao chậm không đúng hẹn)
    (0, 0, 1, 0),
    # 1022: "treo đầu dê bán thịt. bảo mua 3 tặng 1 vali nhưng không tặng"
    # Service (không tặng quà như quảng cáo - lừa đảo)
    (0, 1, 0, 0),
    # 1023: "do đợi lâu quá. chất lượng chưa biết"
    # Shipping (giao quá chậm)
    (0, 0, 1, 0),
    # 1024: "chất lượng tốt, tuy nhiên không có quà tặng như quảng cáo"
    # Quality (+), Service (không có quà như quảng cáo)
    (1, 1, 0, 0),
    # 1025: "sản phẩm tốt, giao sản phẩm hơi lâu"
    # Quality (+), Shipping (giao hơi chậm)
    (1, 0, 1, 0),
    # 1026: "mất lòng tin về vụ sản phẩm không có. thất vọng"
    # Service (không có quà, mất lòng tin)
    (0, 1, 0, 0),
    # 1027: "nhận sản phẩm không có quà tặng"
    # Service (không có quà tặng)
    (0, 1, 0, 0),
    # 1028: "diều bay cũng được cao, nhưng mỏng manh, chưa dùng đã sứt chỉ lòi khung, cây xương khung không đủ kích thước... kết cuộc con diều bị đứt dây. hơi thất vọng"
    # Quality (diều mỏng manh, sứt chỉ, khung ngắn thiếu - kém chất lượng)
    (1, 0, 0, 0),
    # 1029: "sản phẩm quá tệ so với hình ảnh"
    # Quality (SP tệ, không đúng như hình)
    (1, 0, 0, 0),
    # 1030: "đã đặt mua 2 con diều hình doremon nhưng chỉ nhận được 1 con"
    # Shipping (giao thiếu 1 con diều)
    (0, 0, 1, 0),
    # 1031: "diều như loại 5k không đáng giá đó"
    # Quality (SP chất lượng rất kém, không đáng giá)
    (1, 0, 0, 0),
    # 1032: "mua 4 hộp, giao tới cái thùng rách rồi 4 hộp sữa bị móp tùm lum, 1 hộp bị gãy cái nắp gài hộp sữa luôn. đóng gói gì quá sơ sài, vận chuyển chắc quăng dữ lắm"
    # Service (yêu cầu đổi), Packing (thùng rách, 4 hộp móp, 1 hộp gãy nắp - đóng gói sơ sài)
    (0, 1, 0, 1),
    # 1033: "hạn sử dụng còn dài. vì dịch bệnh nên sản phẩm giao trễ 1 tháng. đóng gói ọp ẹp. sản phẩm sử dụng rất tốt!"
    # Quality (+), Shipping (giao trễ 1 tháng do dịch), Packing (đóng gói ọp ẹp)
    (1, 0, 1, 1),
    # 1034: "giao sản phẩm lâu, thời gian ghi giao là 15/9 mãi đến 25 mới nhận, trong khi đó đã đặt trước 1 tháng, sữa về hộp bị méo mó"
    # Shipping (giao chậm 10 ngày so với hẹn), Packing (hộp sữa méo mó)
    (0, 0, 1, 1),
    # 1035: "đợt này giao quá trễ đặt sản phẩm 20 tháng sáu tới 28 tây tháng sáu mình mới nhận được sản phẩm"
    # Shipping (giao trễ 8 ngày)
    (0, 0, 1, 0),
    # 1036: "số lượng ít, giá cao hơn loại khác"
    # Service (giá cao so với loại khác)
    (0, 1, 0, 0),
    # 1037: "giao sản phẩm quá lâu. đặt hôm 16/9 hẹn giao sản phẩm 20/9 nhưng đến nay vẫn chưa nhận được"
    # Shipping (giao chậm hơn hẹn nhiều ngày)
    (0, 0, 1, 0),
    # 1038: "đóng gói cẩu thả, thà cho túi nilông đen buộc lại nhưng lịch sự hơn"
    # Packing (đóng gói cẩu thả)
    (0, 0, 0, 1),
    # 1039: "giao sản phẩm quá chậm, nhưng đóng gói kỹ"
    # Shipping (giao quá chậm), Packing (+)
    (0, 0, 1, 1),
    # 1040: "chưa thấy ai giao nhưng hệ thống báo đã giao thành công. hài"
    # Shipping (xác nhận giao ảo)
    (0, 0, 1, 0),
    # 1041: "để tặng khăn ướt, nhưng giao sản phẩm không có"
    # Service (không nhận được quà khăn ướt)
    (0, 1, 0, 0),
    # 1042: "đặt size l8, giao m9 là sao? dối vậy sao?"
    # Shipping (giao sai size)
    (0, 0, 1, 0),
    # 1043: "ở trên ghi 499k được tặng quà. mình mua 1 lúc 5 combo. nhưng khi nhận sản phẩm không thấy tặng quà gì"
    # Service (không nhận được quà dù mua đủ điều kiện)
    (0, 1, 0, 0),
    # 1044: "tã quá mỏng, dùng 3h là nước tiểu thấm ướt người"
    # Quality (tã mỏng, thấm hút kém)
    (1, 0, 0, 0),
    # 1045: "đóng gói sản phẩm không cẩn thận"
    # Packing (đóng gói không cẩn thận)
    (0, 0, 0, 1),
    # 1046: "sản phẩm dùng tốt phù hợp giao sản phẩm nhanh"
    # Quality (+), Shipping (+)
    (1, 0, 1, 0),
    # 1047: "giao sản phẩm nhanh chóng, tốt"
    # Quality (+), Shipping (+)
    (1, 0, 1, 0),
    # 1048: "vừa mua xong thì mấy tiếng sau giá giảm! quá chán tiki!"
    # Service (giá giảm ngay sau khi mua - thiệt thòi)
    (0, 1, 0, 0),
    # 1049: "cửa hàng ơi giao sản phẩm lâu vậy cửa hàng mình đặt hôm 7/3 nhưng giờ vẫn bàn giao là sao"
    # Shipping (giao rất chậm, vẫn đang bàn giao)
    (0, 0, 1, 0),
    # 1050: "đặt tã quần nhưng giao tã dán, đã đổi trả sản phẩm 1 lần nhưng vẫn giao lại tã dán"
    # Service (đổi rồi vẫn giao sai lần 2), Shipping (giao sai loại 2 lần)
    (0, 1, 1, 0),
    # 1051: "tã dán nb của moony trắng rất oke nhưng tã quần thì thất vọng thật chun lỏng lẻo, không đứng form. chất liệu không có gì đặc biệt"
    # Quality (tã quần chất lượng kém - chun lỏng, không đứng form)
    (1, 0, 0, 0),
    # 1052: "bỉm dày phù hợp dùng ban đêm... bé mặc bị hăm bẹn, dùng sản phẩm khác không sao nhưng dùng moony lại hăm trở lại"
    # Quality (bỉm gây hăm - chất lượng đáng ngờ)
    (1, 0, 0, 0),
    # 1053: "bỉm số 1 là nhà mình đang dùng mình mua ở aeon, màu sắc vỏ bên ngoài đậm hơn, mở miếng bỉm ra thì dày và mềm hơn bịch số 2 mới mua của tiki trading, đang hoang mang quá không dám cho con dùng"
    # Quality (bỉm tiki khác biệt - mỏng mềm hơn mua tại shop - nghi hàng kém chất)
    (1, 0, 0, 0),
    # 1054: "thời điểm mình chọn mua sản phẩm trên ảnh có ghi đơn trên 1 triệu được khuyến mãi bàn đồ chơi cho bé nhưng khi giao sản phẩm lại không có. giao thì chậm, hẹn 24 giao thì 1/10 mới đến nơi"
    # Service (không nhận được quà), Shipping (giao chậm ~1 tuần so hẹn)
    (0, 1, 1, 0),
    # 1055: "mua 2 bịch sale 287k nhưng sao sản phẩm không giống sản phẩm thường vậy, lại có mùi hôi"
    # Quality (SP mùi hôi, khác biệt - nghi hàng kém/giả)
    (1, 0, 0, 0),
    # 1056: "treo đầu dê bán thịt. lên deal cho khách săn sale 4b tặng nôi nằm em bé xong giao bỉm trước, khách nhận bỉm xong thì huỷ mẹ đơn quà tặng"
    # Service (hủy quà tặng sau khi giao bỉm - lừa đảo)
    (0, 1, 0, 0),
    # 1057: "đơn sản phẩm của mình là bịch bỉm theo chương trình khuyến mãi được tặng gấu bông nhưng giao sản phẩm bỉm không thấy quà tặng kèm theo"
    # Service (không nhận được quà gấu bông)
    (0, 1, 0, 0),
    # 1058: "con mình xài tã moony natural hơn 1 năm nay... lần này mua thì tã bị hắc mùi hôi hóa chất rất khó chịu"
    # Quality (tã có mùi hóa chất hắc - chất lượng thay đổi/nghi hàng giả)
    (1, 0, 0, 0),
    # 1059: "quá thất vọng về bao bì sản phẩm, sản phẩm bị rách. bẩn và hôi, động tay vào bịch bỉm nhưng phải rửa tay xà phòng mới hết hôi. đồ dùng cho trẻ em nhưng bán không có tâm"
    # Quality (bỉm bẩn, hôi - không an toàn cho trẻ), Packing (bao bì rách, bẩn)
    (1, 0, 0, 1),
    # 1060: "đóng gói quá sơ sài làm rách bao bì"
    # Packing (đóng gói sơ sài làm rách bao bì)
    (0, 0, 0, 1),
    # 1061: "tại sao không có tặng gấu bông? yêu cầu gửi bù gấu bông cho tôi"
    # Service (không có quà gấu bông, yêu cầu gửi bù)
    (0, 1, 0, 0),
    # 1062: "mua đợt kmai 21/9, tưởng được tặng quà vì đơn 1200k, không ngờ chả có gì. bt thế mình mua của đại lý giá rẻ hơn nhưng vẫn có quà trug thu cho bé"
    # Service (không nhận được quà dù đủ điều kiện, giá tiki không cạnh tranh)
    (0, 1, 0, 0),
    # 1063: "bỉm đóng gói quá tệ. chỉ quấn 1 lớp mỏng bọc nilong. nhận được bỉm rách như vầy"
    # Packing (đóng gói quá tệ - 1 lớp mỏng bị rách)
    (0, 0, 0, 1),
    # 1064: "hiện tại mình đang dùng moony xanh. hôm nay nhận sản phẩm moony trắng. đợi mới biết chất lượng ntn. tã mềm đẹp"
    # Quality (+, mềm đẹp)
    (1, 0, 0, 0),
    # 1065: "đơn 5 bịch đóng sản phẩm thiếu cẩn thận, bẩn. túi đựng bỉm cũ. rất không hài lòng"
    # Packing (đóng gói thiếu cẩn thận, túi bẩn/cũ)
    (0, 0, 0, 1),
    # 1066: "mua nhiều để được tặng đệm nôi, xong giao mỗi bỉm huỷ không giao quà của khách. tôi muốn trả sản phẩm. tiki đảo khách sản phẩm"
    # Service (hủy quà tặng sau khi giao bỉm, yêu cầu trả hàng - lừa đảo)
    (0, 1, 0, 0),
    # 1067: "không nhận ra sự khác biệt so với bỉm moony xanh"
    # Quality (SP không có điểm khác biệt đáng kể)
    (1, 0, 0, 0),
    # 1068: "giao sản phẩm nhanh. nói là đơn sản phẩm từ 599k được tặng gấu bông nhưng khi nhận sản phẩm thì không có"
    # Service (không nhận được quà gấu bông), Shipping (+)
    (0, 1, 1, 0),
    # 1069: "bao bì bị rách cửa hàng dán băng dính che đi nhưng không hết. ghi ngoài ảnh đặt sản phẩm được tặng gấu bông nhưng không thấy có"
    # Service (không có quà gấu bông), Packing (bao bì rách, dán băng keo che)
    (0, 1, 0, 1),
    # 1070: "bao bì bẩn, rách, không kèm quà tặng như khuyến mãi, mọi người cân nhắc khi mua"
    # Service (không có quà tặng), Packing (bao bì bẩn, rách)
    (0, 1, 0, 1),
    # 1071: "hài lòng về chất lượng sản phẩm"
    # Quality (+)
    (1, 0, 0, 0),
    # 1072: "mua ngày 8/8 có khuyến mãi nhưng giao sản phẩm không có sản phẩm khuyến mãi"
    # Service (không nhận được SP khuyến mãi)
    (0, 1, 0, 0),
    # 1073: "e đặt 6 bịch tã nhưng không nhận được cái xe trượt như khuyến mãi nói ngày 11/1"
    # Service (không nhận được xe trượt như khuyến mãi)
    (0, 1, 0, 0),
    # 1074: "đóng gói sơ sài, không biết là túi bỉm rách trước hay shipper làm rách. quá thất vọng"
    # Packing (đóng gói sơ sài, túi bỉm rách)
    (0, 0, 0, 1),
    # 1075: "mua lúc 0:00 ngày 21/9, đầu chương trình luôn nhưng không có đồ chơi"
    # Service (không nhận được đồ chơi dù mua đúng chương trình)
    (0, 1, 0, 0),
    # 1076: "mua 3 bịch tã mà chẳng thấy tặng quà gì hết"
    # Service (không có quà tặng)
    (0, 1, 0, 0),
    # 1077: "chất lượng tốt hợp với giá tiền"
    # Quality (+), Service (+, giá)
    (1, 1, 0, 0),
    # 1078: "chưa nhận được quà tặng đã cập nhận là đã giao sản phẩm"
    # Service (quà tặng chưa giao dù báo đã giao), Shipping (xác nhận giao ảo cho quà)
    (0, 1, 1, 0),
    # 1079: "không có quà tặng như quảng cáo. không bao giờ mua lại tiki"
    # Service (không có quà như quảng cáo)
    (0, 1, 0, 0),
    # 1080: "cửa hàng đảo. giao sản phẩm xong rồi hủy quà. sớm sập tiệm nhé"
    # Service (hủy quà tặng sau khi giao SP - lừa đảo)
    (0, 1, 0, 0),
    # 1081: "sản phẩm hết hạn sử dụng sao lại còn bán"
    # Quality (SP hết hạn sử dụng - nghiêm trọng)
    (1, 0, 0, 0),
    # 1082: "gây dị ứng trẻ nhỏ, thua xa moony thường, nghi ngờ không phải chính hãng"
    # Quality (gây dị ứng, nghi hàng giả - kém hơn moony thường)
    (1, 0, 0, 0),
    # 1083: "sản phẩm bên ngoài bị bẩn quá"
    # Packing (bên ngoài bẩn)
    (0, 0, 0, 1),
    # 1084: "chất lượng tốt nhưng cửa hàng đóng sản phẩm không có trách nhiệm. cái hộp to đùng quăng cái chai vô không đệm mút hay giấy vô. kết quả gãy mất cái vòi không biết sài kiểu gì luôn. liệu có đổi lại được không"
    # Service (yêu cầu đổi), Packing (đóng gói vô trách nhiệm - gãy vòi)
    (0, 1, 0, 1),
    # 1085: "tiki giao sản phẩm chậm nhưng bị tốn phí. đặt chai nước rửa bình mấy ngày nhưng chẳng thấy đâu. đặt ở shoptretho giao trong vòng 12 đến 24h không tốn phí. chắc không mua sản phẩm nữa quá"
    # Service (giao chậm tốn phí, shop khác nhanh hơn không phí), Shipping (giao rất chậm)
    (0, 1, 1, 0),
    # 1086: "sản phẩm giao nhanh, nhận sản phẩm bị gãy mất cái vòi. sợ giống mấy ng mua trước nào ngờ mình nhận cũng bị luôn. nên gói và lót thêm"
    # Quality (SP gãy vòi), Shipping (+), Packing (không có lót đệm)
    (1, 0, 1, 1),
    # 1087: "vòi xịt đã bị gãy, không tìm thấy đâu trong bao bì, chắc bị gãy trước khi đóng gói nhưng vẫn giao cho khách"
    # Quality (vòi gãy từ trước khi đóng gói - cố tình bán SP hỏng), Packing (đóng gói không kiểm tra)
    (1, 0, 0, 1),
    # 1088: "mình không hiểu sao chai bị gãy vòi bơm nhưng vẫn giao khách. đã mua sản phẩm tiki nhiều lần rồi, lần đầu bị vậy"
    # Quality (vòi gãy - cố tình bán SP lỗi)
    (1, 0, 0, 0),
    # 1089: "sản phẩm giao chậm 2 ngày so với dự kiến, mở ra thấy chai nước rửa bình đã gãy vòi xịt, tìm trong thùng không thấy, chứng tỏ chai bị gãy vòi từ trước chứ không phải do vận chuyển, vậy nhưng vẫn cố tình giao sản phẩm"
    # Quality (vòi gãy từ trước - cố tình giao SP lỗi), Shipping (giao chậm 2 ngày)
    (1, 0, 1, 0),
    # 1090: "vì mua chung với nhiều món khác không hỗ trợ giao 2h nhưng phải chọn giao tiết kiệm, nhưng lúc giao sản phẩm lại tách ra giao riêng từng món. đặt từ thứ 6 sang tận thứ 5 tuần sau mới giao sản phẩm. cạn lời"
    # Service (tách đơn không hợp lý), Shipping (giao chậm - 1 tuần)
    (0, 1, 1, 0),
    # 1091: "giao sản phẩm quá chậm, tiki gửi xin lỗi không xác đáng, nếu không có sản phẩm thì báo hết sản phẩm. tại sao để khách chờ gần 1 tuần vẫn chưa đi giao"
    # Service (xử lý kém, xin lỗi không xác đáng), Shipping (giao chậm - gần 1 tuần)
    (0, 1, 1, 0),
    # 1092: "mua 2 chai, 1 chai bị gãy vòi, nhờ tiki đổi dùm, mong sớm được liên hệ"
    # Quality (1 chai gãy vòi), Service (yêu cầu đổi)
    (1, 1, 0, 0),
    # 1093: "tôi nhận sản phẩm thì vòi đã bị gãy. mọi lần tiki gói cẩn thận có cả xốp nhưng lần này bị vậy"
    # Quality (vòi gãy), Packing (lần này không có xốp đệm)
    (1, 0, 0, 1),
    # 1094: "sản phẩm được bọc không kỹ"
    # Packing (bọc không kỹ)
    (0, 0, 0, 1),
    # 1095: "sản phẩm bị gãy vòi bơm sản phẩm. để đổi lại sản phẩm khác thì làm thế nào ạ"
    # Quality (vòi gãy), Service (hỏi cách đổi)
    (1, 1, 0, 0),
    # 1096: "cửa hàng lần sau gói đồ cẩn thận của mình mở ra gãy vòi"
    # Quality (vòi gãy), Packing (gói không cẩn thận)
    (1, 0, 0, 1),
    # 1097: "tiki nên gói sản phẩm cẩn thận hơn vì mình về mở ra vòi đã bị gãy r nhưng nếu đổi trả thì tận 2-3 ngày sau mới đổi nên thôi mình dùng tạm"
    # Quality (vòi gãy), Service (thủ tục đổi chậm), Packing (gói không cẩn thận)
    (1, 1, 0, 1),
    # 1098: "dùng cũng được không bị nhờn lắm. rửa với nước là sạch"
    # Quality (+)
    (1, 0, 0, 0),
    # 1099: "đặt từ ngày 13/8 nhưng tới nay vẫn chưa nhận được. trong khi đã để đang vận chuyển rồi"
    # Shipping (giao cực kỳ chậm, không thấy tiến triển)
    (0, 0, 1, 0),
    # 1100: "bị hủy đơn sản phẩm hoài chán không muốn mua sản phẩm trên tiki nữa"
    # Service (đơn bị hủy liên tục)
    (0, 1, 0, 0),
    # 1101: "rất hài lòng, giao sản phẩm nhanh, sản phẩm đúng tiêu chuẩn"
    # Quality (+), Shipping (+)
    (1, 0, 1, 0),
    # 1102: "sản phẩm xài rất tốt tuy nhiên lúc giao sản phẩm mở ra vòi bị gãy"
    # Quality (+, nhưng vòi gãy khi nhận), Packing (đóng gói không bảo vệ vòi)
    (1, 0, 0, 1),
    # 1103: "order 2 bình, khi nhận được, khui thùng ra, chỉ có 1 bình thôi"
    # Shipping (giao thiếu 1 bình)
    (0, 0, 1, 0),
    # 1104: "có chai nước rửa nhưng đặt mua cả tuần cũng không thấy sản phẩm đâu. dạo này khâu giao sản phẩm quá kém"
    # Shipping (giao cực kỳ chậm - cả tuần không thấy)
    (0, 0, 1, 0),
    # 1105: "chưa nhận được sản phẩm nhưng tiki báo thành công, đã phản hồi nhưng chưa được giải quyết"
    # Service (không giải quyết), Shipping (xác nhận giao ảo)
    (0, 1, 1, 0),
    # 1106: "vừa mới đặt mua phát hiện cửa hàng gần nhà bán giá rẻ hơn, tiếc quá"
    # Service (giá tiki cao hơn cửa hàng gần nhà)
    (0, 1, 0, 0),
    # 1107: "e book sản phẩm từ hôm 21 đến nay chưa nhận được sản phẩm. tại sao vậy"
    # Shipping (giao cực kỳ chậm)
    (0, 0, 1, 0),
    # 1108: "giao sản phẩm quá chậm. 2 tuần rồi vẫn chưa nhận được sản phẩm"
    # Shipping (giao chậm - 2 tuần chưa có)
    (0, 0, 1, 0),
    # 1109: "nước rửa mua trong đợt khuyến mãi nên giá thành tốt"
    # Service (+, giá tốt do khuyến mãi)
    (0, 1, 0, 0),
    # 1110: "giặt thì mùi thơm nhưng nước giặt loãng xẹt, không giống như chất keo đặc mình mua bên cửa hàng con cưng. 1 chai này chắc dùng được 10 ngày quá"
    # Quality (nước giặt loãng, hao nhanh - chất lượng kém)
    (1, 0, 0, 0),
    # 1111: "sản phẩm không đúng như mô tả. không hài lòng. không biết có phải dán sai tem phụ ko"
    # Quality (SP không đúng mô tả, nghi tem sai - có thể hàng giả)
    (1, 0, 0, 0),
    # 1112: "sản phẩm không giống với hình ảnh, sản phẩm không hài lòng, giá hơi mắc so với sản phẩm, người giao sản phẩm thân thiện"
    # Quality (SP không giống hình), Service (giá mắc), Shipping (+, shipper thân thiện)
    (1, 1, 1, 0),
    # 1113: "sản phẩm quá cũ, rách bao nilông ở ngoài. sản xuất từ năm 2018"
    # Quality (SP quá cũ, bao bì rách, NSX từ 2018)
    (1, 0, 0, 0),
    # 1114: "mình đặt mua loại này nhưng khi giao sản phẩm thì lại giao loại màu trắng có vòi nên mình không hài lòng"
    # Shipping (giao sai loại)
    (0, 0, 1, 0),
    # 1115: "sản phẩm không giống hình ảnh, rất không hài lòng"
    # Quality (SP không giống hình)
    (1, 0, 0, 0),
    # 1116: "chai nước giặt của mình phần nắp lại là nắp ấn chứ không phải là nắp xoáy"
    # Quality (SP khác mô tả - nắp khác loại)
    (1, 0, 0, 0),
    # 1117: "dùng cũng được. có điều bao bì bị vận chuyển biến dạng túi bóng của bỉm nhưng không bị thủng túi"
    # Packing (bao bì bị biến dạng do vận chuyển)
    (0, 0, 0, 1),
    # 1118: "sữa thì chất lượng đó nhưng móp thì thôi rồi mua mỗi lần 6 con mình gần 6 tháng uống sữa móp rồi"
    # Quality (+), Packing (hộp sữa móp liên tục - nhiều lần)
    (1, 0, 0, 1),
    # 1119: "sản phẩm bị móp méo biến dạng"
    # Packing (SP bị móp méo biến dạng)
    (0, 0, 0, 1),
    # 1120: "sản phẩm giao bị móp. bên đây giao sản phẩm bị hoài"
    # Packing (SP móp - tái diễn nhiều lần)
    (0, 0, 0, 1),
    # 1121: "sản phẩm dày nhưng keo dán chưa tới 20 phút thì bung hết"
    # Quality (keo dán bung nhanh - SP lỗi)
    (1, 0, 0, 0),
    # 1122: "quá kém, mua 2m xong về dán cạnh bàn không dính"
    # Quality (SP không dính - chất lượng rất kém)
    (1, 0, 0, 0),
    # 1123: "sao chuông không kêu hư bây giờ có đổi được không"
    # Quality (SP hỏng - chuông không kêu), Service (hỏi cách đổi)
    (1, 1, 0, 0),
    # 1124: "mua 3 hộp sữa nhưng hết 2 hộp bị móp ntn. không bao bọc kỹ lưỡng bằng nylon chống sốc nhưng chỉ bỏ vô thùng rồi. cũng may hộp sữa chưa bị bung nắp. mình đọc thấy quá trời cmt góp ý vụ này nhưng cửa hàng vẫn chưa thay đổi"
    # Packing (không có chống sốc, 2/3 hộp bị móp)
    (0, 0, 0, 1),
    # 1125: "lần đầu tiên mua đúng sản phẩm ensure không ngon như vầy... khi mở hộp thì không ngửi thấy mùi thơm đặc trưng của loại sữa này, nhưng có mùi như sản phẩm để lâu bị lên dầu vậy. pha uống thì cũng không thơm ngon như sữa ensure mua siêu thị. nsx là tháng 11/2018, hsd là 11/2020"
    # Quality (sữa cũ, mùi khác, NSX 2018 - nghi hàng tồn kho lâu)
    (1, 0, 0, 0),
    # 1126: "tem nhập khẩu mờ toẹt, như kiểu fake. vỏ móp. cho 2 sao"
    # Quality (tem nhập khẩu mờ - nghi fake), Packing (vỏ móp)
    (1, 0, 0, 1),
    # 1127: "chưa biết sản phẩm như nào chứ giao sản phẩm hơn 10 ngày chưa thấy đâu, qua tiêu chuẩn giao sản phẩm dự kiến 1 tuần. gọi tổng đài không giải quyết được gì. liên tục 3 đơn sản phẩm tiki đều rất tệ"
    # Service (tổng đài không giải quyết được), Shipping (giao chậm - 10+ ngày, vượt dự kiến)
    (0, 1, 1, 0),
    # 1128: "tạm ổn tốt được cũng nên mua uống không tệ lắm"
    # Quality (+, tạm ổn)
    (1, 0, 0, 0),
    # 1129: "rất tốt, chỉ có 1 sơ sót nhỏ là nó bị móp ở đáy một chút!"
    # Quality (+), Packing (móp nhẹ ở đáy)
    (1, 0, 0, 1),
    # 1130: "mùi không thơm như sữa phân phối tại Việt Nam"
    # Quality (mùi khác biệt - nghi không phải hàng chính hãng VN)
    (1, 0, 0, 0),
    # 1131: "sữa ít thơm. giá mềm, date còn xa"
    # Quality (sữa ít thơm), Service (+, giá mềm)
    (1, 1, 0, 0),
    # 1132: "giao sản phẩm quá lâu, không bao giờ nên mua"
    # Shipping (giao quá chậm)
    (0, 0, 1, 0),
    # 1133: "tôi đặt cỡ lớn loại 54 miếng nhưng sao giao loại nhỏ 51 miếng tiền đã trả loại lớn rồi lại giao loại nhỏ"
    # Service (tính tiền loại lớn nhưng giao loại nhỏ - gian lận), Shipping (giao sai số lượng)
    (0, 1, 1, 0),
    # 1134: "sản phẩm rất sấu bào không nhẵn nói chung là tệ hại"
    # Quality (SP xấu, bào không nhẵn - gia công kém)
    (1, 0, 0, 0),
    # 1135: "một số cục bị lỗi, cũng hên xui. sản phẩm công ty nhưng không có kiểm tra sản phẩm trước khi đóng gói"
    # Quality (SP lỗi, không kiểm tra trước khi đóng gói)
    (1, 0, 0, 0),
    # 1136: "ủa mình chưa nhận sản phẩm gấu này nhưng, hình như mình huỷ này rồi nhưng sao vẫn giao được hay vậy"
    # Shipping (giao SP đã bị hủy - lỗi hệ thống)
    (0, 0, 1, 0),
    # 1137: "đặt con 40cm. giao con bé xíu 20cm. đảo! không bao giờ mua lại!"
    # Shipping (giao sai kích thước - 20cm thay vì 40cm - lừa đảo)
    (0, 0, 1, 0),
    # 1138: "giao sản phẩm nhanh, đóng gói cẩn thận"
    # Shipping (+), Packing (+)
    (0, 0, 1, 1),
    # 1139: "sản phẩm đúng như mô tả. rất hài lòng!"
    # Quality (+)
    (1, 0, 0, 0),
    # 1140: "sản phẩm đã thay đổi chất lượng thông qua quá trình sản xuất, đóng gói và vận chuyển"
    # Quality (chất lượng thay đổi - không còn tốt như trước)
    (1, 0, 0, 0),
    # 1141: "không hài lòng, đồ chơi cho em bé nhưng làm ẩu quá gỗ không mài nhẵn để tứ tưa vậy trẻ con chơi rồi đâm vào tay nó thì sao. thấy cửa hàng mô tả sản phẩm được mài giũa mịn màng nhưng giao cho khách thì ngược lại. lỗi sản xuất"
    # Quality (gỗ không mài nhẵn - lỗi sản xuất, nguy hiểm cho trẻ), Service (mô tả sai thực tế)
    (1, 1, 0, 0),
    # 1142: "sản phẩm đóng gói cẩn thận nhưng bên trong mở ra đồ bị gãy"
    # Quality (SP bị gãy), Packing (+)
    (1, 0, 0, 1),
    # 1143: "gãy đôi. không sử dụng được. nhắn tin cửa hàng không phản hồi. không hỗ trợ khách sản phẩm"
    # Quality (SP gãy đôi), Service (không phản hồi, không hỗ trợ)
    (1, 1, 0, 0),
    # 1144: "xe thiếu ốc, nhanh hỏng, chất lượng kém"
    # Quality (thiếu ốc, hỏng nhanh - chất lượng kém)
    (1, 0, 0, 0),
    # 1145: "xe không sử dụng được, kích thước qua bé và sản phẩm bị lỗi. bán sản phẩm cho bé nhưng như vậy thì tốt nhất cửa hàng không nên bán"
    # Quality (SP lỗi, kích thước nhỏ hơn mô tả)
    (1, 0, 0, 0),
    # 1146: "mình nhận được sản phẩm khi mở ra thì 2 bánh bị toét phần vít ốc nên bánh bị bung ra không vặn lại được. hy vọng cửa hàng gửi lại cho mình 2 cái bánh"
    # Quality (2 bánh bị toét vít ốc - lỗi SP), Service (yêu cầu gửi bù)
    (1, 1, 0, 0),
    # 1147: "giao thiếu sản phẩm, nhưng lại không cho xem sản phẩm, làm này để lấy tiền xây mã cho cả nhà nó"
    # Service (không cho xem SP trước khi nhận), Shipping (giao thiếu)
    (0, 1, 1, 0),
    # 1148: "cửa hàng giao sản phẩm bị súc bánh, súc gọng, và mất bánh xe đào chạy. nản"
    # Quality (SP bị hỏng - súc bánh, mất bánh), Shipping (giao SP bị hư)
    (1, 0, 1, 0),
    # 1149: "sản phẩm không giống hình mẫu, thực sự có chút thất vọng"
    # Quality (SP không giống hình mẫu)
    (1, 0, 0, 0),
    # 1150: "lỏng lẻo, 2 ngày đã bung keo của xe"
    # Quality (lỏng lẻo, keo bung sau 2 ngày - chất lượng rất kém)
    (1, 0, 0, 0),
    # 1151: "sản phẩm về bóc ra chưa dùng đã gãy không dùng được yêu cầu cửa hàng xử lý"
    # Quality (SP gãy khi mở ra chưa dùng), Service (yêu cầu xử lý)
    (1, 1, 0, 0),
    # 1152: "xe hơi bé nhưng chất lượng cũng tạm ổn"
    # Quality (xe hơi bé, tạm ổn)
    (1, 0, 0, 0),
    # 1153: "nhận được cái xe cho con mất hẳn góc"
    # Quality (SP bị mất góc - hư hỏng khi nhận)
    (1, 0, 0, 0),
    # 1154: "thiếu 1 con vít, gặp dịch không mua được luôn"
    # Quality (thiếu phụ kiện - 1 con vít)
    (1, 0, 0, 0),
    # 1155: "không biết do người bán hay do vận chuyển bị vỡ"
    # Quality (SP bị vỡ)
    (1, 0, 0, 0),
    # 1156: "giao sản phẩm lâu cần sản phẩm nhanh"
    # Shipping (giao chậm trong khi cần gấp)
    (0, 0, 1, 0),
    # 1157: "2 bánh trước bị kẹt rất khó đẩy"
    # Quality (bánh xe kẹt - lỗi SP)
    (1, 0, 0, 0),
    # 1158: "kém lắm, không mượt"
    # Quality (SP kém, không mượt)
    (1, 0, 0, 0),
    # 1159: "tôi cho bé tập đi nhưng khi di chuyển các con vật không đập lên thanh ngang nên bé không thích đi. kiểm tra phần thanh ngang gắn với bánh xe bị hư. thật sự tôi không hài lòng chút nào"
    # Quality (SP hư ở bộ phận thanh ngang - lỗi sản xuất)
    (1, 0, 0, 0),
    # 1160: "con gà bị hỏng không gõ được"
    # Quality (SP hỏng - con gà không gõ được)
    (1, 0, 0, 0),
    # 1161: "bị nứt gỗ khi nhận sản phẩm, không chắc chắn!"
    # Quality (gỗ bị nứt khi nhận - lỗi SP)
    (1, 0, 0, 0),
    # 1162: "đóng gói sơ sài. sản phẩm bị trầy xước nhiều. không giống hình trên gian hàng. đề nghị các cửa hàng bán sản phẩm thì chụp ảnh sản phẩm thật đưa lên"
    # Quality (SP trầy xước, không giống hình), Service (yêu cầu ảnh thật), Packing (đóng gói sơ sài)
    (1, 1, 0, 1),
    # 1163: "nói chung tạm ổn được thôi"
    # Quality (+, tạm ổn)
    (1, 0, 0, 0),
    # 1164: "mình mới nhận sản phẩm và sản phẩm bị bể vỡ. giờ muốn trả lại thì phải làm thế nào?"
    # Quality (SP bị bể vỡ khi nhận), Service (hỏi cách trả hàng)
    (1, 1, 0, 0),
    # 1165: "ron cao su bọc bánh bung ngay và luôn. nên có keo dán"
    # Quality (ron cao su bung ngay - lỗi SP)
    (1, 0, 0, 0),
    # 1166: "sản phẩm mua không đúng với hình ảnh. cảm thấy thất vọng. chắc mua 1 lần"
    # Quality (SP không đúng hình ảnh)
    (1, 0, 0, 0),
    # 1167: "giao sản phẩm lâu hơn dự kiến 4 ngày"
    # Shipping (giao trễ 4 ngày)
    (0, 0, 1, 0),
    # 1168: "hạn sử dụng quá gần. thùng 48 hộp nhưng hạn tháng 8 đã hết, giờ là tháng 6 rồi"
    # Quality (HSD chỉ còn 2 tháng cho 48 hộp - không kịp dùng hết)
    (1, 0, 0, 0),
    # 1169: "để là tặng thú nhồi bông nhưng không thấy giao kèm sữa"
    # Service (không nhận được thú bông tặng kèm)
    (0, 1, 0, 0),
    # 1170: "không có quà tặng như đã giới thiệu"
    # Service (không có quà như giới thiệu)
    (0, 1, 0, 0),
    # 1171: "sàn bóng tróc tràn sữa ra ngoài hộp. hộp sữa căng tròn như trái bóng. sữa có mùi không dùng được"
    # Quality (sữa bị phồng, mùi lạ - hỏng không dùng được)
    (1, 0, 0, 0),
    # 1172: "đánh giá không tính điểm mình mua sản phẩm hình 3 em bé tăng chiều cao nhưng lại giao sản phẩm hình sư tử cho bé suy dinh dưỡng. trong giỏ sp thì hình sư tử nhưng bấm vào link chính thì là hình 3 em bé. không đồng nhất dẫn đến khách hàng chịu thiệt. lỡ rồi khui ra cho con uống thì bé chê"
    # Service (giao sai sản phẩm do thông tin không nhất quán, không cho đổi), Shipping (giao sai SP)
    (0, 1, 1, 0),
    # 1173: "mùi hắc hắc, không được thơm lắm, chất sữa quá lỏng, chai có vết trầy"
    # Quality (mùi hắc, sữa lỏng, chai trầy - chất lượng kém)
    (1, 0, 0, 0),
    # 1174: "ưu điểm: giá tốt, giao sản phẩm nhanh, hạn sử dụng xa! nhược điểm: vỏ ngoài bịch tã rất cũ, dơ, bám đầy bụi và vết xước bẩn, nên chứng tỏ bảo quản sản phẩm trong kho kém"
    # Quality (+, hsd xa), Service (+, giá tốt), Shipping (+), Packing (bịch tã cũ, bẩn, bảo quản kém)
    (1, 1, 1, 1),
    # 1175: "sản phẩm tốt. đúng chất lượng, sản phẩm chính hãng. nhưng về phần quà tặng thi tôi không hài lòng, vì khi tôi chốt đơn thì có khuyến mãi 1 chai nước xả vải 800ml. nhưng tôi không nhận được. tôi gọi lên tổng đài thì trả lời là khi tôi coi sản phẩm thì còn khuyến mãi, nhưng khi đặt sản phẩm thì hết. vẫn hiển thị quà tặng khi thanh toán nhưng không giải thích được"
    # Quality (+), Service (CSKH không giải thích được, không nhận được quà)
    (1, 1, 0, 0),
    # 1176: "quá tệ, bao bì cũ, màu nhạt hơn sản phẩm mua trước đó của tiki trading, mở ra dùng thì tã khô cứng"
    # Quality (tã khô cứng, bao bì màu nhạt - chất lượng kém)
    (1, 0, 0, 0),
    # 1177: "không chịu giao nhưng gọi ra bưu cục lấy. mình không đi lấy thì 2 hôm sau mới chịu giao vô"
    # Shipping (shipper yêu cầu khách ra lấy, không giao tận nơi đúng quy trình)
    (0, 0, 1, 0),
    # 1178: "sản phẩm dỏm chất lượng kém mỏng dính"
    # Quality (SP dỏm, mỏng dính - chất lượng rất kém)
    (1, 0, 0, 0),
    # 1179: "sản phẩm chất lượng kém. mỏng dính"
    # Quality (SP mỏng dính - chất lượng kém)
    (1, 0, 0, 0),
    # 1180: "hãng lởm mỏng dính chất lượng kém"
    # Quality (SP mỏng dính - chất lượng kém)
    (1, 0, 0, 0),
    # 1181: "tốt. giao sản phẩm nhanh. gói sản phẩm kỹ"
    # Quality (+), Shipping (+), Packing (+)
    (1, 0, 1, 1),
    # 1182: "đặt tã dán giao tã quần"
    # Shipping (giao sai loại)
    (0, 0, 1, 0),
    # 1183: "giao không đúng loại bỉm. đặt bỉm quần nhưng giao bỉm tã dán"
    # Shipping (giao sai loại)
    (0, 0, 1, 0),
    # 1184: "mua 2 bịch luôn nhưng chẳng thấy quà gì đâu. hơi thất vọng tí"
    # Service (không nhận được quà tặng)
    (0, 1, 0, 0),
    # 1185: "không thấy quà tặng đính kèm ah"
    # Service (không thấy quà tặng)
    (0, 1, 0, 0),
    # 1186: "tôi đặt mua 2 bịch tã có khuyến mãi... hẹn giao thứ 2 ngày 16/12 nhưng nay trễ đã 5 ngày chưa thấy giao"
    # Shipping (giao chậm 5 ngày)
    (0, 0, 1, 0),
    # 1187: "mình mua sản phẩm lúc đó có ghi mua 2 gói bobby lớn tặng ngôi nhà phát nhạc. nhưng khi nhận thì không có giao chỉ giao 2 gói không có quà"
    # Service (không nhận được quà ngôi nhà phát nhạc)
    (0, 1, 0, 0),
    # 1188: "mua sản phẩm cho rồi không có quà tặng"
    # Service (không có quà tặng)
    (0, 1, 0, 0),
    # 1189: "kém, tràng nước tiểu. buồn"
    # Quality (thấm hút kém, tràn nước tiểu)
    (1, 0, 0, 0),
    # 1190: "hài lòng, tốt sản phẩm chất lượng"
    # Quality (+)
    (1, 0, 0, 0),
    # 1191: "bé 19kg mặc vào đái tràn. bữa nào cũng vậy. do thích đồ chơi nên mua. thật hối hận. chán tã dán"
    # Quality (tã tràn nước tiểu liên tục - thấm hút kém)
    (1, 0, 0, 0),
    # 1192: "bỉm như bỉm cũ, vỏ bên ngoài nhăn nheo, đóng gói không cẩn thận"
    # Quality (bỉm cũ, vỏ nhăn nheo), Packing (đóng gói không cẩn thận)
    (1, 0, 0, 1),
    # 1193: "đặt lộn size. đổi hay trả được không?"
    # Service (hỏi về đổi trả do lỗi người dùng)
    (0, 1, 0, 0),
    # 1194: "mua 2 bịch tã dán bobby xl total 522k nhưng không nhận được sản phẩm tặng mặc dù thấy tiki đăng khuyến mãi tặng bobby chăn hoặc thước vải"
    # Service (không nhận được quà tặng)
    (0, 1, 0, 0),
    # 1195: "giao 4 bịch tã quần tặng bộ gối mền hà mã mà cửa hàng chỉ giao cho mình con gấu hà mã không vậy"
    # Service (giao sai quà tặng - gấu thay vì bộ gối mền)
    (0, 1, 0, 0),
    # 1196: "thất vọng về tiki quá để hình có quà tặng nhưng không nhận được quà chỉ có bịch tã"
    # Service (không nhận được quà như hình quảng cáo)
    (0, 1, 0, 0),
    # 1197: "chất lượng sản phẩm rất tốt. nhưng chưa hài lòng vì mua sản phẩm ngày 12/6 có quà tặng sao đến nay tôi vẫn chưa nhận được"
    # Quality (+), Service (không nhận được quà tặng sau nhiều ngày)
    (1, 1, 0, 0),
    # 1198: "sản phẩm đã nhận. nhưng đến nay vẫn chưa thấy quà tặng gửi về"
    # Service (quà tặng chưa được giao)
    (0, 1, 0, 0),
    # 1199: "đóng gói không có giấy lót may hộp không méo"
    # Packing (không có giấy lót nhưng may không méo)
    (0, 0, 0, 1),
    # 1200: "giao thiếu sản phẩm tôi đặt combo 3 hộp nhưng chỉ giao 1 hộp kèm quà tặng"
    # Shipping (giao thiếu - 1 hộp thay vì 3 hộp)
    (0, 0, 1, 0),
    # 1201: "sản phẩm bể, vỡ. yêu cầu đổi trả sản phẩm"
    # Quality (SP bể, vỡ), Service (yêu cầu đổi trả)
    (1, 1, 0, 0),
    # 1202: "cảm thấy không tin cậy vì các tem dán đã bị rách, có vẻ như được dán lại. 2 hộp nào cũng bị móp méo. lần sau không mua sữa qua mạng nữa vì cảm thấy không an tâm"
    # Quality (tem bị rách rồi dán lại - nghi bị mở), Packing (2 hộp móp méo)
    (1, 0, 0, 1),
    # 1203: "chào tiki, khi mình đặt sản phẩm phần khuyến mãi có nêu rõ đặt 3 hộp sẽ được tặng 1 máy đo huyết áp. không hề có thông tin là số lượng sản phẩm có hạn. tiki đã nêu rõ như vậy tại sao đến lúc nhận sữa thì mình lại không được nhận máy đo huyết áp?"
    # Service (không nhận được quà máy đo huyết áp dù đủ điều kiện)
    (0, 1, 0, 0),
    # 1204: "giao sản phẩm 2h nhanh thế nào thì giao sản phẩm tiêu chuẩn thì ngược lại luôn. đặt sản phẩm từ 3/9 nhưng đến tận 17/9 mới giao. hối tiki mãi mới giao. giao trong việt nam nhưng chậm hơn giao sản phẩm quốc tế về"
    # Shipping (giao chậm - 14 ngày, chậm hơn giao quốc tế)
    (0, 0, 1, 0),
    # 1205: "tiki trả lời: vì sao tôi có khuyến mãi khi đặt sẵn phần này mà khi giao không có! thà không treo khuyến mãi, khi đã nói có khuyến mãi thì phải giao cho khách hàng chứ"
    # Service (không nhận được khuyến mãi, tiki không giải thích thỏa đáng)
    (0, 1, 0, 0),
    # 1206: "mình đã nhận được sản phẩm sau 1 tuần đặt, mã vạch mình hay mua của loại sữa này và ở trên miêu tả sản phẩm của tiki là 871 ở hà lan, nhưng mình nhận được là mã vạch ở singapore 888. mình cần tiki nói rõ vụ này"
    # Quality (mã vạch khác quốc gia so với mô tả - nghi sản phẩm khác nguồn gốc), Service (yêu cầu giải thích)
    (1, 1, 0, 0),
    # 1207: "đóng gói chưa kỹ lắm. lần sau vui lòng đóng gói kỹ hơn"
    # Packing (đóng gói chưa kỹ)
    (0, 0, 0, 1),
    # 1208: "sữa to đùng nhưng cho vào hộp bé tí, vì hộp nhỏ nên phồng lên 1 khoảng. làm sữa bị móp. đóng gói kém"
    # Packing (hộp không phù hợp, gây móp sữa - đóng gói kém)
    (0, 0, 0, 1),
    # 1209: "giao sản phẩm lâu. nhận sản phẩm xong hộp méo"
    # Shipping (giao chậm), Packing (hộp méo)
    (0, 0, 1, 1),
    # 1210: "sản phẩm không thơm như những lần đầu mua, rất nhạt"
    # Quality (SP thay đổi mùi - không thơm, nhạt so với trước)
    (1, 0, 0, 0),
    # 1211: "chưa giao sản phẩm đã báo giao thành công, đơn thanh toán trước, nếu không khiếu nại tự hỏi có giao sản phẩm cho mình không?"
    # Shipping (xác nhận giao ảo)
    (0, 0, 1, 0),
    # 1212: "giao sản phẩm chậm, đóng gói cẩn thận"
    # Shipping (giao chậm), Packing (+)
    (0, 0, 1, 1),
    # 1213: "tiki giải thích giúp vì sao seal đã bị xé và dán seal mới? vì sao trên nắp hộp có tem bị đánh dấu 'x' là gì?"
    # Quality (seal bị xé và dán lại - nghi bị mở/giả mạo), Service (yêu cầu giải thích)
    (1, 1, 0, 0),
    # 1214: "bỉm dày, có mùi hôi, không thấm hút, may sao mua có 1 bịch"
    # Quality (bỉm mùi hôi, không thấm hút - chất lượng rất kém)
    (1, 0, 0, 0),
    # 1215: "mất uy tín, chất lượng kém. thêm nữa là tiki để nhà cung cấp sử dụng chiêu trò pr bẩn. tạo voucher các kiểu đểu thu hút khách sản phẩm coi gian hàng, đặt sản phẩm, sau đó hủy đơn sản phẩm của khách"
    # Quality (chất lượng kém), Service (chiêu trò hủy đơn bất hợp lý - lừa đảo)
    (1, 1, 0, 0),
    # 1216: "đã rất mong chờ để nhận sản phẩm nhưng khi nhận được thì phải sản phẩm fake. bỉm không có đệm chun sau lưng cho bé"
    # Quality (bỉm fake - không có đệm chun sau lưng)
    (1, 0, 0, 0),
    # 1217: "giá sau khi cửa hàng giảm bằng giá in trên bao bì. lần này hơi thất vọng về giá"
    # Service (giảm giá chỉ bằng giá gốc in bao bì - không thực chất)
    (0, 1, 0, 0),
    # 1218: "tã mỏng, thấm hút kém, bé dùng bị hăm"
    # Quality (tã mỏng, thấm hút kém, gây hăm)
    (1, 0, 0, 0),
    # 1219: "giao đến bụi trên nắp hộp không hài lòng"
    # Packing (hộp bụi bẩn khi giao)
    (0, 0, 0, 1),
    # 1220: "thái độ nhân viên best giao sản phẩm rất tệ, hối thúc khách sản phẩm trả tiền khi khách chưa xem sản phẩm và nói chuyện khó nghe"
    # Shipping (shipper thái độ rất kém, hối thúc khách trả tiền, nói khó nghe)
    (0, 0, 1, 0),
    # 1221: "sao mã vạch mình không check được. có ai mua sữa này check được chưa a"
    # Quality (mã vạch không check được - nghi hàng giả)
    (1, 0, 0, 0),
    # 1222: "hộp sữa móp méo tùm lum, quá thất vọng"
    # Packing (hộp sữa móp méo nhiều)
    (0, 0, 0, 1),
    # 1223: "đăng lên đây bảo mua đơn 299k có chương trình tặng kèm thú bông xong cuối cùng không có tặng kèm gì cả. gọi lên tổng đài thì bảo số lượng có hạn nên không giao được. thế sao lúc không có quà tặng thì không thông báo trên đơn? đúng là đảo"
    # Service (không nhận được quà, tổng đài biện hộ số lượng có hạn - lừa đảo)
    (0, 1, 0, 0),
    # 1224: "sản phẩm này chỉ 1 sao thôi. mùi hắc kinh khủng. không biết pigeon kiểu gì"
    # Quality (mùi hắc kinh khủng - chất lượng rất kém, nghi hàng nhái)
    (1, 0, 0, 0),
    # 1225: "tắm rất nhờn. tắm mãi mới sạch"
    # Quality (tắm nhờn, khó sạch - chất lượng kém)
    (1, 0, 0, 0),
    # 1226: "đặt đơn sản phẩm hơn 2 tháng mới nhận được sản phẩm đặt 22/8, nhận 8/11. huỷ đơn không được, trả sản phẩm shipper không cho. bỉm đã 2 tháng thì làm sao con mình xài vừa size đó nữa nhưng không cho mình trả sản phẩm"
    # Service (không cho hủy đơn, không cho trả hàng dù giao chậm 2 tháng), Shipping (giao chậm gần 3 tháng)
    (0, 1, 1, 0),
    # 1227: "mình đặt 2 bịch bỉm. 1 bịch size mình và 1 bịch size xl nhưng tiki chỉ giao cho mình 1 bịch size mình thôi. làm cách nào để tiki giao bổ sung đây ạ?"
    # Service (yêu cầu giao bổ sung), Shipping (giao thiếu 1 bịch)
    (0, 1, 1, 0),
    # 1228: "mình mua 2 bịch hơn 600k, nhưng không có quà tặng kèm hả cửa hàng"
    # Service (không có quà tặng kèm)
    (0, 1, 0, 0),
    # 1229: "giao sản phẩm quá lâu. xem kho ở đâu thì là ở hà nội nhưng, vận chuyển từ trong hcm"
    # Shipping (giao từ kho xa - hà nội trong khi ở hcm)
    (0, 0, 1, 0),
    # 1230: "không được tặng quà, giao sản phẩm siêu lâu"
    # Service (không được quà), Shipping (giao siêu chậm)
    (0, 1, 1, 0),
    # 1231: "đánh giá không tính điểm không thấy quà tặng kèm mặc dù đặt sản phẩm lúc 00:01"
    # Service (không có quà dù đặt đúng thời gian)
    (0, 1, 0, 0),
    # 1232: "nhân viên gọi điện thoại upsale với thái độ lòi lõm. đánh giá 0 sao cho cửa hàng đổi nhân viên chăm sóc khách sản phẩm"
    # Service (nhân viên gọi upsale thái độ tệ)
    (0, 1, 0, 0),
    # 1233: "sản phẩm đã trả lại, bên tiki đã thu hồi sản phẩm ngày 14/10 đến 21/10 vẫn chưa thấy hoàn tiền cho khách"
    # Service (hoàn tiền chậm - 7 ngày chưa hoàn)
    (0, 1, 0, 0),
    # 1234: "sản phẩm nhận lâu hơn thời gian giao dự kiến"
    # Shipping (giao trễ so với dự kiến)
    (0, 0, 1, 0),
    # 1235: "bán mắc hơn lazada. nhân viên hỗ trợ không nhiệt tình"
    # Service (giá mắc hơn lazada, CSKH không nhiệt tình)
    (0, 1, 0, 0),
    # 1236: "bị móp méo không hài lòng tí nào cả"
    # Packing (SP bị móp méo)
    (0, 0, 0, 1),
    # 1237: "tôi muốn cửa hàng liên hệ lại để đổi sản phẩm"
    # Service (yêu cầu cửa hàng liên hệ đổi SP)
    (0, 1, 0, 0),
    # 1238: "sản phẩm có vấn đề, bên trong khi mở nắp chai nào cũng dính bẩn như đất, phải bỏ cả thùng đi"
    # Quality (tất cả chai đều bẩn bên trong - chất lượng rất tệ)
    (1, 0, 0, 0),
    # 1239: "mua giao sản phẩm trong 3h nhưng đến ngày 8/9 mới giao sản phẩm"
    # Shipping (giao sản phẩm cực kỳ chậm so với cam kết 3h)
    (0, 0, 1, 0),
    # 1240: "sữa giá cao tiền nhưng giao cho mình thùng sữa ướt, ngày sản xuất từ đầu năm đến bây giờ là đã 7 tháng rồi. lần đầu mua nhưng cảm thấy chán"
    # Quality (sữa ướt - có thể ngấm nước, NSX đầu năm - 7 tháng rồi), Service (giá cao)
    (1, 1, 0, 0),
    # 1241: "mẹ ở quê nhận sản phẩm báo shipper giao sản phẩm đòi chụp hình mặt khách? khách không cho vẫn lén chụp là sao? kêu công ty quy định vậy?"
    # Shipping (shipper lén chụp hình khách - vi phạm quyền riêng tư)
    (0, 0, 1, 0),
    # 1242: "nhân viên giao sản phẩm best rất tệ nói chuyện khó nghe"
    # Shipping (shipper thái độ tệ, nói chuyện khó nghe)
    (0, 0, 1, 0),
    # 1243: "ủa không hiểu đóng gói rồi có đọc sản phẩm người ta đặt không?"
    # Shipping (giao sai SP do không đọc kỹ đơn)
    (0, 0, 1, 0),
    # 1244: "sản phẩm không dán tem nhập khẩu đại thịnh. không rõ ràng xuất xứ. có khách khác mua thì có nhãn. nghi ngờ sản phẩm giả. nhắn tin hỏi thì không trả lời"
    # Quality (không có tem nhập khẩu - nghi hàng giả), Service (không trả lời tin nhắn)
    (1, 1, 0, 0),
    # 1245: "đặt xanh lá nhưng giao xanh dương"
    # Shipping (giao sai màu)
    (0, 0, 1, 0),
    # 1246: "đặt xanh lá giao xanh dương? mình có được đổi không ạ"
    # Service (hỏi về đổi hàng), Shipping (giao sai màu)
    (0, 1, 1, 0),
    # 1247: "giao sản phẩm không đúng loại tôi đặt mua. đặt màu xanh lá giao màu xanh dương. màu xanh dương mùi hắt kinh khủng. chờ đổi trả thì quy trình lâu lắt. cạch mặt"
    # Quality (SP mùi hắc), Service (thủ tục đổi trả lâu lắt), Shipping (giao sai màu)
    (1, 1, 1, 0),
    # 1248: "yêu cầu đăng hình nào giao sản phẩm hình ấy. cứ tưởng được giảm giá chai mình muốn mua. hóa ra nhận chai khác. thất vọng"
    # Quality (nhận chai khác hình đăng), Service (hình ảnh quảng cáo gây hiểu lầm)
    (1, 1, 0, 0),
    # 1249: "tôi không nhận xét về sản phẩm nước giặt, nhưng tôi muốn tiki trả lời về việc thẻ game tôi mua. 3 lần mua thẻ đều không nạp được, toàn bị báo là thẻ bị nạp rồi. không thể tin tưởng trang này nữa, toàn bị mất tiền. gọi tổng đài hỏi thì trả lời vòng vo, không giải quyết được"
    # Service (thẻ game bị nạp rồi - có thể bị đánh tráo; tổng đài không giải quyết)
    (0, 1, 0, 0),
    # 1250: "tôi có đặt sản phẩm nước giặt dnee, tiki hẹn giao sản phẩm 18/11/2019 nhưng tới 19/11/2019 nhưng cũng chưa thấy giao và không thấy thông báo gì hết"
    # Shipping (giao trễ không thông báo)
    (0, 0, 1, 0),
    # 1251: "giao sản phẩm chậm. làm tôi phải đi mua chỗ khác về dùng"
    # Shipping (giao chậm phải đi mua chỗ khác)
    (0, 0, 1, 0),
    # 1252: "chả biết sản phẩm chuẩn hay không do chưa khui nhưng thấy cách dán bao bì là chán rồi á haiza"
    # Packing (cách dán bao bì kém - gây nghi ngờ)
    (0, 0, 0, 1),
    # 1253: "đặt một sản phẩm đường giao sản phẩm một nẻo, chán"
    # Shipping (giao sai sản phẩm)
    (0, 0, 1, 0),
    # 1254: "mình mua 192k đã giảm giá. ở ngoài bán 160k. đóng gói tốt. nhưng nắp đã mở. không có niêm phong. không đầy như can mới"
    # Quality (nắp đã mở, không niêm phong - nghi bị dùng), Service (giá tiki cao hơn bên ngoài), Packing (+)
    (1, 1, 0, 1),
    # 1255: "đóng gói cẩn thận, giao sản phẩm nhanh nhưng nước giặt lỏng không đặc giống như mình mua ở siêu thị"
    # Quality (nước giặt loãng so với siêu thị - nghi chất lượng kém), Shipping (+), Packing (+)
    (1, 0, 1, 1),
    # 1256: "cũng thơm. nhưng phơi xong không đọng lại mùi gì cả. hơi thất vọng. với lại hao nước giặt quá. vù ít bọt"
    # Quality (không lưu mùi sau khi phơi, hao nhanh, ít bọt - chất lượng không như kỳ vọng)
    (1, 0, 0, 0),
    # 1257: "vận chuyển vỡ nắp. nước giặt đổ tung toé"
    # Packing (nắp vỡ khi vận chuyển, nước giặt đổ ra)
    (0, 0, 0, 1),
    # 1258: "thơm nhẹ, thích hợp cho em bé. nhưng 179.000 cho 03 lít với giá đó không hề rẻ"
    # Quality (+), Service (giá cao)
    (1, 1, 0, 0),
    # 1259: "mùi thơm, nhưng mình thích mùi hương của chai màu hồng và tím hơn"
    # Quality (+, thơm nhưng không thích bằng loại khác)
    (1, 0, 0, 0),
    # 1260: "mình cho 2 sao cho việc đóng gói kiện sản phẩm, rách rới, hở toang hoác ra như có người mở ra rồi vậy. cực kỳ thất vọng khi mở ra thì chai nước xả méo mó, bẩn thỉu, đầy bụi bặm, không hiểu sao bụi như thế nhưng vẫn để vậy giao đến tay khách. sản phẩm để lâu rồi, xước xát tùm lum hết cả lên"
    # Quality (SP để lâu, xước xát, bẩn), Packing (bao bì rách, hở, chai bẩn bụi)
    (1, 0, 0, 1),
    # 1261: "mua nước xả thì giao nước giặt, sản phẩm không tem mác, tiki giờ cũng cho cửa hàng bán sản phẩm giả nữa, yêu cầu đổi trả thì không xử lý"
    # Quality (không tem mác - nghi hàng giả), Service (không xử lý đổi trả), Shipping (giao sai SP)
    (1, 1, 1, 0),
    # 1262: "nghe mùi hương thì dễ chịu nhưng sản phẩm lại khác nhau khi nhận được như vậy. hay mẫu mới mẫu cũ"
    # Quality (SP khác biệt so với mua trước - có thể lô khác nhau)
    (1, 0, 0, 0),
    # 1263: "đặt nước xả nhưng giao nước giặt. mình tin tưởng tiki nên nhận sản phẩm mấy ngày không xem. cửa hàng hết sản phẩm thì huỷ đơn hoàn tiền chứ ngta đặt nước xả nhưng giao nc giặt là sao"
    # Shipping (giao sai loại SP hoàn toàn)
    (0, 0, 1, 0),
    # 1264: "đặt nước xả nhưng giao nước giặt"
    # Shipping (giao sai loại)
    (0, 0, 1, 0),
    # 1265: "chất lượng tốt. giao sản phẩm nhanh"
    # Quality (+), Shipping (+)
    (1, 0, 1, 0),
    # 1266: "bình mua lần gần nhất không thơm như trước. tôi sẽ đổi loại khác"
    # Quality (mùi thay đổi so với lần trước - chất lượng không đồng nhất)
    (1, 0, 0, 0),
    # 1267: "chai dnee xả mà dùng không có mùi thơm nào hết, giống như không dùng gì cả, lãng phí tiền"
    # Quality (không có mùi thơm - chất lượng cực kém)
    (1, 0, 0, 0),
    # 1268: "mùi thơm rất ít, không thấy bọt xà bông nên giặt đồ không sạch. yêu cầu tiki xem xét lại sản phẩm này"
    # Quality (ít thơm, ít bọt, không sạch - chất lượng kém), Service (yêu cầu xem xét)
    (1, 1, 0, 0),
    # 1269: "mua ngoài cửa hàng sao nước màu trắng có bọt và thơm. sao trên tiki thì khác"
    # Quality (SP tiki khác biệt so với mua ngoài - nghi chất lượng kém/giả)
    (1, 0, 0, 0),
    # 1270: "cửa hàng ơi mình mới mua 3 bình mà mình nhầm xả. mình muốn mua nc giặt"
    # Service (hỏi về đổi do nhầm loại - lỗi người dùng)
    (0, 1, 0, 0),
    # 1271: "cũng là nước xả dnee nhưng mua ở chỗ khác chất lượng hơn nhiều, thơm hơn và đặc hơn. lỡ mua 1 lần không có lần 2"
    # Quality (SP tiki kém hơn mua ở chỗ khác - loãng, ít thơm)
    (1, 0, 0, 0),
    # 1272: "về cân nhưng không đủ số lượng 3000l"
    # Quality (số lượng thiếu - không đủ 3000ml)
    (1, 0, 0, 0),
    # 1273: "mình mua nước giặt giao nước xả"
    # Shipping (giao sai loại SP)
    (0, 0, 1, 0),
    # 1274: "nước xả lỏng, không lưu mùi thơm sau khi quần áo khô. không có ấn tượng gì"
    # Quality (loãng, không lưu mùi - chất lượng không đạt)
    (1, 0, 0, 0),
    # 1275: "lúc mua có đăng tặng kèm gấu bông nhưng sao khi giao sản phẩm không có quà tặng kèm vậy ạ"
    # Service (không nhận được gấu bông tặng kèm)
    (0, 1, 0, 0),
    # 1276: "không giao sản phẩm đúng hẹn, hẹn giao 13h ngày 31/12 nhưng tới ngày 1/1/2025 vẫn chưa nhận được"
    # Shipping (giao trễ không đúng hẹn)
    (0, 0, 1, 0),
    # 1277: "vỏ hộp sản phẩm bên ngoài dính bụi bẩn"
    # Packing (vỏ hộp bụi bẩn)
    (0, 0, 0, 1),
    # 1278: "giao sản phẩm quá lâu vẫn chưa khắc phục được vấn đề này. đời đại này rồi nhưng vẫn giao sản phẩm lâu"
    # Shipping (giao quá chậm, vấn đề không được khắc phục)
    (0, 0, 1, 0),
    # 1279: "mới mua lần đầu loại số 3... về đóng gói thấy sơ xài, không cẩn thận, chỉ quấn màng co lại và đi giao"
    # Packing (đóng gói sơ xài, chỉ quấn màng co)
    (0, 0, 0, 1),
    # 1280: "giao sản phẩm trễ, đóng gói quá tệ. đây là thực phẩm cho em bé, không phải đồ chơi"
    # Shipping (giao trễ), Packing (đóng gói quá tệ cho thực phẩm em bé)
    (0, 0, 1, 1),
    # 1281: "date sản xuất cũ năm ngoái"
    # Quality (date sản xuất cũ)
    (1, 0, 0, 0),
    # 1282: "đóng gói không cẩn thận, gây móp méo hộp đựng sản phẩm và có 1 túi sữa bột bị rách"
    # Packing (đóng gói không cẩn thận, hộp móp, túi sữa rách)
    (0, 0, 0, 1),
    # 1283: "sản phẩm tôi nhận được có 2 hộp sữa hộp giấy. không có sữa. nhờ cửa hàng hỗ trợ"
    # Service (yêu cầu hỗ trợ), Shipping (giao SP rỗng - không có sữa trong hộp)
    (0, 1, 1, 0),
    # 1284: "sữa kém chất lượng, mùi vị khác thường, check mã code không được, trả sản phẩm không được"
    # Quality (sữa mùi vị lạ, mã code không check được - nghi giả), Service (không cho trả hàng)
    (1, 1, 0, 0),
    # 1285: "sữa giao date nsx: 01/2021 hsd: 01/2023 sữa đã chuyển sang vàng sẫm và vón cục"
    # Quality (sữa đổi màu vàng sẫm, vón cục - hư hỏng dù còn HSD)
    (1, 0, 0, 0),
    # 1286: "mình thấy sữa khác với loại mua từ nơi khác. không biết chất lượng sữa thế nào. đang phân vân"
    # Quality (sữa khác biệt so với mua nơi khác - gây nghi ngờ)
    (1, 0, 0, 0),
    # 1287: "giao sản phẩm nhanh. hộp giấy bị móp méo nên cho 3 sao"
    # Shipping (+), Packing (hộp giấy móp méo)
    (0, 0, 1, 1),
    # 1288: "giao về lũng chảy tùm lum"
    # Packing (SP bị lũng chảy ra ngoài - đóng gói kém)
    (0, 0, 0, 1),
    # 1289: "giao sản phẩm chậm quá, sản phẩm thì tốt đúng chất lượng"
    # Quality (+), Shipping (giao chậm)
    (1, 0, 1, 0),
    # 1290: "1 hộp sữa bị phồng và đổ chảy sang cả thùng. cái này chắc là vấn đề về chất lượng"
    # Quality (sữa bị phồng, đổ chảy - chất lượng có vấn đề)
    (1, 0, 0, 0),
    # 1291: "không hài lòng hộp sữa móp méo chán không thể tả được cho con uống mất hết cả tự tin"
    # Packing (hộp sữa móp méo nặng)
    (0, 0, 0, 1),
    # 1292: "sữa giao bị móp méo, ẩm mốc, date cũ. thùng sữa 1tr mấy. cứ như mua sữa 3-400k. giao sữa cho em bé uống nhưng bị gì? ai chịu trách nhiệm"
    # Quality (ẩm mốc, date cũ - rất nguy hiểm), Packing (hộp móp méo)
    (1, 0, 0, 1),
    # 1293: "đặt từ tháng 8 đến cuối tháng 10 mới giao tới cực kỳ bực bội"
    # Shipping (giao chậm gần 3 tháng)
    (0, 0, 1, 0),
    # 1294: "giao thiếu 1 lốc sữa, sản phẩm móp méo, 2 lốc đã bị khui bóc ra"
    # Quality (2 lốc đã bị khui - nghi bị mở), Shipping (giao thiếu 1 lốc), Packing (sản phẩm móp méo)
    (1, 0, 1, 1),
    # 1295: "sữa bị hôi, không giống như mua ở ngoài siêu thị. con uống đau bụng nên cẩn thận"
    # Quality (sữa hôi, gây đau bụng - nguy hiểm)
    (1, 0, 0, 0),
    # 1296: "sữa bể hết. có mùi thối của sữa. tiki giải quyết làm sao đây?"
    # Quality (sữa bể, mùi thối), Service (yêu cầu giải quyết)
    (1, 1, 0, 0),
    # 1297: "bán sản phẩm ghi thùng 48 hộp nhưng nhận thùng 36 hộp là sao"
    # Service (giao thiếu - 36 thay vì 48 hộp), Shipping (giao sai số lượng)
    (0, 1, 1, 0),
    # 1298: "là một tmđt lớn. chất lượng ngày càng đi xuống. đầu năm đi mua sản phẩm thì giao sản phẩm rất bẩn và rách cho khách. tiki nên xem lại kho sản phẩm"
    # Packing (SP giao bẩn và rách - tái diễn nhiều lần)
    (0, 0, 0, 1),
    # 1299: "nhân viên giao sản phẩm rất thái độ với người nhận sản phẩm, giao tối ở công ty không có ai sao nhận được, hẹn hôm khác thì khó chịu. hơn nữa mọi lần mua tiki đều có băng dính của tiki nhưng lần này không hề có"
    # Shipping (shipper thái độ kém, cọc cằn), Packing (lần này thiếu băng dính tiki)
    (0, 0, 1, 1),
    # 1300: "đặt sản phẩm thì tận cả 2 tháng mới nhận được. biết là dịch nhưng xử lí đơn sản phẩm quá chậm. đến lúc nhận được sản phẩm thì thất vọng kinh khủng sản phẩm bị rách tả tơi"
    # Shipping (giao chậm 2 tháng), Packing (SP rách tả tơi khi nhận)
    (0, 0, 1, 1),
    # 1301: "giao sản phẩm thì quá chậm, hệ thống báo 27/9 nhận nhưng 15/10 mới giao sau khi mình gọi điện hối thúc. sản phẩm giao thì cũ rích, bám bụi, nhưng bị rách nữa chứ. từ nay về sau không dám mua nữa"
    # Quality (SP cũ rích, bẩn, rách), Shipping (giao chậm 18 ngày, phải hối thúc), Packing (SP rách khi giao)
    (1, 0, 1, 1),
    # 1302: "lúc mua có khuyến mãi tặng xe khi đơn sản phẩm được hơn 1 triệu. mình mua 4 bịch bỉm nhưng lại chia 2 lần giao. cuối cùng giao sản phẩm đến không có xe"
    # Service (không nhận được xe khuyến mãi dù đủ điều kiện)
    (0, 1, 0, 0),
    # 1303: "may lần trước bao bì mới gói kỹ, nhưng lần này bao bì của sản phẩm củ kỹ và nhìn trầy xước, gói sản phẩm cho có không cẩn thận giống sản phẩm để lâu lắm rồi"
    # Quality (SP trầy xước, bao bì cũ kỹ - trông như hàng tồn kho lâu)
    (1, 0, 0, 0),
    # 1304: "giao sản phẩm siêu chậm! đặt sản phẩm ngày 9/9, giao ngày 22/10. cùng ngày 9/9 mình mua trên các ứng dụng khác thì họ giao luôn trong tháng 9. trải nghiệm với tiki ngày càng tệ!"
    # Shipping (giao chậm 43 ngày, kém hơn đối thủ rất nhiều)
    (0, 0, 1, 0),
    # 1305: "bé mình dùng moony từ nhỏ, không bị hăm không gì hết. gần đây dùng moony mua từ tiki thì bị nổi hột đỏ quanh bẹn. thật sự rất thất vọng, không tin tưởng sản phẩm từ tiki được"
    # Quality (bỉm tiki gây nổi hột đỏ - chất lượng thay đổi/nghi hàng giả)
    (1, 0, 0, 0),
    # 1306: "mình mua tã moony mấy lần nhưng lần này nhận được gói tã khá cũ, bao bì hơi dơ, sắp rách, có dấu hiệu bạc màu"
    # Quality (tã trông cũ), Packing (bao bì dơ, sắp rách, bạc màu)
    (1, 0, 0, 1),
    # 1307: "mình đặt đơn sản phẩm 16/3, hôm nay 19/3 có nv giao nhận điện thoại để giao... tới đường vô nhà mình thì bíp còi inh ỏi, vô tới nhà tìm sản phẩm 1 cách dằn mặt... quà tặng không thấy"
    # Service (không nhận được quà tặng), Shipping (shipper thái độ dằn mặt, bíp còi inh ỏi)
    (0, 1, 1, 0),
    # 1308: "tại sao sản phẩm mua trên 599k thì được tặng gấu bông. nhưng đơn sản phẩm của tôi thì không được giao gấu bông vậy?"
    # Service (không nhận được quà gấu bông dù đủ điều kiện)
    (0, 1, 0, 0),
    # 1309: "không thấy có xe scooter dù đơn sản phẩm đáp ứng đủ điều kiện như quảng cáo"
    # Service (không nhận được xe scooter dù đủ điều kiện)
    (0, 1, 0, 0),
    # 1310: "mình mua sản phẩm tã moony size l loại 44 miếng, mua 2 bịch sẽ được tặng một bộ nous cho bé 6-12 tháng, tã thì đã giao nhưng sản phẩm tặng tới nay không thấy. gần một tuần vẫn chưa thấy sản phẩm tặng. cũng không thấy phản hồi gì của tiki"
    # Service (không nhận được quà nous, không có phản hồi từ tiki)
    (0, 1, 0, 0),
    # 1311: "mình mua bịch tã này. về cho bé sử dụng thấy không êm mềm như bình thường. bé tè 2 lần thì thấy lớp bên trong tã bở ra chỉ nhưng phần vỏ tã. tã bị đứt thun. sản phẩm này có phải chính hãng không"
    # Quality (tã bở, đứt thun sau 2 lần dùng - nghi hàng giả)
    (1, 0, 0, 0),
    # 1312: "lần đầu tiên mua sản phẩm của tiki đến 3 tuần mới nhận được sản phẩm"
    # Shipping (giao chậm 3 tuần)
    (0, 0, 1, 0),
    # 1313: "tã quần size mình toàn mẫu mã cũ dùng cứng nhưng form bé, bé mặc hay bị lằn, có đúng 1 lần mua được mẫu mới mặc thích hơn"
    # Quality (tã mẫu cũ, cứng, form bé gây lằn - chất lượng không đồng nhất)
    (1, 0, 0, 0),
    # 1314: "số lượng quà tặng không rõ ràng về số lượng"
    # Service (thông tin quà tặng không rõ ràng)
    (0, 1, 0, 0),
    # 1315: "như bỉm hết hạn không nên mua con mình xài hăm"
    # Quality (bỉm nghi hết hạn - gây hăm)
    (1, 0, 0, 0),
    # 1316: "đóng gói sơ sài bằng bao nilông, lần đầu tiên không hài lòng về cách gói sản phẩm"
    # Packing (đóng gói sơ sài, chỉ bọc nilông)
    (0, 0, 0, 1),
    # 1317: "không có gấu bông tặng kèm"
    # Service (không có quà gấu bông)
    (0, 1, 0, 0),
    # 1318: "mình dùng moony từ trước giờ cho bé rất thích. tã không bị vón cục. nhưng sao lần này mua của tilomart thấy bé mặc tiểu tí xíu đã thấy vón cục. không biết trúng tã giả hay sao đây"
    # Quality (tã vón cục sau 1 lần tè - nghi hàng giả)
    (1, 0, 0, 0),
    # 1319: "không tràn đều toàn bỉm. tập trung hầu hết ở trước"
    # Quality (bỉm thấm hút không đều - kém chất lượng)
    (1, 0, 0, 0),
    # 1320: "bề mặt thấm hút kém không mịn bị xù"
    # Quality (thấm hút kém, bề mặt xù)
    (1, 0, 0, 0),
    # 1321: "bỉm không được mềm mại như mua chỗ khác"
    # Quality (bỉm cứng hơn so với mua ở nơi khác)
    (1, 0, 0, 0),
    # 1322: "có gấu tặng kèm nhưng mình nhận sản phẩm lại không có"
    # Service (không nhận được gấu tặng kèm)
    (0, 1, 0, 0),
    # 1323: "mình mua lần trước được tặng bộ nuos đẹp, lần sau cũng ghi tặng nous nhưng thực tế nhận được bộ áo dài tay+quần cộc. chất thì xấu thôi rồi. thất vọng về quà"
    # Service (nhận quà tặng sai - chất lượng quà tệ so với mô tả)
    (0, 1, 0, 0),
    # 1324: "giao sản phẩm nhanh sản phẩm tạm ổn"
    # Quality (+), Shipping (+)
    (1, 0, 1, 0),
    # 1325: "mình đặt 2 bịch cho bé gái nhưng thấy bao bì ngoài ghi là man. bên trong thì bỉm màu hồng, chả biết có nhầm không nhỉ?"
    # Quality (bao bì ghi man nhưng bỉm màu hồng - gây nhầm lẫn)
    (1, 0, 0, 0),
    # 1326: "mua sữa tắm giao lotion. này lấy ra xài mới phát hiện"
    # Shipping (giao sai SP - sữa tắm thay vì lotion)
    (0, 0, 1, 0),
    # 1327: "bọc không kỹ, bể 1 nắp chai chảy, đề nghị đổi lại"
    # Service (yêu cầu đổi), Packing (bọc không kỹ, bể nắp chai chảy)
    (0, 1, 0, 1),
    # 1328: "mua sữa tắm nhưng giao lotion. 2 chai luôn mới đau chứ"
    # Shipping (giao sai loại - 2 chai lotion thay vì sữa tắm)
    (0, 0, 1, 0),
    # 1329: "chưa dùng chưa biết chất lượng"
    # (không đủ thông tin)
    (0, 0, 0, 0),
    # 1330: "sản phẩm có mùi nhựa, chất lượng thực sự chưa xứng đáng giá thành"
    # Quality (mùi nhựa, không xứng giá - chất lượng kém), Service (giá không tương xứng)
    (1, 1, 0, 0),
    # 1331: "đặt sản phẩm loại newborn cho trẻ sơ sinh, giao sản phẩm loại cho trẻ 2 tuổi. nhà bán để sai hình ảnh để khách chọn nhầm. yêu cầu đổi sản phẩm thì nhân viên tiki nói do khách đặt sai, nhà bán không chịu trách nhiệm"
    # Service (không chịu trách nhiệm khi thông tin sai, không đổi SP), Shipping (giao sai độ tuổi)
    (0, 1, 1, 0),
    # 1332: "cửa hàng qua lấy sản phẩm về giúp, sản phẩm này sao sử dụng được nhưng đem bán cho khách vậy, mốc, mọt, hư hết, nhìn hình thì khó thấy nhưng bên ngoài thì quá nhiều, mở cái bọc ra nhưng hắt xì phải đóng vào"
    # Quality (SP mốc, mọt, hư hỏng hoàn toàn - không thể dùng), Service (yêu cầu thu hồi)
    (1, 1, 0, 0),
    # 1333: "sản phẩm mốc xanh, mốc meo, một lỗ chỗ nhưng nhưng bán cho khách"
    # Quality (SP mốc xanh, một lỗ chỗ - không thể dùng)
    (1, 0, 0, 0),
    # 1334: "sản phẩm quá tệ, bị hư nhiều nhưng vẫn giao cho khách sản phẩm"
    # Quality (SP hư hỏng nhiều vẫn giao - chất lượng rất tệ)
    (1, 0, 0, 0),
    # 1335: "giao thiếu sản phẩm, không có bếp"
    # Shipping (giao thiếu bếp)
    (0, 0, 1, 0),
    # 1336: "sản phẩm và đóng gói như bên dưới hình. quá tệ"
    # Packing (đóng gói quá tệ)
    (0, 0, 0, 1),
    # 1337: "giao thiếu đồ. đặt sản phẩm thu tiền rồi nhưng không giao. nhờ tiki hỗ trợ"
    # Service (yêu cầu hỗ trợ), Shipping (giao thiếu, thu tiền rồi không giao)
    (0, 1, 1, 0),
    # 1338: "trái lép mua xông nhà thì được"
    # Quality (trái lép - chất lượng không đạt)
    (1, 0, 0, 0),
    # 1339: "bồ kết bị mọt hoàn toàn không dùng được"
    # Quality (bồ kết bị mọt - hư hỏng hoàn toàn)
    (1, 0, 0, 0),
    # 1340: "cân thiếu sản phẩm và sản phẩm bị vỡ không sạch sẽ"
    # Quality (SP vỡ, bẩn), Shipping (cân thiếu SP)
    (1, 0, 1, 0),
    # 1341: "bồ kết rẻ thì tốt hơn"
    # Quality (chất lượng không tương xứng giá), Service (giá cao)
    (1, 1, 0, 0),
    # 1342: "đánh giá không tính điểm rất không hài lòng bồ kết củ, mốc nhưng sâu nữa. chán thay bán sản phẩm không có tâm"
    # Quality (bồ kết cũ, mốc, có sâu - không thể dùng)
    (1, 0, 0, 0),
    # 1343: "hộp bị móp dù đã chống sốc nên không rõ là móp từ trước khi gửi hay trong quá trình vận chuyển"
    # Packing (hộp móp dù đã chống sốc)
    (0, 0, 0, 1),
    # 1344: "tikinow tốn 29k nhưng giao chán tệ sản phẩm bị móp hết nhìn sữa nhỏ 300k nhưng xót xa"
    # Service (phí tikinow cao nhưng giao tệ), Shipping (giao tệ), Packing (SP bị móp)
    (0, 1, 1, 1),
    # 1345: "đơn đặt là mẫu hồng 2021 nhưng vẫn giao mẫu xanh cũ"
    # Shipping (giao sai mẫu - giao mẫu cũ thay vì mới)
    (0, 0, 1, 0),
    # 1346: "bình thường. giống hình. phí giao sản phẩm cao"
    # Quality (+), Service (phí giao cao)
    (1, 1, 0, 0),
    # 1347: "tốt, mình chưa dùng nhưng đúng sản phẩm"
    # Quality (+)
    (1, 0, 0, 0),
    # 1348: "sản phẩm không giống hình, mua 3 cái trong đó của 2 cửa hàng khác nhau, tiền cửa hàng này mua đắt hơn nhưng giống hệt, mép sản phẩm dày quá không giống ảnh"
    # Quality (SP không giống hình, mép dày quá), Service (giá đắt hơn nhưng SP giống hệt loại rẻ)
    (1, 1, 0, 0),
    # 1349: "bán sản phẩm dỏm, không như hình. người mua nên cẩn thận khi mua ở đây"
    # Quality (SP dỏm, không như hình)
    (1, 0, 0, 0),
    # 1350: "rubic cứng, khó xoay, màu sắc được dán bằng giấy màu"
    # Quality (rubik cứng khó xoay, màu dán bằng giấy - chất lượng kém)
    (1, 0, 0, 0),
    # 1351: "sản phẩm dỏm quá! chỉ là mô hình rubik thôi chứ không phải là rubik"
    # Quality (SP không phải rubik xoay được - lừa đảo)
    (1, 0, 0, 0),
    # 1352: "sản phẩm tạm ổn tốt được, cửa hàng cần tìm loại tốt hơn"
    # Quality (+, tạm ổn)
    (1, 0, 0, 0),
    # 1353: "đẹp nhưng xoay hơi cứng không đã tay"
    # Quality (xoay cứng)
    (1, 0, 0, 0),
    # 1354: "cũng được chứ không ưng lắm"
    # Quality (tạm ổn)
    (1, 0, 0, 0),
    # 1355: "sản phẩm không có chất lượng"
    # Quality (SP không có chất lượng)
    (1, 0, 0, 0),
    # 1356: "sản phẩm có vấn đề... check mã vạch không ra. mình cũng không biết nguyên nhân có phải do bỉm hay là ko, nhưng con mình xài gần hết bịch bây giờ bị cả mông, ban đầu nó nổi ít dần nổi nặng hơn"
    # Quality (bỉm gây nổi đỏ cả mông, mã vạch không check được - nghi hàng giả)
    (1, 0, 0, 0),
    # 1357: "sản phẩm có mùi lạ. tôi thường mua của tiki sản phẩm có tem phụ và hoàn toàn không có mùi. sản phẩm của cửa hàng không có tem phụ nên tôi khá nghi ngờ, kiểm tra bao bì có chút khác biệt nhưng đặc biệt nhất là có mùi hôi"
    # Quality (mùi hôi, không có tem phụ - rất nghi hàng giả)
    (1, 0, 0, 0),
    # 1358: "trên trang giới thiệu hóa đơn hơn 1 triệu bỉm moony được nhận xe cho bé nhưng hóa đơn của mình hơn 1 triệu chẳng thấy quà cho bé đâu cả. cửa hàng làm ăn chán quá!"
    # Service (không nhận được quà xe cho bé dù đủ điều kiện)
    (0, 1, 0, 0),
    # 1359: "trên ảnh cửa hàng mua giá trị trên 1199k tặng xe mk mua giá trị 1224k nhưng không được tặng xe là sao"
    # Service (không nhận được quà xe dù đủ điều kiện - mua 1224k > 1199k)
    (0, 1, 0, 0),
    # 1360: "từ shopee sang đây mua thử. ai ngờ mua gặp bao bỉm cái nào cũng bị rạch 1 đường. quá tệ. mọi người mua cẩn thận nhé"
    # Packing (tất cả bao bỉm đều bị rạch - chất lượng đóng gói tệ)
    (0, 0, 0, 1),
    # 1361: "cửa hàng giao nhầm bỉm cho mình rồi. mình đặt tã quần chứ không phải tã dán"
    # Shipping (giao sai loại - dán thay vì quần)
    (0, 0, 1, 0),
    # 1362: "sản phẩm size nhỏ không phân biệt giới tính nhưng thực tế thiết kế phù hợp cho bé trai hơn. miếng bỉm khá dày dễ bí khiến da con bị hăm"
    # Quality (thiết kế không phù hợp, dày quá gây hăm)
    (1, 0, 0, 0),
    # 1363: "mặt sau tất cả các miếng tã đều bị rạch xước, sản phẩm lỗi nhưng chạy sale off đẩy sản phẩm rất kỹ. hài lòng giao sản phẩm nhanh"
    # Quality (tất cả miếng tã bị rạch xước - lỗi sản xuất/bán SP lỗi), Shipping (+)
    (1, 0, 1, 0),
    # 1364: "mỏng hơn hẳn so với loại mua từ aeon. bé mặc bị đỏ da"
    # Quality (bỉm mỏng hơn, gây đỏ da - chất lượng kém so với mua tại shop)
    (1, 0, 0, 0),
    # 1365: "thời gian giao sản phẩm quá lâu. đặt mua từ lúc nhưng hơn nửa bì bỉm hết bỉm vẫn không có, phải mua trước bì nữa để dùng"
    # Shipping (giao quá chậm - phải mua thêm ở nơi khác)
    (0, 0, 1, 0),
    # 1366: "tiki đưa ra chương trình khuyến mại khi mua đơn sản phẩm đạt giá trị 1199k. tuy nhiên mua đạt giá trị đấy lại không được"
    # Service (không nhận được khuyến mãi dù đủ điều kiện)
    (0, 1, 0, 0),
    # 1367: "quà tặng bê bối, kém chất lượng"
    # Quality (quà tặng kém chất lượng), Service (bê bối về quà)
    (1, 1, 0, 0),
    # 1368: "mua tã quần giao tã dán, mình thật sự rất bực mình. trúng mùa dịch không đổi trả được"
    # Service (không đổi trả được trong dịch), Shipping (giao sai loại)
    (0, 1, 1, 0),
    # 1369: "bỉm quần phù hợp với bé dưới 6kg, con mình 5.5kg mặc thấy hơi chật rùi, đũng hơi dài, độ mềm hình như không bằng tã dán, thấm hút được, có thể xài ban đêm"
    # Quality (tã quần chặt, đũng dài, kém mềm so với tã dán - nhược điểm SP)
    (1, 0, 0, 0),
    # 1370: "vì sao mình không nhận được quà khuyến mãi cùng lúc với nhận sản phẩm?"
    # Service (quà tặng không giao cùng lúc với SP)
    (0, 1, 0, 0),
    # 1371: "giao sản phẩm siêu lâu. không có cách nào để khách sản phẩm chat với nhân viên tư vấn của tiki trading để giục giao sản phẩm"
    # Service (không có kênh liên hệ trực tiếp), Shipping (giao siêu chậm)
    (0, 1, 1, 0),
    # 1372: "mua 2 bịch nhưng 1 bịch cái nào cũng rách vầy"
    # Packing (1/2 bịch bị rách tất cả miếng trong đó)
    (0, 0, 0, 1),
    # 1373: "đóng gói bị rách bịch bỉm"
    # Packing (đóng gói bị rách bịch bỉm)
    (0, 0, 0, 1),
    # 1374: "mua tã quần size mình nhưng giao tã dán, gọi lên tổng đài thì không ai nghe"
    # Service (tổng đài không nghe máy), Shipping (giao sai loại)
    (0, 1, 1, 0),
    # 1375: "hôm mình đặt từ 8/8 2 bịch bỉm tặng 1 gấu bông, nhưng đến 17/8 mới nhận sản phẩm và không thấy được tặng gấu bông"
    # Service (không nhận được quà gấu bông), Shipping (giao chậm 9 ngày)
    (0, 1, 1, 0),
    # 1376: "mình đặt mua tã quần. nhưng lại giao cho mình tã dán. haizzz"
    # Shipping (giao sai loại)
    (0, 0, 1, 0),
    # 1377: "tôi mua sản phẩm có khuyến mãi tặng xe khi đơn sản phẩm 1199k nhưng không thấy tặng kèm xe là sao"
    # Service (không nhận được xe tặng dù đủ điều kiện)
    (0, 1, 0, 0),
    # 1378: "tại sao mình mua 12-12 có quà là đệm cho bé nhưng khi giao lại không có vậy ạ?"
    # Service (không nhận được quà đệm trong dịp 12-12)
    (0, 1, 0, 0),
    # 1379: "đóng gói tạm ổn tốt được. nếu bỏ túi bỉm gói trong thùng carton thì tốt hơn"
    # Packing (đóng gói tạm ổn, góp ý cải thiện)
    (0, 0, 0, 1),
    # 1380: "bịch ngoài bị rách làm dơ vài cái tã"
    # Packing (bao bì ngoài rách làm bẩn tã bên trong)
    (0, 0, 0, 1),
    # 1381: "kiếm hoài không thấy ngày sản xuất vậy cửa hàng ơi? chat với cửa hàng thì không gửi tin được"
    # Quality (không tìm thấy NSX - thiếu thông tin), Service (không liên hệ được cửa hàng)
    (1, 1, 0, 0),
    # 1382: "mình đặt tã quần nhưng lại giao sản phẩm tã dán. không hài lòng chút nào"
    # Shipping (giao sai loại)
    (0, 0, 1, 0),
    # 1383: "tã mềm nhưng dày quá, khi bé tè nhiều bị phồng lên"
    # Quality (tã dày, phồng khi tè nhiều - không thoải mái)
    (1, 0, 0, 0),
    # 1384: "cửa hàng giao nhầm tã quần thành tã dán mình liên hệ 1906035 nhưng không có ai nghe máy"
    # Service (không ai nghe máy), Shipping (giao sai loại)
    (0, 1, 1, 0),
    # 1385: "thông tin có kèm khuyến mãi nhưng giao sản phẩm lại không có, đóng gói sơ xài"
    # Service (không có khuyến mãi), Packing (đóng gói sơ xài)
    (0, 1, 0, 1),
    # 1386: "đặt đơn sản phẩm 1tr2 nhưng không có quà"
    # Service (không có quà dù mua đủ điều kiện)
    (0, 1, 0, 0),
    # 1387: "vẫn luôn hài lòng với dịch vụ giao sản phẩm bên tiki. đóng gói kỹ, sản phẩm đúng hãng. chất kem dễ thoa, không bị vàng da... chỉ thấy mịn lúc mới thoa lên thôi"
    # Quality (+, đúng hãng, mịn khi thoa), Shipping (+), Packing (+)
    (1, 0, 1, 1),
    # 1388: "thoa vào bị ngứa mặt. liệu có phải sản phẩm fake"
    # Quality (SP gây ngứa mặt - nghi hàng giả)
    (1, 0, 0, 0),
    # 1389: "kem dùng dưỡng ẩm thì được nhưng thấy da đen hơn"
    # Quality (kem gây đen da - tác dụng ngược)
    (1, 0, 0, 0),
    # 1390: "tuần đầu mình bôi thấy giảm mụn nhưng hiện tại tuần thứ 2 thì mụn bọc mụn viêm nổi lên đang thất vọng"
    # Quality (kem gây mụn bọc, mụn viêm ở tuần 2 - tác dụng ngược)
    (1, 0, 0, 0),
    # 1391: "dùng vào da dỡ khô nhiều thấm nhanh. mới dùng nên chưa biết hiệu quả cao không?"
    # Quality (thấm nhanh - tạm ổn, chưa đánh giá được)
    (1, 0, 0, 0),
    # 1392: "hộp kem đã bị bóc rất lâu rồi. mở ra kem vón cục như đã bị sử dụng"
    # Quality (kem vón cục, hộp bị bóc từ trước - nghi đã dùng/hàng cũ)
    (1, 0, 0, 0),
    # 1393: "bình thường. chưa thấy kết quả trắng"
    # Quality (hiệu quả không như quảng cáo - chưa trắng)
    (1, 0, 0, 0),
    # 1394: "e dùng không hợp bị nổi mụn"
    # Quality (SP gây nổi mụn - không phù hợp)
    (1, 0, 0, 0),
    # 1395: "kem rít, hiệu quả kém như mong đợi"
    # Quality (kem rít, hiệu quả kém)
    (1, 0, 0, 0),
    # 1396: "sản phẩm giao hơi cũ, bụi. tiki nên xem lại bên đối tác"
    # Quality (SP cũ, bụi - bảo quản kém)
    (1, 0, 0, 0),
    # 1397: "nhận sản phẩm không có hộp không có gì có mỗi cái hũ không. sao kỳ vậy. tiki kiểm tra lại xem có phải sản phẩm chất lượng không"
    # Quality (không có hộp, thiếu bao bì - SP không đầy đủ), Service (yêu cầu kiểm tra)
    (1, 1, 0, 0),
    # 1398: "sử dụng có mịn nhưng không hết mụn, không trắng. lúc đầu cũng mong đợi lắm nhưng thất vọng"
    # Quality (hiệu quả không như quảng cáo - không hết mụn, không trắng)
    (1, 0, 0, 0),
    # 1399: "giao sản phẩm khá nhanh đóng gói cẩn thận"
    # Shipping (+), Packing (+)
    (0, 0, 1, 1),
    # 1400: "kem như bột gạo bôi bị vàng da"
    # Quality (kem gây vàng da - tác dụng ngược)
    (1, 0, 0, 0),
    # 1401: "khi mua đã nghe một số người bảo miếng dán kém. dán lên tường mấy ngày là rơi... dán lên bề mặt gỗ. nhưng có cái được 1 ngày, có cái sau 2 ngày đã bị rơi. dán lại được mấy tiếng sau lại rơi"
    # Quality (miếng dán rơi nhanh - keo dán kém chất lượng)
    (1, 0, 0, 0),
    # 1402: "đóng gói tốt, mẫu mã đẹp. tuy nhiên cái decal thước đo chiều cao thì khó gỡ và dễ rách. mua 2 cái nhưng chỉ xài được 1 cái thước đo, nên cũng thấy chưa hài lòng lắm"
    # Quality (decal thước đo khó gỡ, dễ rách - chỉ dùng được 1/2), Packing (+)
    (1, 0, 0, 1),
    # 1403: "dán tường không chắc chắn"
    # Quality (dán tường không chắc - chất lượng keo kém)
    (1, 0, 0, 0),
    # 1404: "chơi không được lâu, chất keo bám ít"
    # Quality (keo bám ít, dùng không được lâu)
    (1, 0, 0, 0),
    # 1405: "trời ạ. ghi là bộ đồ chơi. hóa ra 80k/1 con. con khủng long tí teo. quá thảm. quá thất vọng"
    # Quality (SP nhỏ xíu không đúng kỳ vọng), Service (giá 80k/con - quá đắt)
    (1, 1, 0, 0),
    # 1406: "xe không chạy được. sản phẩm không đúng mô tả"
    # Quality (xe không chạy được, không đúng mô tả)
    (1, 0, 0, 0),
    # 1407: "giao mẫu cũ, nhưng đăng mẫu mới, đã vậy bình sữa như đồ se cần hand. trả sản phẩm rồi nhưng không được trả lại tiền. tiki vì trăm mấy chục ngàn nhưng bảo vệ người bán, bỏ mặc người mua, toàn hứa nhưng không trả tiền"
    # Quality (bình sữa cũ, dơ), Service (không hoàn tiền dù đã trả hàng - lừa đảo), Shipping (giao mẫu cũ thay vì mẫu mới)
    (1, 1, 1, 0),
    # 1408: "mua cùng đơn nhưng cửa hàng tách ra 2 đơn rồi giao có một đơn nhưng đơn kia không thấy đâu, bảo cửa hàng huỷ đơn thì lại bảo tự liên hệ huỷ, làm ăn kỳ cục"
    # Service (không hỗ trợ hủy đơn, tách đơn không thông báo), Shipping (giao thiếu 1 đơn)
    (0, 1, 1, 0),
    # 1409: "bình sữa nhận được rập tốt... phí giao sản phẩm bình sữa là 44k. mình vẫn không hiểu sao phải tách 2 lần như vậy"
    # Service (phí giao cao do tách 2 lần giao không cần thiết)
    (0, 1, 0, 0),
    # 1410: "bình bị lỗi ngay cái quai cầm. mua 2 hôm rồi không để ý. mong cửa hàng hãy kiểm sản phẩm trước lúc giao cho khách"
    # Quality (bình bị lỗi quai cầm)
    (1, 0, 0, 0),
    # 1411: "mình mua 2 bình sữa giao cho mình bịch khăn khô"
    # Shipping (giao sai SP hoàn toàn - bịch khăn thay vì bình sữa)
    (0, 0, 1, 0),
    # 1412: "đầu ty chảy quá nhanh, không dùng được cho bé ít tháng tuổi"
    # Quality (đầu ty chảy nhanh - không phù hợp cho bé nhỏ)
    (1, 0, 0, 0),
    # 1413: "thấy ghi ppsu giao pp"
    # Shipping (giao sai chất liệu - pp thay vì ppsu)
    (0, 0, 1, 0),
    # 1414: "đặt sản phẩm lộn và không được đổi trả, thất vọng"
    # Service (không được đổi trả dù đặt nhầm)
    (0, 1, 0, 0),
    # 1415: "phần kết nối của mảnh cắt không đều"
    # Quality (phần kết nối không đều - lỗi gia công)
    (1, 0, 0, 0),
    # 1416: "giao sản phẩm nhanh. hàng gói kỹ"
    # Shipping (+), Packing (+)
    (0, 0, 1, 1),
    # 1417: "size quá nhỏ để chơi, theo tôi không nên mua. cửa hàng đăng hình con cờ gấp đôi ngón tay trỏ. thực tế con cờ như đầu bút bi nhỏ bằng 1/3 ngón tay trỏ. cửa hàng gắn hình đánh người mua thôi"
    # Quality (SP nhỏ xíu không đúng hình), Service (hình ảnh quảng cáo gây hiểu lầm cố tình)
    (1, 1, 0, 0),
    # 1418: "đặt sau 2 tuần mới có sản phẩm! đến khi nhận thì thấy cực kỳ hối hận, chất lượng quân cờ tương ứng giá tiền nhưng số lượng quân bị thiếu, thiếu 1 tượng và 1 mã đen"
    # Quality (thiếu quân cờ - SP không đầy đủ), Shipping (giao chậm 2 tuần)
    (1, 0, 1, 0),
    # 1419: "bàn cờ nhỏ xíu 12x12 cm, quân cờ bé tí teo không thể nào chơi được"
    # Quality (SP quá nhỏ không thể chơi được)
    (1, 0, 0, 0),
    # 1420: "cửa hàng cố tình cung cấp hình ảnh không chính xác ảnh 2 gây nhầm lẫn cho khách. quân cờ có mức độ hoàn thiện kém, không được như hình đâu"
    # Quality (quân cờ hoàn thiện kém, không đúng hình), Service (cố tình dùng hình không chính xác)
    (1, 1, 0, 0),
    # 1421: "mới giao là đã rụng nam châm và bàn cờ cầm lên lại gãy, có vẻ vẫn nếu bảo quản được thì đã rất tốt"
    # Quality (nam châm rụng, bàn cờ gãy ngay khi nhận - lỗi SP)
    (1, 0, 0, 0),
    # 1422: "tưởng rằng sau khi có nhận xét sản phẩm bé thì cửa hàng phải thay đổi, ai dè bàn cờ bé xíu thế thì sao dám cho trẻ chơi được, lỡ chúng nuốt phải thì đi cấp cứu có kịp không? đề nghị tiki xem lại cách ghi chú về kích thước. tôi muốn trả sản phẩm"
    # Quality (SP nguy hiểm cho trẻ - quá nhỏ có thể nuốt), Service (yêu cầu trả hàng, tiki chưa cải thiện)
    (1, 1, 0, 0),
    # 1423: "bộ cờ nhỏ gọn nam châm hít tốt dễ mang đi. có điều chất lượng không thật sự tốt. nam châm bị chênh làm một số quân cờ đứng bị chênh"
    # Quality (nam châm chênh - chất lượng không đồng đều)
    (1, 0, 0, 0),
    # 1424: "mini gì cái này siêu tí hon thì có, đúng là quên đọc đánh giá thì phải trả giá nhưng, muốn hoàn trả sản phẩm. mặc dù biết giá rẻ nhưng không nghĩ bán 1 sản phẩm như vây để đánh cờ"
    # Quality (SP quá nhỏ không thể dùng), Service (muốn hoàn trả)
    (1, 1, 0, 0),
    # 1425: "thiếu cờ, gia công xấu. tiền nào của đấy"
    # Quality (thiếu cờ, gia công xấu - chất lượng kém)
    (1, 0, 0, 0),
    # 1426: "ối dồi ôi, nó nhỏ xíu, nhựa đểu, mở ra gãy luôn, không thể chơi được. chỉ để trong tủ kính ngắm là được"
    # Quality (SP nhỏ xíu, nhựa kém, gãy ngay khi mở)
    (1, 0, 0, 0),
    # 1427: "trên hình đăng thì to bằng ngón tay nhưng nhận thì bé xíu. như vậy sao cầm chơi được. tôi muốn trả lại thì làm như nào?"
    # Quality (SP nhỏ hơn nhiều so với hình), Service (hỏi cách trả hàng)
    (1, 1, 0, 0),
    # 1428: "bài đăng hình con cờ to bằng ngón tay, nhưng thực tế thì sản phẩm nhận về cả bàn cờ nằm gọn trong lòng bàn tay. kích thước ô cờ là 1cm. cờ này đưa cho em bé thì chỉ có nuốt chứ chơi gì"
    # Quality (SP nhỏ xíu, nguy hiểm cho trẻ), Service (hình ảnh quảng cáo gây hiểu lầm)
    (1, 1, 0, 0),
    # 1429: "không nên mua tốn tiền kém chất lượng"
    # Quality (SP kém chất lượng)
    (1, 0, 0, 0),
    # 1430: "cách đổi trả sản phẩm không ra đâu vào đâu"
    # Service (thủ tục đổi trả không rõ ràng)
    (0, 1, 0, 0),
    # 1431: "quá nhỏ, nên có kích thước khi giới thiệu để biết khi mua"
    # Quality (SP quá nhỏ), Service (thiếu thông tin kích thước)
    (1, 1, 0, 0),
    # 1432: "sản phẩm bé tẹo. giao sản phẩm thì hơi vớ vẩn"
    # Quality (SP bé tẹo), Shipping (giao hơi vớ vẩn)
    (1, 0, 1, 0),
    # 1433: "đúng là tiền nào của đấy"
    # Quality (SP đúng với giá tiền - không đáng)
    (1, 0, 0, 0),
    # 1434: "bộ cờ quá nhỏ, đảo khách sản phẩm"
    # Quality (SP quá nhỏ), Service (lừa đảo khách hàng)
    (1, 1, 0, 0),
    # 1435: "sản phẩm này chỉ để trưng bày cho vui thôi chứ không chơi được vì quá nhỏ. ô thì bị lệch"
    # Quality (SP quá nhỏ, ô bị lệch - không chơi được)
    (1, 0, 0, 0),
    # 1436: "sản phẩm quá nhỏ luôn cửa hàng ơi!"
    # Quality (SP quá nhỏ)
    (1, 0, 0, 0),
    # 1437: "quân cờ bé hơn ngón út của tôi, tôi đã bị, trước khi bán đi thì phải xem có sử dụng được không chứ"
    # Quality (SP quá nhỏ, vô dụng)
    (1, 0, 0, 0),
    # 1438: "đúng với giá thành"
    # Quality (+, đúng giá)
    (1, 0, 0, 0),
    # 1439: "đặt mùi ca cao hạt mỡ thì giao lộn sản phẩm qua gói không mùi, gọi lên tiki phản hồi thì mấy ngày chưa thấy có nhân viên thu sản phẩm và đổi lại. trong khi khách người ta cần nên mới mua, giao sai sản phẩm cho khách làm không xài được lại phải mất công chạy ra cửa hàng khác mua. đánh giá 1 sao cho cả cửa hàng cung cấp sản phẩm và tiki"
    # Service (giao sai SP, không xử lý đổi trong nhiều ngày), Shipping (giao sai loại)
    (0, 1, 1, 0),
    # 1440: "sản phẩm gần hết date. bao bì cũ, dòng chữ on trên bao bì bị lem tùm lum. một vài bịch bóc ra có mùi hăng hắc khó chịu. đề nghị nhà bán sản phẩm nên viết rõ date cho khách sản phẩm biết trước khi mua"
    # Quality (gần hết date, bao bì cũ, mùi hắc - chất lượng kém), Service (không ghi rõ date)
    (1, 1, 0, 0),
    # 1441: "mùi hương cacao hơi nồng và gây khó chịu, vì sử dụng lau chùi khi bé đi vệ sinh nên không biết có ảnh hưởng gì không. khăn ướt có độ dai kém, khi bóc 1 miếng chưa ra khỏi gói là bị đứt giữa chừng"
    # Quality (mùi nồng gây khó chịu, khăn ướt yếu - dễ đứt)
    (1, 0, 0, 0),
    # 1442: "mua 12 bịch - tương đương 1 thùng - vậy nhưng tiki cũng không đóng thùng giúp mình, gói 1 nùi làm mất mỹ quan. chất lượng thì để dùng xem thế nào"
    # Packing (không đóng thùng dù mua số lượng lớn - gói lộn xộn)
    (0, 0, 0, 1),
    # 1443: "giao chậm nhưng không thông báo gì hết, mặc dù mới order là thấy bàn giao vận chuyển. về mở ra coi thì thấy rỉ đầy ra ngoài"
    # Shipping (giao chậm không thông báo), Packing (SP bị rỉ ra ngoài)
    (0, 0, 1, 1),
    # 1444: "mua combo 2 chai 118k 200ml. lại giao 4 chai 60ml. cửa hàng gì nhưng kỳ"
    # Shipping (giao sai combo - 4 chai 60ml thay vì 2 chai 200ml)
    (0, 0, 1, 0),
    # 1445: "mình có đặt sản phẩm 2 món như trên hình. nhưng khi nhận sản phẩm chỉ có 1 món là chậu tắm. túi trữ sữa không có. phản hồi từ 24/06/19 đến nay nhưng tiki vẫn chưa kiểm tra xong và có hồi báo lại cho mình"
    # Service (không phản hồi trong thời gian dài), Shipping (giao thiếu 1 SP)
    (0, 1, 1, 0),
    # 1446: "túi giống mô tả. nhưng khi mình dùng thử thì vòng tròn không có đổi màu xanh sang trắng khi nhiệt độ > 34°c mở túi ra có mùi nhựa nồng"
    # Quality (tính năng cảm ứng nhiệt không hoạt động, mùi nhựa nồng - lỗi SP)
    (1, 0, 0, 0),
    # 1447: "quảng cáo mô tả là túi trữ nhiệt cảm ứng nhưng khi giao sản phẩm là túi bình thường, giá gốc chỗ khác bán chỉ 44k thôi, đúng kiểu treo đầu dê bán thịt"
    # Quality (SP không có tính năng cảm ứng nhiệt như quảng cáo), Service (giá quá cao so với SP thực tế)
    (1, 1, 0, 0),
    # 1448: "mùi nhựa, địa chỉ khác với địa chỉ công ty ghi trên web!"
    # Quality (mùi nhựa, địa chỉ khác trên web - nghi không chính hãng)
    (1, 0, 0, 0),
    # 1449: "sản phẩm giá rẻ nhưng chỉ có 1 khóa zip nên không thích hợp trữ sữa ở ngăn mát lâu vì cảm giác khóa không kỹ"
    # Quality (thiếu tính năng - chỉ 1 khóa zip, không kín)
    (1, 0, 0, 0),
    # 1450: "chất lượng tạm ổn tốt tốt, nhưng giao sản phẩm quá chậm, đặt sản phẩm ngày 28/5, đến ngày 22/6 mới giao sản phẩm"
    # Quality (+), Shipping (giao chậm 25 ngày)
    (1, 0, 1, 0),
    # 1451: "thông tin sản phẩm ghi là 2 đường zip nhưng sản phẩm nhận được chỉ có 1 đường zip"
    # Quality (SP không đúng mô tả - 1 zip thay vì 2 zip)
    (1, 0, 0, 0),
    # 1452: "bình thiết kế kiểu có vòi giống thế này chỉ thích hợp với dầu gội hoặc sữa tắm. tìm mãi mới kiếm được cái nắp khác thay thế. mùi giống phấn rôm trẻ em, khá nồng"
    # Quality (thiết kế vòi không phù hợp với mục đích, mùi nồng)
    (1, 0, 0, 0),
    # 1453: "tôi đặt loại thường và loại đặc biệt thì nhận được chai đặc biệt 50ml, mở ra thử thì mùi nồng đậm đặc y như mùi chai dầu khuynh diệp. hoàn toàn không có mùi dầu tràm. hình thức mẫu mã thì rất đẹp nhưng ruột là dầu khuynh diệp. tôi mong muốn trả lại sản phẩm"
    # Quality (SP có mùi khuynh diệp thay vì dầu tràm - gian lận), Service (muốn trả hàng)
    (1, 1, 0, 0),
    # 1454: "về chất lượng thì mình thấy rất tốt, nhưng tiki đóng sản phẩm cẩu thả, đổ gần hết 1/5 chai dầu. do mình dễ tính nên nhận dùng luôn. đề nghị tiki cẩn thận hơn, nếu lần sau bị nữa mình sẽ không nhận"
    # Quality (+), Packing (đóng gói cẩu thả gây đổ 1/5 chai dầu)
    (1, 0, 0, 1),
    # 1455: "chả thơm dai gì hết giống sản phẩm giả quá"
    # Quality (không thơm - nghi hàng giả)
    (1, 0, 0, 0),
    # 1456: "đóng gói không cẩn thận, nắp dầu bị bể đổ tràn hết cả ra"
    # Packing (đóng gói không cẩn thận, nắp bể đổ tràn)
    (0, 0, 0, 1),
    # 1457: "tôi thật sự không hiểu! tôi đã mua 3 chai dầu tràm cung đình, loại chai nhãn trắng... rất hài lòng! vì thấy đây là chai đặc biệt, giá cao hơn gấp đôi... khi mở ra thì hoàn toàn thất vọng! mùi rất kinh, vừa hắc vừa khó ngửi, chả thấy chút nào mùi dầu tràm!... không thể dùng để làm gì cả!"
    # Quality (SP có mùi hắc, không phải dầu tràm - gian lận, giá gấp đôi)
    (1, 0, 0, 0),
    # 1458: "mua 3 hộp, 1 hộp bị bung nắp, chắc để lâu rồi nên hôi không uống được phải đổ bỏ"
    # Quality (1 hộp bung nắp, hôi không uống được - hư hỏng), Packing (1 hộp bung nắp)
    (1, 0, 0, 1),
    # 1459: "mở ra bị móp đổ bột ra ngoài luôn, không vừa lòng"
    # Packing (hộp bị móp, bột đổ ra ngoài)
    (0, 0, 0, 1),
    # 1460: "bình thường, sau 3 tháng mới nhận được sản phẩm"
    # Quality (+), Shipping (giao cực kỳ chậm - 3 tháng)
    (1, 0, 1, 0),
    # 1461: "chất lượng bình thường"
    # Quality (+, bình thường)
    (1, 0, 0, 0),
    # 1462: "nhận sản phẩm không phải là bàn chải điện tử như quảng cáo, đề nghị xem lại và mang lại quyền lợi cho khách sản phẩm. nếu nhầm đề nghị đổi"
    # Quality (SP không đúng mô tả - không phải bàn chải điện), Service (yêu cầu đổi)
    (1, 1, 0, 0),
    # 1463: "make in china giao sản phẩm không gọi trước khi giao thái độ shipper quá tệ"
    # Quality (SP made in china), Shipping (shipper không gọi trước, thái độ tệ)
    (1, 0, 1, 0),
    # 1464: "giống đồ chơi hơn. được cái con nít thích"
    # Quality (SP giống đồ chơi hơn thiết bị chăm sóc răng)
    (1, 0, 0, 0),
    # 1465: "dùng được 10 lần là hư. sút cán"
    # Quality (SP hỏng sau 10 lần dùng - chất lượng rất kém)
    (1, 0, 0, 0),
    # 1466: "bình thường không có gì nên cho 1 sao"
    # Quality (SP không đạt kỳ vọng dù đã đánh giá thấp)
    (1, 0, 0, 0),
    # 1467: "sản phẩm giao 10 ngày mới có ảnh thì có để dạ quan nhưng sản phẩm giao thì không có"
    # Shipping (giao thiếu SP, xác nhận giao ảo)
    (0, 0, 1, 0),
    # 1468: "mình mua máy hút sữa của fatzbaby nên mua bình sữa này để lắp vô máy hút luôn cho tiện. nhưng không ngờ là không lắp vừa... bình không kèm núm và nắp đậy núm như các bình khác. chỉ không hài lòng sản phẩm"
    # Quality (bình không tương thích với máy hút - thiếu phụ kiện, không lắp được)
    (1, 0, 0, 0),
    # 1469: "1 sao cho việc giao sai màu. sh không tôn trọng lựa chọn của kh. giao sai nhưng không báo khách. nhưng sản phẩm thì tốt"
    # Quality (+), Shipping (giao sai màu không báo khách)
    (1, 0, 1, 0),
    # 1470: "đặt mua màu hồng thì lại giao màu xanh. giới thiệu lắp được vào máy hút sữa fatz baby nhưng kết quả là không lắp vừa"
    # Quality (SP không lắp được như quảng cáo), Shipping (giao sai màu)
    (1, 0, 1, 0),
    # 1471: "150ml nhưng thực tế chỉ có 120ml"
    # Quality (dung tích thực tế kém hơn quảng cáo - 120ml thay vì 150ml)
    (1, 0, 0, 0),
    # 1472: "mua 1 lốc màu xanh 3 bình thì 2 bình nắp trầy, cũ, nhựa nhìn đểu nên không xài"
    # Quality (2/3 bình nắp trầy, cũ, nhựa kém)
    (1, 0, 0, 0),
    # 1473: "đặt màu xanh giao màu hồng"
    # Shipping (giao sai màu)
    (0, 0, 1, 0),
    # 1474: "đánh giá không tính điểm cửa hàng ơi, giao thiếu của mình 1 bộ 3 bình rồi. mình mua 2 bộ 6 bình nhưng giao có 3 bình à?"
    # Shipping (giao thiếu 1 bộ - chỉ có 3 bình thay vì 6)
    (0, 0, 1, 0),
    # 1475: "sản phẩm thiếu chi tiết. cụ thể bông màu xanh lá chỉ có 1"
    # Quality (thiếu phụ kiện - bông xanh lá chỉ có 1)
    (1, 0, 0, 0),
    # 1476: "mình đặt sản phẩm, thanh toán thẻ visa trước, chưa hề nhận được sản phẩm nhưng kiểm tra tình trạng đơn thì thấy cập nhật giao sản phẩm thành công. khiếu nại cả tuần không thấy giải quyết. không thể chấp nhận cách làm ăn dối trá này"
    # Service (không giải quyết khiếu nại cả tuần - lừa đảo), Shipping (xác nhận giao ảo dù không giao)
    (0, 1, 1, 0),
    # 1477: "sản phẩm đóng gói cẩn thận, tuy nhiên mùi rất nồng. mặc dù đã rửa rất kỹ nhưng vẫn còn mùi xà bông sau khi rửa bình sữa. không biết như vậy là bình thường hay sản phẩm giả"
    # Quality (mùi nồng bám sau khi rửa - nghi hàng giả), Packing (+)
    (1, 0, 0, 1),
    # 1478: "1 sao cho cửa hàng nhé. đặt sản phẩm dnee nhưng lại giao wesser"
    # Shipping (giao sai nhãn hiệu)
    (0, 0, 1, 0),
    # 1479: "với mình thì nước rửa này cho bé nhưng mùi hương quá nồng, mình rửa đi rửa lại rồi nhưng mùi chanh vẫn bám vào bình"
    # Quality (mùi nồng bám dai - không phù hợp cho bình bé)
    (1, 0, 0, 0),
    # 1480: "sản phẩm không đúng như đăng bán. ghi d-nee, giao thì giao feeding bottle"
    # Shipping (giao sai SP - giao feeding bottle thay vì d-nee)
    (0, 0, 1, 0),
    # 1481: "chờ xài xong mới biết được, tạm cứ hy vọng tốt"
    # (không đủ thông tin đánh giá)
    (0, 0, 0, 0),
    # 1482: "rửa bình cho bé xong vẫn còn mùi nước rửa mặc dù đã khử trùng"
    # Quality (mùi nước rửa bám sau khi khử trùng - không an toàn)
    (1, 0, 0, 0),
    # 1483: "chất lượng tốt nhưng dịch nên giao lâu quá"
    # Quality (+), Shipping (giao chậm do dịch)
    (1, 0, 1, 0),
    # 1484: "mẫu mã sản phẩm thì không có vấn đề gì. tôi chỉ xin góp ý cho nhà phân phối sản phẩm về việc ghi trực tiếp, rõ ràng số của khách hàng trên sản phẩm... thường là 0973. mong nhà bán lưu ý và rút kinh nghiệm"
    # Service (góp ý về bảo mật thông tin - số điện thoại ghi trên kiện hàng)
    (0, 1, 0, 0),
    # 1485: "thông tin sản phẩm là đất nặng không dính tay, rồi bla bla mua về mở ra bóc vào thì dính tay, rửa bằng nước nhưng không sạch. hộp gì giòn mục, nhưng bị móp vào đất sét"
    # Quality (SP dính tay, không đúng mô tả), Packing (hộp giòn mục, móp vào SP)
    (1, 0, 0, 1),
    # 1486: "sản phẩm ghi có quà tặng kèm nhưng khi nhận sản phẩm thì không có. tiki cũng không viết cách kiểm tra là được tặng hay không. thiếu thông tin"
    # Service (không nhận được quà, thông tin không rõ ràng)
    (0, 1, 0, 0),
    # 1487: "không hài lòng về giao sản phẩm, cứ nói người mua vắng nhà, nhưng ở nhà có thấy ai giao, cũng chẳng gọi điện, 1 đơn rồi đơn tiếp theo vẫn bị, mất cả time, bực bội"
    # Shipping (shipper báo vắng nhà rồi không giao - tái diễn nhiều lần)
    (0, 0, 1, 0),
    # 1488: "mua 4 combo đăng có quà khi giao nói không có vậy là sao"
    # Service (không nhận được quà khi giao)
    (0, 1, 0, 0),
    # 1489: "trả lại khuyến mãi cho tôi. nhận tiền rồi nhưng không trả khuyến mãi là sao. cửa hàng làm ăn đảo hả"
    # Service (không trả khuyến mãi dù đã thanh toán - lừa đảo)
    (0, 1, 0, 0),
    # 1490: "tã dày dễ rách độ thấm hút kém lắm"
    # Quality (tã dày nhưng dễ rách, thấm hút kém - chất lượng rất kém)
    (1, 0, 0, 0),
    # 1491: "1 tháng rưỡi mới nhận được sản phẩm!"
    # Shipping (giao cực kỳ chậm - 1.5 tháng)
    (0, 0, 1, 0),
    # 1492: "giao nhầm loại"
    # Shipping (giao sai loại)
    (0, 0, 1, 0),
    # 1493: "giao gì vậy cửa hàng. có miếng carton và danh thiếp là sao"
    # Shipping (giao SP rỗng - chỉ có carton và danh thiếp, không có SP)
    (0, 0, 1, 0),
    # 1494: "mình cần đổi sản phẩm vì mình mua sai sản phẩm"
    # Service (yêu cầu đổi SP do mua nhầm - lỗi người dùng)
    (0, 1, 0, 0),
    # 1495: "đặt sản phẩm 2 miếng, giao sản phẩm 1 miếng. bán sản phẩm không trung thực, đảo. tại sao tiki lại hợp tác với 1 ncc như vậy? gây mất uy tín cho tiki"
    # Service (bán không trung thực - giao thiếu), Shipping (giao thiếu 1 miếng)
    (0, 1, 1, 0),
    # 1496: "sản phẩm lỗi mang về kêu cửa hàng đổi nhưng cửa hàng đùn đẩy qua hãng để ngta liên hệ báo đổi lại chờ hoài chẳng thấy ma nào gọi, tiền mất tật mang cạch mặt cửa hàng này ra"
    # Quality (SP lỗi), Service (đùn đẩy trách nhiệm, không ai gọi lại - CSKH rất tệ)
    (1, 1, 0, 0),
    # 1497: "móc mùng bị gãy trước khi dùng, em bé nằm 1 bên, nôi bị nghiêng 1 bên, cảm giác không an toàn"
    # Quality (móc mùng gãy ngay khi nhận, nôi nghiêng - không an toàn cho bé)
    (1, 0, 0, 0),
    # 1498: "bị lỗi không chơi được. thất vọng sản phẩm bị lỗi không thể ráp được"
    # Quality (SP lỗi - không ráp được)
    (1, 0, 0, 0),
    # 1499: "sản phẩm mình đã thanh toán, báo là đã giao. nhưng cả nhà mình vẫn chưa nhận được sản phẩm. tiki hỗ trợ kiếm sản phẩm giúp mình nhé"
    # Service (yêu cầu hỗ trợ), Shipping (xác nhận giao ảo)
    (0, 1, 1, 0),
]

# Áp dụng labels cho index 1000-1499
for i, (q, s, sh, p) in enumerate(manual_labels):
    idx = 1000 + i
    df.at[idx, "Quality"] = q
    df.at[idx, "Service"] = s
    df.at[idx, "Shipping"] = sh
    df.at[idx, "Packing"] = p

# Chuyển về Int64
for col in ["Quality", "Service", "Shipping", "Packing"]:
    df[col] = pd.to_numeric(df[col], errors='coerce').astype("Int64")

# Ghi lại file gốc
df.to_csv(
    r"C:\Users\admin\Desktop\KHDL\IT4930-T2\data\Commentsauxuly\comments_data_ncds_preprocessed_toy.csv",
    index=False
)

print("Hoan thanh label 500 dong (index 1000-1499)!")
print()
print("=== THONG KE 1500 DONG DAU (0-1499) ===")
first_1500 = df.head(1500)
for col in ["Quality", "Service", "Shipping", "Packing"]:
    count = int(first_1500[col].sum())
    print(f"  {col}: {count}/1500 dong co nhan 1 ({count/15:.1f}%)")

print()
print("=== THONG KE RIENG 500 DONG MOI (1000-1499) ===")
batch = df.iloc[1000:1500]
for col in ["Quality", "Service", "Shipping", "Packing"]:
    count = int(batch[col].sum())
    print(f"  {col}: {count}/500 dong co nhan 1 ({count/5:.1f}%)")
