# Summary: Bao cao Nhom 21 - Phan loai phan anh nguoi dung tren san TMDT

**De tai**: Phan loai phan anh cua nguoi dung tren cac san thuong mai dien tu
**Truong**: DH Bach Khoa Ha Noi - Truong CNTT va Truyen thong
**Giang vien**: PGS. TS. Than Quang Khoat
**Nhom**: 6 thanh vien (Mai Thu Hien, Tran Thi Nhu Quynh, Nguyen Duy Khanh, Nguyen Thuy Duong, Le Duc Anh Duy, Nguyen Ha Phu Thinh)

---

## 1. Muc tieu

Phan loai binh luan tieu cuc (duoi 3 sao) cua nguoi dung tren Tiki theo 4 nhan:
- **Quality** (chat luong san pham)
- **Shipping** (van chuyen)
- **Packing** (dong goi)
- **Service** (dich vu khach hang)

Gia tri nhan: `1` (tich cuc), `0` (tieu cuc), `-1` (khong lien quan/trong)

## 2. Thu thap du lieu

- Nguon: Tiki API
- Buoc 1: Thu thap product ID qua API danh muc (`/api/personalish/v1/blocks/listings`)
- Buoc 2: Thu thap binh luan qua API review (`/api/v2/reviews?product_id=...`)
- Chi giu lai binh luan co rating <= 3 (binh luan tieu cuc)

## 3. Tien xu ly du lieu

1. **Chuan hoa Unicode**: Chuyen ve chuan NFC (Canonical Composition)
2. **Chuan hoa dau cau**: Thong nhat kieu go dau tieng Viet ("hoa" vs "hoa") - xu ly dac biet "qu" va "gi"
3. **Lowercase**: Chuyen tat ca ve chu thuong
4. **Chuan hoa cau**:
   - Loai bo khoang trang thua
   - Xoa ky tu khong hop le
   - Loai bo dau cau
   - Loai bo stopwords (tu file co san)
   - Xoa emoji
   - Thay the tu viet tat ("k" -> "khong", "sp" -> "san pham", ...)

## 4. Xu ly mat can bang du lieu

- Van de: Quality co 9188 mau, cac nhan khac chi < 1000 mau
- Giai phap: **Synonym Replacement** - thay the tu bang tu dong nghia de tang cuong du lieu, giu nguyen nhan goc

## 5. Phuong phap phan loai

### 5.1. Mo hinh hoc may (ML) - Su dung TF-IDF lam dac trung

#### a) Random Forest
- **Thuat toan**: Ensemble learning ket hop nhieu decision trees
- **Ky thuat chinh**: Bagging (Bootstrap Aggregating) + Random Feature Selection
- **Du doan**: Majority voting
- **Cau hinh**: `n_estimators=100`, `random_state=42`
- **Dac trung dau vao**: Ma tran TF-IDF (`X_train_tfidf`)
- **Uu diem**: Giam overfitting, do chinh xac cao, xu ly du lieu mat can bang tot, it nhay cam voi outliers

#### b) Support Vector Machine (SVM)
- **Thuat toan**: Tim hyperplane toi uu phan tach cac lop, cuc dai hoa margin
- **Cau hinh**: `kernel='linear'`, `random_state=42` (su dung `SVC` tu sklearn)
- **Dac trung dau vao**: Ma tran TF-IDF
- **Uu diem**: Hieu qua cho phan lop van ban

#### c) Logistic Regression
- **Thuat toan**: Su dung ham sigmoid de du doan xac suat thuoc lop
- **Cau hinh**: Mac dinh tu sklearn
- **Dac trung dau vao**: Ma tran TF-IDF
- **Uu diem**: Don gian, it tai nguyen, cho ket qua xac suat, hien thi tam quan trong cua dac trung
- **Han che**: Gia dinh tuyen tinh, khong mo hinh hoa quan he phuc tap

### 5.2. Mo hinh hoc sau (Deep Learning) - Su dung Embedding + Tokenizer

#### a) LSTM (Long Short-Term Memory)
- **Kien truc**: Embedding -> Conv1D -> MaxPool1D -> LSTM -> Dense (Fully Connected)
- **Optimizer**: Adam
- **Loss**: Sparse Categorical Crossentropy
- **Metric**: Accuracy
- **Uu diem**: Hoc chuoi dai, xu ly chuoi phuc tap, chong nhieu tot

#### b) GRU (Gated Recurrent Unit)
- **Kien truc**: Embedding -> GRU -> Dense (Fully Connected)
- **Co che**: Update Gate + Reset Gate + Candidate State
- **Don gian hon LSTM** nhung van hoc duoc phu thuoc thoi gian dai

#### c) CNN (Convolutional Neural Network)
- **Kien truc**: Embedding -> Conv1D -> MaxPool1D -> Dense (Fully Connected)
- **Ung dung**: Trich xuat dac trung cuc bo tu chuoi van ban

## 6. Ket qua danh gia

### Mo hinh hoc may

| Model               | Accuracy | Precision | Recall  | F1 Score |
|----------------------|----------|-----------|---------|----------|
| **Random Forest**    | 0.95871  | 0.95866   | 0.95871 | 0.95858  |
| SVM                  | 0.90188  | 0.90181   | 0.90188 | 0.90059  |
| Logistic Regression  | 0.87556  | 0.87697   | 0.87556 | 0.87254  |

**Ket luan**: Random Forest tot nhat trong 3 mo hinh ML (95.87% accuracy). Precision va Recall can bang tot.

### Mo hinh hoc sau

- **CNN**: Hieu suat tot nhat - accuracy train va test cao nhat, loss thap nhat
- Tat ca 3 mo hinh (LSTM, GRU, CNN) deu dat accuracy > 0.89

**Ket luan chung**: CNN la mo hinh hoc sau tot nhat. Random Forest la mo hinh hoc may tot nhat.

## 7. Pipeline tong the

```
Thu thap du lieu (Tiki API)
    |
    v
Loc binh luan tieu cuc (rating <= 3)
    |
    v
Gan nhan thu cong (Quality, Shipping, Packing, Service)
    |
    v
Tien xu ly (Unicode, dau cau, lowercase, stopwords, emoji, viet tat)
    |
    v
Tang cuong du lieu (Synonym Replacement)
    |
    v
+-------------------+-------------------+
|                   |                   |
v                   v                   v
TF-IDF          Tokenizer +         Tokenizer +
|               Embedding           Embedding
v                   |                   |
ML Models       DL Models           DL Models
(RF, SVM, LR)   (LSTM, GRU)         (CNN)
|                   |                   |
v                   v                   v
Du doan nhan cho binh luan moi
```

## 8. Han che va huong phat trien

- Mo rong quy mo du lieu
- Thu nghiem mo hinh hoc sau phuc tap hon
- So sanh voi cac phuong phap phan loai khac
- Thu nghiem Regularized Logistic Regression, Polynomial LR
- Su dung Grid Search / Random Search de toi uu tham so
