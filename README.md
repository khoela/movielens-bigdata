# Hệ thống gợi ý phim cá nhân hóa — Checkpoint 2

Checkpoint 2 tập trung vào **môi trường thực thi, ingestion và raw storage** cho dữ liệu MovieLens 25M.

## 1. Phạm vi đã triển khai

- Thiết lập và kiểm tra môi trường Spark.
- Chuẩn bị snapshot MovieLens 25M từ GroupLens.
- Trích xuất dữ liệu nguồn vào raw storage bằng Python.
- Tạo manifest ghi nguồn, thời gian, kích thước và SHA-256.
- Đọc raw bằng Spark, xem schema, dữ liệu mẫu và kiểm tra số dòng.
- Kiểm tra tính toàn vẹn của raw và hành vi chạy lại ingestion.
- Tạo sample nhỏ phục vụ demo.
- Lưu log và minh chứng chọn lọc để báo cáo.

Checkpoint này chưa triển khai làm sạch hoàn chỉnh, Parquet, ALS, API hoặc dashboard.

## 2. Kiến trúc hiện tại

| Bước | Thành phần | Vai trò |
| --- | --- | --- |
| 1 | MovieLens ZIP | Snapshot nguồn được tải từ GroupLens |
| 2 | Python ingestion | Trích xuất file, tổ chức thư mục và tạo manifest |
| 3 | Raw storage | Giữ CSV nguyên bản trên local filesystem |
| 4 | PySpark | Đọc schema, hiển thị sample và đếm số dòng |
| 5 | Chương trình kiểm chứng | Đối chiếu kích thước, checksum và các lần chạy |
| 6 | Log và sample | Cung cấp minh chứng và dữ liệu nhỏ để demo |

Dữ liệu được lưu trên máy local. Spark chạy ở chế độ `local[2]`; hệ thống hiện chưa triển khai cluster nhiều máy hoặc HDFS.

## 3. Môi trường và cài đặt

### 3.1. Cấu hình sử dụng

| Thành phần | Phiên bản hoặc chế độ |
| --- | --- |
| Python | 3.11 |
| Java | OpenJDK 17 |
| PySpark | 3.5.7 |
| Quản lý môi trường | Conda, môi trường `movielens` |
| Terminal | PowerShell trên Windows |
| Spark execution mode | `local[2]` |

Phiên bản thực tế được lưu trong log môi trường.

### 3.2. Tạo và kích hoạt môi trường

Máy cần có Conda. Nếu môi trường `movielens` chưa tồn tại, tạo bằng lệnh:

```powershell
conda create -n movielens --override-channels -c conda-forge python=3.11 openjdk=17 pip -y
```

Kích hoạt môi trường trong cửa sổ PowerShell đang dùng:

```powershell
conda activate movielens
```

Kiểm tra Python và Java:

```powershell
python --version
java -version
```

Kết quả cần tương ứng với Python 3.11 và Java 17.

### 3.3. Chọn Java trong môi trường Conda nếu cần

Nếu PowerShell vẫn nhận một Java khác, tìm `java.exe` trong môi trường Conda đang kích hoạt:

```powershell
$javaExe = Get-ChildItem "$env:CONDA_PREFIX" -Filter java.exe -Recurse |
    Where-Object { $_.Directory.Name -eq "bin" } |
    Select-Object -First 1

if ($null -eq $javaExe) {
    throw "Khong tim thay Java trong moi truong Conda dang kich hoat."
}

$env:JAVA_HOME = $javaExe.Directory.Parent.FullName
$env:Path = "$env:JAVA_HOME\bin;$env:Path"

java -version
```

Các thiết lập trên áp dụng cho cửa sổ PowerShell hiện tại. Khi mở cửa sổ mới, kích hoạt lại môi trường và kiểm tra phiên bản Java trước khi chạy Spark.

### 3.4. Cài thư viện dự án

Chuyển đến thư mục gốc của repo, nơi chứa `requirements.txt`, rồi chạy:

```powershell
python -m pip install -r requirements.txt
```

Trong môi trường Conda này, sử dụng lệnh `python`; không cần tạo thêm `.venv`.

## 4. Nguồn dữ liệu

- **Dataset:** MovieLens 25M.
- **Đơn vị phát hành:** GroupLens, University of Minnesota.
- **Nhãn snapshot:** `ml-25m`.
- **Trang nguồn:** [MovieLens 25M](https://grouplens.org/datasets/movielens/25m/).
- **Tệp tải về:** [ml-25m.zip](https://files.grouplens.org/datasets/movielens/ml-25m.zip).
- **README nguồn:** [MovieLens 25M README](https://files.grouplens.org/datasets/movielens/ml-25m-README.html).

Tạo các thư mục local nếu chưa có:

```powershell
New-Item -ItemType Directory -Force -Path "incoming","data/raw","data/sample","metadata","logs","docs/evidence"
```

Tải ZIP và đặt tại:

```text
incoming/ml-25m.zip
```

Bước tải ZIP hiện được thực hiện thủ công. Script ingestion đọc ZIP đã có trên máy.

### Các file được sử dụng

| File | Cột dữ liệu | Mục đích |
| --- | --- | --- |
| `ratings.csv` | `userId`, `movieId`, `rating`, `timestamp` | Lịch sử đánh giá phim |
| `movies.csv` | `movieId`, `title`, `genres` | Danh mục và thông tin phim |
| `README.txt` | Tài liệu đi kèm dataset | Mô tả dữ liệu, điều kiện sử dụng và cách trích dẫn |

Điều kiện sử dụng và cách trích dẫn cần được xem trong README nguồn. Thông tin nguồn của dự án được ghi tại `metadata/source_info.txt`.

So với đề xuất ban đầu ghi kênh Kaggle, checkpoint này lấy snapshot trực tiếp từ GroupLens.

## 5. Cấu trúc thư mục và chương trình

| Đường dẫn | Nội dung |
| --- | --- |
| `src/` | Các chương trình Python |
| `incoming/` | ZIP nguồn trên máy local |
| `data/raw/` | Các snapshot raw |
| `data/sample/` | Hai CSV mẫu và thông tin nguồn mẫu |
| `metadata/` | Thông tin nguồn dữ liệu |
| `logs/` | Log vận hành trên máy local |
| `docs/evidence/` | Minh chứng chọn lọc dùng cho báo cáo |
| `README.md` | Hướng dẫn cài đặt, chạy và diễn giải kết quả |
| `requirements.txt` | Phiên bản thư viện Python |
| `.gitignore` | Quy tắc bỏ qua file khi đưa lên Git |

### Vai trò từng chương trình

| Chương trình | Vai trò |
| --- | --- |
| `src/env_check.py` | Khởi động Spark và kiểm tra phép đếm một triệu dòng |
| `src/ingest_movielens.py` | Trích xuất dữ liệu và tạo manifest cho một run mới |
| `src/kiem_tra_raw.py` | Spark đọc một snapshot, in schema, sample và đếm dòng |
| `src/kiem_tra_manifest.py` | Đối chiếu file raw với kích thước và hash trong manifest |
| `src/kiem_tra_chay_lai.py` | Đối chiếu ba snapshot mới nhất với ZIP hiện tại và với nhau |
| `src/tao_sample.py` | Tạo tối đa 100 record mẫu từ mỗi CSV |

Git lưu code, dependencies, tài liệu, metadata, sample nhỏ và evidence chọn lọc. ZIP, raw đầy đủ, môi trường cá nhân và log vận hành được bỏ qua theo `.gitignore`.

Sau khi clone repo, người chạy cần tạo các thư mục local và tải ZIP theo hướng dẫn; raw đầy đủ không nằm trong repo.

## 6. Các bước chạy

Chạy tất cả lệnh từ thư mục gốc của repo, trong môi trường Conda `movielens`.

### 6.1. Kiểm tra Spark

```powershell
python src/env_check.py
```

Kết quả cần có:

```text
Count: 1000000
ENV CHECK: PASS
```

### 6.2. Nạp dữ liệu vào raw

Đảm bảo `incoming/ml-25m.zip` tồn tại, sau đó chạy:

```powershell
python src/ingest_movielens.py
```

Chương trình tạo một thư mục run mới, trích xuất các file cần dùng và ghi `manifest.json`.

### 6.3. Đọc raw bằng Spark

```powershell
python src/kiem_tra_raw.py
```

Chương trình chọn snapshot mới nhất có manifest theo tên thư mục thời gian. Nó in schema, dữ liệu mẫu và số dòng của hai CSV.

### 6.4. Kiểm tra kích thước và checksum

```powershell
python src/kiem_tra_manifest.py
```

Kết quả cần có:

```text
MANIFEST CHECK: PASS
```

### 6.5. Kiểm tra hành vi chạy lại

Cần ít nhất ba snapshot có manifest. Nếu mới ingest một lần, chạy thêm hai lần, lần lượt đợi mỗi lệnh hoàn tất:

```powershell
python src/ingest_movielens.py
python src/ingest_movielens.py
```

Sau đó chạy:

```powershell
python src/kiem_tra_chay_lai.py
```

Kết quả cần có:

```text
RERUN CHECK: PASS
```

Phép kiểm tra này dùng ba snapshot mới nhất. Nó đối chiếu hash ZIP nguồn, kích thước và hash file raw, sau đó so sánh nội dung giữa các snapshot.

### 6.6. Tạo sample

```powershell
python src/tao_sample.py
```

Đầu ra:

```text
data/sample/ratings.csv
data/sample/movies.csv
data/sample/sample_info.json
```

### 6.7. Lưu log và evidence

Ví dụ lưu log smoke test và kiểm tra raw trong PowerShell:

```powershell
cmd /c "python src\env_check.py 2>&1" | Tee-Object -FilePath .\logs\env_check.txt
cmd /c "python src\kiem_tra_raw.py 2>&1" | Tee-Object -FilePath .\logs\kiem_tra_raw.txt
```

Lưu phiên bản Java:

```powershell
cmd /c "java -version 2>&1" | Tee-Object -FilePath .\logs\java_version.txt
```

Chép những log nhỏ cần dùng vào `docs/evidence/`. Khi chốt báo cáo, dùng log và manifest tương ứng với snapshot được trình bày.

## 7. Kết quả kiểm chứng của checkpoint

Các kết quả đã được ghi nhận trong quá trình chạy trên máy thực hiện dự án:

| Nội dung | Kết quả |
| --- | --- |
| Smoke test | Spark đếm được 1.000.000 dòng |
| `ratings.csv` | 25.000.095 dòng dữ liệu, không tính header |
| `movies.csv` | 62.423 dòng dữ liệu, không tính header |
| Spark inspection | Đọc được schema và dữ liệu mẫu |
| Kiểm tra manifest | Raw khớp kích thước và SHA-256 đã ghi |
| Kiểm tra chạy lại | Ba snapshot được kiểm tra có cùng nguồn và nội dung |

Log và manifest dùng để đối chiếu nằm trong `docs/evidence/` khi đã được đưa vào bản bàn giao. Người chạy lại cần xác nhận bằng kết quả mới trên môi trường của mình.

Schema toàn chuỗi được sử dụng ở bước đọc raw. Count và checksum không thay thế việc kiểm tra chất lượng ngữ nghĩa toàn bộ dữ liệu.

## 8. Quy ước raw, manifest và hành vi chạy lại

### 8.1. Quy ước đường dẫn

```text
data/raw/movielens25m/ingest_date=YYYY-MM-DD/run_<UTC_TIMESTAMP>/
```

Trong mỗi run có:

| Đường dẫn tương đối | Nội dung |
| --- | --- |
| `manifest.json` | Metadata của lần nạp |
| `ml-25m/ratings.csv` | Bản raw của lịch sử rating |
| `ml-25m/movies.csv` | Bản raw của danh mục phim |
| `ml-25m/README.txt` | Tài liệu nguồn |

`ingest_date` là ngày đưa dữ liệu vào hệ thống, không phải ngày người dùng đánh giá phim. Timestamp trong tên run được tạo theo UTC.

### 8.2. Nội dung manifest

Manifest ghi các trường chính:

- `dataset`: tên dataset.
- `run_id`: định danh lần chạy.
- `ingested_at_utc`: thời gian bắt đầu lần chạy theo UTC được code ghi nhận.
- `source_url`: URL nguồn.
- `source_zip`: đường dẫn ZIP local.
- `source_sha256`: dấu vân tay của ZIP nguồn trên máy.
- `status`: trạng thái thành công khi quá trình tạo manifest hoàn tất.
- `validation_scope`: phạm vi kiểm tra được thực hiện trong ingestion.
- `files`: đường dẫn tương đối, số byte và SHA-256 của từng file.

Đường dẫn file trong `files` được hiểu tương đối với thư mục chứa manifest. Vị trí của manifest xác định thư mục snapshot.

Checksum hiện được dùng để đối chiếu với dữ liệu đã ghi nhận trong hệ thống; code hiện tại chưa tự đối chiếu checksum do nhà phát hành công bố.

### 8.3. Hành vi chạy lại

- Mỗi lần ingestion tạo một snapshot mới theo run ID.
- Snapshot cũ không bị ghi đè.
- Cùng ZIP có thể tạo nhiều snapshot có nội dung giống nhau.
- Hiện chưa tự bỏ qua nguồn có cùng checksum.
- Các chương trình kiểm tra raw, kiểm tra manifest và tạo sample chọn snapshot mới nhất có manifest theo tên thư mục thời gian.
- Chương trình kiểm tra chạy lại chọn ba snapshot mới nhất có manifest.

Chỉ đọc một snapshot khi xử lý dữ liệu. Gom tất cả các run có thể làm đếm trùng cùng dữ liệu nguồn.

## 9. Sample

Mỗi CSV sample chứa tối đa 100 record đầu, giữ header và thứ tự record được chọn từ nguồn.

Đây là mẫu để thử đọc, không phải mẫu đại diện thống kê và không dùng làm kết quả huấn luyện. Hai sample được lấy độc lập nên không bảo đảm mọi `movieId` trong sample ratings đều có trong sample movies.

Nguồn và cách chọn mẫu được ghi trong `data/sample/sample_info.json`.

## 10. Hạn chế và bước tiếp theo

- Local storage chưa có replication hoặc khả năng chịu lỗi như hệ lưu trữ phân tán.
- Spark mới chạy local, chưa có kiểm chứng triển khai nhiều máy.
- Lưu nhiều snapshot giống nhau làm tăng dung lượng.
- Chưa tự động tải nguồn hoặc bỏ qua snapshot trùng.
- Chưa kiểm tra đầy đủ missing values, miền giá trị, duplicate hoặc quan hệ khóa.
- Chưa hoàn thiện xử lý tình huống ingestion bị gián đoạn giữa chừng.

Các bước tiếp theo là bổ sung quality checks, chuẩn hóa kiểu dữ liệu và timestamp, tạo clean layer/Parquet, sau đó chuẩn bị dữ liệu cho ALS. Đầu ra xử lý được lưu riêng để bảo toàn raw.
