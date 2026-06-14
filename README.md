# Phân loại Bình luận Thương mại Điện tử Đa khía cạnh (IT4930-T2)

Dự án nghiên cứu và xây dựng hệ thống phân loại bình luận khách hàng trên nền tảng thương mại điện tử (Tiki) thành 4 khía cạnh chính: **Chất lượng (Quality)**, **Dịch vụ (Service)**, **Vận chuyển (Shipping)**, và **Đóng gói (Packing)**.

---

## 📖 1. Tổng quan Dự án (Project Review)

Hệ thống được phát triển nhằm mục đích tự động hóa việc phân tích phản hồi của khách hàng. Hệ thống chuyển đổi các phản hồi dạng văn bản tự do thành các nhãn khía cạnh cụ thể, phục vụ cho việc thống kê chất lượng bán hàng và cải thiện trải nghiệm người dùng.

### 🌟 Khía cạnh phân loại (Target Aspects)
* **Quality (Chất lượng):** Đánh giá về tính năng sản phẩm, độ bền, hàng thật/giả, lỗi kỹ thuật.
* **Service (Dịch vụ):** Thái độ tư vấn, chính sách đổi trả/hoàn tiền, tặng quà kèm, bảo hành.
* **Shipping (Vận chuyển):** Tốc độ giao nhận, thái độ của shipper, thời gian giao hàng.
* **Packing (Đóng gói):** Quy cách bọc hàng, hộp móp méo/rách, chống sốc, màng co bảo vệ.

### ⚙️ Pipeline Xử lý Dữ liệu
Hệ thống sử dụng quy trình xử lý dữ liệu khép kín tối ưu:
```
[Dữ liệu gốc theo DM] ➔ [Tiền xử lý (Preprocessing)] ➔ [Lọc & Gộp (Merge)]
       ➔ [Tách mệnh đề đa nhãn (Clause Splitting)] ➔ [Tăng cường (Augmentation)] ➔ [Huấn luyện Mô hình]
```

1. **Tiền xử lý nâng cao (`preprocessing_multilabel.py`):** 5 bước chuẩn hóa (Lọc rác, Chuẩn hóa Unicode NFC, Loại bỏ Emoji, Sửa lỗi viết tắt/Teen code bằng lookbehind thông minh, Xử lý tiếng Anh lai và Tách từ tiếng Việt).
2. **Gộp dữ liệu đơn nhãn (`merge_filtered_data.py`):** Tập hợp dữ liệu sạch từ các danh mục sản phẩm khác nhau.
3. **Trích xuất dữ liệu thiểu số (`split_multilabel_comments.py`):** Chặt câu đa nhãn bằng Regex liên từ (`nhưng`, `mỗi tội`, `bù lại`,...) để bóc tách thêm dữ liệu đơn nhãn cho các lớp thiểu số (`Service`, `Shipping`, `Packing`).
4. **Tăng cường dữ liệu cân bằng (`augment_data.py`):** Nhân bản dữ liệu thiểu số lên tối thiểu 5,000 dòng mỗi nhãn để tránh hiện tượng mất cân bằng dữ liệu khi huấn luyện mô hình PhoBERT.

---

## 📂 2. Cấu trúc Thư mục (Directory Structure)

```
IT4930-T2/
├── data/
│   ├── Commentsauxuly/                     # Thư mục chứa dữ liệu đã tiền xử lý theo danh mục
│   │   ├── comments_data_ncds_preprocessed_*_filtered.csv
│   │   ├── comments_split_from_multilabel.csv  # Dữ liệu tách ra từ bình luận đa nhãn
│   │   ├── comments_merged_single_label.csv    # Dữ liệu gộp Master cuối cùng
│   │   └── comments_merged_single_label_augmented.csv # Dữ liệu gộp đã tăng cường cân bằng
│   ├── Laptop_HuyDQ_3000.csv               # (Đã dọn dẹp)
│   └── vietnamese-stopwords.txt            # Danh sách từ dừng tiếng Việt
├── preprocessing_multilabel.py             # Kịch bản tiền xử lý đa nhãn cốt lõi
├── merge_filtered_data.py                  # Kịch bản gộp dữ liệu danh mục
├── split_multilabel_comments.py            # Kịch bản tách câu và tích hợp dữ liệu đa nhãn
├── augment_data.py                         # Kịch bản tăng cường dữ liệu tự động
├── app.py                                  # Ứng dụng web cục bộ (Flask Web UI)
└── templates/                              # Giao diện ứng dụng Flask
```

---

## 🛠️ 3. Hướng dẫn Cài đặt (Installation Guide)

### Yêu cầu hệ thống
* **Python**: Phiên bản `3.8` trở lên.
* **Hệ điều hành**: Windows, macOS hoặc Linux.

### Các bước cài đặt

1. **Tải mã nguồn về máy tính:**
   ```bash
   git clone https://github.com/Binh21112004/IT4930-T2.git
   cd IT4930-T2
   ```

2. **Cài đặt các thư viện cần thiết:**
   Cài đặt tất cả các gói phụ thuộc qua `pip`:
   ```bash
   pip install pandas openpyxl underthesea regex flask
   ```

---

## 🚀 4. Hướng dẫn Sử dụng (Usage Instructions)

### A. Chạy quy trình cập nhật dữ liệu (Data Pipeline)

Nếu bạn muốn tạo lại dữ liệu huấn luyện sạch hoặc cập nhật thêm bình luận mới:

1. **Gộp và lọc dữ liệu đơn nhãn:**
   ```bash
   python merge_filtered_data.py
   ```
2. **Thực hiện tách câu từ bình luận đa nhãn và tăng cường cân bằng dữ liệu:**
   ```bash
   python split_multilabel_comments.py
   ```
   *(Kịch bản này sẽ tự động gọi `augment_data.py` để sinh ra file dữ liệu tăng cường cuối cùng `comments_merged_single_label_augmented.csv` với 26,109 dòng).*

### B. Chạy thử nghiệm bộ tiền xử lý đơn lẻ
Để kiểm tra xem văn bản được xử lý và làm sạch như thế nào:
```bash
python preprocessing_multilabel.py
```

### C. Khởi chạy Ứng dụng Web dự đoán (Flask App)
Khởi chạy giao diện Web cục bộ để nhập bình luận trực quan và xem phân loại:
```bash
python app.py
```
Sau đó truy cập trình duyệt tại địa chỉ: `http://127.0.0.1:5000`
