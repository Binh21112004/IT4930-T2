import pandas as pd, sys
sys.stdout.reconfigure(encoding='utf-8')

df = pd.read_csv(
    r"C:\Users\admin\Desktop\KHDL\IT4930-T2\data\Commentsauxuly\comments_data_ncds_preprocessed_toy.csv"
)

# -----------------------------------------------------------------------
# LABEL THỦ CÔNG DÒNG 100 -> 599 (index 100-599, tức file line 102-601)
# Quality  : chất lượng SP (hư hỏng, vị lạ, hàng giả/nhái, sai mẫu/loại SP)
# Service  : CSKH, tư vấn, đổi trả, khuyến mãi/quà không đúng, giá
# Shipping : giao trễ, giao nhầm/thiếu, shipper thái độ, shipper tự xác nhận giao
# Packing  : đóng gói sơ sài, hộp móp/rách, bao bì rách
# -----------------------------------------------------------------------

manual_labels = [
    # 100: "đạt yêu cầu, giao sản phẩm nhanh, đóng gói tốt"
    # -> Shipping(+), Packing(+)
    (0, 0, 1, 1),
    # 101: "người giao sản phẩm thái độ kém"
    # -> Shipping (shipper thái độ kém)
    (0, 0, 1, 0),
    # 102: "tiki gói sản phẩm quá ẩu"
    # -> Packing
    (0, 0, 0, 1),
    # 103: "sản phẩm giao xong. không hoàn asa... khách yêu cầu trả sản phẩm cũng không cho"
    # -> Service (không hoàn, không cho đổi trả, buôn bán bất hợp lý)
    (0, 1, 0, 0),
    # 104: "không có muỗng trong hộp, tổng đài giải quyết rất chán. đổi sữa cho con và đổi chỗ mua"
    # -> Quality (thiếu muỗng trong hộp), Service (tổng đài tệ)
    (1, 1, 0, 0),
    # 105: "sữa loãng, hơi ngọt so với năm, giá thành cao"
    # -> Quality (chất lượng sữa thay đổi, loãng), Service (giá cao)
    (1, 1, 0, 0),
    # 106: "tiki nên cho kiểm tra sản phẩm khi nhận. sản phẩm hay bị cấn móp"
    # -> Packing (SP hay bị cấn móp), Service (không cho kiểm hàng)
    (0, 1, 0, 1),
    # 107: "cảm thấy thất vọng, nhận sản phẩm không nguyên vẹn, hộp sữa bị mốp, trầy xước, nắp đậy không được"
    # -> Packing (hộp sữa bị móp, nắp không đóng được)
    (0, 0, 0, 1),
    # 108: "sữa giao bị móp méo. tiki đóng gói quá cẩu thả"
    # -> Packing
    (0, 0, 0, 1),
    # 109: "sản phẩm dùng tương đối tốt"
    # -> Quality (+)
    (1, 0, 0, 0),
    # 110: "giá hợp lý. giao hơi chậm"
    # -> Service (giá), Shipping (chậm)
    (0, 1, 1, 0),
    # 111: "về sản phẩm sữa friso thì chất lượng đảm bảo... giao trễ... bể nắp và móp méo vỏ... gửi khiếu nại"
    # -> Quality (+), Service (khiếu nại), Shipping (giao trễ), Packing (bể nắp, móp)
    (1, 1, 1, 1),
    # 112: "đóng sản phẩm cực kì ẩu, dịch vụ kém... gọi dịch vụ xử lý không thoả đáng, ăn hiếp khách"
    # -> Service (dịch vụ kém, không thoả đáng), Packing (đóng ẩu)
    (0, 1, 0, 1),
    # 113: "giao sữa date cũ. yêu cầu trả sản phẩm cũng không cho... gởi kiện tiki"
    # -> Quality (date cũ), Service (không cho đổi trả)
    (1, 1, 0, 0),
    # 114: "ẩu tã mua nhưng làm như xin vậy. cửa hàng"
    # -> Service (thái độ phục vụ kém)
    (0, 1, 0, 0),
    # 115: "đóng gói lỏng lẻo... hộp sữa bị móp... giao rất nhanh"
    # -> Shipping (+), Packing (lỏng lẻo, hộp móp)
    (0, 0, 1, 1),
    # 116: "sản phẩm chuẩn nhưng bị méo mó rồi"
    # -> Packing (bị méo)
    (0, 0, 0, 1),
    # 117: "gửi cho mình hộp bị móp, bị mất seal, đề nghị đổi lại hộp khác"
    # -> Service (yêu cầu đổi), Packing (hộp móp, mất seal)
    (0, 1, 0, 1),
    # 118: "giao sản phẩm quá tệ, đặt 15/11 báo giao 16/11 nhưng đến 21/11 mới giao"
    # -> Shipping (giao trễ rất nhiều)
    (0, 0, 1, 0),
    # 119: "mua 4 hộp hết 3 hộp bị móp nặng"
    # -> Packing (3/4 hộp bị móp nặng)
    (0, 0, 0, 1),
    # 120: "mình chưa sử dụng, nhưng là sản phẩm thiết yếu nhưng giao sản phẩm lâu không thể tưởng"
    # -> Shipping (giao rất chậm)
    (0, 0, 1, 0),
    # 121: "sản phẩm giao tốt. nhưng phải được kiểm sản phẩm"
    # -> Shipping (+), Service (muốn được kiểm hàng khi nhận)
    (0, 1, 1, 0),
    # 122: "giá thành tốt. đóng gói cẩn thận. mỗi việc boăn khoăn là không check được hình ảnh sữa"
    # -> Quality (không check được ảnh sữa - hoang mang), Service (giá tốt), Packing (+)
    (1, 1, 0, 1),
    # 123: "goi hang qua lau can nhanh hon"
    # -> Shipping (giao hàng quá lâu)
    (0, 0, 1, 0),
    # 124: "giao sản phẩm nhanh đóng gói cẩn thận"
    # -> Shipping (+), Packing (+)
    (0, 0, 1, 1),
    # 125: "chất lượng tốt. hạn sử dụng xa nên mua. sẽ ủng hộ lần 2"
    # -> Quality (+)
    (1, 0, 0, 0),
    # 126: "thùng bên ngoài nguyên vẹn, chỉ có sản phẩm bên trong bung bét: sữa bung cả nắp, móp méo, bột giặt rơi khắp thùng"
    # -> Quality (sản phẩm bị ảnh hưởng - sữa bung nắp), Packing (đóng gói tệ, hộp bung bét)
    (1, 0, 0, 1),
    # 127: "giao sản phẩm lâu quá trời, chán không muốn nói"
    # -> Shipping (giao rất chậm)
    (0, 0, 1, 0),
    # 128: "hài lòng về sản phẩm giao sản phẩm nhanh"
    # -> Quality (+), Shipping (+)
    (1, 0, 1, 0),
    # 129: "vận chuyển quăng quật thế nào nhưng bị thủng mất vài hộp. hỏng nhưng mất thời gian vệ sinh"
    # -> Shipping (vận chuyển ẩu), Packing (hộp thủng)
    (0, 0, 1, 1),
    # 130: "mình mua sản phẩm tiki trading chính hãng, khi đặt xong vô lại thì hiện cửa hàng tào lao nào đó?"
    # -> Service (thông tin cửa hàng bị thay đổi, gây nghi ngờ)
    (0, 1, 0, 0),
    # 131: "giao sản phẩm nhanh nhân viên nhiệt tình sản phẩm chưa sử dụng chưa biết chất lượng ra sao"
    # -> Shipping (+)
    (0, 0, 1, 0),
    # 132: "mình mua 3 hộp được tặng ấm pha trà, nhưng khi nhận sản phẩm không có ấm pha trà"
    # -> Service (không nhận được quà tặng kèm)
    (0, 1, 0, 0),
    # 133: "nhận gói sữa xong muốn vứt luôn, tiki giao sản phẩm tệ quá"
    # -> Shipping (giao tệ - ấn tượng xấu khi nhận)
    (0, 0, 1, 0),
    # 134: "mua sữa bột anlene gold movepro nhưng tiki giao sữa anlene thường, đổi lại 2 lần vẫn giao sai, support không đảm bảo giao đúng"
    # -> Service (support kém, không đảm bảo), Shipping (giao sai sản phẩm nhiều lần)
    (0, 1, 1, 0),
    # 135: "sản phẩm sữa anl dùng ngon"
    # -> Quality (+)
    (1, 0, 0, 0),
    # 136: "tôi đặt SP cho người trên 51 tuổi, tiki giao SP dành cho người trên 40. thậm chí đã thay đổi thông tin SP và không thông báo"
    # -> Service (thay đổi thông tin SP không báo, giao sai), Shipping (giao sai SP)
    (0, 1, 1, 0),
    # 137: "mua sản phẩm dành cho người trên 51 tuổi nhưng giao thành SP dành cho người trên 40, đây không phải trường hợp đầu tiên"
    # -> Shipping (giao sai SP)
    (0, 0, 1, 0),
    # 138: "giao sản phẩm không đúng như trên bao bì, mình thấy dành cho trên 51 tuổi mới đặt mua, khi nhận thì ghi trên 40"
    # -> Shipping (giao sai SP)
    (0, 0, 1, 0),
    # 139: "không hiểu sao rất nhiều người bị như này nhưng vẫn giao sản phẩm tắc trách như thế này"
    # -> Shipping (giao tắc trách, giao sai lặp đi lặp lại)
    (0, 0, 1, 0),
    # 140: "hộp bị méo mó và bẩn. có hộp thiếu hạn sử dụng. đã trả lại sản phẩm, tuy nhiên tiki tiếp tục giao trễ 3 ngày"
    # -> Quality (thiếu HSD), Service (đã trả hàng), Shipping (giao trễ), Packing (hộp méo, bẩn)
    (1, 1, 1, 1),
    # 141: "mình nhận sữa có bao bì là 40t thay vì 51t trở lên. có thể đổi lại cho mình được không?"
    # -> Service (yêu cầu đổi), Shipping (giao sai SP)
    (0, 1, 1, 0),
    # 142: "đánh giá không tính điểm chưa uống chưa biết thế nào"
    # -> (không đề cập khía cạnh nào rõ ràng)
    (0, 0, 0, 0),
    # 143: "sữa uống được 9 lọ sữa thì gặp lọ sữa này, hi vọng không gặp thêm lọ sữa như vậy nữa"
    # -> Quality (lọ sữa có vấn đề)
    (1, 0, 0, 0),
    # 144: "giá ở tiki cao hơn các sàn khác. sao bảo tặng thêm 1 bịch tã... khi giao thì không tặng"
    # -> Service (giá cao, không nhận được quà như cam kết)
    (0, 1, 0, 0),
    # 145: "giao sản phẩm lơ đễnh suýt làm thất lạc. trợ lý tư vấn thì không sát sao, cứ trả lời chung chung"
    # -> Service (tư vấn kém), Shipping (giao lơ đễnh)
    (0, 1, 1, 0),
    # 146: "giao sản phẩm chậm trễ không báo trước"
    # -> Shipping (giao chậm, không thông báo)
    (0, 0, 1, 0),
    # 147: "giá cửa hàng bán mắc hơn cửa hàng gần nhà... khuyến mãi bình trà nhỏ xíu không được nhiêu nước"
    # -> Service (giá mắc, khuyến mãi kém)
    (0, 1, 0, 0),
    # 148: "giao sản phẩm trễ hẹn không như dự kiến"
    # -> Shipping (giao trễ)
    (0, 0, 1, 0),
    # 149: "hộp sữa méo lệch, móp không đúng hình dạng"
    # -> Packing (hộp méo lệch)
    (0, 0, 0, 1),
    # 150: "mua 8 hộp móp cả 8. bên giao sản phẩm đóng cực kỳ cẩn thận. vậy nên đây là sữa bị móp hộp từ trước vẫn bán cho khách. đồ dối trá"
    # -> Quality (SP đã bị móp trước khi bán), Service (gian lận, dối trá)
    (1, 1, 0, 0),
    # 151: "nestle đang thu hồi sản phẩm lỗi, ở vn nếu có thì mình gửi trả sản phẩm ntn"
    # -> Quality (SP lỗi bị thu hồi), Service (hỏi cách trả hàng)
    (1, 1, 0, 0),
    # 152: "đóng cẩu thả, 4 hộp bẹp 3 hộp, 1 hộp bẹp móp nặng"
    # -> Packing (đóng cẩu thả, hộp bẹp)
    (0, 0, 0, 1),
    # 153: "shipper không điện thoại liên lạc người nhận, và sản phẩm chưa được giao tới tay đã vội xác nhận giao thành công"
    # -> Shipping (shipper gian lận xác nhận giao giả), Service (mong tiki giải quyết)
    (0, 1, 1, 0),
    # 154: "nhận được hộp sữa móp méo biến dạng là thấy khó chịu vô cùng"
    # -> Packing (hộp móp biến dạng)
    (0, 0, 0, 1),
    # 155: "giao sản phẩm chậm và đóng gói kém, không có chống sốc, hộp lỏng lẻo. mua 3 hộp nhưng nhận về 2 hộp móp méo hết cả"
    # -> Shipping (giao chậm), Packing (đóng gói kém, hộp móp)
    (0, 0, 1, 1),
    # 156: "đã mua nhiều lần, tuy nhiên lần này đóng gói quá tệ, hộp sữa móp méo chả ra gì"
    # -> Packing (đóng gói tệ, hộp móp)
    (0, 0, 0, 1),
    # 157: "cần xem lại cách đóng gói, học hỏi ở cửa hàng khác... nhận được sản phẩm thật sự thất vọng"
    # -> Packing (đóng gói tệ)
    (0, 0, 0, 1),
    # 158: "giao sản phẩm không giống như hình, phản hồi không trả lời"
    # -> Service (không phản hồi), Shipping (giao sai SP)
    (0, 1, 1, 0),
    # 159: "giao sản phẩm không đúng mẫu mã, đề nghị nhận lại"
    # -> Service (yêu cầu nhận lại), Shipping (giao sai mẫu mã)
    (0, 1, 1, 0),
    # 160: "tiki giao sản phẩm không đúng mẫu mã, chủng loại đã giới thiệu"
    # -> Shipping (giao sai mẫu mã, chủng loại)
    (0, 0, 1, 0),
    # 161: "sản phẩm giao nhanh nhưng khuyến mãi date cũ"
    # -> Quality (date cũ), Shipping (+)
    (1, 0, 1, 0),
    # 162: "giao sản phẩm lâu lắm, đặt cả tháng mới nhận được, đợi được sữa con nhà người ta cũng lớn luôn rồi"
    # -> Shipping (giao cực kỳ chậm)
    (0, 0, 1, 0),
    # 163: "3 hộp thì 2 hộp bẹp méo nhưng chất lượng thì chưa dùng chưa biết"
    # -> Packing (hộp bẹp méo)
    (0, 0, 0, 1),
    # 164: "sản phẩm vận chuyển từ hà nội vào nhưng tiki không đóng thùng nên sữa bị móp méo nhiều"
    # -> Packing (không đóng thùng, sữa bị móp)
    (0, 0, 0, 1),
    # 165: "toàn bộ 3 đều móp do vận chuyển. móp nặng"
    # -> Shipping (vận chuyển gây móp), Packing (3 hộp đều móp nặng)
    (0, 0, 1, 1),
    # 166: "do dịch nên giao sản phẩm hơi lâu"
    # -> Shipping (giao chậm do dịch - thông cảm)
    (0, 0, 1, 0),
    # 167: "giáo sản phẩm hộp móp méo sữa cũng bị móp méo nặng"
    # -> Shipping (giao tệ), Packing (hộp móp nặng)
    (0, 0, 1, 1),
    # 168: "chờ nhận được hộp sữa hết cả tuổi thanh xuân"
    # -> Shipping (giao cực kỳ chậm)
    (0, 0, 1, 0),
    # 169: "kiểm tra dùm mua 2 đơn hàng nhưng mới nhận có 1 đơn"
    # -> Shipping (giao thiếu)
    (0, 0, 1, 0),
    # 170: "đóng gói sơ xài, sản phẩm tới tay móp hết, bung luôn nắp vàng, không bao giờ mua thêm lần nào nữa"
    # -> Packing (đóng gói sơ sài, hộp móp, bung nắp)
    (0, 0, 0, 1),
    # 171: "sao nắp hộp đợt này của mình lại khác loại cũ thế dùng không tiện chút nào"
    # -> Quality (nắp hộp thay đổi, bất tiện)
    (1, 0, 0, 0),
    # 172: "móp méo quá trời. may không quá miếng bạc không bị bục ra"
    # -> Packing (hộp móp)
    (0, 0, 0, 1),
    # 173: "hộp bị móp hai bên. tiki nên lưu ý vận chuyển và đóng sản phẩm kỹ hơn"
    # -> Shipping (vận chuyển gây móp), Packing (hộp móp)
    (0, 0, 1, 1),
    # 174: "hộp bị méo móp hết. không biết sản phẩm lỗi ngay từ đầu hay sao"
    # -> Packing (hộp méo), Quality (nghi ngờ SP lỗi)
    (1, 0, 0, 1),
    # 175: "giao sản phẩm nhanh. đóng gói cẩn thận"
    # -> Shipping (+), Packing (+)
    (0, 0, 1, 1),
    # 176: "đợt này mình mua 3, 2 bé đang dùng bị nhiễm trùng tiêu hóa phải nhập viện. không biết do lô sữa lỗi hay sữa giả"
    # -> Quality (sữa gây bệnh, nghi lô lỗi/hàng giả)
    (1, 0, 0, 0),
    # 177: "lần thứ 2 mua sữa enfamil và cũng nhận được sản phẩm bị móp méo. hạt sữa vàng hơn loại enfamil màu vàng. nhưng vị thì béo béo nhạt thanh"
    # -> Quality (chất lượng sữa thay đổi), Packing (hộp bị móp)
    (1, 0, 0, 1),
    # 178: "nắp hộp hơi khác so với hộp cũ mình mua trước đó. nắp này không kín bằng và cũng không có chỗ gác muỗng"
    # -> Quality (nắp thay đổi, không kín)
    (1, 0, 0, 0),
    # 179: "hộp méo mó nặng, chất lượng thì chưa bóc nên chưa biết"
    # -> Packing (hộp móp nặng)
    (0, 0, 0, 1),
    # 180: "chuyến này giao sữa bị móp nhiều mong lần sau hộp phải nguyên vẹn"
    # -> Packing (hộp bị móp nhiều)
    (0, 0, 0, 1),
    # 181: "không hợp với bé, đi ngoài nhiều"
    # -> Quality (SP không phù hợp, gây đi ngoài)
    (1, 0, 0, 0),
    # 182: "nhà bán không có tâm không bọc kỹ khui thùng bể nắp"
    # -> Packing (không bọc kỹ, bể nắp)
    (0, 0, 0, 1),
    # 183: "đánh giá không tính điểm móp quá nhiều không biết chất lượng bên trong thế nào"
    # -> Packing (móp nhiều)
    (0, 0, 0, 1),
    # 184: "hộp sữa thì móp méo... thùng ngoài thì vừa rách vừa móp, gọi tiki để thu hồi thì ì ạch, 3-4 ngày rồi chưa thấy tới"
    # -> Service (tiki phản hồi chậm), Packing (hộp móp, thùng rách)
    (0, 1, 0, 1),
    # 185: "giao chất lượng tốt, sản phẩm hsd xa tuy nhiên đóng gói và vận chuyển bị móp méo sữa, có 1 gãy niêm nắp hộp. chưa hài lòng về chất lượng dv"
    # -> Quality (+, hsd xa), Shipping (vận chuyển gây móp), Packing (đóng gói gây móp, gãy niêm nắp)
    (1, 0, 1, 1),
    # 186: "mua 4 hộp sữa méo hết 2 vỏ hộp, sữa cho bé cần phải quấn chống sốc chứ"
    # -> Packing (2/4 hộp méo, thiếu chống sốc)
    (0, 0, 0, 1),
    # 187: "gói sản phẩm sơ sài, chỉ bỏ hai sữa vào thùng giấy... móp hết hai sữa. chat hỏi thì không ai trả lời"
    # -> Service (không có ai trả lời), Packing (đóng gói sơ sài, hộp móp)
    (0, 1, 0, 1),
    # 188: "hộp bị bẹp đóng sản phẩm không cẩn thận dẫn đến vận chuyển bị bẹp hộp"
    # -> Packing (đóng gói không cẩn thận gây bẹp)
    (0, 0, 0, 1),
    # 189: "hơi thất vọng, đáng lý sữa phải được vận chuyển kỹ, hộp sữa mới nhận, nhưng thấy ngại cho anh vận chuyển nên mình nhận luôn"
    # -> Shipping (vận chuyển không cẩn thận)
    (0, 0, 1, 0),
    # 190: "mỗi lần đặt sản phẩm sữa trên tiki rất là sợ. khi nhận toàn bị móp méo. đóng gói thì sơ sài"
    # -> Packing (đóng gói sơ sài, hộp móp thường xuyên)
    (0, 0, 0, 1),
    # 191: "ghi sữa mới nhưng lại giao mẫu cũ. date vẫn xa nhưng sản xuất lâu rồi không phải mã check qr"
    # -> Quality (giao sai mẫu, nghi ngờ hàng giả/sản xuất lâu)
    (1, 0, 0, 0),
    # 192: "giao sản phẩm chậm, đóng gói không cẩn thận. nhận được sản phẩm thùng bên ngoài rách, hộp thì méo mó hết"
    # -> Shipping (giao chậm), Packing (thùng rách, hộp méo)
    (0, 0, 1, 1),
    # 193: "giao sản phẩm nhanh nhưng bị cấn móp"
    # -> Shipping (+), Packing (bị cấn móp)
    (0, 0, 1, 1),
    # 194: "giao sản phẩm quá lâu. mua từ 8/8 đến nay 15/10 mới nhận được"
    # -> Shipping (giao cực kỳ chậm - 2 tháng)
    (0, 0, 1, 0),
    # 195: "sản phẩm giao qua lâu nên không còn nhu cầu sử dụng"
    # -> Shipping (giao quá chậm)
    (0, 0, 1, 0),
    # 196: "sữa móp nhìn mất thẩm mỹ"
    # -> Packing (hộp sữa bị móp)
    (0, 0, 0, 1),
    # 197: "giao sản phẩm không đúng ngày"
    # -> Shipping (giao không đúng ngày cam kết)
    (0, 0, 1, 0),
    # 198: "sản phẩm giao không lót cẩn thận bị móp hộp sữa, không hài lòng với cách đóng sản phẩm của tiki"
    # -> Packing (không lót cẩn thận, hộp móp)
    (0, 0, 0, 1),
    # 199: "giao sản phẩm nhưng hộp sữa bị như này rồi sao dám mua nữa"
    # -> Packing (hộp sữa bị móp/hỏng)
    (0, 0, 0, 1),
    # 200: "móp. nên rút kinh nghiệm"
    # -> Packing (hộp bị móp)
    (0, 0, 0, 1),
    # 201: "giao sản phẩm quá lâu nhưng không thông báo"
    # -> Shipping (giao chậm, không thông báo)
    (0, 0, 1, 0),
    # 202: "sữa chính hãng nhưng đóng gói quá cẩu thả nên không hài lòng lắm"
    # -> Packing (đóng gói cẩu thả)
    (0, 0, 0, 1),
    # 203: "giao sản phẩm nhanh, nhưng đóng gói thì sơ sài"
    # -> Shipping (+), Packing (đóng gói sơ sài)
    (0, 0, 1, 1),
    # 204: "đóng gói quá tệ, móp quá nhiều"
    # -> Packing (đóng gói tệ, hộp móp nhiều)
    (0, 0, 0, 1),
    # 205: "rất không hài lòng, nhận sản phẩm bị bung nắp văng sữa ra, sữa bị vón cục hở nắp không thể cho bé uống. đề nghị tiki giải quyết và hoàn tiền"
    # -> Quality (sữa vón cục, không dùng được), Service (yêu cầu hoàn tiền), Packing (bung nắp)
    (1, 1, 0, 1),
    # 206: "đóng sản phẩm quá tệ, sữa vơi ra ngoài, mong cửa hàng xử lý nhanh"
    # -> Service (yêu cầu xử lý), Packing (đóng gói tệ, sữa vơi ra ngoài)
    (0, 1, 0, 1),
    # 207: "móp méo sữa bị vón cục cửa hàng xem lại chất lượng sữa và cách bảo quản đóng gói"
    # -> Quality (sữa vón cục), Packing (hộp móp, bảo quản kém)
    (1, 0, 0, 1),
    # 208: "cửa hàng lấy hộp sữa bị bật nắp giao cho mình... hoàn trả thì cửa hàng lại đổ thừa do lỗi shipper và trừ tiền 750k"
    # -> Service (không xử lý đúng, đổ lỗi và trừ tiền), Packing (hộp bật nắp)
    (0, 1, 0, 1),
    # 209: "bao bì dán bị lệch, sản phẩm có phải chính hãng không? bé nhà mình uống bị trớ"
    # -> Quality (nghi ngờ hàng giả - bao bì lệch, bé bị trớ)
    (1, 0, 0, 0),
    # 210: "sữa pha có nhiều bột hơn dòng khác nhưng bé vẫn hợp tác"
    # -> Quality (nhận xét về chất lượng sữa)
    (1, 0, 0, 0),
    # 211: "giao nhanh, đóng gói chắc chắn. date đến tháng 10/2022. nhận được quà như lúc đặt đơn, rất hài lòng"
    # -> Service (+, quà tặng đúng), Shipping (+), Packing (+)
    (0, 1, 1, 1),
    # 212: "giao sản phẩm quá lâu, nhân viên hỗ trợ không nhiệt tình luôn hướng dẫn khách hủy đơn thay vì đưa giải pháp"
    # -> Service (NV kém, không hỗ trợ tốt), Shipping (giao chậm)
    (0, 1, 1, 0),
    # 213: "sản phẩm giao lâu! đến nơi thì hộp vận chuyển móp méo, sữa bị đổ ra ngoài. không đóng gói chắc chắn"
    # -> Shipping (giao lâu), Packing (hộp móp, sữa đổ ra)
    (0, 0, 1, 1),
    # 214: "không tư vấn, tương tác hỗ trợ cho khách khi mua sản phẩm"
    # -> Service (không tư vấn, thiếu hỗ trợ)
    (0, 1, 0, 0),
    # 215: "giao lâu nhưng giao lộn. vui lòng liên hệ để đổi sản phẩm"
    # -> Service (yêu cầu đổi), Shipping (giao lâu, giao nhầm)
    (0, 1, 1, 0),
    # 216: "giao sản phẩm nhanh. date xa. 5 sao"
    # -> Quality (+, date xa), Shipping (+)
    (1, 0, 1, 0),
    # 217: "cảm giác đợt này sản phẩm không chất lượng, túi dựng vừa tháo bọc kính đã bị phuy sẵn. giấy mỏng hơn nhiều so với loại đang xài. nghi ngờ hàng nhái"
    # -> Quality (SP kém hơn, mỏng hơn, nghi nhái)
    (1, 0, 0, 0),
    # 218: "trước giờ an tâm về nhân sự. nhưng chỉ vì không ném thùng sản phẩm vào trong nhà. nhưng tôi mất hết toàn bộ sản phẩm"
    # -> Shipping (shipper không giao vào nhà, mất hàng)
    (0, 0, 1, 0),
    # 219: "mua 2 combo... khi nhận thì bị rách bao bì bên ngoài. kiểm tra lại thì thiếu mất 1 bịch. shipper nói đã xác nhận đơn thành công rồi nên không trả lại"
    # -> Service (shipper xác nhận nhầm, không giải quyết), Shipping (giao thiếu), Packing (bao bì rách)
    (0, 1, 1, 1),
    # 220: "bao bì khăn hoàn toàn khác nhau về mẫu mã... tại sao lại giao mẫu cũ? treo đầu dê bán thịt"
    # -> Quality (giao sai mẫu, nghi ngờ), Service (giao không đúng mô tả)
    (1, 1, 0, 0),
    # 221: "chất lượng khăn ướt thì khỏi bàn vì bobby quá tốt rồi. điều không hài lòng là tiki tặng quà nhưng lại bắt khách trả tiền"
    # -> Quality (+), Service (quà tặng không đúng cam kết - phải trả tiền)
    (1, 1, 0, 0),
    # 222: "cảm giác sản phẩm không được sắc nét, bao bì màu sắc nhạt nhoà, nhìn cứ như sản phẩm nhái. chỉ được cái giao sản phẩm cực nhanh"
    # -> Quality (nghi ngờ hàng nhái - bao bì nhạt), Shipping (+)
    (1, 0, 1, 0),
    # 223: "mùa dịch giao 8 ngày. quà tặng kèm đệm nôi thì dính bẩn từ trước. tiki đã tạo lệnh thu hồi. khăn ướt thì không vấn đề gì"
    # -> Quality (+, khăn ok), Service (quà tặng hỏng, yêu cầu đổi), Shipping (giao chậm do dịch)
    (1, 1, 1, 0),
    # 224: "mình mua nguyên set để nhận kèm bộ gấu khuyến mãi... vừa nhận sản phẩm lại không thấy bộ gấu khuyến mãi"
    # -> Service (không nhận được quà khuyến mãi)
    (0, 1, 0, 0),
    # 225: "khăn ướt dùng kích ứng, ngứa, mẩn đỏ... sao dám dùng cho con mình đây"
    # -> Quality (SP gây kích ứng da)
    (1, 0, 0, 0),
    # 226: "chất lượng tốt vì mua nhiều rồi nhưng đóng gói lần này thất vọng quá vận chuyển bị rách bẩn vỏ khăn giấy"
    # -> Quality (+), Shipping (vận chuyển gây rách), Packing (vỏ bị rách, bẩn)
    (1, 0, 1, 1),
    # 227: "nhân viên giao sản phẩm dễ thương. sản phẩm mới, bao bì đóng gói đẹp. chất lượng kém. miếng khăn giấy nhỏ, mỏng; dệt không chắc"
    # -> Quality (khăn kém - nhỏ, mỏng, không chắc), Shipping (+), Packing (+)
    (1, 0, 1, 1),
    # 228: "mua loại 100 miếng, giao loại 80 miếng. cạch cửa hàng này"
    # -> Shipping (giao sai số lượng/loại)
    (0, 0, 1, 0),
    # 229: "mình đặt combo 6 gói khăn ướt nhưng giao chỉ có 4 gói"
    # -> Shipping (giao thiếu)
    (0, 0, 1, 0),
    # 230: "mình đã mua lần thứ 2. khi dùng để lau mặt người lớn lại bị rát và chích chích rất khó chịu"
    # -> Quality (SP gây rát, khó chịu khi dùng)
    (1, 0, 0, 0),
    # 231: "mua gói 6 gói khăn nhưng giao chỉ có 5 bọc có dấu hiệu bị rách! cần hỗ trợ ngay"
    # -> Service (yêu cầu hỗ trợ), Shipping (giao thiếu), Packing (bọc bị rách)
    (0, 1, 1, 1),
    # 232: "trong 6 gói sản phẩm, chỉ có 4 gói có đóng dấu ngày sản xuất và hạn sử dụng, 2 gói không có và bị dơ. không biết 2 gói này có phải chính hãng không"
    # -> Quality (2 gói không có NSX/HSD, nghi hàng giả)
    (1, 0, 0, 0),
    # 233: "giao thiếu cả 6 gói khăn ướt mất toi 150k!"
    # -> Shipping (giao thiếu hoàn toàn 6 gói)
    (0, 0, 1, 0),
    # 234: "để hình thì đơn 1tr199 tặng xe scooter 11.1 mình mua đơn trên 1tr199 ngày 11.1 không thấy tặng gì"
    # -> Service (không nhận được quà như quảng cáo)
    (0, 1, 0, 0),
    # 235: "giao sản phẩm không đúng như ảnh trên website, không có lời giải thích rõ ràng, sản phẩm bao bì có vẻ không chất lượng"
    # -> Quality (nghi ngờ chất lượng SP), Service (không giải thích), Shipping (giao sai)
    (1, 1, 1, 0),
    # 236: "mua số lượng nhiều chủ yếu nhận quà. thế nhưng tự động chia đơn ra rồi không biết quà có tới tay không nữa"
    # -> Service (chia đơn tự động ảnh hưởng quà, không biết kết quả)
    (0, 1, 0, 0),
    # 237: "đã mua nhiều lần do tiki bán nhưng lần này đóng gói quá tệ, nhận sản phẩm thấy nilon bao quanh bung ra nhiều, xộc xệch"
    # -> Packing (đóng gói tệ, nilon bung, xộc xệch)
    (0, 0, 0, 1),
    # 238: "mình đặt combo 6 gói sao gửi mình có 5 gói. thất vọng"
    # -> Shipping (giao thiếu 1 gói)
    (0, 0, 1, 0),
    # 239: "đợi sản phẩm rất lâu nhưng đến lúc nhận rồi giao sản phẩm lại báo là bên tiki tự huỷ đơn nên thu hồi lại"
    # -> Service (tiki tự hủy đơn sau khi khách đợi lâu), Shipping (giao rất chậm)
    (0, 1, 1, 0),
    # 240: "sản phẩm fake. con mình dùng bị khô da nổi mẩn. đến mình dùng cũng khác sản phẩm bobby mua chính tại cửa hàng"
    # -> Quality (hàng fake/giả, gây kích ứng)
    (1, 0, 0, 0),
    # 241: "khăn ướt tốt nhưng giao sản phẩm lâu trong hcm mà 10 ngày, đóng gói sơ sài quá, lúc nhận là tanh bành cái vỏ giấy rồi"
    # -> Quality (+), Shipping (giao chậm), Packing (đóng gói sơ sài, vỏ bị rách)
    (1, 0, 1, 1),
    # 242: "quảng cáo mua đơn sản phẩm 1199k tặng cái xe duy nhất ngày 11.1 làm mình mua... nhưng giao không có sản phẩm tặng"
    # -> Service (không nhận được quà tặng như quảng cáo)
    (0, 1, 0, 0),
    # 243: "sản phẩm bao bì khác so với thị trường, sản phẩm có mùi chua"
    # -> Quality (bao bì khác, mùi chua - nghi hàng lỗi/giả)
    (1, 0, 0, 0),
    # 244: "khăn ướt dai nhưng mỏng, mỗi lần rút ra cả tệp chứ không ra từng cái 1"
    # -> Quality (khăn mỏng, rút ra cả tệp - thiết kế kém)
    (1, 0, 0, 0),
    # 245: "mua tận 6 gói khăn ướt nhưng đóng gói sơ xài, chỉ có bọc bao ni lông ở ngoài, giao sản phẩm giao tới thì rách"
    # -> Shipping (giao tới bị rách), Packing (đóng gói sơ sài)
    (0, 0, 1, 1),
    # 246: "thấy ảnh đăng thì được tặng set chăn gối, đến lúc hỏi cửa hàng thì bảo không được, qua ngày chương trình khuyến mãi"
    # -> Service (quảng cáo gây hiểu lầm, không nhận được quà như ảnh)
    (0, 1, 0, 0),
    # 247: "tách đơn sản phẩm khuyến mại, sau khi mình nhận sản phẩm và thanh toán thì bên nhà bán hủy đơn sản phẩm khuyến mại không giao luôn"
    # -> Service (hủy đơn khuyến mãi sau khi đã nhận - lừa đảo)
    (0, 1, 0, 0),
    # 248: "cửa hàng mới giao bỉm nhưng thiếu combo mấy bịch khăn ướt của mình"
    # -> Shipping (giao thiếu)
    (0, 0, 1, 0),
    # 249: "mùi hơi hắc, không dễ chịu như loại có hương"
    # -> Quality (mùi không dễ chịu)
    (1, 0, 0, 0),
    # 250: "sản phẩm chuẩn hình đã đặt mua"
    # -> Quality (+, đúng mô tả)
    (1, 0, 0, 0),
    # 251: "giao thiếu bịch khăn giấy"
    # -> Shipping (giao thiếu)
    (0, 0, 1, 0),
    # 252: "rõ ràng tôi đã chọn quà thành công nhưng vẫn không có quà... giống như chạy chương trình tặng quà để đảo không mua số lượng lớn vậy"
    # -> Service (không nhận được quà đã chọn, thủ tục mập mờ)
    (0, 1, 0, 0),
    # 253: "đã nhận sản phẩm về sản phẩm thì không có gì nhưng không nhận được quà tặng đi kèm. hỏi nhân viên giao sản phẩm kêu quà gửi sau nhưng không biết bh"
    # -> Service (quà không đến, không thông báo rõ ràng)
    (0, 1, 0, 0),
    # 254: "date thì xa nhưng bao bì dơ, cũ trông rất không ưng, không hài lòng trong bảo quản sản phẩm"
    # -> Packing (bao bì dơ, cũ - bảo quản kém)
    (0, 0, 0, 1),
    # 255: "mình hay mua mall bên này cảm giác tả giả nhưng xài có mấy miếng bị hâm. mua lần 2 bịch g đành bỏ không dám xài"
    # -> Quality (nghi hàng giả, SP bị hâm - lỗi)
    (1, 0, 0, 0),
    # 256: "con mình dùng rất hay bị tràn. trước dùng cùng loại mua ngoài cửa hàng khác thì không bị tình trạng như vậy"
    # -> Quality (SP bị tràn thường xuyên - chất lượng kém)
    (1, 0, 0, 0),
    # 257: "quá tệ, mua sản phẩm lúc 0h để nhận quà tặng nhưng lúc nhận sản phẩm không có"
    # -> Service (không nhận được quà tặng như cam kết)
    (0, 1, 0, 0),
    # 258: "giao sản phẩm trễ hơn so với dự kiến. gói sản phẩm không kỹ, quá sơ sài làm vận chuyển gần rách vỏ bọc"
    # -> Shipping (giao trễ), Packing (gói không kỹ, gần rách)
    (0, 0, 1, 1),
    # 259: "mình muốn trả sản phẩm, tiki giao sản phẩm nhưng bao bì bị rách, đồ cho em bé như vậy sao đảm bảo chất lượng"
    # -> Service (muốn trả hàng), Packing (bao bì rách)
    (0, 1, 0, 1),
    # 260: "đó giờ rất thích cách đóng gói của tiki tuy nhiên lần này thấy khá thất vọng"
    # -> Packing (đóng gói lần này thất vọng)
    (0, 0, 0, 1),
    # 261: "mua ngày 19/5 nói được tặng thảm nhạc cho đơn từ 799k nhưng không thấy"
    # -> Service (không nhận được quà tặng như cam kết)
    (0, 1, 0, 0),
    # 262: "mua 4b để được thêm quà tặng nhưng giao bỉm xong hủy luôn đơn quà tặng của người ta, làm ăn chộp giật"
    # -> Service (hủy đơn quà tặng, hành vi gian lận)
    (0, 1, 0, 0),
    # 263: "cùng loại moony natural organic, nhưng sao mình mua ở con cưng giá 540k không sale, trên tiki thấy cũng để giá 540k sale... con mình dùng bỉm mua trên tiki bị mẩn nốt"
    # -> Quality (SP khác biệt so với mua tại shop, gây mẩn nốt), Service (nghi ngờ hàng kém chất lượng)
    (1, 1, 0, 0),
    # 264: "đặt sản phẩm hồi sale 8.8 nhưng giao sản phẩm nhầm thức ăn cho... hẹn giao lại tới 22/8 giao nhưng đến nay vẫn chưa giao. tiền trả rồi nhưng sản phẩm thì vẫn chưa giao"
    # -> Shipping (giao nhầm, chờ rất lâu vẫn chưa nhận)
    (0, 0, 1, 0),
    # 265: "mua rất nhiều lần nhưng lần này không hài lòng nhất... bóc ra nhìn thấy một vệt băng dính dài gần vết rách. sản phẩm đã vậy nhưng gửi cho khách làm ăn không uy tín gì cả"
    # -> Quality (SP bị rách, không uy tín), Packing (băng dính vá víu)
    (1, 0, 0, 1),
    # 266: "bao bì gói mong manh bịch tả bị rách dễ bị dơ"
    # -> Packing (bao bì mong manh, bị rách)
    (0, 0, 0, 1),
    # 267: "đọc rất nhiều cmt tiêu cực từ khách mua tiki trading, nhưng mình nghĩ đã thay đổi, cải thiện, tuy nhiên nay mình nhận sản phẩm bao bỉm vẫn rách?"
    # -> Packing (bao bỉm rách)
    (0, 0, 0, 1),
    # 268: "nhận sản phẩm nhưng không có quà. mặc dù 21/9 mua là được tặng quà, trong nội dung thanh toán cũng có kèm bộ bàn nhưng nhận thì không có"
    # -> Service (không nhận được quà đã cam kết trong thanh toán)
    (0, 1, 0, 0),
    # 269: "đóng gói cẩn thận, chất lượng tốt"
    # -> Quality (+), Packing (+)
    (1, 0, 0, 1),
    # 270: "đặt sản phẩm có quà tặng giao sản phẩm về không có. chán tiki. không bao giờ mua sản phẩm tiki nữa"
    # -> Service (giao không có quà như cam kết)
    (0, 1, 0, 0),
    # 271: "cảm nhận không xịn như mua ở mall. bị tràn và không vừa vặn"
    # -> Quality (SP kém hơn mua tại mall, bị tràn, không vừa)
    (1, 0, 0, 0),
    # 272: "trẻ đóng bị vón cục không tràn hết được bỉm"
    # -> Quality (SP bị vón cục, không thấm đúng cách)
    (1, 0, 0, 0),
    # 273: "kiện sản phẩm bị rách, yêu cầu đổi lại"
    # -> Service (yêu cầu đổi), Packing (kiện hàng bị rách)
    (0, 1, 0, 1),
    # 274: "lúc đặt thì thấy để hóa đơn trên 399k được tặng gấu bông nhưng lại không thấy. chỉ giao tã"
    # -> Service (không nhận được quà tặng như cam kết)
    (0, 1, 0, 0),
    # 275: "rất thất vọng khi nhận được sản phẩm bị rách như hình. liệu sản phẩm có được đảm bảo chất lượng khi chuyển đến tay khách đã rách to đùng như trên hay không?"
    # -> Quality (SP bị rách, lo chất lượng), Packing (SP rách khi giao)
    (1, 0, 0, 1),
    # 276: "đơn vị vận chuyển quá chán, rách luôn bao bì lòi cả tả bên trong"
    # -> Shipping (đơn vị vận chuyển tệ), Packing (bao bì rách)
    (0, 0, 1, 1),
    # 277: "giao sản phẩm quá lâu. chat với tổng đài báo đã hủy đơn rồi. vậy vẫn giao"
    # -> Service (tổng đài thông tin sai - báo hủy nhưng vẫn giao), Shipping (giao không theo đúng trạng thái)
    (0, 1, 1, 0),
    # 278: "mua nhưng chưa nhận được sản phẩm đến tay thì đánh giá kiểu gì"
    # -> Shipping (chưa nhận được hàng)
    (0, 0, 1, 0),
    # 279: "giao nhận tốt nhưng không biết xem ngày sản xuất bịch tã ở đâu"
    # -> Quality (không rõ ngày sản xuất - thiếu thông tin SP), Shipping (+)
    (1, 0, 1, 0),
    # 280: "quá tệ cho sản phẩm giả này"
    # -> Quality (hàng giả)
    (1, 0, 0, 0),
    # 281: "giao sản phẩm hơi lâu, đóng gói cẩn thận"
    # -> Shipping (hơi lâu), Packing (+)
    (0, 0, 1, 1),
    # 282: "không tặng quà khuyến mãi cho khách sản phẩm, quá tệ"
    # -> Service (không tặng quà như cam kết)
    (0, 1, 0, 0),
    # 283: "lúc mua 2 gói thấy tặng gấu nhưng giao sản phẩm không thấy tặng"
    # -> Service (không nhận được quà tặng)
    (0, 1, 0, 0),
    # 284: "gói sản phẩm không cẩn thận..."
    # -> Packing (đóng gói không cẩn thận)
    (0, 0, 0, 1),
    # 285: "giao đúng 1 tháng mới nhận được"
    # -> Shipping (giao cực kỳ chậm - 1 tháng)
    (0, 0, 1, 0),
    # 286: "bỉm thì giá cao nhưng dùng cho bé trai thì lúc nào cũng 1 bỉm đầy ở đằng trước nhưng phần mông thì không reng. đêm nào cũng phải thay bỉm"
    # -> Quality (bỉm không phù hợp cho bé trai, thiết kế không đúng), Service (giá cao)
    (1, 1, 0, 0),
    # 287: "khi mở nắp ra nhưng phần răng cưa không dính lại phần chai mà dính theo phần nắp luôn, vậy sao biết được chai đã bị khui hay chưa? đơn sản phẩm thì tiki giao rất nhanh, đóng gói cẩn thận"
    # -> Quality (nghi ngờ chai đã bị khui - hàng giả?), Shipping (+), Packing (+)
    (1, 0, 1, 1),
    # 288: "thất vọng quá! nước giặt kỳ này lỏng quá, mùi cũng không thơm lâu và dai... cứ thấy giống sản phẩm nháy hay sao"
    # -> Quality (nước giặt loãng, mùi kém, nghi hàng nhái)
    (1, 0, 0, 0),
    # 289: "chưa dùng nên chưa thể đánh giá về chất lượng, cho 3 là vì nắp sản phẩm đã bị mở, không nguyên đai nguyên kiện. không biết là xà phòng bên trong có bị tráo đổi hay rút bớt không"
    # -> Quality (nghi bị tráo/rút bớt), Packing (nắp đã bị mở, không nguyên kiện)
    (1, 0, 0, 1),
    # 290: "tôi đặt đơn 2 chai nước xả và 1 chai nước giặt... 3 chai xếp trong hộp không có xốp hay bất kỳ đồ gì để lót, hộp carton bị rách hết. chai nước giặt nhãn bị rách, cũ, dán giấy chằng chịt. nước xả thì không có tem phụ"
    # -> Quality (nhãn rách, không có tem phụ - nghi giả), Packing (không lót, hộp rách)
    (1, 0, 0, 1),
    # 291: "đây là lần thứ 2 mình nhận được sản phẩm lỗi như này rồi. tem nhãn bong tróc, dính dơ... yêu cầu đổi sản phẩm khác"
    # -> Quality (SP lỗi, tem nhãn bong tróc, dơ), Service (yêu cầu đổi)
    (1, 1, 0, 0),
    # 292: "sản phẩm giờ rất loãng chứ không sánh như trước"
    # -> Quality (chất lượng SP thay đổi - loãng hơn)
    (1, 0, 0, 0),
    # 293: "nhận được nước giặt gói cẩn thận nhưng dung tích trong bình không đúng thực tế, mở nắp ra nhìn vào thử hụt cả khúc"
    # -> Quality (dung tích không đúng - bị rút bớt?)
    (1, 0, 0, 0),
    # 294: "mình mua bình đầu giao ngày 4/6... ngày 18/6 mẹ mình giặt đồ thấy nước giặt lợn cợn trắng như bị pha... quét mã thì thấy dẫn đến link của dnee thailand... bình sau cũng bị y như vậy"
    # -> Quality (nước giặt bị pha/lỗi, mã không đúng nguồn gốc)
    (1, 0, 0, 0),
    # 295: "mua 1 chai... xài tốt... mới mua chai thứ 2 cùng tiki trading nhưng bọt xuất hiện nhiều, nước màu ngả vàng, không trắng"
    # -> Quality (chai mới chất lượng thay đổi - nước vàng, nhiều bọt)
    (1, 0, 0, 0),
    # 296: "sản phẩm giao đến xộc xệch, đóng gói không kỹ dẫn đến đổ hết ra ngoài, bao bì rách mướp. tiki tính thêm phí giao sản phẩm cồng kềnh nhưng dịch vụ thì tệ"
    # -> Service (tính phí cao nhưng dịch vụ tệ), Packing (đóng gói không kỹ, bao bì rách, đổ ra ngoài)
    (0, 1, 0, 1),
    # 297: "giao thiếu, đặt và thanh toán 2 nhưng chỉ nhận 1"
    # -> Shipping (giao thiếu)
    (0, 0, 1, 0),
    # 298: "đặt mua 2 can 4L nhưng giao 1 can. nhờ cửa hàng kiểm tra lại nhưng chưa thấy phản hồi"
    # -> Service (không phản hồi), Shipping (giao thiếu)
    (0, 1, 1, 0),
    # 299: "sản phẩm để trong thùng cartoon không có lót chèn, bên ngoài bám bụi bẩn. đóng sản phẩm dồn 4 can vào 1 thùng chồng lên nhau khiến can bị hơi móp"
    # -> Packing (không lót chèn, bẩn, can bị móp do đóng gói kém)
    (0, 0, 0, 1),
    # 300: "dạo này bộ phận giao sản phẩm tiki lạ quá, giao thiếu, giao sai tùm lum... đặt nước giặt này đem giao nước giặt khác"
    # -> Shipping (giao thiếu, giao sai lặp đi lặp lại)
    (0, 0, 1, 0),
    # 301: "giao sản phẩm quá chậm, hủy đơn thì đem tới liền nhưng không phản hồi, đồ móp méo"
    # -> Service (không phản hồi), Shipping (giao chậm), Packing (đồ bị móp)
    (0, 1, 1, 1),
    # 302: "tôi mua 1 chai tháng 9 và 1 chai ngày 13/12 cùng tiki trading... tại sao màu dung dịch lại nhạt hơn nhiều? giặt đồ phơi xong có mùi tanh rất lạ"
    # -> Quality (màu nhạt, mùi tanh lạ - nghi chất lượng thay đổi)
    (1, 0, 0, 0),
    # 303: "xài loại này cho con từ lúc con chưa ra đời, chuộng vì thơm nhẹ, giặt tốt... đợt này mua 3 chai có giới thiệu bạn mua nữa. nhưng lại trúng mấy thùng bị pha thêm nước vào"
    # -> Quality (nước giặt bị pha - loãng, mùi thơm kém)
    (1, 0, 0, 0),
    # 304: "sản phẩm nhìn vô là không muốn sử dụng. tem nhãn rách, mất chữ, bình thì nhìn dơ không chấp nhận được"
    # -> Quality (SP trông bẩn, tem rách, mất chữ)
    (1, 0, 0, 0),
    # 305: "mình order chai nước giặt dnee xanh dương, tiki giao nhầm thành nước xả vải. hôm nay mang ra sử dụng mới phát hiện ra. nhờ tiki hỗ trợ đổi sản phẩm"
    # -> Service (yêu cầu hỗ trợ đổi), Shipping (giao nhầm SP)
    (0, 1, 1, 0),
    # 306: "nhãn mác không có hsd cũng không có, rách rưới như đồ phế liệu vậy nhưng cũng bán trên 200k. sản phẩm cho em bé nhưng tệ hết sức tệ"
    # -> Quality (nhãn mác kém, không có HSD, trông như đồ cũ)
    (1, 0, 0, 0),
    # 307: "shipper không biết đường gọi hỏi, nghe chỉ đã kêu khó kiếm... nặng nhẹ người nhận giùm. sản phẩm chưa dùng nhưng nhận sản phẩm thấy trầy trật rồi"
    # -> Shipping (shipper thái độ kém, không biết đường)
    (0, 0, 1, 0),
    # 308: "chất lượng tốt shipper giao sản phẩm vui vẻ"
    # -> Quality (+), Shipping (+)
    (1, 0, 1, 0),
    # 309: "sản phẩm dùng tốt!"
    # -> Quality (+)
    (1, 0, 0, 0),
    # 310: "nhìn hình nắp trong nhưng giao sản phẩm về là nắp đục"
    # -> Shipping (giao sai mẫu - nắp khác hình)
    (0, 0, 1, 0),
    # 311: "mình mua 2 chai nước giặt và 1 chai dung dịch rửa bình nhưng giao chỉ có 1 chai nước giặt và 1 chai dung dịch rửa bình. gọi điện nhưng chưa được phản hồi"
    # -> Service (chưa phản hồi), Shipping (giao thiếu)
    (0, 1, 1, 0),
    # 312: "tiki bán sản phẩm cho trẻ em, tuy nhiên khi giao sản phẩm nước giặt này lại không có nhãn mác, vỏ bề ngoài không có dính logo thương hiệu"
    # -> Quality (không có nhãn mác, không có logo - nghi hàng giả)
    (1, 0, 0, 0),
    # 313: "đóng gói kỹ. nhưng nước giặt có màu nhạt, lỏng, không đậm đặc và mùi không thơm như chai mình mua ở con cưng"
    # -> Quality (màu nhạt, loãng, mùi kém - chất lượng thay đổi), Packing (+)
    (1, 0, 0, 1),
    # 314: "tiki giao sản phẩm nhanh, đóng gói cẩn thận. mình đặt bình xanh... sản phẩm không như mong đợi, chai màu xanh mùi không dễ chịu, giặt quần áo nhưng tay mình khô ráp, quần áo giặt xong không có mùi"
    # -> Quality (mùi khó chịu, làm khô tay, không thơm sau giặt), Shipping (+), Packing (+)
    (1, 0, 1, 1),
    # 315: "lần đầu mua ở cửa hàng này mà quá thất vọng sản phẩm không có một chút bọt nào. ya như sản phẩm nhái vậy. đã mua nhiều cửa hàng xài cửa hàng nào cũng bọt nhiều và thơm lắm luôn"
    # -> Quality (không có bọt, nghi hàng nhái)
    (1, 0, 0, 0),
    # 316: "mình mua 1 bình nước giặt 1 bình nước xả, vậy nhưng giao 2 lần đều là nước xả hết"
    # -> Shipping (giao sai SP - 2 lần liên tiếp)
    (0, 0, 1, 0),
    # 317: "giao sản phẩm bị chảy nước giặt nắp bị bể nước giặt rỉ chảy nhiều, tiki đổi sản phẩm cho mình nhé"
    # -> Service (yêu cầu đổi), Packing (nắp bị bể, nước giặt chảy ra)
    (0, 1, 0, 1),
    # 318: "giao sản phẩm lâu, sản phẩm bị móp. giá bán cũng cao hơn ở shopee"
    # -> Service (giá cao), Shipping (giao chậm), Packing (SP bị móp)
    (0, 1, 1, 1),
    # 319: "sản phẩm bị rỉ sét nhẹ ở viền mép hộp, hạn sử dụng chỉ 6 tháng. tuy nhiên không có mã qr để kiểm tra chính hãng. đã gọi lên tổng đài tới giờ vẫn chưa thấy phản hồi"
    # -> Quality (hộp rỉ sét, không có mã QR - nghi giả), Service (tổng đài không phản hồi)
    (1, 1, 0, 0),
    # 320: "rõ ràng là tôi đặt mùi hương chocolate... biết hết sản phẩm vẫn cố giao hương vani... tôi gọi đề nghị đổi... tiki liên tục đổ lỗi cho bên phía sữa anmum... đến 1 cuộc gọi lấy sản phẩm lại không có. ngày tôi đặt mua sữa là 14/11/2018... vẫn không chịu đổi sản phẩm và cũng không chịu hoàn tiền"
    # -> Service (không đổi, không hoàn tiền, đổ lỗi), Shipping (giao sai hương vị)
    (0, 1, 1, 0),
    # 321: "tốt đóng gói tốt, giao hơi lâu tí"
    # -> Shipping (hơi lâu), Packing (+)
    (0, 0, 1, 1),
    # 322: "mình đặt sản phẩm là hương chocolate nhưng giao là hương vani, trong khi đó hóa đơn in ra vẫn là hương chocolate. lần đầu mua sản phẩm của tiki nhưng thất vọng quá"
    # -> Shipping (giao sai hương vị)
    (0, 0, 1, 0),
    # 323: "sao sản phẩm mình check mã vạch không ra vậy? khi pha có hiện tượng vón cục. hoang mang quá"
    # -> Quality (mã vạch không ra - nghi giả, vón cục khi pha)
    (1, 0, 0, 0),
    # 324: "không giống sữa tươi, mùi vị như bột đậu thông thường"
    # -> Quality (chất lượng sữa không như kỳ vọng)
    (1, 0, 0, 0),
    # 325: "tôi cảm thấy bị lừa khá là thất vọng... combo note rõ tặng ấm đun siêu tốc nhưng khi mẹ tôi nhận sản phẩm thấy chỉ là một cái bình nhựa như hình... tôi không biết có sai sót ở khâu đóng sản phẩm/shipper hay có gì ở đây nên đề nghị tiki làm rõ"
    # -> Service (quà tặng không đúng như mô tả, yêu cầu làm rõ)
    (0, 1, 0, 0),
    # 326: "vui lòng đổi lại 2 hộp ensure gold, sản phẩm đặt chiều qua, trưa nay giao nhưng tình trạng bung nắp, đổ sữa tùm lum"
    # -> Service (yêu cầu đổi), Packing (bung nắp, đổ sữa)
    (0, 1, 0, 1),
    # 327: "sản phẩm ghi sữa ít ngọt nhưng sản phẩm nhận về tay lại là sữa ngọt... giao sản phẩm cực kỳ thô sơ. mua hơn 1 triệu, tiền giao sản phẩm gần 50 ngàn nhưng gói sản phẩm cực kỳ thô sơ"
    # -> Service (phí giao cao nhưng đóng gói thô sơ), Shipping (giao sai loại sữa), Packing (đóng gói thô sơ)
    (0, 1, 1, 1),
    # 328: "chán tiki, 2 lần mua gần nhất đều bị bục sản phẩm. không hiểu đóng gói kiểu gì hay cố tình cho sản phẩm bị bục đi nữa"
    # -> Packing (sản phẩm bị bục 2 lần liên tiếp - đóng gói tệ)
    (0, 0, 0, 1),
    # 329: "mình mua sữa này cho mẹ dùng, nhưng khi mở ra thì sữa bị hư hỏng, tràn hết ra ngoài, mình đã liên hệ với tiki... 3 lần điện thoại lên chăm sóc khách hàng của tiki nhưng chưa nhận được phản hồi. chắc giờ sữa đã mốc xanh"
    # -> Quality (sữa hư hỏng, tràn), Service (CSKH không phản hồi sau nhiều lần liên hệ), Packing (bị tràn/hư)
    (1, 1, 0, 1),
    # 330: "rất khó chịu về dịch vụ chăm sóc khách hàng của hãng này, rất làm phiền khách hàng, chán lắm luôn"
    # -> Service (CSKH kém, làm phiền)
    (0, 1, 0, 0),
    # 331: "mình mua để tặng người thân! mọi lần cũng mua không bị trường hợp này, lần này dù date xa nhưng vỏ hộp thế này... yêu cầu tiki đổi hộp mới cho mình thì không thấy tăm hơi"
    # -> Quality (vỏ hộp cũ/mốc dù date xa), Service (yêu cầu đổi không được phản hồi)
    (1, 1, 0, 0),
    # 332: "đơn hàng của mình: hộp bị móp, nắp bị hở, sữa đổ vương ra ngoài... seal đã bị bung, sữa dính bết ra xung quanh thành hộp"
    # -> Packing (hộp móp, nắp hở, seal bung, sữa đổ ra)
    (0, 0, 0, 1),
    # 333: "cửa hàng có cách nào để check sữa là sản phẩm chuẩn không, mình mở sữa mua nó không thơm như trước đây mua"
    # -> Quality (nghi ngờ SP chuẩn, mùi thay đổi)
    (1, 0, 0, 0),
    # 334: "không như mô tả, sản phẩm tệ"
    # -> Quality (SP không như mô tả, tệ)
    (1, 0, 0, 0),
    # 335: "giao trễ hơn cả tháng... lần nào mở ra sữa cũng đổ ra ngoài. cho tôi biết phải đổi lại sản phẩm này ntn?"
    # -> Service (yêu cầu đổi trả), Shipping (giao trễ cả tháng), Packing (sữa đổ ra ngoài - bao bì/hộp bị hở)
    (0, 1, 1, 1),
    # 336: "mình mua 2 lớn vinamilk và 1 ensure lớn. giao sản phẩm trễ đã vậy lúc nhận sản phẩm thì sữa bị bể, sữa đổ ra ngoài"
    # -> Shipping (giao trễ), Packing (sữa bể, đổ ra)
    (0, 0, 1, 1),
    # 337: "đặt sản phẩm và bị hủy đơn do hết sản phẩm"
    # -> Service (hủy đơn do hết hàng - trải nghiệm mua sắm kém)
    (0, 1, 0, 0),
    # 338: "sản phẩm tới tay là gói rách tứ tung, không biết trong quá trình vận chuyển quăng nhòi nhéc, ném lung tung hay sao. sản phẩm người ta mua nhưng không tôn trọng gì cả"
    # -> Shipping (vận chuyển ẩu), Packing (gói rách)
    (0, 0, 1, 1),
    # 339: "mình không nhận được ly quà tặng. hôm 11/11 ghi rõ là tặng 2 ly. nên mình đặt luôn 2 hộp. giao sản phẩm thì chẳng có quà tặng gì hết"
    # -> Service (không nhận được quà tặng như quảng cáo)
    (0, 1, 0, 0),
    # 340: "sản phẩm giao về vỡ hết nhưng không chịu xử lý"
    # -> Service (không xử lý), Packing (SP vỡ hết)
    (0, 1, 0, 1),
    # 341: "sản phẩm nguyên seal, nhưng mua ensure gold hương lúa mạch ít ngọt nhưng giao cho ensure gold hương lúa mạch (ngọt)"
    # -> Shipping (giao sai loại)
    (0, 0, 1, 0),
    # 342: "sản phẩm bị bung nắp thiếc. bột đổ ra ngoài 1/3 hộp sữa. hộp để nghiêng khi giao. hộp bị móp méo phần nắp đậy. giao sản phẩm đã không chú ý dù trên hộp dán cẩn thận"
    # -> Shipping (giao không cẩn thận - để nghiêng), Packing (bung nắp, đổ sữa, hộp móp)
    (0, 0, 1, 1),
    # 343: "sản phẩm giao bị móp quá tệ"
    # -> Packing (SP bị móp)
    (0, 0, 0, 1),
    # 344: "mình đánh giá 3 sao vì giao không đúng sản phẩm, mua sữa lúa mạch ít ngọt nhưng lại giao sữa lúa mạch ngọt"
    # -> Shipping (giao sai SP)
    (0, 0, 1, 0),
    # 345: "giao sản phẩm rất lâu nhân viên tư vấn rất dập khuôn"
    # -> Service (tư vấn kém), Shipping (giao chậm)
    (0, 1, 1, 0),
    # 346: "mình đặt mua sữa ít đường cho mẹ, nhưng trên hộp không có chữ ít đường"
    # -> Shipping (giao sai loại)
    (0, 0, 1, 0),
    # 347: "hộp giao tới rất bẩn và rách hết giấy dán, đã thấy có một số comment nhưng mình nghĩ tiki đã khắc phục nên vẫn đặt, không ngờ vẫn bị như vậy"
    # -> Packing (hộp bẩn, rách giấy dán)
    (0, 0, 0, 1),
    # 348: "giao sản phẩm chậm, phục vụ kém"
    # -> Service (phục vụ kém), Shipping (giao chậm)
    (0, 1, 1, 0),
    # 349: "không có bọc chống sốc, không có ni lông bao bên ngoài hộp sữa, lần này tiki đóng gói quá ẩu tả"
    # -> Packing (không có chống sốc, không bọc nilon, đóng gói ẩu)
    (0, 0, 0, 1),
    # 350: "mua ít ngọt mà giao sữa ngọt. tiền trả rồi cho người giao sản phẩm"
    # -> Shipping (giao sai loại)
    (0, 0, 1, 0),
    # 351: "đây là loại lúa mạch ngọt chứ không phải ít ngọt như mô tả"
    # -> Shipping (giao sai loại - ngọt thay vì ít ngọt)
    (0, 0, 1, 0),
    # 352: "đặt ít ngọt nhưng gửi sản phẩm về thì lại là sữa ngọt?"
    # -> Shipping (giao sai loại)
    (0, 0, 1, 0),
    # 353: "chất lượng tốt. nhưng shipper thì tiki bắt giao sản phẩm của xanh sm..."
    # -> Quality (+), Shipping (shipper do đơn vị khác giao - vấn đề về quy trình)
    (1, 0, 1, 0),
    # 354: "đặt mua loại 2,2kg, đã thanh toán 1 triệu 61 ngàn đồng. giao hộp 400gram nhưng ở ngoài kiện dám ghi là 2,3kg. đã vậy giao sản phẩm trễ 4 ngày"
    # -> Service (gian lận - ghi sai trọng lượng), Shipping (giao sai trọng lượng, trễ)
    (0, 1, 1, 0),
    # 355: "đã nhận được sản phẩm, sản phẩm đóng nguyên hộp có bốn túi ở trong... tuy nhiên tiki lại chuyển sản phẩm từ thành phố hcm ra khiến sản phẩm đến trễ mất 3 ngày nhưng không hề có thông báo gì"
    # -> Service (không thông báo), Shipping (giao trễ, không thông báo lý do)
    (0, 1, 1, 0),
    # 356: "hộp bị móp méo, không hài lòng giao sản phẩm lâu không hài lòng với sữa lần này, thất vọng"
    # -> Shipping (giao lâu), Packing (hộp móp méo)
    (0, 0, 1, 1),
    # 357: "giao đúng hạn, đóng gói sơ sài"
    # -> Shipping (+), Packing (đóng gói sơ sài)
    (0, 0, 1, 1),
    # 358: "đóng gói quá tệ. giao sản phẩm chậm"
    # -> Shipping (giao chậm), Packing (đóng gói tệ)
    (0, 0, 1, 1),
    # 359: "rất hài lòng"
    # -> (hài lòng chung, không cụ thể khía cạnh nào)
    (0, 0, 0, 0),
    # 360: "sản phẩm chất lượng tốt. giao nhanh"
    # -> Quality (+), Shipping (+)
    (1, 0, 1, 0),
    # 361: "đóng sản phẩm cẩu thả. móp méo và rách hộp"
    # -> Packing (cẩu thả, hộp móp, rách)
    (0, 0, 0, 1),
    # 362: "thùng sản phẩm bị rách, cũ, không nguyên vẹn"
    # -> Packing (thùng rách, cũ)
    (0, 0, 0, 1),
    # 363: "giao không đúng sản phẩm. không hài lòng"
    # -> Shipping (giao sai SP)
    (0, 0, 1, 0),
    # 364: "tôi mua sữa cho cháu, do đặt nhầm loại sữa cần mua số 1 nhưng đặt loại số 2, tôi liên hệ tổng đài để đổi, nhưng nv trả lời không áp dụng đổi sản phẩm. dv tiki quá tệ"
    # -> Service (không hỗ trợ đổi sản phẩm, dịch vụ tệ)
    (0, 1, 0, 0),
    # 365: "giao sản phẩm quá lâu, phản hồi đơn hàng chậm. đóng gói cẩn thận, sản phẩm đúng mô tả"
    # -> Service (phản hồi chậm), Shipping (giao chậm), Packing (+)
    (0, 1, 1, 1),
    # 366: "12 có 1 móp nặng nhé cửa hàng"
    # -> Packing (1/12 hộp bị móp nặng)
    (0, 0, 0, 1),
    # 367: "hộp sữa được giao không giống hình trên, nắp hộp mở được liền, không phải kiểu có mối mở"
    # -> Quality (SP khác hình - nắp hộp khác), Shipping (giao sai mẫu)
    (1, 0, 1, 0),
    # 368: "cửa hàng ơi mình đặt nhầm sữa không đường vậy có đổi lại được không"
    # -> Service (yêu cầu đổi sản phẩm)
    (0, 1, 0, 0),
    # 369: "hộp móp méo đủ đường. có 1 hộp bung luôn cả nắp"
    # -> Packing (hộp móp đủ đường, bung nắp)
    (0, 0, 0, 1),
    # 370: "giao sản phẩm quá chậm sau cả thời gian dự kiến"
    # -> Shipping (giao chậm hơn dự kiến)
    (0, 0, 1, 0),
    # 371: "đặt sản phẩm ngày 10/10 lúc 13h nhưng không gửi kèm quà là sữa tắm và hộp sữa. đừng ai bị gạt giống tôi nhé"
    # -> Service (không giao quà tặng kèm như cam kết - gạt người mua)
    (0, 1, 0, 0),
    # 372: "sữa thơm ngon, nhưng ngày sản xuất từ tháng 10/2022"
    # -> Quality (+, thơm ngon; nhưng date xa - sản xuất lâu)
    (1, 0, 0, 0),
    # 373: "check được mã nhưng hộp sữa trầy xước và nhìn như cũ"
    # -> Quality (hộp trầy xước, nhìn cũ dù hàng chính hãng)
    (1, 0, 0, 0),
    # 374: "giao sản phẩm không đúng hẹn. chậm"
    # -> Shipping (giao không đúng hẹn, chậm)
    (0, 0, 1, 0),
    # 375: "đóng hộp quá tệ. lần đầu mình mua bên này. đóng gói quá sơ sài. hộp bị bóp méo hết"
    # -> Packing (đóng gói tệ, sơ sài, hộp móp)
    (0, 0, 0, 1),
    # 376: "sản phẩm chính hãng check qr đúng. nhưng gói sản phẩm rất sơ sài. chỉ quấn 1 lớp màng co khiến hộp bị móp bung đáy"
    # -> Quality (+), Packing (đóng gói sơ sài, hộp móp bung đáy)
    (1, 0, 0, 1),
    # 377: "đóng gói không chắc chắn, vận chuyển bị móp méo"
    # -> Packing (đóng gói không chắc), Shipping (vận chuyển gây móp)
    (0, 0, 1, 1),
    # 378: "đóng gói ẩu. mua của tiki nhiều rồi nhưng lần đầu tiên bị vậy luôn"
    # -> Packing (đóng gói ẩu)
    (0, 0, 0, 1),
    # 379: "sản phẩm giao chậm, hộp sữa bị móp"
    # -> Shipping (giao chậm), Packing (hộp sữa bị móp)
    (0, 0, 1, 1),
    # 380: "sản phẩm dễ vỡ mà tiki bọc mỗi 1 lớp nylon, sản phẩm giao vỏ bị móp méo hết!"
    # -> Packing (đóng gói không đủ cho SP dễ vỡ, vỏ móp)
    (0, 0, 0, 1),
    # 381: "đóng gói cẩn thận, giao hàng nhanh"
    # -> Shipping (+), Packing (+)
    (0, 0, 1, 1),
    # 382: "đạm a2 nên vị hơi nhận kiểu đậu nành, có độ ngậy nên bé nhà mình không thích. khó nhất là 4 muỗng pha vs 188ml nước"
    # -> Quality (vị đặc thù của SP, bé không thích, hướng dẫn pha phức tạp)
    (1, 0, 0, 0),
    # 383: "sản phẩm mình mới vừa mua hôm qua. sao chất lượng sản phẩm không như mình mua ở cửa hàng. mùi vị của sữa mặn không có ngọt thanh và con mình cũng không uống được"
    # -> Quality (chất lượng thay đổi so với mua tại shop, mùi vị sai)
    (1, 0, 0, 0),
    # 384: "chất lượng tốt, nhưng tiki rất hay hết sản phẩm"
    # -> Quality (+), Service (thường xuyên hết hàng)
    (1, 1, 0, 0),
    # 385: "giao sản phẩm quá lâu đóng gói sản phẩm không cẩn thận"
    # -> Shipping (giao chậm), Packing (đóng gói không cẩn thận)
    (0, 0, 1, 1),
    # 386: "đóng gói nhưng không gói chống sốc cho hộp sữa!"
    # -> Packing (không có chống sốc)
    (0, 0, 0, 1),
    # 387: "sản phẩm vận chuyển bị móp 1 hộp"
    # -> Shipping (vận chuyển gây móp), Packing (1 hộp bị móp)
    (0, 0, 1, 1),
    # 388: "đánh giá không tính điểm tiki kiểm tra lại khâu giao sản phẩm đóng sản phẩm, nhận sản phẩm khui ra thì bị như vầy"
    # -> Packing (đóng gói có vấn đề, SP bị hư khi mở)
    (0, 0, 0, 1),
    # 389: "sữa có vấn đề. bột sữa vón cục. nước pha sữa lấy từ bình nước giữ nhiệt nhưng nó vón cục không tan nổi. bé uống xong đi ngoài mấy hôm liền"
    # -> Quality (sữa vón cục, gây đi ngoài - chất lượng nghiêm trọng)
    (1, 0, 0, 0),
    # 390: "sản phẩm giao đúng hẹn, thái độ nhân viên giao sản phẩm chưa linh hoạt. tôi chưa kiểm tra sản phẩm"
    # -> Shipping (đúng hẹn +; thái độ chưa linh hoạt)
    (0, 0, 1, 0),
    # 391: "lớp bọc chống vỡ nằm 1 nơi, hộp sữa 1 nơi, nắp nhựa bị bể, pha mùi vị không thơm ngon như hộp nhà sẵn có, bị cặn"
    # -> Quality (mùi vị thay đổi, bị cặn), Packing (lớp bọc tách rời, nắp bể)
    (1, 0, 0, 1),
    # 392: "tại sao tôi check mã vạch của sản phẩm này lại không được? tiki trading trả lời giúp tôi? hoặc tiki trading bán sản phẩm giả? liên hệ ngay để xử lý và hoàn tiền"
    # -> Quality (nghi hàng giả - không check được mã vạch), Service (yêu cầu hoàn tiền)
    (1, 1, 0, 0),
    # 393: "thái độ nhân viên giao sản phẩm... tự ý hoàn đơn khi khách hẹn ngày khác... không hề gọi cho khách nhưng dám cập nhật trạng thái giao không thành công... tiki xử lý khiếu nại quá kém, thất hứa lỡ hẹn. hẹn 48 tiếng gọi lại phản hồi nhưng không..."
    # -> Service (xử lý khiếu nại kém, thất hứa), Shipping (shipper tự ý hủy đơn, không gọi khách)
    (0, 1, 1, 0),
    # 394: "giao sản phẩm chậm, không đúng hẹn"
    # -> Shipping (giao chậm, không đúng hẹn)
    (0, 0, 1, 0),
    # 395: "đăng bài mua sữa tặng gấu khủng long nhưng chẳng thấy quà. gạt nhau thôi"
    # -> Service (không nhận được quà tặng như quảng cáo)
    (0, 1, 0, 0),
    # 396: "hình thì để b/a nhưng sản phẩm thì không có"
    # -> Quality (SP không đúng với hình ảnh - giao sai/thiếu)
    (1, 0, 0, 0),
    # 397: "cái này mình vẫn chưa nhận được sản phẩm nhưng sao nhân viên tiki tự ý vào ghi giao thành công vậy? không phải một, lần này là lần thứ 2 rồi"
    # -> Shipping (shipper gian lận - xác nhận giao khi chưa giao, lặp lại nhiều lần)
    (0, 0, 1, 0),
    # 398: "giao hai hộp sữa có đóng gói khác nhau, không biết có fake không"
    # -> Quality (nghi hàng giả - đóng gói khác nhau)
    (1, 0, 0, 0),
    # 399: "lần đầu tiên nhận sản phẩm nhưng vô cùng thất vọng vì nhận được y như ảnh chụp. đặt sữa về quê cho con vì giãn cách, không biết hộp như vậy liệu sữa có đúng hãng không"
    # -> Quality (nghi ngờ hàng kém/không đúng hãng)
    (1, 0, 0, 0),
    # 400: "tiki dối khách sản phẩm, mua sản phẩm xong không hoàn astra"
    # -> Service (không hoàn điểm astra - gian lận)
    (0, 1, 0, 0),
    # 401: "tiki không hoàn astra theo hạng thành viên của khách sản phẩm"
    # -> Service (không hoàn điểm đúng hạng)
    (0, 1, 0, 0),
    # 402: "giao sữa bị cấn móp, nhìn hộp sữa phát chán"
    # -> Packing (hộp sữa bị cấn móp)
    (0, 0, 0, 1),
    # 403: "giao sản phẩm móp cần đổi lại"
    # -> Service (yêu cầu đổi), Packing (SP bị móp)
    (0, 1, 0, 1),
    # 404: "thông tin có để là tặng kèm khủng long bông nhưng khi giao sản phẩm lại không có"
    # -> Service (không tặng quà kèm như cam kết)
    (0, 1, 0, 0),
    # 405: "đặt gần 2 tháng mới thấy giao, quá lâu luôn, định không nhận luôn, nhưng nghĩ lại thấy tội shipper"
    # -> Shipping (giao cực kỳ chậm - gần 2 tháng)
    (0, 0, 1, 0),
    # 406: "giao sản phẩm sớm. tuy nhiên, tiki không đóng gói hộp sữa cẩn thận, sản phẩm nhận được móp méo!"
    # -> Shipping (+, giao sớm), Packing (đóng gói không cẩn thận, hộp móp)
    (0, 0, 1, 1),
    # 407: "không có quà nhưng giá bán hơi mắc"
    # -> Service (không có quà, giá mắc)
    (0, 1, 0, 0),
    # 408: "đặt sản phẩm màu vàng nhưng lại giao màu xanh, mỏng hơn"
    # -> Quality (giao sai màu và mỏng hơn - chất lượng kém hơn), Shipping (giao sai màu)
    (1, 0, 1, 0),
    # 409: "tiki đăng mua 1 combo tặng 1 bịch, tôi mua 2 combo không tặng bịch nào là sao? mọi người mua thì xem kỹ nha, nhà bán đăng cho vui thôi"
    # -> Service (không tặng quà như cam kết - thông tin sai)
    (0, 1, 0, 0),
    # 410: "sao mình chọn mua đơn hơn 800k nhưng không được tặng gói chườm nóng"
    # -> Service (không nhận được quà tặng như cam kết)
    (0, 1, 0, 0),
    # 411: "chất lượng tốt, nhưng dv giao sản phẩm quá chậm. gần 2 tháng mới nhận sản phẩm, nhưng sản phẩm lại cần gấp!"
    # -> Quality (+), Shipping (giao cực kỳ chậm - gần 2 tháng)
    (1, 0, 1, 0),
    # 412: "mình order từ ngày 9/7 đến nay ngày 14/7 chưa nhận được sản phẩm!"
    # -> Shipping (giao chậm)
    (0, 0, 1, 0),
    # 413: "đã nhận được 2 đơn sản phẩm, nhưng giao thiếu 2 túi quà tặng"
    # -> Service (thiếu quà tặng)
    (0, 1, 0, 0),
    # 414: "chất lượng, giao sản phẩm nhanh"
    # -> Quality (+), Shipping (+)
    (1, 0, 1, 0),
    # 415: "check mã vạch thì ra sản phẩm khác, mới đổ bột sữa chưa khuấy thì nó đã tan. mã vạch thì râu ông nọ cắm cằm bà kia. bán sữa giả à. đề nghị trả sản phẩm"
    # -> Quality (hàng giả - mã vạch sai, sữa tan bất thường), Service (yêu cầu trả hàng)
    (1, 1, 0, 0),
    # 416: "tôi đã đề cho ba tôi trải nghiệm, tuy nhiên sản phẩm không chất lượng, dễ bị rách và bị rã khi có chút nước. chắc chắn tôi sẽ không mua sản phẩm này lần thứ 2"
    # -> Quality (SP dễ rách, kém chất lượng)
    (1, 0, 0, 0),
    # 417: "tã dỏm lắm không thấm nhưng mặc 1 lần bị hăm đỏ cả. đề nghị trả lại sản phẩm"
    # -> Quality (tã kém - không thấm, gây hăm), Service (yêu cầu trả hàng)
    (1, 1, 0, 0),
    # 418: "nhân viên giao sản phẩm best thái độ kém khách sản phẩm, hối thúc khách tra tiền, mặt bộ khách"
    # -> Shipping (shipper thái độ kém, hối thúc, mặt khó đăm đăm)
    (0, 0, 1, 0),
    # 419: "thấm hút kém như caryn. mặc dù có giá rẻ hơn chút"
    # -> Quality (thấm hút kém), Service (giá rẻ hơn)
    (1, 1, 0, 0),
    # 420: "giao sản phẩm chậm quá chậm phải liên hệ thúc mãi mới nhận được sản phẩm"
    # -> Shipping (giao cực kỳ chậm, phải thúc)
    (0, 0, 1, 0),
    # 421: "nhân viên giao sản phẩm best giao sản phẩm rất tệ, nói chuyện rất tệ"
    # -> Shipping (shipper giao tệ, thái độ tệ)
    (0, 0, 1, 0),
    # 422: "sao nhưng cái đáy cụt ngắn - miếng bông vải thì ngắn không biết là sản phẩm loại 2?"
    # -> Quality (SP có vấn đề về kích thước - nghi loại 2)
    (1, 0, 0, 0),
    # 423: "dùng cho người già thấm hút tạm ổn được"
    # -> Quality (tạm ổn)
    (1, 0, 0, 0),
    # 424: "giao sản phẩm rất rất lâu mọi người. sản phẩm bình thường như các đợt trước dùng"
    # -> Quality (+), Shipping (giao rất chậm)
    (1, 0, 1, 0),
    # 425: "chất lượng tốt, rất vừa ý, cảm ơn rất nhiều"
    # -> Quality (+)
    (1, 0, 0, 0),
    # 426: "đóng gói sản phẩm không cẩn thận"
    # -> Packing (đóng gói không cẩn thận)
    (0, 0, 0, 1),
    # 427: "tã sunmate so về kích thước thì nhỏ hơn hãng khác, và chất lượng chỉ mức tạm ổn được"
    # -> Quality (kích thước nhỏ hơn hãng khác, chất lượng tạm)
    (1, 0, 0, 0),
    # 428: "nằm thôi ngồi là ra ngoài"
    # -> Quality (tã không vừa khi ngồi - bị tràn)
    (1, 0, 0, 0),
    # 429: "bạn ơi size mình nhưng nhỏ xíu so với tã khác. mặc không vừa rồi có được đổi lại không bạn ơi"
    # -> Quality (size nhỏ, không vừa), Service (yêu cầu đổi)
    (1, 1, 0, 0),
    # 430: "tôi mua 3 túi tấm lót 8 túi tã dán caryn nhưng nhận 4 túi tấm lót và 7 túi tã dán. giao sản phẩm sai quy cách, đề nghị giải quyết khiếu nại này"
    # -> Service (yêu cầu giải quyết), Shipping (giao sai số lượng/quy cách)
    (0, 1, 1, 0),
    # 431: "cửa hàng lấy mất quà tặng kèm của sản phẩm, giá thì chỉ rẻ hơn giá gốc 5k. mình hỏi cả tuần lễ mới trả lời xong vấn đề, làm mất quyền lợi đổi trả sản phẩm với tiki!"
    # -> Service (quà tặng bị lấy mất, phản hồi chậm, mất quyền đổi trả)
    (0, 1, 0, 0),
    # 432: "mùa dịch không đi được phải mua tiki, nhưng tiki giao sản phẩm quá tệ! có món trễ cả tháng, 1,2,3 tuần phải hủy đơn luôn? vậy không biết tiki rao bán làm chi nữa?"
    # -> Shipping (giao cực kỳ chậm, phải hủy đơn)
    (0, 0, 1, 0),
    # 433: "bọc ni long trong suốt bên ngoài lúc nhận sản phẩm mình khá ngại, giao sản phẩm rất lâu mình chọn giao trong ngày nhưng mấy ngày sau không thấy tung tích gì"
    # -> Shipping (giao rất chậm, không như cam kết giao trong ngày), Packing (đóng gói sơ sài - chỉ bọc nilon)
    (0, 0, 1, 1),
    # 434: "5 bịch đệm lót chỉ có một là tương đối sạch nhưng 4 thì bao bì cũ, nhăn, dính băng keo và bụi bám rất mất vệ sinh. lần giao sản phẩm này rất tệ"
    # -> Quality (bao bì cũ, bẩn - SP không đảm bảo vệ sinh), Shipping (giao sản phẩm tệ)
    (1, 0, 1, 0),
    # 435: "đặt từ 23/7, tiki hiện ngày giao là 24/7 nhưng nay 29/7 mới giao. chat hỏi thì đưa con bot ra đổ cho bên giao sản phẩm nhanh"
    # -> Service (CSKH dùng bot, đổ lỗi), Shipping (giao trễ 5 ngày)
    (0, 1, 1, 0),
    # 436: "giao sản phẩm rất là lâu ai cần thì nên mua trước một tháng cho chắc ăn"
    # -> Shipping (giao rất chậm)
    (0, 0, 1, 0),
    # 437: "có nhận được sản phẩm đâu mà nhận xét. đặt sản phẩm lúc giãn cách. hết giãn cách tiki không giao sản phẩm"
    # -> Shipping (không giao hàng sau giãn cách)
    (0, 0, 1, 0),
    # 438: "rất tiện lợi cho người lớn tuổi. chi phí hợp lý cho mỗi lần sử dụng thấp. dai và thấm được nhiều nước"
    # -> Quality (+, tiện lợi, thấm tốt), Service (+, chi phí hợp lý)
    (1, 1, 0, 0),
    # 439: "giao sản phẩm qua lâu hơn 3 tháng dừng ra nếu không giao được trong phạm vi 1 tháng thì nên báo tự hủy đơn đi"
    # -> Shipping (giao cực kỳ chậm - hơn 3 tháng)
    (0, 0, 1, 0),
    # 440: "giao sản phẩm lâu so với ngày dự kiến, trải nghiệm mua sản phẩm quá tệ"
    # -> Shipping (giao chậm so với dự kiến)
    (0, 0, 1, 0),
    # 441: "quá tệ đặt 20 miếng giao 10 miếng đúng 7 bịch"
    # -> Shipping (giao thiếu - chỉ giao 10/20 miếng, 7 bịch)
    (0, 0, 1, 0),
    # 442: "giao sản phẩm quá lâu, đổ thừa do dịch bệnh, quá sợ"
    # -> Shipping (giao quá chậm)
    (0, 0, 1, 0),
    # 443: "tiki trading làm việc thế nào mà đặt 2 đơn sản phẩm cùng nhà cung cấp... giao có 1 không rõ khi nào giao nốt hay để cả tuần rồi báo hết sản phẩm"
    # -> Shipping (giao thiếu, không rõ tình trạng)
    (0, 0, 1, 0),
    # 444: "tôi chưa nhận được sản phẩm này"
    # -> Shipping (chưa nhận được hàng)
    (0, 0, 1, 0),
    # 445: "vẫn chưa nhận được sản phẩm, nhưng ghi chú là giao sản phẩm thành công"
    # -> Shipping (shipper gian lận xác nhận giao khi chưa giao)
    (0, 0, 1, 0),
    # 446: "chưa nhận được sản phẩm, nhưng vào tình trạng đơn hàng thấy đã giao sản phẩm thành công, gọi điện, nhắn tin báo với tiki 2 lần rồi nhưng đến nay đã 6 ngày vẫn chưa nhận được phản hồi gì hết"
    # -> Service (không phản hồi sau 6 ngày), Shipping (shipper xác nhận giao ảo)
    (0, 1, 1, 0),
    # 447: "khong có bình như đăng trong hình. mặc dù mua trên 1tr"
    # -> Service (không có quà/sản phẩm như quảng cáo)
    (0, 1, 0, 0),
    # 448: "mình nhận được sản phẩm thực tế là trên 40 tuổi nhưng trên hình của tiki là trên 51 tuổi"
    # -> Shipping (giao sai SP)
    (0, 0, 1, 0),
    # 449: "mình đặt anlene trên 51 tuổi nhưng giao trên 40 tuổi"
    # -> Shipping (giao sai SP)
    (0, 0, 1, 0),
    # 450: "đặt sản phẩm hôm 14/7 trạng thái ngày giao 16/7 đến nay 23/7 chưa thấy sản phẩm đâu hết"
    # -> Shipping (giao chậm - 7 ngày so với cam kết 2 ngày)
    (0, 0, 1, 0),
    # 451: "chai to, thơm nhẹ nhàng, đáng mua"
    # -> Quality (+)
    (1, 0, 0, 0),
    # 452: "đóng gói không được đảm bảo lắm, không có mút chống va đập. như vậy hộp sữa dễ móp"
    # -> Packing (không có chống va đập, hộp dễ móp)
    (0, 0, 0, 1),
    # 453: "mình pha sữa kiểu bị vón cục, uống bên trên thì lợ lợ nhạt nhạt, bên dưới thì đọng bột, cảm giác không phải sữa thật"
    # -> Quality (sữa vón cục, vị nhạt, nghi không phải sữa thật)
    (1, 0, 0, 0),
    # 454: "giao sản phẩm quá chậm so với dự kiến, đóng gói cẩn thận, giá hợp lý"
    # -> Service (+, giá), Shipping (giao chậm), Packing (+)
    (0, 1, 1, 1),
    # 455: "quà khuyến mãi không giống như quảng cáo"
    # -> Service (quà không đúng như quảng cáo)
    (0, 1, 0, 0),
    # 456: "mua ba hộp thì hai hộp bị móp. đề nghị tiki cho đổi"
    # -> Service (yêu cầu đổi), Packing (2/3 hộp bị móp)
    (0, 1, 0, 1),
    # 457: "chất lượng tốt nhưng quà tặng cái quạt mini cầm tay bật chạy chưa được 2 giây là tắt mất rồi thì tặng làm gì"
    # -> Quality (+, sản phẩm chính), Service (quà tặng bị hỏng - kém chất lượng)
    (1, 1, 0, 0),
    # 458: "cửa hàng ơi, vui lòng đổi giúp em thùng sữa có đường đi, cửa hàng giao không đường, bé nhà em không uống được. em sẽ bù thêm, mong cửa hàng hỗ trợ"
    # -> Service (yêu cầu đổi), Shipping (giao sai loại sữa - không đường thay vì có đường)
    (0, 1, 1, 0),
    # 459: "sản phẩm bình thường, shipper giao sản phẩm của tiki tên ngô trọng nghĩa giao sản phẩm thái độ, chửi nhau với khách. đề nghị tiki liên hệ khách và xử lý"
    # -> Service (yêu cầu xử lý), Shipping (shipper chửi bới khách hàng)
    (0, 1, 1, 0),
    # 460: "về chất liệu thấy khác hơn nhiều so với loại 18 miếng. mọi người cân nhắc khi mua sản phẩm này"
    # -> Quality (chất liệu khác biệt so với loại khác)
    (1, 0, 0, 0),
    # 461: "trong mỗi gói có vài miếng không chống thấm. giao sản phẩm nhanh"
    # -> Quality (một số miếng lỗi - không chống thấm), Shipping (+)
    (1, 0, 1, 0),
    # 462: "đánh giá không tính điểm bị méo quá, mọi lần mua không bị thế nhưng lần này méo quá"
    # -> Packing (hộp bị méo)
    (0, 0, 0, 1),
    # 463: "không mô tả rõ về quà tặng kèm. lúc nhận mới biết không có quà"
    # -> Service (mô tả không rõ về quà, không có quà)
    (0, 1, 0, 0),
    # 464: "tiki bán sản phẩm tào lao. khách sản phẩm mua nhầm nhưng không cho đổi đúng sản phẩm phù hợp để khách có thể sử dụng dù sản phẩm nguyên đai nguyên kiện... dịch vụ khách hàng 19006035 khuyên khách tự đăng sản phẩm bán lại trên mạng"
    # -> Service (CSKH tư vấn vô lý, không hỗ trợ đổi trả)
    (0, 1, 0, 0),
    # 465: "tiki đợt này giao sản phẩm đóng gói sơ sài móp méo sản phẩm"
    # -> Packing (đóng gói sơ sài, móp méo)
    (0, 0, 0, 1),
    # 466: "giao nhanh nhưng bị móp. lần nào mua cũng vậy"
    # -> Shipping (+), Packing (bị móp thường xuyên)
    (0, 0, 1, 1),
    # 467: "đóng gói ẩu giao toàn bị móp"
    # -> Packing (đóng gói ẩu, toàn bị móp)
    (0, 0, 0, 1),
    # 468: "đánh giá không tính điểm đóng gói không chặt giao tới hộp sữa xình không? dô tới sữa luôn. mong cửa hàng rep cmt em với giải quyết cho em"
    # -> Service (yêu cầu giải quyết), Packing (đóng gói không chặt, hộp thủng, sữa đổ ra)
    (0, 1, 0, 1),
    # 469: "mình mua theo chương trình khuyến mãi quảng cáo là mua 399k được tặng kệ chữ a. canh giờ đặt đầu giờ nhưng mua trên tiki thì không được tặng kệ và cũng không hiểu những ai được tặng"
    # -> Service (không nhận được quà khuyến mãi, thông tin mập mờ)
    (0, 1, 0, 0),
    # 470: "size bé hơn mình nghĩ rất nhiều. mình đặt size s nhưng bỉm về nhỏ hơn size nb của merries. đang muốn đổi size"
    # -> Quality (size không đúng như kỳ vọng/mô tả), Service (muốn đổi)
    (1, 1, 0, 0),
    # 471: "tại sao không được nhận quà khuyến mãi như đã chạy chương trình"
    # -> Service (không nhận được quà khuyến mãi)
    (0, 1, 0, 0),
    # 472: "không nhận được quà của chương trình"
    # -> Service (không nhận được quà)
    (0, 1, 0, 0),
    # 473: "tốt nhưng băng nhưng cấn đùi bé gây khó chịu"
    # -> Quality (băng dán cấn đùi, gây khó chịu)
    (1, 0, 0, 0),
    # 474: "thiếu quà tặng của tã dán"
    # -> Service (thiếu quà tặng kèm)
    (0, 1, 0, 0),
    # 475: "tại sao lại không nhận được quà"
    # -> Service (không nhận được quà)
    (0, 1, 0, 0),
    # 476: "tiki xem lại đơn vị giao sản phẩm, nhận 2 hộp sữa móp méo tùm lum"
    # -> Shipping (đơn vị giao tệ), Packing (2 hộp sữa móp)
    (0, 0, 1, 1),
    # 477: "khuyên thật lòng ai ở miền nam muốn mua thì cân nhắc, mình ở sg, đặt sản phẩm xong mới biết SP giao từ hà nội, khi nhận sản phẩm cái thùng mềm nhũn... mở ra thấy hơn chục hộp bị móp mép"
    # -> Shipping (giao từ xa, thùng mềm nhũn), Packing (hơn chục hộp bị móp)
    (0, 0, 1, 1),
    # 478: "rất không hài lòng về dịch vụ của tiki, đơn sản phẩm tiếp nhận giao đến khách 24/08 nhưng đến 17g nhắn tin khách dời lại tới 28/08. dịch vụ như thế sao khách tin tưởng"
    # -> Service (dịch vụ giao hàng tệ, dời ngày giao đột ngột), Shipping (hoãn giao hàng)
    (0, 1, 1, 0),
    # 479: "sản phẩm giao nhanh, nhưng có điều shipper không có lịch sự gõ cửa nhà đùng đùng. dt đâu không gọi? thái độ giao sản phẩm không vui vẻ trong khi lần nào giao cho mình cũng gửi tiền thêm"
    # -> Shipping (shipper thái độ kém, gõ cửa ầm ĩ, không gọi điện trước)
    (0, 0, 1, 0),
    # 480: "mình cứ nghĩ 350k là giá hộp lớn, lúc nhận sản phẩm mới rõ hộp nhỏ, nếu tính hộp nhỏ thì hơi mắc so với mua hộp lớn gần 100k, hơi thất vọng, giao sản phẩm lâu gần 1 tuần"
    # -> Service (giá mắc so với kỳ vọng, mô tả không rõ về kích cỡ), Shipping (giao chậm)
    (0, 1, 1, 0),
    # 481: "mua 36h sữa nhận về đúng 32h, không 1 lời giải thích của tiki, không chấp nhận được"
    # -> Shipping (giao thiếu - 32 thay vì 36 hộp), Service (không giải thích)
    (0, 1, 1, 0),
    # 482: "thùng bị móp và bễ hộp sữa chảy sữa ra ngoài luôn"
    # -> Packing (thùng móp, bể hộp sữa chảy ra)
    (0, 0, 0, 1),
    # 483: "giao sản phẩm qua lâu, gần 2 tuần nhưng vẫn không nhận được, rốt cuộc phải hủy đơn hàng"
    # -> Shipping (giao cực kỳ chậm, phải hủy)
    (0, 0, 1, 0),
    # 484: "xin chào, theo tinh thần ủng hộ mua sắm online... tôi đã mua mấy gói sản phẩm tã dán người già caryn size mình loại 40 miếng... tuy nhiên sản phẩm không đúng chất lượng như mong muốn... không đúng chất lượng so với mẫu sản phẩm cùng mẫu cùng loại nhưng gia đình tôi đã mua trước từ đại lý của nhãn sản phẩm caryn. kính mong tiki.vn xem xét lại"
    # -> Quality (SP không đúng chất lượng như mua tại đại lý chính hãng), Service (yêu cầu xem xét)
    (1, 1, 0, 0),
    # 485: "lúc trước có mua thử loại này ngoài cửa hàng rồi, gói mình-l3 thấy tã dày dặn, vách ngăn và viền có chun khá chắc chắn, ôm tốt. nay mua thử của tiki... thấy in là cải tiến mới nhưng hơi thất vọng. lõi bông giữa tã rất lỏng... chun có như không. chọn size mình nhưng hóa to hơn cả mình-l. mùi thảo mộc khá nồng"
    # -> Quality (SP khác biệt so với mua tại cửa hàng - lõi lỏng, chun yếu, size sai, mùi nồng)
    (1, 0, 0, 0),
    # 486: "tiki giao sản phẩm cực kỳ chậm. giao trễ nhưng không phản hồi với khách. khách gọi điện rất nhiều lần và nv tiki hứa phản hồi lại nhưng không hề có 1 cuộc gọi. nv giao sản phẩm thì nói chuyện bất lịch sự"
    # -> Service (không phản hồi, thất hứa), Shipping (giao cực kỳ chậm, shipper bất lịch sự)
    (0, 1, 1, 0),
    # 487: "kích thước vừa, nhưng lớp thấm mỏng, dày khoảng gấp rưỡi thì tốt!"
    # -> Quality (lớp thấm mỏng - cần dày hơn)
    (1, 0, 0, 0),
    # 488: "tôi đã mua sản phẩm này cho mẹ chồng dùng, sản phẩm dùng được"
    # -> Quality (+, dùng được)
    (1, 0, 0, 0),
    # 489: "tã dán xài tốt, giống như mô tả"
    # -> Quality (+)
    (1, 0, 0, 0),
    # 490: "giá rẻ hơn mong đợi, thanks giao sản phẩm siêu nhanh, đặt hôm qua nay có rồi"
    # -> Service (+, giá tốt), Shipping (+, rất nhanh)
    (0, 1, 1, 0),
    # 491: "sản phẩm đóng gói cẩn thận nhưng giao sản phẩm quá lâu"
    # -> Shipping (giao chậm), Packing (+)
    (0, 0, 1, 1),
    # 492: "giao sản phẩm không đúng với kích thước đã đặt, 60 70cm, 14 miếng. nhưng lại giao 42 72 cm. 20 miếng. không có nhu cầu sử dụng với kích thước này. muốn trả sản phẩm!"
    # -> Service (muốn trả hàng), Shipping (giao sai kích thước)
    (0, 1, 1, 0),
    # 493: "sau này giao sản phẩm cho khách nhờ kiểm kỹ dùm, vì việc đổi trả khá lâu"
    # -> Service (quy trình đổi trả chậm, góp ý kiểm hàng)
    (0, 1, 0, 0),
    # 494: "tôi dùng đã 6 năm cho mẹ tôi... cách đây gần 2 năm chất lượng gòn giảm xuống... từ 4 tháng nay thì rất mỏng, gòn giữa miếng lỏng lẻo, hình như nhà sản xuất đang cắt xén khách hàng, dù giá vẫn lên! đề nghị xem lại chất lượng sản phẩm"
    # -> Quality (chất lượng giảm theo thời gian - mỏng hơn, lỏng lẻo hơn), Service (giá tăng nhưng chất lượng giảm - đề nghị xem lại)
    (1, 1, 0, 0),
    # 495: "giao không đúng loại sản phẩm"
    # -> Shipping (giao sai loại)
    (0, 0, 1, 0),
    # 496: "đặt 10 bịch giao có 9 bịch"
    # -> Shipping (giao thiếu 1 bịch)
    (0, 0, 1, 0),
    # 497: "mua sản phẩm nói tặng quà nhưng cuối cùng lại hủy không tặng nhưng cũng không giải thích gì"
    # -> Service (hủy quà tặng không giải thích)
    (0, 1, 0, 0),
    # 498: "sản phẩm đặt lúc giãn cách nhưng tiki không giao sản phẩm và giờ không cần nữa"
    # -> Shipping (không giao hàng trong thời gian giãn cách)
    (0, 0, 1, 0),
    # 499: "phù hợp về chất lượng, giá cả cho người cao tuổi"
    # -> Quality (+), Service (+, giá)
    (1, 1, 0, 0),
]

# Áp dụng labels cho index 100-599
for i, (q, s, sh, p) in enumerate(manual_labels):
    idx = 100 + i
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

print("Hoan thanh label 500 dong (index 100-599)!")
print()
print("=== THONG KE 600 DONG DAU ===")
first_600 = df.head(600)
for col in ["Quality", "Service", "Shipping", "Packing"]:
    count = int(first_600[col].sum())
    print(f"  {col}: {count}/600 dong co nhan 1 ({count/6:.1f}%)")

print()
print("=== THONG KE RIENG 500 DONG MOI (100-599) ===")
batch = df.iloc[100:600]
for col in ["Quality", "Service", "Shipping", "Packing"]:
    count = int(batch[col].sum())
    print(f"  {col}: {count}/500 dong co nhan 1 ({count/5:.1f}%)")
