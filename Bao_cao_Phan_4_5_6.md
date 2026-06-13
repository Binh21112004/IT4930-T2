# CHƯƠNG II. Cách tiếp cận (Tiếp theo)

## 4. Lựa chọn mô hình, lý thuyết, phương pháp

### a) Định dạng lại bài toán (Reformulate problem)
- **Input:** Dữ liệu dạng văn bản là các bình luận, phản hồi tiêu cực (đánh giá từ 3 sao trở xuống) của người dùng trên các nền tảng thương mại điện tử. Dữ liệu này đã qua bước tiền xử lý, chuẩn hóa unicode, dấu câu, loại bỏ stopwords và từ nhiễu.
- **Output:** Nhãn dự đoán của bình luận, phân loại vào 1 trong 4 danh mục: 
  - `Quality` (0): Phản ánh về chất lượng sản phẩm.
  - `Service` (1): Phản ánh về dịch vụ khách hàng (thái độ người bán, tư vấn).
  - `Packing` (2): Phản ánh về quy cách đóng gói.
  - `Shipping` (3): Phản ánh về khâu vận chuyển.

### b) Lý thuyết và phương pháp
Trong bài toán này, nhóm em đã thử nghiệm hai hướng tiếp cận chính: Học máy truyền thống (Machine Learning) và Học sâu (Deep Learning).

**Học máy (Machine Learning):**
- **Random Forest (RF):** Là một thuật toán học tập tổng hợp (ensemble) dựa trên nhiều cây quyết định. Nhóm sử dụng `n_estimators=200` và `class_weight='balanced'` để xử lý tình trạng mất cân bằng dữ liệu giữa các lớp.
- **Support Vector Machine (SVM):** Tìm một siêu phẳng (hyperplane) tối ưu để phân tách các lớp dữ liệu. Nhóm sử dụng `kernel='linear'`, rất phù hợp với dữ liệu văn bản thưa (sparse) khi được kết hợp cùng kỹ thuật trích xuất đặc trưng TF-IDF mức độ bigram.
- **Logistic Regression (LR):** Mô hình phân loại cơ bản, thiết lập `class_weight='balanced'` và `max_iter=1000`. Cung cấp xác suất cho từng dự đoán.

**Học sâu (Deep Learning):**
Các mô hình học sâu đều đi qua một lớp nhúng `Embedding` (`EMBEDDING_DIM = 48`, giới hạn kích thước từ vựng `NUM_WORDS = 8000`).
- **LSTM (Long Short Term Memory):** Mạng nơ-ron hồi quy có khả năng học các phụ thuộc xa trong chuỗi văn bản. Kiến trúc: Embedding -> SpatialDropout1D -> Conv1D (kèm L2) -> MaxPooling1D -> LSTM -> Dropout -> Dense.
- **GRU (Gated Recurrent Unit):** Biến thể tối ưu và đơn giản hơn của LSTM. Kiến trúc: Embedding -> SpatialDropout1D -> Bidirectional(GRU) -> Dropout -> Dense.
- **CNN (Convolutional Neural Network):** Mạng tích chập 1 chiều. Sử dụng lớp `Conv1D` để trích xuất các đặc trưng cục bộ (các cụm từ quan trọng) đi kèm với `GlobalMaxPooling1D`.

### c) Phương pháp có gì tốt hay khác biệt với các phương pháp khác
- **Trong Machine Learning:** Việc sử dụng `class_weight='balanced'` kết hợp với trích xuất đặc trưng TF-IDF dạng bigram đã mang lại sự cải thiện rất lớn cho việc nhận diện các nhãn thiểu số (như Service, Shipping). So với Random Forest, SVM với Kernel Linear cho thấy hiệu quả phân lớp ưu việt hơn hẳn trên không gian đặc trưng nhiều chiều do TF-IDF tạo ra.
- **Trong Deep Learning:** 
  - Các mô hình GRU và CNN có tốc độ học rất nhanh, hội tụ tốt và đạt được kết quả tiệm cận với ML truyền thống. Đặc biệt CNN sử dụng `GlobalMaxPooling1D` rất phù hợp với các review ngắn vì nó lấy ra được đặc trưng quan trọng nhất không phụ thuộc vào vị trí.
  - Để tránh mô hình học vẹt (overfitting), nhóm em đã thêm các kỹ thuật điều chuẩn (Regularization) như `SpatialDropout1D`, `Dropout`, và `L2 regularization`. Điều này tạo ra sự khác biệt lớn so với các phiên bản trước (khoảng cách gap train-val giảm rệt).

### d) Đề xuất cải thiện, điểm tốt và xấu
- **Điểm tốt:** Pipeline của các mô hình ML vô cùng ổn định. Mô hình CNN và GRU hoạt động rất hiệu quả, đặc biệt CNN hội tụ cực kỳ nhanh (~2.5s/epoch). Vấn đề nghiêm trọng về tốc độ huấn luyện ở phiên bản cũ (do `recurrent_dropout` vô hiệu hóa cuDNN khiến GPU chạy chậm đi 28 lần) đã được nhóm khắc phục triệt để, giảm tổng thời gian huấn luyện từ hơn 3 giờ xuống chỉ còn khoảng 20 phút.
- **Điểm xấu & Đề xuất:** 
  - Dù đã điều chuẩn, mô hình DL vẫn còn hiện tượng overfitting nhẹ (gap ~7%). Nguyên nhân một phần đến từ việc sinh dữ liệu (augmented data) tạo ra các mẫu quá giống nhau. Để cải thiện triệt để, cần thu thập thêm dữ liệu thực tế hoặc sử dụng các pretrained word embeddings tiếng Việt như PhoBERT hoặc fastText.
  - Mô hình LSTM đã **thất bại hoàn toàn** (dự đoán tất cả đều là một lớp với độ chính xác 41.72%). Hiện tượng này là do "Dead ReLU" sinh ra khi kết hợp `Conv1D` (có phạt L2) và `SpatialDropout1D` trước khi đưa vào LSTM. Đề xuất cho phiên bản tới là đơn giản hóa cấu trúc LSTM (giống với GRU), loại bỏ hoàn toàn khối `Conv1D + MaxPooling1D`.

---

# CHƯƠNG III. Tiến hành dự đoán

## 1. Tiến hành dự đoán trên các mô hình
### a) Mô hình học máy
Đầu tiên, câu bình luận mới sẽ được đi qua hàm tiền xử lý văn bản tiếng Việt để làm sạch, chuẩn hóa unicode và dấu câu. Tiếp theo, nhóm sử dụng công cụ `TfidfVectorizer` (đã được fit với tập train) để chuyển đổi bình luận này thành ma trận vector TF-IDF. Ma trận này đại diện cho bình luận dưới dạng các giá trị số tần suất, phản ánh mức độ quan trọng của các từ vựng (đặc biệt là bigram). Cuối cùng, vector này được đưa trực tiếp vào các mô hình đã huấn luyện (như SVM, Random Forest) để mô hình đưa ra dự đoán nhãn cuối cùng.

### b) Mô hình học sâu
Đối với mô hình học sâu, sau bước chuẩn hóa và làm sạch văn bản, câu bình luận được đưa vào đối tượng `Tokenizer` (đã huấn luyện từ trước). Lệnh `tokenizer.texts_to_sequences()` sẽ chuyển đổi bình luận thành một dãy số nguyên dựa trên từ điển đã xây dựng. Sau đó, dãy số này đi qua hàm `pad_sequences()` để thêm các giá trị padding (số 0) nhằm đảm bảo dãy số đạt đúng chiều dài cố định (`MAXLEN`), đáp ứng yêu cầu kích thước đầu vào của mạng nơ-ron. Khi đưa vào các mô hình CNN hay GRU, mạng sẽ xuất ra ma trận phân phối xác suất cho 4 lớp và lớp có xác suất cao nhất sẽ được chọn làm dự đoán.

---

# CHƯƠNG IV. Kịch bản đánh giá và Kết quả thực nghiệm

## 1. Kịch bản đánh giá và kết quả
Qua nhiều phiên bản thử nghiệm (từ V4, V5 đến V6), nhóm em đã đánh giá khả năng phân loại và hiện tượng overfitting của các mô hình trên tập Validation (chiếm 15-20% tập dữ liệu).

**Bảng tổng hợp kết quả (độ chính xác Accuracy) qua các phiên bản:**

| Mô hình | V4 | V5 | V6 | Đánh giá hiện tại (V6) |
|---|---|---|---|---|
| **Random Forest** | 91.27% | 91.27% | 91.27% | Rất ổn định |
| **SVM** | 91.36% | 91.36% | **91.36%** | Cân bằng tốt, đạt kết quả cao nhất |
| **Logistic Regression**| 89.95% | 89.95% | 89.95% | Cải thiện cân bằng nhãn |
| **CNN** | 90.43% | 90.09% | **90.35%** | Tốt, giảm overfitting (gap 6.96%) |
| **GRU** | 90.31% | 89.92% | **90.25%** | Tốt, ổn định (gap 6.98%) |
| **LSTM** | 90.54% | 41.72% ⚠️ | 41.72% ⚠️ | Thất bại (Dự đoán một class duy nhất) |

## 2. Phân tích kết quả
**Đối với các mô hình Machine Learning:**
- Nhóm mô hình học máy truyền thống (RF, SVM, LR) cho thấy sự ổn định tuyệt đối, không có sự dao động qua các phiên bản.
- Mô hình **SVM** sử dụng Linear Kernel đạt kết quả tốt nhất (91.36%). Đặc biệt, nhờ trọng số `class_weight='balanced'`, SVM đã khắc phục tốt sự mất cân bằng dữ liệu, đẩy recall của lớp "Service" và "Shipping" lên mức cao (xấp xỉ 0.88 - 0.95), vượt qua Random Forest.

**Đối với các mô hình Deep Learning:**
- **Giải quyết Overfitting:** Tại V4, các mô hình DL có độ lệch (gap) giữa train và test lên tới trên 8%. Bằng cách bổ sung kỹ thuật `L2 Regularization` và tinh chỉnh `Dropout`, phiên bản V6 đã khống chế thành công gap này về mức an toàn (~6.96% cho CNN), độ chính xác được phục hồi lên mức 90.35% và mô hình không còn học vẹt (memorize) như trước.
- **Khắc phục tốc độ chạy:** Việc gỡ bỏ cấu hình `recurrent_dropout=0.2` ở V6 đã kích hoạt lại nhân cuDNN trên GPU, giúp mô hình GRU chạy nhanh hơn 26 lần (từ 283 giây/epoch xuống chỉ còn 10.8 giây/epoch).
- **Phát hiện lỗi ở LSTM:** Một phát hiện quan trọng là LSTM bị đóng băng độ chính xác tại 41.72% (chính xác bằng tỷ lệ nhãn "Quality" trong tập Validation). Khác biệt của LSTM so với GRU và CNN là nó sử dụng chuỗi lớp `Conv1D + L2 + MaxPooling1D` ngay trước lớp LSTM. Sự kết hợp này cộng với `SpatialDropout1D` đã gây ra hiện tượng chết ReLU (Dead ReLU), triệt tiêu toàn bộ gradient, làm mô hình chỉ dự đoán một lớp duy nhất cho mọi đầu vào.

## 3. Tổng kết
- **Mô hình khuyến nghị:** Để đạt độ chính xác tối ưu và cân bằng các nhãn, **SVM** là lựa chọn số 1. Trong nhóm Học sâu, **CNN** là mô hình sáng giá nhất nhờ tốc độ train cực nhanh và độ chính xác ổn định.
- **Hướng phát triển:** Trong phiên bản tiếp theo, nhóm sẽ gỡ bỏ lớp `Conv1D` khỏi LSTM để sửa lỗi cấu trúc, đồng thời xem xét tích hợp mô hình ngôn ngữ PhoBERT để đẩy giới hạn độ chính xác lên trên 94%.
