import pandas as pd, sys
sys.stdout.reconfigure(encoding='utf-8')

df = pd.read_csv(
    r"C:\Users\admin\Desktop\KHDL\IT4930-T2\data\Commentsauxuly\comments_data_ncds_preprocessed_toy.csv"
)

# -----------------------------------------------------------------------
# LABEL THỦ CÔNG DÒNG 600 -> 999 (index 600-999, file line 602-1001)
# Quality  : chất lượng SP (hư hỏng, vị lạ, hàng giả/nhái, sai mẫu, date cận/hết hạn)
# Service  : CSKH, tư vấn, đổi trả, khuyến mãi/quà không đúng, giá cao/sai, astra
# Shipping : giao trễ, giao nhầm/thiếu, shipper thái độ, xác nhận giao ảo
# Packing  : đóng gói sơ sài, hộp móp/rách, bao bì rách/bẩn, nắp bung
# -----------------------------------------------------------------------

manual_labels = [
    # 600: "ông nội mình mặc ml20 nhưng đi đặt m20. chưa mặc nên không biết có vừa không"
    # -> (nhầm size khi đặt - lỗi người dùng, chưa đánh giá SP)
    (0, 0, 0, 0),
    # 601: "xài rồi nhưng phát hiện loại khác giá rẻ hơn và dùng tốt hơn"
    # -> Quality (loại khác tốt hơn), Service (giá không cạnh tranh)
    (1, 1, 0, 0),
    # 602: "sản phẩm date mới, đóng gói cẩn thận... sản phẩm không phải do cty đại thịnh nhập khẩu... mua xài thử, chắc sau không mua nữa"
    # -> Quality (nghi ngờ nguồn gốc, mùi bám khó chịu), Packing (+)
    (1, 0, 0, 1),
    # 603: "mình vừa mua sản phẩm này cách đây vài ngày... túi rửa y chang chỉ có 49k, trong khi ở tiki là 72k, chênh nhau quá lớn"
    # -> Service (giá tiki cao hơn thị trường quá nhiều)
    (0, 1, 0, 0),
    # 604: "nhận sản phẩm rất khó chịu vì sản phẩm nhập khẩu không có tem phụ, không thể hiện nhà nhập khẩu và thương nhân có trách nhiệm"
    # -> Quality (không có tem phụ, thiếu thông tin nhà nhập khẩu)
    (1, 0, 0, 0),
    # 605: "sản phẩm thì tốt nhưng giao sản phẩm lâu quá, sản phẩm tới không giao cứ dt hỏi đường... rồi cũng không thấy giao, xong vài ngày lại dt hỏi đường"
    # -> Quality (+), Shipping (shipper vô năng, giao rất chậm)
    (1, 0, 1, 0),
    # 606: "nước rửa mùi rất nặng hăng bám mùi vô bình và núm ti... mới rửa lần đổ đi... nếu sản phẩm nhái thì rất tội cho các bé"
    # -> Quality (mùi hắc, nghi hàng nhái - ảnh hưởng sức khỏe bé)
    (1, 0, 0, 0),
    # 607: "trước dùng màu trắng mua ở kids không sao, giờ mua màu xanh này mùi kinh khủng... cắt vỏ bưởi ngâm mới hết mùi"
    # -> Quality (mùi kinh khủng, không phù hợp)
    (1, 0, 0, 0),
    # 608: "mở ra thấy sản phẩm là chán rồi. sản phẩm nhập nhưng không biết nhập từ bao giờ. miệng bao nhưng dơ đen thui. bao bì cũ, xài thấy không thơm như những lần trước mua"
    # -> Quality (bao bì dơ, cũ; mùi thay đổi), Packing (bao bì cũ, bẩn)
    (1, 0, 0, 1),
    # 609: "d-nee loại chai trắng xài rất được, nhưng loại gói xanh này thì mùi thơm nồng nặc quá, rửa xong bình sạch nhưng mùi nước rửa bám dai dẳng trên núm silicon"
    # -> Quality (mùi nặng, bám dai trên núm ti - không an toàn cho bé)
    (1, 0, 0, 0),
    # 610: "nước rửa bình sữa sao nghe mùi hắc như mùi nước rửa chén. khó chịu. không giống như những lần trước mình mua của tiki trading. cũng không có tem nhãn gì hết"
    # -> Quality (mùi hắc, không có tem nhãn - nghi hàng giả)
    (1, 0, 0, 0),
    # 611: "rửa không sạch, mùi hăng, không thơm dịu như mua ngoài cửa hàng. thất vọng cực kỳ"
    # -> Quality (rửa không sạch, mùi hăng, khác biệt so với mua tại shop)
    (1, 0, 0, 0),
    # 612: "có mùi ám lại, nên dùng loại không mùi"
    # -> Quality (mùi ám lại - không phù hợp)
    (1, 0, 0, 0),
    # 613: "sản phẩm giao bẩn, cũ và rò rỉ nước bên trong ra"
    # -> Quality (SP bẩn, cũ, rò rỉ - chất lượng kém), Packing (bao bì bẩn, rò rỉ)
    (1, 0, 0, 1),
    # 614: "tiki đóng gói cùng kệ lò vi sóng, đóng gói sao nhưng làm lủng mất túi nước rửa này, chảy không gì cả. ai lại đi đóng gói bằng cách cuộn băng keo như vậy?"
    # -> Packing (đóng gói cùng đồ nặng gây lủng túi, chảy hết sản phẩm)
    (0, 0, 0, 1),
    # 615: "tiki giao sản phẩm nhanh nhưng sản phẩm quá bẩn, nhìn vào không biết hạn dùng không. chắc không dám dùng luôn"
    # -> Quality (SP bẩn, không rõ HSD), Shipping (+)
    (1, 0, 1, 0),
    # 616: "túi hơi bẩn và không có tem phụ. ngoài siêu thị bán có mấy ngàn thôi, được cái mua tiki now nên nhận sản phẩm ngay"
    # -> Quality (túi bẩn, không có tem phụ), Service (giá cao so với siêu thị)
    (1, 1, 0, 0),
    # 617: "lần trước mình mua ở cửa hàng mùi rất dịu nhẹ, nay mua trên tiki thì mùi lại khác, không biết sao"
    # -> Quality (mùi thay đổi so với mua tại shop - nghi ngờ)
    (1, 0, 0, 0),
    # 618: "sản phẩm, dịch vụ đều tốt, có mỗi cái bao bì sản phẩm cái nào cũng bẩn. nhìn vào nhiều khi không biết sản phẩm mới hay cũ từ đời nào"
    # -> Packing (bao bì bẩn, trông cũ)
    (0, 0, 0, 1),
    # 619: "chất lượng sản phẩm đảm bảo, tuy nhiên bao bì hơi cũ!"
    # -> Quality (+), Packing (bao bì hơi cũ)
    (1, 0, 0, 1),
    # 620: "mới sử dụng có 1 lần nên không đánh giá được nhưng không thích mùi này lắm"
    # -> Quality (mùi không thích)
    (1, 0, 0, 0),
    # 621: "đóng gói kỹ. có vẻ hơi loãng hơn mua dạng chai 1 chút"
    # -> Quality (loãng hơn chai), Packing (+)
    (1, 0, 0, 1),
    # 622: "mình đặt sản phẩm hôm t3, tiki hẹn giao t4 nhưng đến nay vẫn chưa nhận được sản phẩm"
    # -> Shipping (giao chậm hơn hẹn)
    (0, 0, 1, 0),
    # 623: "hộp bị bong tróc, móp méo"
    # -> Packing (hộp bong tróc, móp méo)
    (0, 0, 0, 1),
    # 624: "không hài lòng hình ảnh 1 kiểu thực tế 1 kiểu"
    # -> Quality (SP không như hình ảnh quảng cáo)
    (1, 0, 0, 0),
    # 625: "mình nhận được sản phẩm rồi nhưng hộp bị móp tới bên trong bàn cờ"
    # -> Packing (hộp bị móp nặng tới bên trong)
    (0, 0, 0, 1),
    # 626: "mình cho 1 sao vì giao tã mình trễ 5 ngày, mình nhắn tin cho cửa hàng nhưng không có lấy 1 tin trả lời"
    # -> Service (không trả lời tin nhắn), Shipping (giao trễ 5 ngày)
    (0, 1, 1, 0),
    # 627: "hai bên mép cứng... đóng chất lượng tốt"
    # -> Quality (mép cứng - chất lượng SP), Packing (+)
    (1, 0, 0, 1),
    # 628: "để hình ảnh gây hiểu lầm cho người mua"
    # -> Service (quảng cáo gây hiểu lầm)
    (0, 1, 0, 0),
    # 629: "không bọc sản phẩm chống sốc cẩn thận vận chuyển bị móp bật nắp văng sữa bột ra ngoài"
    # -> Packing (không chống sốc, vận chuyển gây móp bật nắp, sữa đổ ra)
    (0, 0, 0, 1),
    # 630: "hoàn toàn không hài lòng chất lượng dịch vụ. mình mua 2 thùng sữa trị giá 1,363,000vnd... 2 sữa bị móp và seal thiết không nguyên vẹn... liên hệ nhân viên hỗ trợ đổi sản phẩm thì được báo chỉ giải quyết trong 48 tiếng... không hỗ trợ khách hàng một cách linh hoạt... nhân viên chăm sóc khách hàng chỉ muốn phủi trách nhiệm"
    # -> Quality (sữa bị móp, seal không nguyên vẹn), Service (CSKH kém, phủi trách nhiệm), Packing (hộp móp, seal hỏng)
    (1, 1, 0, 1),
    # 631: "giao sản phẩm móp méo, rất tệ"
    # -> Packing (SP bị móp méo)
    (0, 0, 0, 1),
    # 632: "sản phẩm không biết chất lượng như thế nào. nhưng bảo quản rất kém. bụi đóng cả lớp trên nắp"
    # -> Quality (bảo quản kém, bụi đóng trên nắp - nghi chất lượng)
    (1, 0, 0, 0),
    # 633: "giao sản phẩm nhanh đúng giờ đã ghi... hộp sữa bị móp trên miếng khui không kín nắp hộp, đề nghị những hộp như vậy không nên bán cho khách"
    # -> Service (phản ánh về việc bán SP bị lỗi), Shipping (+), Packing (hộp móp, nắp không kín)
    (0, 1, 1, 1),
    # 634: "sáng nay tôi nhận được sản phẩm, khui ra thấy hộp sữa đen thui như vừa moi trong đống rác, đáy hộp đã có dấu hiệu rỉ sét dù hạn dùng đến tháng 8/2021, sợ quá không dám dùng. liên hệ bộ phận chăm sóc khách hàng thì không ai nghe máy"
    # -> Quality (hộp sữa bẩn, rỉ sét - không an toàn), Service (CSKH không nghe máy)
    (1, 1, 0, 0),
    # 635: "dù biết do dịch nên sản phẩm giao chậm, nhưng chậm hơn dự kiến tận 20 ngày... phản hồi và chat nhiều lần thì không được hỗ trợ"
    # -> Service (không hỗ trợ khi khiếu nại), Shipping (giao chậm hơn 20 ngày)
    (0, 1, 1, 0),
    # 636: "mình mua sữa cho ông bà ở quê... ông bà vừa nhận sản phẩm xong và rất bức xúc vì mình mua 2 hộp và 1 hộp bị mở tung nắp, sữa bị nước vào ẩm hết. đề nghị tiki hỗ trợ!"
    # -> Service (yêu cầu hỗ trợ), Packing (nắp bị mở tung, sữa ẩm)
    (0, 1, 0, 1),
    # 637: "giao đến sản phẩm bị bể 1 hộp. sữa văng ra khắp nơi trong hộp tiki xử lý khiếu nại chậm chạp, bắt làm quá nhiều việc trong khi đây là lỗi của bên tiki và ncc"
    # -> Service (xử lý khiếu nại chậm, bắt khách làm nhiều việc), Packing (hộp bể, sữa văng ra)
    (0, 1, 0, 1),
    # 638: "đã mua rất nhiều sản phẩm này mấy lần trước rất tốt, nhưng lần này khi về mở hộp thì sữa đã bị đổ ra ngoài hộp"
    # -> Packing (sữa đổ ra ngoài hộp - đóng gói kém)
    (0, 0, 0, 1),
    # 639: "tiki dối khách sản phẩm, mua sản phẩm xong không hoàn astra"
    # -> Service (không hoàn điểm astra - gian lận)
    (0, 1, 0, 0),
    # 640: "cảm thấy không an tâm khi sản phẩm không nguyên serial và nắp hộp bẩm. rất may sản phẩm vẫn hạn sd đến 2021. tuy nhiên nhìn vào thấy thiếu an tâm về sản phẩm"
    # -> Quality (mất serial, nghi không an toàn), Packing (nắp hộp bẩm - hỏng)
    (1, 0, 0, 1),
    # 641: "đặt mua sản phẩm mới nhưng khi nhận khui ra y như sản phẩm trong kho 2 end của tiki. mặc dù tem chưa bóc nhưng nhìn phát nản. mua đi biếu người thân nhưng trông thế này sao dám biếu cơ chứ?"
    # -> Quality (SP trông cũ, bẩn như hàng kho lâu ngày)
    (1, 0, 0, 0),
    # 642: "đóng sản phẩm quá ẩu. sản phẩm bị móp bụng nắp đổ"
    # -> Packing (đóng gói ẩu, hộp móp, nắp đổ)
    (0, 0, 0, 1),
    # 643: "giao rất chậm. nhưng đóng gói tốt"
    # -> Shipping (giao chậm), Packing (+)
    (0, 0, 1, 1),
    # 644: "giao sản phẩm chậm 5 ngày so với lịch hẹn"
    # -> Shipping (giao chậm 5 ngày)
    (0, 0, 1, 0),
    # 645: "sản phẩm date dài. giao sản phẩm rất nhanh. đóng gói không chuyên nghiệp, bên ngoài hộp khá là bụi bẩn, tem giữa vỏ hộp và phần nắp nhựa đã rách từ lâu"
    # -> Quality (+, date xa), Shipping (+), Packing (đóng gói không chuyên, hộp bẩn, tem rách)
    (1, 0, 1, 1),
    # 646: "đóng sản phẩm cẩn thận đúng sản phẩm cần mua"
    # -> Packing (+)
    (0, 0, 0, 1),
    # 647: "tem bị bóc, hộp bị móp. thất vọng"
    # -> Quality (tem bị bóc - nghi đã mở), Packing (hộp móp)
    (1, 0, 0, 1),
    # 648: "sản phẩm đã bị bóc tem dán bên ngoài, vỏ hộp trầy, nhìn cũ. rất không hài lòng"
    # -> Quality (tem bị bóc, vỏ trầy, nhìn cũ - nghi đã dùng/hàng cũ)
    (1, 0, 0, 0),
    # 649: "mua rất nhiều lần sữa gửi về nhà cho mẹ nhưng lần này tiki làm ăn quá chán. chống sốc kém, hộp sữa thì bị vỡ bục hết cả ra thùng. chả biết bục từ trước hay giờ do vận chuyển làm bục nữa"
    # -> Shipping (vận chuyển gây vỡ), Packing (chống sốc kém, hộp vỡ bục)
    (0, 0, 1, 1),
    # 650: "bình thường mấy ngày gần đây tôi có mua sản phẩm mỗi ngày. dùng bằng voucher đổi điểm asa không hiểu sao tiki báo mình vi phạm. khoá chắc năng tiki now... xoá ngay tài khoản. không bao giờ dùng lại tiki"
    # -> Service (tiki khóa tài khoản bất hợp lý, trải nghiệm tồi tệ)
    (0, 1, 0, 0),
    # 651: "giao sản phẩm lâu, sản phẩm giao tới bị đổ vỡ sữa bị mốc, vón cục. hi vọng được giải quyết"
    # -> Quality (sữa bị mốc, vón cục), Service (yêu cầu giải quyết), Shipping (giao lâu), Packing (SP bị đổ vỡ)
    (1, 1, 1, 1),
    # 652: "giao sản phẩm quá lâu, nếu với thời gian giao sản phẩm đó thì thua"
    # -> Shipping (giao quá chậm)
    (0, 0, 1, 0),
    # 653: "đặt của tiki trading nhưng không hiểu sao lại có thể gói sản phẩm sơ sài và ẩu như thế này được. may là sữa chưa bị bung ra"
    # -> Packing (đóng gói sơ sài, ẩu)
    (0, 0, 0, 1),
    # 654: "rất không hài lòng bên đơn vị vận chuyển. mình mua 2 hộp khi nhận thì chỉ có 1 hộp nguyên, 1 hộp móp méo văng sữa ra ngoài. mình mua gửi biếu mẹ chồng nên không chụp lại được ảnh lúc nhận"
    # -> Shipping (đơn vị vận chuyển tệ), Packing (1 hộp móp méo, sữa văng ra)
    (0, 0, 1, 1),
    # 655: "hộp bị bung, đổ sữa ra hộp. bao bọc kém. đề nghị tiki thu hồi"
    # -> Service (yêu cầu thu hồi), Packing (hộp bung, sữa đổ ra, bao bọc kém)
    (0, 1, 0, 1),
    # 656: "chưa thấy thưởng astra đề nghị tiki xem xét lại"
    # -> Service (không nhận được điểm astra)
    (0, 1, 0, 0),
    # 657: "gói sản phẩm sơ sài tệ hại, không hề có chống sốc... giao sản phẩm lâu, muốn ủng hộ tiki nhưng ntn thì xin phép bỏ"
    # -> Shipping (giao chậm), Packing (đóng gói sơ sài, không có chống sốc)
    (0, 0, 1, 1),
    # 658: "giao sản phẩm nhanh. nhưng vận chuyển làm móp méo hết thùng bên ngoài dù đã có cảnh báo sản phẩm dễ vỡ. may không móp hộp sữa bên trong"
    # -> Shipping (+, nhanh; nhưng vận chuyển tệ - móp thùng ngoài)
    (0, 0, 1, 0),
    # 659: "tiki làm ăn giao sản phẩm mất uy tín quá, sản phẩm đóng gói rách te tua, sữa thì bung nắp, sữa đổ ra ngoài dính hộp dẻo nhẹo"
    # -> Packing (đóng gói rách te tua, sữa bung nắp, đổ ra)
    (0, 0, 0, 1),
    # 660: "gói sản phẩm quá sơ sài, sản phẩm bục hết cả sữa ra ngoài. tôi muốn được đổi sản phẩm nguyên vẹn"
    # -> Service (muốn đổi sản phẩm), Packing (đóng gói sơ sài, SP bục sữa ra)
    (0, 1, 0, 1),
    # 661: "sản phẩm giao về vỡ hết nhưng tiki không chịu xử lý"
    # -> Service (không xử lý), Packing (SP vỡ hết)
    (0, 1, 0, 1),
    # 662: "sản phẩm mỏng keo không dính không nên mua vì xài không được"
    # -> Quality (SP mỏng, keo không dính - chất lượng kém)
    (1, 0, 0, 0),
    # 663: "giao 3 hộp sữa, 1 tuần chưa tới. thôi dẹp mẹ đi"
    # -> Shipping (giao cực kỳ chậm - 1 tuần chưa có)
    (0, 0, 1, 0),
    # 664: "tiki ơi em mua 2 đơn này đều đủ điều kiện để nhận quà tặng là 380g nhưng sao không có cái nào hết vậy"
    # -> Service (không nhận được quà tặng như cam kết)
    (0, 1, 0, 0),
    # 665: "mua 2 được giảm giá nhưng sao bị móp và bể vậy. cửa hàng trả lời giùm"
    # -> Service (yêu cầu phản hồi), Packing (hộp bị móp và bể)
    (0, 1, 0, 1),
    # 666: "chất lượng tốt, giao sản phẩm nhanh chóng"
    # -> Quality (+), Shipping (+)
    (1, 0, 1, 0),
    # 667: "sữa date mới, thơm, vị nhạt hơn sữa mẫu cũ. đóng gói cẩn thận. tiếc là thành phần bột sữa gầy lên sẽ ít chất béo"
    # -> Quality (+, date mới; nhưng nhận xét vị thay đổi), Packing (+)
    (1, 0, 0, 1),
    # 668: "sản phẩm tặng vỡ nhưng không đổi cho khách"
    # -> Quality (SP tặng bị vỡ), Service (không chịu đổi)
    (1, 1, 0, 0),
    # 669: "nắp hộp bị rách, hộp bọc bên ngoài bị méo"
    # -> Packing (nắp rách, hộp bọc méo)
    (0, 0, 0, 1),
    # 670: "hộp sữa bị móp và bung nắp"
    # -> Packing (hộp bị móp, bung nắp)
    (0, 0, 0, 1),
    # 671: "đánh giá không tính điểm đóng gói sơ sài hộp móp méo"
    # -> Packing (đóng gói sơ sài, hộp móp)
    (0, 0, 0, 1),
    # 672: "check mã vạch không ra. mình cần lời giải thích từ cửa hàng"
    # -> Quality (mã vạch không ra - nghi hàng giả), Service (yêu cầu giải thích)
    (1, 1, 0, 0),
    # 673: "sản phẩm như mô tả, mùi sữa bé không thích"
    # -> Quality (bé không thích mùi - vấn đề SP)
    (1, 0, 0, 0),
    # 674: "gói sản phẩm không kỹ lưỡng bị móp méo"
    # -> Packing (đóng gói không kỹ, hộp móp)
    (0, 0, 0, 1),
    # 675: "giao sản phẩm không đúng mẫu mình đặt"
    # -> Shipping (giao sai mẫu)
    (0, 0, 1, 0),
    # 676: "đóng gói tệ nhất mình từng thấy sữa thì bị lấy mất quai, niêm phong không có. mua một lần không dám mua lần nữa"
    # -> Quality (mất quai, không có niêm phong - nghi bị mở), Packing (đóng gói tệ)
    (1, 0, 0, 1),
    # 677: "mua 1 thùng tặng kèm khủng long nhưng lại tách làm 2 lần giao sản phẩm cũng như tính phí giao sản phẩm 2 lần... đơn sản phẩm hơn 400 ngàn nhưng không được hỗ trợ giao sản phẩm, lại không giao nhanh được"
    # -> Service (tính phí giao 2 lần, không hỗ trợ freeship dù đủ điều kiện)
    (0, 1, 0, 0),
    # 678: "đặt sản phẩm thì 1 tuần mới tới nhưng không hề nhận được quà đi kèm. nhưng bây giờ vào thì vẫn thấy để quà bên cạnh nhằm dụ dỗ lòng tin của khách. làm vậy rất mất uy tín và cũng không hề báo khách không có quà"
    # -> Service (không nhận được quà, vẫn giữ hình ảnh quà - gian lận), Shipping (giao chậm 1 tuần)
    (0, 1, 1, 0),
    # 679: "sản phẩm hình có gấu bông nhưng giao sản phẩm không có gấu bông, làm bọn trẻ con thất vọng không muốn uống sữa cứ đòi đi mua gấu bông khác"
    # -> Service (không nhận được quà tặng như ảnh quảng cáo)
    (0, 1, 0, 0),
    # 680: "hết quà cửa hàng nên gỡ ảnh tặng quà xuống, để tặng nhưng giao không có, buồn"
    # -> Service (không có quà như quảng cáo, không gỡ ảnh quà khi hết)
    (0, 1, 0, 0),
    # 681: "sao mình mua ghi được tặng balo nhưng sao không có vậy shops. giao sản phẩm nha"
    # -> Service (không nhận được quà tặng balo)
    (0, 1, 0, 0),
    # 682: "tôi đặt mua lần 2 nhưng thời gian chờ đợi sản phẩm quá lâu. đối với mặt sản phẩm sữa cho trẻ em nên rút ngắn thời gian giao sản phẩm. mặc dù sử dụng tikinow nhưng thời gian chờ lên đến 4 ngày"
    # -> Shipping (giao chậm - tikinow mà 4 ngày)
    (0, 0, 1, 0),
    # 683: "ad ơi, sao mình mua 1 thùng nhưng không nhận được balo ạ? quảng cáo thì có nhưng nhận sản phẩm không có ạ?"
    # -> Service (không nhận được quà balo như quảng cáo)
    (0, 1, 0, 0),
    # 684: "không có khuyến mãi kèm theo trong khi lúc mua sản phẩm và tt là có"
    # -> Service (không nhận được khuyến mãi)
    (0, 1, 0, 0),
    # 685: "mình không nhận được balo khuyến mãi. có thể check giúp mình được không ạ"
    # -> Service (không nhận được balo khuyến mãi)
    (0, 1, 0, 0),
    # 686: "của mình không nhận được khuyến mãi balo là tn"
    # -> Service (không nhận được khuyến mãi)
    (0, 1, 0, 0),
    # 687: "giao sản phẩm chậm. sữa gần hết hạn"
    # -> Quality (sữa gần hết hạn), Shipping (giao chậm)
    (1, 0, 1, 0),
    # 688: "lấy ra cho con uống mới thấy phần đáy hộp vỏ hộp không được như mọi lần mua ở cửa hàng thấy không được yên tâm"
    # -> Quality (SP khác biệt so với mua tại shop, gây lo ngại)
    (1, 0, 0, 0),
    # 689: "thời gian giao sản phẩm quá chậm"
    # -> Shipping (giao quá chậm)
    (0, 0, 1, 0),
    # 690: "đóng gói tốt, chưa dùng nên chưa có đánh giá"
    # -> Packing (+)
    (0, 0, 0, 1),
    # 691: "1 sao dành cho vận chuyển"
    # -> Shipping (vận chuyển tệ)
    (0, 0, 1, 0),
    # 692: "bán sản phẩm đảo không quà tặng trả sản phẩm thì không được"
    # -> Service (quà tặng không có - lừa đảo, không cho trả hàng)
    (0, 1, 0, 0),
    # 693: "sản phẩm nhưng 2 tháng nữa hết date"
    # -> Quality (date chỉ còn 2 tháng - gần hết hạn)
    (1, 0, 0, 0),
    # 694: "thấy ghi là tặng con khủng long nhưng nhận sản phẩm không có khủng long?"
    # -> Service (không nhận được quà tặng)
    (0, 1, 0, 0),
    # 695: "con mình thích uống. muốn mua tiếp. nhưng lại không thấy tặng khủng long bông"
    # -> Quality (+), Service (không nhận được quà bông)
    (1, 1, 0, 0),
    # 696: "sản phẩm thì không sao, tuy nhiên hơi buồn khi cách dán mác giá rẻ vô đối của tiki trong lần này... tôi mua thẳng x10... tổng tiền mình bỏ ra để mua x10 giá lẻ 105k/sp. trong khi cùng kiểu sản phẩm theo kiểu +2 sp lẻ mình sẽ có thể mua được giá 95k/sp... tổng đơn của mình bị thiệt hơn"
    # -> Service (gán mác giá sai lệch, khách mua thiệt hơn do chiêu trò giá)
    (0, 1, 0, 0),
    # 697: "đặt sản phẩm 19/9, tiki hẹn giao 5/10, đến 18/10 mới giao sản phẩm. tiki đợt này giao sản phẩm quá chậm... khách sản phẩm không liên lạc thì tiki cũng không thèm thông báo lý do, khách liên hệ lại thì lấy bot để trả lời rất rập khuôn"
    # -> Service (bot trả lời rập khuôn, không thông báo), Shipping (giao chậm 13 ngày, không báo lý do)
    (0, 1, 1, 0),
    # 698: "mua 1 sản phẩm thì tốt. mua 2 sản phẩm chịu thêm 6k phụ phí. mua 10 sản phẩm chịu 74k phụ phí... thôi đành chịu khó tiết kiệm vậy"
    # -> Service (phí phụ trội khi mua nhiều - bất hợp lý)
    (0, 1, 0, 0),
    # 699: "mọi người nên cân nhắc trước khi mua nhé"
    # -> (không rõ khía cạnh)
    (0, 0, 0, 0),
    # 700: "đóng gói cẩn thận. nhưng miếng dán của tã cứ bung ra"
    # -> Quality (miếng dán bung ra - lỗi SP), Packing (+)
    (1, 0, 0, 1),
    # 701: "keo dán của tã không có độ bám dính tốt dù date đến tận 2024, giao sản phẩm nhanh"
    # -> Quality (keo dán không bám - lỗi SP), Shipping (+)
    (1, 0, 1, 0),
    # 702: "giao sản phẩm nhanh, sản phẩm không vấn đề gì, có 2 cục tã nhưng cũng tính phí cồng kềnh"
    # -> Service (tính phí cồng kềnh cho tã - không hợp lý), Shipping (+)
    (0, 1, 1, 0),
    # 703: "mọi lần trước tốt, lần này giao sản phẩm chậm quá"
    # -> Shipping (giao chậm)
    (0, 0, 1, 0),
    # 704: "số lượng được mua ít quá"
    # -> Service (giới hạn số lượng mua)
    (0, 1, 0, 0),
    # 705: "tiki giao bịch tã bị rách, tã bên trong dơ hết, không thể sử dụng được. liên lạc với tiki hơn 1 tháng rồi nhưng tiki vẫn không có bất kỳ hành động khắc phục nào. tã để lâu em bé sẽ lên size, không thể sử dụng được nữa"
    # -> Service (không khắc phục sau hơn 1 tháng), Packing (bịch tã bị rách, tã dơ)
    (0, 1, 0, 1),
    # 706: "mua của tiki trading 2 lần! lần đầu các bạn tiki đã đóng gói rất cẩn thận chắc chắn! lần này tiki hà nội gói sản phẩm quá ẩu thả! bung hết lớp bao ra, sản phẩm giao đến nơi bị xô xệch, đất bám vô rất bẩn!"
    # -> Packing (đóng gói ẩu thả, bung bao, đất bẩn vào SP)
    (0, 0, 0, 1),
    # 707: "thật sự mua nhà mình cũng lần thứ 2 rồi, nhưng lần này cảm giác như bỉm có vấn đề, bông bỉm cứng hơn, chun 2 bên không ôm, không biết là nhà sản xuất thay đổi cái dính bằng màu khác hay sản phẩm này có vấn đề"
    # -> Quality (bỉm thay đổi chất lượng - bông cứng hơn, chun không ôm)
    (1, 0, 0, 0),
    # 708: "giao sản phẩm nhanh... thấy trên hình sản phẩm đặt 899k khung giờ 9h-12h được tặng bộ đệm nằm cho bé... mình đặt hơn 1tr và đúng khung giờ nhưng không thấy tặng quà tặng"
    # -> Service (không nhận được quà tặng đúng khung giờ), Shipping (+)
    (0, 1, 1, 0),
    # 709: "mua đúng vào khung giờ nói có quà tặng và giá trị món sản phẩm trên 600k nhưng khi giao không hề thấy có quà tặng"
    # -> Service (không nhận được quà dù đúng điều kiện)
    (0, 1, 0, 0),
    # 710: "không hiểu giao sản phẩm kiểu gì, bịch bỉm bị rách. hở hết bỉm bên trong, thất vọng thật sự"
    # -> Packing (bịch bỉm bị rách, hở bỉm trong)
    (0, 0, 0, 1),
    # 711: "cực kì không hài lòng. đặt sản phẩm bỉm dán giao bỉm quần, chót bóc ra nên đành chịu. mở bỉm ra có mùi hơi khó chịu"
    # -> Quality (bỉm có mùi khó chịu), Shipping (giao sai loại - dán thay vì quần)
    (1, 0, 1, 0),
    # 712: "đặt tã dán nhưng giao tã quần?"
    # -> Shipping (giao sai loại)
    (0, 0, 1, 0),
    # 713: "giao sản phẩm nhanh. nhưng sản phẩm không đảm bảo chất lượng. bịch bỉm đã rách dùng băng dính dán lại, bỉm bên trong bẩn, đen xì. bán sản phẩm không có trách nhiệm. bán sản phẩm cho trẻ sơ sinh nhưng thế"
    # -> Quality (bỉm bẩn, đen - chất lượng kém, không an toàn cho trẻ sơ sinh), Shipping (+), Packing (bịch rách, dán băng keo)
    (1, 0, 1, 1),
    # 714: "mua 2 bịch bỉm moony natural từ tiki đều bị rách và dán băng dính vá tạm ổn lại như thế này. bỉm thì dùng 3 đêm cả 3 đêm tràn bỉm. tung hết cả viền chun bên trong"
    # -> Quality (bỉm kém - tràn, chun bị tung), Packing (bịch rách, vá băng keo)
    (1, 0, 0, 1),
    # 715: "chưa bàn về chất lượng tả chỉ thấy tiki đóng gói quá tệ, chỉ bọc màng bọc thực phẩm tới tay mình bọc thì rách, rách phạm luôn vào bọc tã. trời mưa nước mưa với bùn đất bẩn thấm vào hư mất mấy miếng tã, bên ngoài bịch tã dơ"
    # -> Packing (đóng gói quá tệ - chỉ bọc màng mỏng bị rách, tã dính bùn bẩn)
    (0, 0, 0, 1),
    # 716: "miếng dán là màu vàng chứ không phải màu xanh như bình thường vẫn mua. sản phẩm gói thì bọc mỗi túi bóng mỏng"
    # -> Quality (màu miếng dán thay đổi - SP khác biệt), Packing (bọc mỏng)
    (1, 0, 0, 1),
    # 717: "sản phẩm đẹp tốt. nhưng thái độ người giao sản phẩm không thích. đặt sản phẩm ghi đầy đủ thông tin... khi đến thì cáu. mong tiki xem lại"
    # -> Quality (+), Shipping (shipper thái độ cáu kỉnh)
    (1, 0, 1, 0),
    # 718: "chất lượng tốt, giao sản phẩm đúng tiến độ"
    # -> Quality (+), Shipping (+)
    (1, 0, 1, 0),
    # 719: "gói sản phẩm xơ xài, giao bịch tã bị rách"
    # -> Packing (đóng gói sơ xài, tã bị rách)
    (0, 0, 0, 1),
    # 720: "giá rẻ. nhưng chất lượng bỉm không giống loại mình đã dùng cho bé. độ thấm hút không bằng. tiền nào của đó"
    # -> Quality (thấm hút kém, khác biệt so với trước), Service (giá rẻ nhưng kém chất lượng)
    (1, 1, 0, 0),
    # 721: "mình không thấy quà đi kèm"
    # -> Service (không thấy quà tặng)
    (0, 1, 0, 0),
    # 722: "bỉm vón cục, không chắc chắn, giống sản phẩm fake mặc dù bé tè chưa nhiều"
    # -> Quality (bỉm vón cục, nghi hàng fake)
    (1, 0, 0, 0),
    # 723: "sản phẩm không chuẩn, kém chất lượng sản phẩm rởm"
    # -> Quality (SP kém chất lượng, rởm)
    (1, 0, 0, 0),
    # 724: "không giao quà tặng như trong đơn sản phẩm"
    # -> Service (không giao quà tặng theo đơn)
    (0, 1, 0, 0),
    # 725: "mang bỉm bị hăm nặng cho bé"
    # -> Quality (bỉm gây hăm nặng - chất lượng kém, không an toàn)
    (1, 0, 0, 0),
    # 726: "muốn đổi size nhưng không được hỗ trợ. mua 2 bịch yêu cầu nhân viên tiki liên hệ cửa hàng giúp nhưng nhân viên báo không có số cửa hàng để liên hệ. bó tay"
    # -> Service (không hỗ trợ đổi size, không có số liên hệ cửa hàng - phục vụ kém)
    (0, 1, 0, 0),
    # 727: "mình nhận được thùng sữa nhưng bị thiếu 1 lốc và 1 hộp, chưa bao giờ mua sản phẩm tiki lại bị thế này"
    # -> Shipping (giao thiếu 1 lốc và 1 hộp)
    (0, 0, 1, 0),
    # 728: "tại sao giao sữa bị phù phải bỏ hết 2 lốc, buôn bán cho trẻ em nhưng làm vậy à"
    # -> Quality (sữa bị phù - lỗi SP nguy hiểm cho trẻ em)
    (1, 0, 0, 0),
    # 729: "mua 2 thùng được tặng bộ chăn gối nhưng không thấy ở đâu, haizz"
    # -> Service (không nhận được quà chăn gối)
    (0, 1, 0, 0),
    # 730: "đặt trên app là yoko 110ml nhưng không hiểu sao lại ra optimum, không hiểu được vấn đề ở đây là gì"
    # -> Shipping (giao sai SP hoàn toàn - khác nhãn hiệu)
    (0, 0, 1, 0),
    # 731: "hình ảnh thì để tặng quà nhưng mua lại không có. khác gì đảo"
    # -> Service (ảnh quảng cáo quà nhưng không có - gian lận)
    (0, 1, 0, 0),
    # 732: "sản phẩm giao đa phần nào cũng móp rất nặng. sản phẩm tệ"
    # -> Packing (SP móp nặng mỗi lần giao)
    (0, 0, 0, 1),
    # 733: "hài ..."
    # -> (không đủ thông tin)
    (0, 0, 0, 0),
    # 734: "đăng bán thì bảo tặng gối ôm. giao sản phẩm thì không có thất vọng?"
    # -> Service (không nhận được quà gối ôm như quảng cáo)
    (0, 1, 0, 0),
    # 735: "sua uong toi hop thu 7 van không len kg nao, chua ke so hyperactive, se doi sua khac cho con"
    # -> Quality (sữa uống 7 hộp không tăng cân, bé hyperactive - chất lượng không đáp ứng)
    (1, 0, 0, 0),
    # 736: "nhận sản phẩm nhưng không có gấu. đăng nhận xét thì bị xóa?"
    # -> Service (không có quà gấu, nhận xét bị xóa - kiểm duyệt bất công)
    (0, 1, 0, 0),
    # 737: "không có quà tặng tiki ơi. xem lại dùm mình với"
    # -> Service (không có quà tặng)
    (0, 1, 0, 0),
    # 738: "trên app ghi tặng bộ ghép hình 80k cho đơn 999k. mình đặt 2 thùng hơn 1tr nhưng khi nhận sản phẩm không có bộ ghép hình"
    # -> Service (không nhận được quà như cam kết)
    (0, 1, 0, 0),
    # 739: "do giờ bé uống sữa này từ khi vừa lọt lòng. không hiểu kiểu gì nhưng ngày càng giá trên trời. tiki nhưng đỡ, shopee thì giá trời ơi đất hỡi. mua trên web nhưng mắc hơn ra mấy đại lý lớn nữa"
    # -> Service (giá ngày càng cao, mắc hơn đại lý)
    (0, 1, 0, 0),
    # 740: "vận chuyển không đảm bảo. kiến vào trong sữa rất nhiều. đơn sản phẩm sữa mua cho em bé. nhưng không đảm bảo chất lượng"
    # -> Quality (kiến vào trong sữa - nguy hiểm, mất vệ sinh), Shipping (vận chuyển không đảm bảo)
    (1, 0, 1, 0),
    # 741: "tại sao hạn sử dụng trên vỏ thùng lại tẩy xóa không cho người mua sản phẩm nhìn thấy, trường hợp này là cố tình tẩy xóa. thiết nghĩ sữa cho trẻ em phải rõ ràng"
    # -> Quality (HSD bị tẩy xóa cố tình - gian lận nghiêm trọng)
    (1, 0, 0, 0),
    # 742: "quả ống hút giấy không thể chịu nổi. cắm vào hộp sữa 1 lúc là mềm nhũn, bé nhà mình hay cắn dẹp ống hút. không thể hút tiếp nữa"
    # -> Quality (ống hút giấy kém - mềm nhũn, không dùng được)
    (1, 0, 0, 0),
    # 743: "mua 08/08/2021 nhưng hạn dùng tới 28/10/2021. làm sao bé uống kịp khi mình mua tới 2 thùng?"
    # -> Quality (HSD quá gần - chỉ còn ~2 tháng, không kịp dùng 2 thùng)
    (1, 0, 0, 0),
    # 744: "giao sản phẩm nhưng 9 ngày hết date"
    # -> Quality (SP gần hết hạn - chỉ còn 9 ngày)
    (1, 0, 0, 0),
    # 745: "chất lượng tốt, nhưng thời gian giao sản phẩm lâu"
    # -> Quality (+), Shipping (giao chậm)
    (1, 0, 1, 0),
    # 746: "date hơi cũ. giá cũng khá rẻ so với các trang mua sắm khác"
    # -> Quality (date cũ), Service (+, giá tốt)
    (1, 1, 0, 0),
    # 747: "sản phẩm thời gian sử dụng đạt mới tốt"
    # -> Quality (+, HSD còn dài)
    (1, 0, 0, 0),
    # 748: "giao sản phẩm quá chậm. đề nghị tiki chấn chỉnh"
    # -> Shipping (giao quá chậm)
    (0, 0, 1, 0),
    # 749: "đặt lâu rồi nhưng cửa hàng chưa giao đến"
    # -> Shipping (chưa giao dù đã đặt lâu)
    (0, 0, 1, 0),
    # 750: "mua sản phẩm 2 lần đều phải hủy vì không có sản phẩm giao. chờ 2 tuần không thấy báo gì cứ treo đơn đó thôi. chán quá"
    # -> Service (hủy đơn do hết hàng không báo, treo đơn không thông báo)
    (0, 1, 0, 0),
    # 751: "mình được giao hộp sữa nhưng tem giấy niêm phong nắp nhựa bên ngoài đã bị xé. nắp kim loại vẫn nhưng mở ra lại không thấy có muỗng gạt ngang trong hộp... liệu tiki có bán sản phẩm không rõ nguồn gốc không?"
    # -> Quality (tem bị xé, thiếu muỗng - nghi bị mở/hàng không rõ nguồn gốc)
    (1, 0, 0, 0),
    # 752: "vừa nhận được sản phẩm, mở nắp nhựa thấy sữa tung toé thế này. quá cẩu thả trong đóng gói"
    # -> Packing (đóng gói cẩu thả, sữa tung toé)
    (0, 0, 0, 1),
    # 753: "sữa dù pha đúng nhiệt độ vẫn bị vón cục, không tan hoàn toàn"
    # -> Quality (sữa vón cục, không tan - lỗi SP)
    (1, 0, 0, 0),
    # 754: "đề nghị cửa hàng liên hệ lại để đổi sản phẩm mới, sản phẩm giao bị bung nắp văng sữa tùm lum, không đảm bảo chất lượng"
    # -> Service (yêu cầu đổi), Packing (bung nắp, sữa văng ra)
    (0, 1, 0, 1),
    # 755: "giao sản phẩm nhanh. sữa không được thơm lắm. khó tan"
    # -> Quality (sữa không thơm, khó tan), Shipping (+)
    (1, 0, 1, 0),
    # 756: "đặt hộp màu hồng nhưng giao hộp màu nâu thua"
    # -> Shipping (giao sai màu)
    (0, 0, 1, 0),
    # 757: "mình pha sữa bằng nước sôi nhưng vẫn bị vón cục và không tan hết sữa có vị nhạt"
    # -> Quality (vón cục dù pha đúng, vị nhạt)
    (1, 0, 0, 0),
    # 758: "mình không hài lòng vì sản phẩm mình nhận được hộp bị méo, nắp bị bật ra và sữa trong hộp rơi ra bên ngoài"
    # -> Packing (hộp méo, nắp bật, sữa rơi ra)
    (0, 0, 0, 1),
    # 759: "miếng lót nói có rảnh rốn nhưng mình không thấy có, không biết sản phẩm như thế nào nữa. như ngoài bìa vẽ rảnh rốn rõ ràng như bỉm thật không thấy, không biết có phải sản phẩm nhái hay không"
    # -> Quality (không có rảnh rốn như mô tả, nghi hàng nhái)
    (1, 0, 0, 0),
    # 760: "bao bì bị rách. mua 3 bịch nhưng 2 bịch bị rách rồi. không biết có ảnh hưởng đến chất lượng sản phẩm không"
    # -> Packing (2/3 bịch bao bì bị rách)
    (0, 0, 0, 1),
    # 761: "mình mua đơn sản phẩm của tiki trị giá 1tr 028k được tặng 1 trong những quà khuyến mãi trong đó có bộ mền +hà mã booby. nhưng hiện giờ mình chỉ nhận được hà mã bobby. tiki giao thiếu của mình mền bobby. vui lòng giao bổ sung. gọi phản hồi đường dây nóng nhưng không ai phản hồi"
    # -> Service (giao thiếu quà, không phản hồi đường dây nóng)
    (0, 1, 0, 0),
    # 762: "thấm hút kém. chỉ dùng được khoảng 1 tiếng là phải thay nếu không sẽ tràn. mình dùng được khoảng 10 miếng là con bị hăm. bỏ luôn cả bịch"
    # -> Quality (thấm hút kém, gây hăm - chất lượng rất tệ)
    (1, 0, 0, 0),
    # 763: "tiki giao sản phẩm rất rất chậm và phải gọi điện nhiều lần để hối mới giao sản phẩm. nhân viên giao sản phẩm thì cọc cằn"
    # -> Shipping (giao rất chậm, shipper cọc cằn)
    (0, 0, 1, 0),
    # 764: "đặt đơn gần 2 tháng mới giao, ngày nhận sản phẩm thì chưa giãn cách, tiki ngâm đơn không có trách nhiệm"
    # -> Shipping (ngâm đơn gần 2 tháng, vô trách nhiệm)
    (0, 0, 1, 0),
    # 765: "so với tã dán thì miếng lót này không tiện lợi lắm, phải sử dụng kèm tã vải dán vào, dễ bị tràn dịch. khá tốn công. được cái không bó em bé quá, thoáng hơn chút so với tã dán"
    # -> Quality (nhận xét về SP - tiện lợi kém hơn tã dán, dễ tràn)
    (1, 0, 0, 0),
    # 766: "mình ở tp hồ chí minh, đặt sản phẩm lúc kho tiki thành phố đang hết sản phẩm ngày hôm đó. thế là đơn này được chuyển đến kho hà nội. làm thời gian giao sản phẩm đến 1 tuần lễ"
    # -> Shipping (giao từ kho xa - 1 tuần, không tối ưu logistics)
    (0, 0, 1, 0),
    # 767: "mua hai gói nhưng khi quét mã vạch thì thế này mong bên tiki cho một lời giải thích"
    # -> Quality (mã vạch không ra kết quả đúng - nghi hàng giả), Service (yêu cầu giải thích)
    (1, 1, 0, 0),
    # 768: "bỉm giá rẻ, dùng cũng được... nhưng lần này thì không được ưng ý lắm vì mình đặt 2 bịch newborn 2 nhưng cửa hàng giao 1 bịch nb1 và 1 bịch nb2. bỉm mỏng mềm và dùng bị vón cục không như nb1"
    # -> Quality (bỉm giao nb1 thì mỏng và vón cục - chất lượng kém), Shipping (giao sai - 1 nb1 thay vì 2 nb2)
    (1, 0, 1, 0),
    # 769: "khi dùng bỉm cho con mình thấy da con bị dính 1, 2 viên bông nhỏ, thậm chí có lần bị dính chất hút ẩm trên da, chất trắng trong như thạch"
    # -> Quality (bỉm bị bung bông, chất thấm dính vào da con - nguy hiểm)
    (1, 0, 0, 0),
    # 770: "miếng lót mỏng hơn so với mua ở ngoài tiệm tạp hóa. bobby sản xuất nhiều loại mỏng dày khác nhau hay sao"
    # -> Quality (miếng lót mỏng hơn - chất lượng khác biệt)
    (1, 0, 0, 0),
    # 771: "giao đúng thời gian. dùng thích"
    # -> Quality (+), Shipping (+)
    (1, 0, 1, 0),
    # 772: "đảo. khuyến mãi không có thật"
    # -> Service (khuyến mãi lừa đảo, không có thật)
    (0, 1, 0, 0),
    # 773: "bộ đồ chơi tặng kèm khi mua bị thiếu mất 1 phụ kiện"
    # -> Service (thiếu phụ kiện trong quà tặng)
    (0, 1, 0, 0),
    # 774: "giao sản phẩm nhanh. nhưng sao miếng lót sài cho bé nhưng khi vệ sinh cho bé lại thấy có hạt nhựa trong, dẻo dính vào mông bé. thấy lo lắng"
    # -> Quality (hạt nhựa dính vào da con - nguy hiểm, lo lắng), Shipping (+)
    (1, 0, 1, 0),
    # 775: "đóng gói không kỹ lưỡng"
    # -> Packing (đóng gói không kỹ)
    (0, 0, 0, 1),
    # 776: "hình như không chất lượng nên bé mặc chưa hết 1 bịch bị hăm rồi"
    # -> Quality (bỉm kém chất lượng - gây hăm)
    (1, 0, 0, 0),
    # 777: "thật sự chán việc giao sản phẩm của tiki... đơn sản phẩm đặt 9/9 nhưng 24/10 mới nhận được... gần 2 tháng, tiki giờ cũng không nhưng nhiều khuyến mãi tốt như trước nữa dù sản phẩm vẫn chất lượng"
    # -> Quality (+), Service (ít khuyến mãi hơn), Shipping (giao gần 2 tháng)
    (1, 1, 1, 0),
    # 778: "tiki cho mình hỏi là mình có đặt 3 bịch bỉm moony từ 24/10. thấy màu cũ, mình không để ý đến bề mặt bên trong của bỉm, giờ tình cờ thấy nhưng màu nó vàng, sần sần vậy. đây là do bình thường vậy hay chất lượng bỉm kém?"
    # -> Quality (bỉm màu vàng sần - nghi chất lượng kém hoặc SP hết hạn)
    (1, 0, 0, 0),
    # 779: "bỉm quá cũ và bị mốc, bao bì thì bẩn, mình đến hôm nay mới phát hiện bỉm bên trong đã ố thành màu nâu, nsx là 2019. không ngờ official cửa hàng lại bán bỉm hết hạn cho khách. quá kinh khủng, không bao giờ mua lại!"
    # -> Quality (bỉm hết hạn, mốc, bao bì bẩn - cực kỳ nghiêm trọng)
    (1, 0, 0, 0),
    # 780: "giao sản phẩm quá chậm mặc dù đã hết giãn cách xã hội, đặt sản phẩm 04/10/2021, nhận sản phẩm 21/10/2021"
    # -> Shipping (giao chậm 17 ngày dù hết giãn cách)
    (0, 0, 1, 0),
    # 781: "mình dùng tã moony cho bé từ nhỏ... dạo gần đây bé mình hay bị nổi đỏ khi mang tã qua đêm. mình chuyển sang loại khác thì không có tình trạng này"
    # -> Quality (tã gây nổi đỏ - chất lượng thay đổi hoặc hàng kém)
    (1, 0, 0, 0),
    # 782: "màu bỉm úa màu, giống bỉm không chất lượng. đề nghị liên hệ người mua để đổi sản phẩm gấp"
    # -> Quality (màu úa - nghi kém chất lượng), Service (yêu cầu đổi)
    (1, 1, 0, 0),
    # 783: "đặt sản phẩm từ sớm 3/4 nhưng đến 10/4 không chuyển được sản phẩm... phải mua tạm ở chỗ khác cho con dùng"
    # -> Shipping (giao cực kỳ chậm giữa nội thành HN)
    (0, 0, 1, 0),
    # 784: "lần đầu tiên gặp tình huống này. thấy thùng sản phẩm nhẹ lạ lạ mở ra có 4 hộp bánh thay vì 2 bịch bỉm. mong tiki giải quyết sớm vì mình đang cần dùng"
    # -> Service (yêu cầu giải quyết), Shipping (giao hoàn toàn sai SP)
    (0, 1, 1, 0),
    # 785: "sao không có gấu bông tặng kèm tiki ơi"
    # -> Service (không có gấu bông tặng kèm)
    (0, 1, 0, 0),
    # 786: "tiki giao sản phẩm chậm quá. đơn của mình thường phải 4 ngày mới nhận được sản phẩm. hôm nay định đặt tiếp thì báo thứ 2 tuần sau mới được nhận"
    # -> Shipping (giao chậm thường xuyên)
    (0, 0, 1, 0),
    # 787: "hết hạn sử dụng"
    # -> Quality (SP hết hạn sử dụng)
    (1, 0, 0, 0),
    # 788: "lòng tã rất hẹp không được to bản như merries nên bé mặc cấn vào người và rất hay bị trào"
    # -> Quality (tã hẹp, gây cấn và trào - chất lượng không như kỳ vọng)
    (1, 0, 0, 0),
    # 789: "mình đặt 2 bịch bỉm moony. lịch giao sản phẩm vào ngày t2 15/10, mình nhận được tin nhắn sẽ giao chậm 1 ngày. ngày 16/10 bạn shipper hẹn mình giao buổi chiều nhưng mình không có nhà hẹn bạn sang hôm sau giao... 18/10 mình đợi cả ngày ở nhà cũng không thấy giao sản phẩm... gọi điện đến tổng đài và cũng chỉ được hứa hẹn... 48 tiếng không thấy bạn nào gọi điện giao sản phẩm. đơn đã giao chậm 3 ngày rồi"
    # -> Service (tổng đài chỉ hứa hẹn, không giải quyết), Shipping (shipper leo cây, giao chậm 3+ ngày)
    (0, 1, 1, 0),
    # 790: "thật sự trong thời gian gần đây tiki làm việc rất cẩu thả. luôn giao cho khách chất lượng kém. vừa mua xong bịch tã, mở ra đã thấy rách. cảm giác không hài lòng về độ chuyên nghiệp"
    # -> Quality (bịch tã rách - chất lượng kém), Packing (SP bị rách)
    (1, 0, 0, 1),
    # 791: "tả sài tốt, nhưng không có tặng gấu bông"
    # -> Quality (+), Service (không có gấu bông tặng)
    (1, 1, 0, 0),
    # 792: "đặt mua tã quần cho bé gái lại giao bé trai!"
    # -> Shipping (giao sai giới tính)
    (0, 0, 1, 0),
    # 793: "giao sản phẩm lâu đợi mọi mòn"
    # -> Shipping (giao rất chậm)
    (0, 0, 1, 0),
    # 794: "mình có đặt mua 3 bịch bỉm bé gái xl nhưng giao bỉm bé trai cho mình thì sao dùng, có nhắn để đổi sản phẩm nhưng chưa thấy phản hồi, mong cửa hàng giải quyết nhanh giúp mình"
    # -> Service (không phản hồi yêu cầu đổi), Shipping (giao sai giới tính)
    (0, 1, 1, 0),
    # 795: "tiki tự động hủy đơn của khách. chọn dịch vụ giao trong 2h thì tự ý đổi, hủy đơn và tạo đơn mới. giao sau tới 1 tuần lễ. không nhận được lời xin lỗi. bộ phận làm việc thiếu trách nhiệm"
    # -> Service (tự ý hủy và tạo đơn mới, không xin lỗi, vô trách nhiệm), Shipping (giao chậm 1 tuần)
    (0, 1, 1, 0),
    # 796: "cách đây vài ngày mình mua 2 bịch tã thấy được tặng kèm bộ gội xả, đến nay 2 bịch tã đã được giao nhưng quà tặng vẫn chưa nhận được"
    # -> Service (quà tặng chưa giao dù SP đã giao)
    (0, 1, 0, 0),
    # 797: "lần này tiki ẩu quá, sản phẩm giao trông như sản phẩm cũ, gói không cẩn thận bị sứt hết cả vỏ bao bì"
    # -> Quality (trông như SP cũ), Packing (gói không cẩn thận, vỏ bao bì sứt)
    (1, 0, 0, 1),
    # 798: "mua xong bỉm. h thấy giảm giá? cho e hỏi là bỉm đợt này sao khác bỉm cũ?"
    # -> Quality (bỉm thay đổi so với lần trước), Service (giá giảm sau khi mua - thiệt thòi)
    (1, 1, 0, 0),
    # 799: "trước giờ chỉ dùng nhãn moony. chọn mua ở tiki vì được miễn giao sản phẩm, giao đúng hẹn giá tốt hơn so với thị trường"
    # -> Quality (+), Service (+, giá tốt), Shipping (+)
    (1, 1, 1, 0),
    # 800: "đợt này nhìn khác đợt cũ, mua bỉm 4 túi bỉm con gái đã giao hết 3 túi con trai. hỏng hiểu sao luôn"
    # -> Quality (bỉm thay đổi ngoại hình), Shipping (giao sai - 3/4 túi bỉm con trai thay vì con gái)
    (1, 0, 1, 0),
    # 801: "đặt sản phẩm bị hủy... săn mãi được đơn thì hủy hết"
    # -> Service (đơn bị hủy liên tục, trải nghiệm mua sắm tệ)
    (0, 1, 0, 0),
    # 802: "gói sản phẩm ẩu tả, shipper thái độ như ..."
    # -> Shipping (shipper thái độ kém), Packing (đóng gói ẩu)
    (0, 0, 1, 1),
    # 803: "mình đặt cho nhà 2 đơn: 1 đơn từ 8/8... đặt 9/9 đến tận 1/10 mới giao. trong thời gian chờ đợi tiki giao... mình đã phải đặt thêm 2 thùng từ sàn thương mại điện tử khác và họ vẫn sắp xếp giao trong thời gian giãn cách. mình đã báo huỷ vì chờ đợi quá lâu nhưng tiki không hỗ trợ. mình rất không hài lòng"
    # -> Service (không hỗ trợ hủy đơn dù khách đợi quá lâu), Shipping (giao cực kỳ chậm gần 1 tháng)
    (0, 1, 1, 0),
    # 804: "sản phẩm chất lượng đúng như cam kết, giao sản phẩm sau dịch nhận được nhanh hơn mùa giãn cách. nhưng vài đơn sản phẩm tã đặt từ tháng 8 vẫn chưa nhận được. tiki kiểm tra lại giúp tôi"
    # -> Quality (+), Service (yêu cầu kiểm tra đơn tồn), Shipping (+, nhanh hơn)
    (1, 1, 1, 0),
    # 805: "đừng quấn băng keo lên bỉm nữa, dán kín hết cả bịch bỉm, lột ra xong bẩn hết cả bỉm, mong tiki gói sản phẩm đừng quấn băng keo nữa"
    # -> Packing (quấn băng keo lên bỉm gây bẩn - đóng gói không đúng cách)
    (0, 0, 0, 1),
    # 806: "giao sản phẩm sản phẩm quá tệ. khách khiếu nại thì trả lời máy móc, rập khuôn"
    # -> Service (CSKH trả lời máy móc), Shipping (giao tệ)
    (0, 1, 1, 0),
    # 807: "đóng chất lượng tốt ..."
    # -> Packing (+)
    (0, 0, 0, 1),
    # 808: "giao sản phẩm mùa dịch hơi bị lâu"
    # -> Shipping (giao chậm do dịch)
    (0, 0, 1, 0),
    # 809: "đơn sản phẩm hoàn thành sau sáu mươi ngày"
    # -> Shipping (giao cực kỳ chậm - 60 ngày)
    (0, 0, 1, 0),
    # 810: "giao hàng quá chậm. gần 3 tháng"
    # -> Shipping (giao cực kỳ chậm - gần 3 tháng)
    (0, 0, 1, 0),
    # 811: "đánh giá không tính điểm nhận xét về đóng gói đơn hàng chưa tốt, tiki tại sao không bọc bao đen hoặc đóng thùng nhưng chỉ gói ni lông kiếng trong suốt để lộ sản phẩm. làm lộ đơn sản phẩm của khách nữa. không có sự riêng tư"
    # -> Packing (đóng gói không kín đáo, để lộ nội dung sản phẩm)
    (0, 0, 0, 1),
    # 812: "hương vị ngon, thơm. đóng gói sản phẩm lần mua này không đóng trong thùng giấy, chỉ bọc mỗi bọc chống shock như này thì thấy không cẩn thận"
    # -> Quality (+), Packing (không đóng thùng giấy, chỉ bọc màng - không cẩn thận)
    (1, 0, 0, 1),
    # 813: "chất lượng giao sản phẩm quá kém, tôi đã mua sản phẩm ở đây rất nhiều lần, lần này sản phẩm giao làm tôi quá sốc, sữa bị móp, bung cả nắp, sữa đổ ra ngoài, giờ làm sao dám uống... tôi yêu cầu được đền bù sản phẩm khác ngay lập tức"
    # -> Service (yêu cầu đền bù), Packing (sữa móp, bung nắp, đổ ra)
    (0, 1, 0, 1),
    # 814: "giờ mua sản phẩm tiki chán lắm. cũng thẻ tín dụng của mình nhưng nó báo rủi ro thanh toán không an toàn. trong khi thẻ đó mua thì vẫn bình thường"
    # -> Service (cổng thanh toán tiki báo lỗi rủi ro - trải nghiệm tệ)
    (0, 1, 0, 0),
    # 815: "lần nào quét mã qr tạo mật khẩu cũng không được. 6 ký tự, 1 chữ viết hoa, 1 số nhưng không thể nào được lần nào cũng vậy"
    # -> Quality (không quét được mã QR - nghi hàng giả/lỗi SP)
    (1, 0, 0, 0),
    # 816: "giá bán cao. đợi mãi giá rẻ chút không thấy giảm để mua"
    # -> Service (giá cao, không có chương trình giảm giá)
    (0, 1, 0, 0),
    # 817: "mua 2 hộp, 1 hộp bị bung nắp, không biết là do đâu"
    # -> Packing (1/2 hộp bung nắp)
    (0, 0, 0, 1),
    # 818: "khi mở hộp bị bung nắp, hộp bị móp méo"
    # -> Packing (bung nắp, hộp móp méo)
    (0, 0, 0, 1),
    # 819: "mua 3 hộp về một hộp bung seal đổ be bét ra cả"
    # -> Packing (1/3 hộp bung seal, sữa đổ ra)
    (0, 0, 0, 1),
    # 820: "dịch vụ quá tệ, đóng gói ẩu"
    # -> Service (DV tệ), Packing (đóng gói ẩu)
    (0, 1, 0, 1),
    # 821: "giao chất lượng kém chất lượng, bị gãy móc, thất vọng"
    # -> Quality (SP bị gãy móc - chất lượng kém)
    (1, 0, 0, 0),
    # 822: "những người làm việc như thế này tiki nên siết mạnh tay... đặt 1 đường giao 1 nẻo, khác màu khác mẫu không đáng với giá tiền. đặt 2 chiếc xanh và hồng thì giao 2 chiếc vàng, mẫu mã cũng không giống"
    # -> Shipping (giao sai màu, sai mẫu - 2/2 sản phẩm)
    (0, 0, 1, 0),
    # 823: "đặt màu hồng lại giao màu vàng nhưng không hỏi ý khách. mình muốn trả lại sản phẩm thì liên hệ như thế nào?"
    # -> Service (muốn trả hàng), Shipping (giao sai màu)
    (0, 1, 1, 0),
    # 824: "mình đặt màu xanh nhưng cửa hàng giao màu đỏ. đánh giá chất liệu và kiểu dáng không đẹp như hình demo. khá thất vọng"
    # -> Quality (chất liệu/kiểu dáng kém hơn hình), Shipping (giao sai màu)
    (1, 0, 1, 0),
    # 825: "tại sao tôi mua màu hồng nhưng lại giao màu vàng?"
    # -> Shipping (giao sai màu)
    (0, 0, 1, 0),
    # 826: "giao sản phẩm không đúng màu và sản phẩm lỗi"
    # -> Quality (SP lỗi), Shipping (giao sai màu)
    (1, 0, 1, 0),
    # 827: "đặt màu này nhưng giao màu kia"
    # -> Shipping (giao sai màu)
    (0, 0, 1, 0),
    # 828: "hơi yếu, không cứng cáp như tưởng tượng"
    # -> Quality (SP yếu, không đạt kỳ vọng)
    (1, 0, 0, 0),
    # 829: "mình đặt màu nâu kem lại giao màu hồng. con mình con trai, bực mình"
    # -> Shipping (giao sai màu)
    (0, 0, 1, 0),
    # 830: "sản phẩm mình mua chưa được 1 tháng thì khóa đã bị hỏng. liên hệ bảo hành thì từ chối bảo hành. mình đòi trả sản phẩm hoàn tiền theo cam kết thì mới chịu đổi lại khóa. vấn đề đơn giản như xử lý mất hơn 1 tháng, sau 1 tháng thì đổi lại khóa và dây nhưng phí giao sản phẩm người nhận chịu 30k, khác gì tự mua khóa mới. phục vụ kém"
    # -> Quality (SP hỏng sau 1 tháng), Service (bảo hành tệ, kéo dài 1 tháng, bắt khách chịu phí giao)
    (1, 1, 0, 0),
    # 831: "đặt màu hồng nhưng giao màu xanh. cửa hàng mình bị làm sao á"
    # -> Shipping (giao sai màu)
    (0, 0, 1, 0),
    # 832: "ghế này chỉ tạm ổn, nhiều điểm cần khắc phục: phần chân chưa được chắc chắn, thiếu chỗ doãi chân cho bé dưới 1 tuổi chưa với tới khấc gác chân, miếng da lót lưng khá trơn, bé hay tuột xuống"
    # -> Quality (ghế nhiều nhược điểm - không chắc, thiếu chỗ gác chân, dễ tuột)
    (1, 0, 0, 0),
    # 833: "đặt sản phẩm màu xanh, giao màu hồng. chất lượng nhựa nhìn kém lắm! không chắc chắn"
    # -> Quality (nhựa kém, không chắc), Shipping (giao sai màu)
    (1, 0, 1, 0),
    # 834: "miêu tả thương hiệu sản phẩm là umoo nhưng thực tế thương hiệu là high chair xuất xứ china. đặt màu xanh navy nhưng giao màu xanh (khác)"
    # -> Quality (thương hiệu không đúng mô tả), Service (mô tả sai thương hiệu), Shipping (giao sai màu)
    (1, 1, 1, 0),
    # 835: "không nâng hạ được chỉ được sử dụng 1 mức, khung sườn yếu không như quảng cáo"
    # -> Quality (SP không đúng như quảng cáo - không nâng hạ được, yếu)
    (1, 0, 0, 0),
    # 836: "giao sai màu, đã nhắn với cửa hàng trước vẫn sai màu. đặt tặng người ta nhưng sai màu người ta thích. lần thứ 2 đặt bên cửa hàng và giao sai cả 2. tuy nhiên, ghế ngồi cũng tạm ổn"
    # -> Quality (+, tạm ổn), Shipping (giao sai màu 2 lần liên tiếp)
    (1, 0, 1, 0),
    # 837: "ghế không chắc chắn, bánh xe có nhưng khó sử dụng"
    # -> Quality (ghế không chắc, bánh xe khó dùng)
    (1, 0, 0, 0),
    # 838: "mình đặt màu nâu kem nhưng cửa hàng lại giao màu xanh. chỉ không hài lòng về màu sắc được giao"
    # -> Shipping (giao sai màu)
    (0, 0, 1, 0),
    # 839: "sản phẩm rất yếu"
    # -> Quality (SP rất yếu)
    (1, 0, 0, 0),
    # 840: "tạm ổn được, tiền nào của đó"
    # -> Quality (+, tạm ổn)
    (1, 0, 0, 0),
    # 841: "dây đai buộc trẻ vô dụng, không cố định được, rất lỏng lẻo"
    # -> Quality (dây đai lỏng lẻo, không cố định được - không an toàn)
    (1, 0, 0, 0),
    # 842: "giá cao hơn so bới"
    # -> Service (giá cao)
    (0, 1, 0, 0),
    # 843: "đánh giá không tính điểm linh hoạt giờ giao dùm, cứ buổi trưa người ta ngủ trưa thì giao? từ đây không đặt sản phẩm tiki nữa"
    # -> Shipping (shipper giao vào giờ ngủ trưa - không linh hoạt)
    (0, 0, 1, 0),
    # 844: "giá cao hơn sản phẩm bán bên ngoài mình đặt tiki xong ra siêu thị thấy bán có 60 ngàn hộp loại này"
    # -> Service (giá tiki cao hơn ngoài siêu thị)
    (0, 1, 0, 0),
    # 845: "bình thường chưa sử dụng"
    # -> (chưa dùng, không đánh giá)
    (0, 0, 0, 0),
    # 846: "đóng gói cẩn thận"
    # -> Packing (+)
    (0, 0, 0, 1),
    # 847: "sản phẩm bình thường nhưng mua ở concung giá rẻ hơn 10 nghìn"
    # -> Quality (+), Service (giá tiki cao hơn concung)
    (1, 1, 0, 0),
    # 848: "sản phẩm cao tiền nhưng gói sản phẩm vận chuyển tệ, nhận sản phẩm xong thấy gói sản phẩm rách tùm lum. đang trong dịch nên khi nhận sản phẩm xịt cồn ướt bọc cho an toàn, nhưng rách vậy nên xịt bị thấm vào trong. dùng cho bé rất mất vệ sinh"
    # -> Quality (bị nhiễm bởi cồn xịt do bao bì rách - mất vệ sinh), Service (giá cao), Packing (bao bì rách)
    (1, 1, 0, 1),
    # 849: "đặt trên app là 63 miếng và bịch tã vuông khi nhận là 62 và bịch tã không giống hình ảnh"
    # -> Quality (số lượng và hình dạng khác hình ảnh), Shipping (giao sai mô tả)
    (1, 0, 1, 0),
    # 850: "đặt sản phẩm loại newborn 63 pcs organic, nhưng giao sản phẩm là loại 62 pcs loại thường. đề nghị đổi trả sản phẩm"
    # -> Service (yêu cầu đổi), Shipping (giao sai loại)
    (0, 1, 1, 0),
    # 851: "không hiểu sao mình dùng cho con mình bé bị hăm, hăm đỏ hết cả mông lên bé thay liên tục trong ngày... dùng vẫn bỉm này mua ở cửa hàng khác trước nay vẫn bình thường. cửa hàng nên kiểm tra lại chất lượng sản phẩm"
    # -> Quality (bỉm gây hăm nặng, khác biệt so với mua tại shop khác - nghi chất lượng kém)
    (1, 0, 0, 0),
    # 852: "mình đặt tikinow từ tối hôm trước nhưng mình bị trễ hẹn giao mất 2h, quà tặng hẹn 13/6/2019 giao sản phẩm nhưng 17/6/2019 mới giao và không có 1 thông báo trễ hẹn gì với khách sản phẩm"
    # -> Service (quà tặng giao trễ không thông báo), Shipping (giao trễ 2h, quà trễ 4 ngày)
    (0, 1, 1, 0),
    # 853: "mình mua 2 gói moony thì giao 2 gói merries"
    # -> Shipping (giao hoàn toàn sai nhãn hiệu)
    (0, 0, 1, 0),
    # 854: "mình vừa nhận được bỉm nhưng thất vọng quá, gói bỉm bị rách toang không hiểu sao tiki lại không duyệt sản phẩm khi chuyển cho khách"
    # -> Packing (gói bỉm bị rách toang)
    (0, 0, 0, 1),
    # 855: "tã vón cục khi bé tè, mua ở bigc hay cũng vậy. chỉ mỗi tiki trading là 5"
    # -> Quality (tã vón cục - chất lượng SP), Shipping (+)
    (1, 0, 1, 0),
    # 856: "tôi đặt mua rubik lập phương nhưng khi nhận được thì sản phẩm là rubik ghép từ các mảnh gỗ, tôi có thể đổi hoặc trả sản phẩm được không?"
    # -> Quality (SP khác hoàn toàn - rubik gỗ thay vì lập phương), Service (yêu cầu đổi/trả)
    (1, 1, 0, 0),
    # 857: "sản phẩm khô keo rớt tè le ra cũng không đáng trách lắm nhưng lấy lại sản phẩm rồi im ỉm luôn cả tuần không tăm hơi thì tệ quá"
    # -> Quality (SP khô keo, rớt), Service (lấy lại SP nhưng không phản hồi sau 1 tuần)
    (1, 1, 0, 0),
    # 858: "đây là các khối gỗ lắp ghép, không phải rubik, mọi người nên xem kỹ để không bị mua nhầm"
    # -> Quality (SP không phải rubik như mô tả - gây hiểu lầm)
    (1, 0, 0, 0),
    # 859: "tưởng như rubik xoay hóa ra không phải. như xếp hình bằng gỗ thì đúng hơn. lúc đầu nhận được sản phẩm nhưng tưởng sản phẩm lỗi"
    # -> Quality (SP không đúng như kỳ vọng từ mô tả)
    (1, 0, 0, 0),
    # 860: "sữa để cho trẻ bị dị ứng đạm bò uống, mua về uống lại bị dị ứng lại. cửa hàng bán sản phẩm không đúng chất lượng, giờ trả lại thì không được"
    # -> Quality (SP không đúng chất lượng, gây dị ứng), Service (không cho trả hàng)
    (1, 1, 0, 0),
    # 861: "mua nhiều lần nhưng lần này đóng gói tệ nhận sản phẩm thì bị như này"
    # -> Packing (đóng gói tệ)
    (0, 0, 0, 1),
    # 862: "mình mua size lớn nhưng tiki giao size nhỏ?"
    # -> Shipping (giao sai size)
    (0, 0, 1, 0),
    # 863: "có mùi hôi khó chịu. kém cho trẻ chơi"
    # -> Quality (SP có mùi hôi, không phù hợp cho trẻ)
    (1, 0, 0, 0),
    # 864: "sử dụng chục bịch rồi nhưng chưa bao giờ bỉm quần size này bị tràn. mới tè xíu đã tràn, tè lần đầu cũng tràn ngược ướt hết áo quần"
    # -> Quality (bỉm tràn ngay từ lần đầu - chất lượng kém hơn mọi lần)
    (1, 0, 0, 0),
    # 865: "sao đơn trên 600 ngàn nhưng không có quà tặng kèm theo, sao để tặng ghế nhưng"
    # -> Service (không có quà tặng dù đủ điều kiện)
    (0, 1, 0, 0),
    # 866: "sản phẩm sản phẩm không đạt chất lượng, có mùi rất hắc sau khi bé tè, bé mặc khó chịu"
    # -> Quality (tã có mùi hắc sau khi tè, gây khó chịu)
    (1, 0, 0, 0),
    # 867: "mình mua đơn sản phẩm 1 triệu 2 nhưng không có quà tặng kèm gì"
    # -> Service (không có quà tặng dù mua đủ điều kiện)
    (0, 1, 0, 0),
    # 868: "quảng cáo là khuyến mãi sofa cho đơn 499k, nhưng nhận về không thấy khuyến mãi đâu chỉ có bỉm"
    # -> Service (không nhận được khuyến mãi sofa như quảng cáo)
    (0, 1, 0, 0),
    # 869: "không giống với sản phẩm chính hãng"
    # -> Quality (SP khác sản phẩm chính hãng - nghi hàng giả)
    (1, 0, 0, 0),
    # 870: "đóng gói sản phẩm sơ sài, chất lượng tả tốt"
    # -> Quality (+), Packing (đóng gói sơ sài)
    (1, 0, 0, 1),
    # 871: "không có quà tặng kèm như quảng cáo"
    # -> Service (không nhận được quà như quảng cáo)
    (0, 1, 0, 0),
    # 872: "bịch bỉm bị rách ở dưới đáy"
    # -> Packing (bịch bỉm bị rách đáy)
    (0, 0, 0, 1),
    # 873: "sản phẩm có sản phẩm nhái nhưng tem dán chống sản phẩm giả bung cả 2 đầu rồi sao"
    # -> Quality (tem chống giả bị bung - nghi hàng giả)
    (1, 0, 0, 0),
    # 874: "đặt cho bé 0+ nhưng gửi 3+, nhắn tin báo cửa hàng gửi sai cũng không thấy phản hồi cho khách lấy 1 câu"
    # -> Service (không phản hồi), Shipping (giao sai độ tuổi 3+ thay vì 0+)
    (0, 1, 1, 0),
    # 875: "tôi đặt mua hai hộp nhưng cửa hàng gửi 1 hộp nhưng vẫn lấy giá 1 hộp (?) "
    # -> Service (tính tiền 2 hộp nhưng giao 1 - gian lận), Shipping (giao thiếu)
    (0, 1, 1, 0),
    # 876: "giao sản phẩm nhanh, chất lượng tốt"
    # -> Quality (+), Shipping (+)
    (1, 0, 1, 0),
    # 877: "chả hiểu sao lại dám nói đây là khăn giấy ướt luôn. mở ra dùng thấy khô, chỉ hơi ẩm một chút, gần như khô như giấy ăn vậy. phí tiền không có lần sau"
    # -> Quality (khăn ướt gần như khô - chất lượng cực kém)
    (1, 0, 0, 0),
    # 878: "mình đặt 2set 20 gói la 472k mà cửa hàng giao cho mình có 10 gói nhưng vẫn thu tiền 472k"
    # -> Service (tính tiền đầy đủ nhưng giao thiếu - gian lận), Shipping (giao thiếu)
    (0, 1, 1, 0),
    # 879: "không hài lòng. đặt 2set 20 gói mà giao 1set 10 gói lấy tiền 472k"
    # -> Service (giao thiếu nhưng tính tiền đủ), Shipping (giao thiếu)
    (0, 1, 1, 0),
    # 880: "chất lượng tốt phù hợp với giá tiền"
    # -> Quality (+), Service (+, giá)
    (1, 1, 0, 0),
    # 881: "mình không thích giao sản phẩm từ ninjavan. cứ yêu cầu mang chứng minh thư ra chụp lại thì mới cho lấy sản phẩm. chứng minh thư không phải muốn chụp là được... đi đảo thì sao?"
    # -> Shipping (đơn vị vận chuyển yêu cầu chụp CMND - vi phạm quyền riêng tư)
    (0, 0, 1, 0),
    # 882: "vừa nhận sản phẩm nhưng thấy hạn sử dụng ngắn. nhưng sao mặt kinh khủng"
    # -> Quality (HSD ngắn)
    (1, 0, 0, 0),
    # 883: "đóng gói sơ sài mắm bị rỉ ra ngoài mùi rất khó chịu, đặt mua cùng bột nêm hết sản phẩm cũng không báo nhưng chỉ gửi mỗi nước mắm"
    # -> Service (hết hàng không báo, giao thiếu), Packing (đóng gói sơ sài, mắm rỉ ra)
    (0, 1, 0, 1),
    # 884: "bình thường. giao sản phẩm khá chậm"
    # -> Shipping (giao khá chậm)
    (0, 0, 1, 0),
    # 885: "sản phẩm như hình nhưng vị hơi mặn, các mình xem xét mua bổ sung cho con"
    # -> Quality (vị hơi mặn)
    (1, 0, 0, 0),
    # 886: "sản phẩm đóng gói cẩn thận, đợt trước mình mua rất tốt, đợt này cửa hàng giao thiếu sản phẩm cho mình 5 gói"
    # -> Shipping (giao thiếu 5 gói), Packing (+)
    (0, 0, 1, 1),
    # 887: "chưa quét được mã vạch, không biết có phải sản phẩm chính hãng không, sợ mua phải sản phẩm giả"
    # -> Quality (không quét được mã vạch - nghi hàng giả)
    (1, 0, 0, 0),
    # 888: "mẫu không đúng quảng cáo. không có tem của nhà phân phối và không có tem chống sản phẩm giả"
    # -> Quality (không có tem phân phối, không có tem chống giả - nghi hàng giả)
    (1, 0, 0, 0),
    # 889: "không tem mác cảm nhận như sản phẩm giả vậy"
    # -> Quality (không có tem mác - nghi hàng giả)
    (1, 0, 0, 0),
    # 890: "sản phẩm không đúng trong hình"
    # -> Quality (SP không đúng hình - giao sai/khác)
    (1, 0, 0, 0),
    # 891: "sao mình thấy sản phẩm hình minh họa thì có dán tem lưu hành, và tờ giấy hướng dẫn bảo quản nhưng khi mình nhận thì lại không"
    # -> Quality (thiếu tem lưu hành và hướng dẫn bảo quản - nghi hàng giả)
    (1, 0, 0, 0),
    # 892: "không dẻo và sử dụng bị bở như đất sét thông thường"
    # -> Quality (SP không đạt chất lượng - không dẻo, bở)
    (1, 0, 0, 0),
    # 893: "quá nhỏ, không tưởng tượng nhỏ vậy"
    # -> Quality (SP nhỏ hơn kỳ vọng - mô tả không rõ)
    (1, 0, 0, 0),
    # 894: "mua sản phẩm của umoo nhưng bán sản phẩm như này, đưa hình một đằng bán một nẻo, lỡ rồi quá tệ"
    # -> Quality (SP không đúng hình ảnh quảng cáo)
    (1, 0, 0, 0),
    # 895: "trời ơi chất lượng quá tệ. bộ này bán giá 5k nhưng đáng chứ 25k là không chấp nhận được luôn. cục xúc xắc hình không giống hình in trên tờ giấy. dán hình trên cục xúc sắc quá cẩu thả"
    # -> Quality (SP chất lượng cực kém, dán hình cẩu thả), Service (giá không đáng)
    (1, 1, 0, 0),
    # 896: "nv giao sản phẩm rất nhiệt tình, vui vẻ. nhưng sản phẩm cửa hàng đóng gói sản phẩm bẩn thiếu 3 hột xí ngầu bầu cua. không sử dụng được sản phẩm"
    # -> Shipping (+), Packing (đóng gói bẩn, thiếu 3 hột)
    (0, 0, 1, 1),
    # 897: "tui thấy tui đã bị rõ ràng là xúc xắc đá nhưng mua về coi lại là giấy"
    # -> Quality (SP giao sai chất liệu - giấy thay vì đá)
    (1, 0, 0, 0),
    # 898: "sản phẩm tệ không giống hình nói chung là không nên mua"
    # -> Quality (SP tệ, không giống hình)
    (1, 0, 0, 0),
    # 899: "có 1 túi bị rách nên ướt làm chèm nhẹp mấy túi khác"
    # -> Packing (1 túi bị rách làm ướt SP khác)
    (0, 0, 0, 1),
    # 900: "hết hạn sử dụng từ 5/2/2021"
    # -> Quality (SP hết hạn sử dụng - nghiêm trọng)
    (1, 0, 0, 0),
    # 901: "đánh giá không tính điểm tui chưa nhận được sản phẩm và cũng không có điện thoại thông báo cho tui ra nhận sản phẩm sao lại thông báo đã giao thành công. đơn sản phẩm giao cho ai?"
    # -> Shipping (shipper xác nhận giao ảo, không giao thực tế)
    (0, 0, 1, 0),
    # 902: "mình đặt mua sữa tắm gội giao nhầm lotion, bé nhà mình không biết lại bóc sản phẩm mất rồi. cửa hàng giao không check kỹ đơn. chán!"
    # -> Shipping (giao nhầm SP - sữa tắm gội thay vì lotion)
    (0, 0, 1, 0),
    # 903: "sản phẩm không được giao kèm trong đơn. kiện sản phẩm chỉ có chai nước giặt. đề nghị tiki kiểm tra lại"
    # -> Service (yêu cầu kiểm tra), Shipping (giao thiếu SP trong đơn)
    (0, 1, 1, 0),
    # 904: "đã scan barcode không tìm được trên trang chính hãng"
    # -> Quality (barcode không ra kết quả - nghi hàng giả)
    (1, 0, 0, 0),
    # 905: "tại sao nhận sản phẩm phải chụp hình người nhận lại? quy định mới của tiki hả"
    # -> Shipping (đơn vị vận chuyển yêu cầu chụp hình - vi phạm quyền riêng tư)
    (0, 0, 1, 0),
    # 906: "sản phẩm dùng không thích lắm"
    # -> Quality (SP không vừa ý)
    (1, 0, 0, 0),
    # 907: "giao sản phẩm nhanh. chưa sử dụng sản phẩm"
    # -> Shipping (+)
    (0, 0, 1, 0),
    # 908: "lót phơi nắng 2 ngày chưa khô"
    # -> Quality (SP lót khó khô - chất lượng không đạt)
    (1, 0, 0, 0),
    # 909: "tấm lót cứng, lâu khô. quần cạp thấp"
    # -> Quality (tấm lót cứng, lâu khô, quần cạp thấp - nhiều nhược điểm)
    (1, 0, 0, 0),
    # 910: "miếng lót to dày chập 2 miếng may lại, nói chung mua thử cho bé con để tiết kiệm nhưng mặc tội con quá, to nặng đối với trẻ sơ sinh"
    # -> Quality (SP to, nặng không phù hợp cho trẻ sơ sinh)
    (1, 0, 0, 0),
    # 911: "rất không hài lòng! đề nghị tiki xem lại nhà cung cấp, trong 1 tuần nhưng nhận 2 đơn liền không hài lòng. sản phẩm không đúng theo mẫu. đề nghị đổi sản phẩm đúng mẫu, nếu không có sản phẩm thì báo hủy đơn, chứ đừng tự ý thay bằng mẫu khác. chưa kể loại này ngoài siêu thị bán 65k, nhưng loại theo đơn là 89k"
    # -> Quality (SP không đúng mẫu), Service (tự ý đổi SP không hỏi, giá cao hơn siêu thị, yêu cầu đổi đúng mẫu)
    (1, 1, 0, 0),
    # 912: "cửa hàng bán giá cao. không biết giá gốc 190k lấy từ đâu nhưng sau giảm vẫn cao hơn các chỗ khác, gây hiểu nhầm cho người mua"
    # -> Service (giá cao, gây hiểu lầm về mức giảm giá)
    (0, 1, 0, 0),
    # 913: "quá tệ trẻ con nó không thèm ăn"
    # -> Quality (bé không chịu dùng SP - SP không phù hợp)
    (1, 0, 0, 0),
    # 914: "sản phẩm khi nhận được cũ, bẩn không dám cho con dùng"
    # -> Quality (SP cũ, bẩn - không an toàn)
    (1, 0, 0, 0),
    # 915: "giao sản phẩm nhanh chưa sử dụng nên chưa biết bé thích không"
    # -> Shipping (+)
    (0, 0, 1, 0),
    # 916: "bao bì quá dơ bên ngoài, nhìn sản phẩm có vẻ cũ, để lâu. không nên mua"
    # -> Quality (bao bì dơ, SP trông cũ)
    (1, 0, 0, 0),
    # 917: "mua sản phẩm cho da nhạy cảm gửi sản phẩm cho da thường là ntn?"
    # -> Shipping (giao sai loại SP - da nhạy cảm thay vì da thường)
    (0, 0, 1, 0),
    # 918: "khi mở hộp sữa không thấy muỗng, đã kiểm tra kỹ trong hộp... bạn nào mua sữa dòng mới total, nếu cũng gặp vấn đề này thì để lại bình luận"
    # -> Quality (thiếu muỗng trong hộp - lỗi SP hoặc đã bị lấy)
    (1, 0, 0, 0),
    # 919: "mua sữa khui ra bị tét hết 1 bịt"
    # -> Packing (sữa khui ra bị tét bịch - đóng gói kém)
    (0, 0, 0, 1),
    # 920: "giao sản phẩm quá lâu. mình báo hủy thì mới chịu giao. không dám đặt sản phẩm tiki nữa luôn á"
    # -> Shipping (giao cực kỳ chậm, phải báo hủy mới chịu giao)
    (0, 0, 1, 0),
    # 921: "mới mở hộp thì tem abbott bị thế này đây. chưa hết, bình thường mình thanh toán online nên ở ngoài hộp tiki không ghi thông sản phẩm, thế shipper lại biết bên trong có gì... nghi ngờ sản phẩm bị đánh tráo"
    # -> Quality (tem bị hỏng, nghi SP bị đánh tráo), Shipping (shipper biết nội dung hộp - nghi đánh tráo)
    (1, 0, 1, 0),
    # 922: "sản phẩm lỗi không sử dụng được"
    # -> Quality (SP lỗi, không dùng được)
    (1, 0, 0, 0),
    # 923: "tốc độ giao chất lượng kém. khả năng giải quyết đơn sản phẩm trong mùa dịch tệ hơn các sàn thương mại điện tử khác nhiều. các sàn tmdt khác đã hoạt động trở lại nhưng tiki vẫn trùm mềm"
    # -> Service (xử lý đơn kém hơn sàn khác trong mùa dịch), Shipping (tốc độ giao kém)
    (0, 1, 1, 0),
    # 924: "sản phẩm dùng bình thường"
    # -> Quality (+, bình thường)
    (1, 0, 0, 0),
    # 925: "nghe nói sữa ensure của mỹ 2 năm đã không sản xuất, bên mỹ sữa này toàn sữa giả"
    # -> Quality (nghi hàng giả - sữa ensure không còn sản xuất ở Mỹ)
    (1, 0, 0, 0),
    # 926: "tiki gói sản phẩm quá cẩu thả. mình mua sản phẩm ở tiki nhiều lần nhưng chưa khi nào thấy tiki dùng xốp để chống sốc cho sản phẩm. hộp sữa giao cho khách thường xuyên bị móp"
    # -> Packing (đóng gói cẩu thả, không có xốp chống sốc, hộp thường xuyên bị móp)
    (0, 0, 0, 1),
    # 927: "đóng gói ẩu. không bọc chống sốc gì cả để nguyên hộp sữa vào 1 hộp carton. vận chuyển thì lâu mua rất nhiều lần nhưng chưa bao giờ gặp phải trường hợp này"
    # -> Shipping (giao lâu), Packing (đóng gói ẩu, không có chống sốc)
    (0, 0, 1, 1),
    # 928: "mình chấm 1 sao... tiknow nhưng cũng mãi 1 hôm sau mới nhận được... mình nhận ra hộp sữa này bốc mùi kinh khủng, mùi từ nắp hộp... bị gián, chuột đái vào và thêm bụi... không thể nghĩ là quá trình bảo quản ở kho của tiki lại tệ đến vậy. sp này thì nay đã hết hạn"
    # -> Quality (sữa bốc mùi hôi do bảo quản kho tệ, SP hết hạn), Shipping (tiknow giao chậm 1 ngày)
    (1, 0, 1, 0),
    # 929: "đóng gói giao sản phẩm không thể chấp nhận được!"
    # -> Packing (đóng gói không thể chấp nhận)
    (0, 0, 0, 1),
    # 930: "giao sản phẩm đi xa nhưng tiki không bọc sản phẩm bằng nilon chống sốc, nên vỏ hộp sữa bị méo"
    # -> Packing (không bọc nilon chống sốc, hộp bị méo)
    (0, 0, 0, 1),
    # 931: "sản phẩm chất lượng nhưng giao sản phẩm siêu lâu"
    # -> Quality (+), Shipping (giao siêu chậm)
    (1, 0, 1, 0),
    # 932: "lần này vận chuyển bên tiki rất tệ, giao thì lâu, sữa nhưng bị móp nữa"
    # -> Shipping (giao lâu), Packing (sữa bị móp)
    (0, 0, 1, 1),
    # 933: "dạo này tiki giao sản phẩm chậm"
    # -> Shipping (giao chậm)
    (0, 0, 1, 0),
    # 934: "trễ hạn nhưng tiki không phản hồi ngày giao sản phẩm mới"
    # -> Service (không phản hồi), Shipping (giao trễ không thông báo)
    (0, 1, 1, 0),
    # 935: "tạm ổn được, giá bình thường như ở ngoài chứ không rẻ hơn"
    # -> Quality (+), Service (giá không rẻ hơn)
    (1, 1, 0, 0),
    # 936: "đề nghị hoàn tiền lại vì sữa cận đát và thùng không đẹp"
    # -> Quality (sữa cận date), Service (yêu cầu hoàn tiền), Packing (thùng không đẹp)
    (1, 1, 0, 1),
    # 937: "bị hôi uống mùi như hết hạn"
    # -> Quality (sữa có mùi hôi như hết hạn)
    (1, 0, 0, 0),
]

# Áp dụng labels cho index 600-999
for i, (q, s, sh, p) in enumerate(manual_labels):
    idx = 600 + i
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

print("Hoan thanh label 400 dong (index 600-999)!")
print()
print("=== THONG KE 1000 DONG DAU (0-999) ===")
first_1000 = df.head(1000)
for col in ["Quality", "Service", "Shipping", "Packing"]:
    count = int(first_1000[col].sum())
    print(f"  {col}: {count}/1000 dong co nhan 1 ({count/10:.1f}%)")

print()
print("=== THONG KE RIENG 400 DONG MOI (600-999) ===")
batch = df.iloc[600:1000]
for col in ["Quality", "Service", "Shipping", "Packing"]:
    count = int(batch[col].sum())
    print(f"  {col}: {count}/400 dong co nhan 1 ({count/4:.1f}%)")
