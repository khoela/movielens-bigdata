# \# Hệ thống gợi ý phim cá nhân hóa — Checkpoint 2

# 

# \## 1. Phạm vi đã triển khai

# 

# Checkpoint 2 thực hiện:

# 

# \- Thiết lập và kiểm tra môi trường Spark.

# \- Chuẩn bị snapshot MovieLens 25M.

# \- Trích xuất dữ liệu nguồn vào raw storage.

# \- Tạo manifest ghi nguồn, thời gian, kích thước và SHA-256.

# \- Đọc raw bằng Spark và kiểm tra số dòng.

# \- Kiểm tra tính toàn vẹn và hành vi chạy lại.

# \- Tạo sample nhỏ phục vụ demo.

# 

# Chưa triển khai làm sạch hoàn chỉnh, Parquet, ALS, API hoặc dashboard.

# 

# \## 2. Kiến trúc hiện tại

# 

# MovieLens ZIP → Python ingestion → Raw CSV + Manifest

# → Spark đọc kiểm tra → Log và sample.

# 

# Dữ liệu lưu trên máy local. Spark chạy ở chế độ local\[2],

# chưa triển khai cluster nhiều máy.

# 

# \## 3. Môi trường

# 

# \- Python 3.11.

# \- Java 17.

# \- PySpark 3.5.7.

# \- PowerShell trên Windows.

# 

# Phiên bản thực tế được lưu trong logs.

# 

# Tạo môi trường:

# 

# ```powershell

# conda create -n movielens --override-channels -c conda-forge python=3.11 openjdk=17 pip -y

# conda activate movielens

# ```

# 

# Kiểm tra:

# 

# ```powershell

# python --version

# java -version

# ```

# 

# Java phải được nhận là phiên bản 17. Nếu vẫn nhận Java khác,

# chọn Java trong môi trường Conda cho cửa sổ PowerShell hiện tại:

# 

# ```powershell

# $javaExe = Get-ChildItem "$env:CONDA\_PREFIX" -Filter java.exe -Recurse | Where-Object { $\_.Directory.Name -eq "bin" } | Select-Object -First 1

# $env:JAVA\_HOME = $javaExe.Directory.Parent.FullName

# $env:Path = "$env:JAVA\_HOME\\bin;$env:Path"

# ```

# 

# Cài thư viện:

# 

# ```powershell

# python -m pip install -r requirements.txt

# ```

# 

# \## 4. Nguồn dữ liệu

# 

# Dataset: MovieLens 25M.

# 

# Trang nguồn:

# https://grouplens.org/datasets/movielens/25m/

# 

# ZIP:

# https://files.grouplens.org/datasets/movielens/ml-25m.zip

# 

# Tải ZIP và đặt tại:

# 

# incoming/ml-25m.zip

# 

# Hai file dữ liệu sử dụng:

# \- ratings.csv

# \- movies.csv

# 

# Điều kiện sử dụng và cách trích dẫn nằm trong README.txt

# đi kèm dataset. Thông tin nguồn được ghi tại

# metadata/source\_info.txt.

# 

# So với đề xuất ban đầu ghi kênh Kaggle, checkpoint này

# lấy snapshot trực tiếp từ GroupLens.

# 

# \## 5. Cấu trúc thư mục

# 

# \- src/: các chương trình Python.

# \- incoming/: ZIP nguồn.

# \- data/raw/: các snapshot raw.

# \- data/sample/: dữ liệu mẫu nhỏ.

# \- metadata/: thông tin nguồn.

# \- logs/: kết quả chạy.

# \- docs/evidence/: minh chứng chọn lọc để báo cáo.

# 

# ZIP, raw lớn và môi trường cá nhân không được đưa lên Git.

# 

# \## 6. Các bước chạy

# 

# Chạy lệnh từ thư mục gốc của repo.

# 

# Kiểm tra Spark:

# 

# ```powershell

# python src/env\_check.py

# ```

# 

# Nạp dữ liệu:

# 

# ```powershell

# python src/ingest\_movielens.py

# ```

# 

# Kiểm tra raw bằng Spark:

# 

# ```powershell

# python src/kiem\_tra\_raw.py

# ```

# 

# Kiểm tra kích thước và checksum:

# 

# ```powershell

# python src/kiem\_tra\_manifest.py

# ```

# 

# Để kiểm tra chạy lại, cần ít nhất ba lần ingestion thành công.

# Sau đó chạy:

# 

# ```powershell

# python src/kiem\_tra\_chay\_lai.py

# ```

# 

# Tạo sample:

# 

# ```powershell

# python src/tao\_sample.py

# ```

# 

# \## 7. Kết quả kiểm chứng

# 

# \- ratings.csv: 25.000.095 dòng dữ liệu.

# \- movies.csv: 62.423 dòng dữ liệu.

# \- Spark đọc được schema và dữ liệu mẫu.

# \- File raw khớp kích thước và SHA-256 trong manifest.

# \- Ba snapshot được kiểm tra có cùng nguồn và nội dung.

# 

# Count và checksum không thay thế việc kiểm tra chất lượng

# ngữ nghĩa toàn bộ dữ liệu.

# 

# \## 8. Quy ước raw và hành vi chạy lại

# 

# Đường dẫn:

# 

# data/raw/movielens25m/ingest\_date=YYYY-MM-DD/run\_<UTC\_TIMESTAMP>/

# 

# Mỗi run chứa manifest.json và thư mục ml-25m gồm các file

# đã trích xuất. Nội dung file nguồn được giữ nguyên.

# 

# Mỗi lần ingestion tạo một snapshot mới, không ghi đè.

# Hiện tại chưa tự bỏ qua nguồn có cùng checksum.

# 

# Các chương trình kiểm tra raw và tạo sample chọn snapshot

# mới nhất có manifest theo tên thư mục thời gian.

# 

# Chỉ đọc một snapshot khi xử lý; không gom tất cả các run,

# vì có thể đếm trùng dữ liệu.

# 

# \## 9. Sample

# 

# Mỗi CSV sample chứa tối đa 100 record đầu.

# 

# Đây là mẫu để thử đọc, không đại diện thống kê và không dùng

# làm kết quả huấn luyện. Hai sample được lấy độc lập nên không

# bảo đảm đầy đủ quan hệ movieId giữa chúng.

# 

# Nguồn sample được ghi trong data/sample/sample\_info.json.

# 

# \## 10. Hạn chế và bước tiếp theo

# 

# \- Local storage chưa có replication hoặc khả năng chịu lỗi

# &#x20; như hệ lưu trữ phân tán.

# \- Lưu nhiều snapshot giống nhau làm tăng dung lượng.

# \- Chưa kiểm tra đầy đủ missing values, miền giá trị,

# &#x20; duplicate hoặc quan hệ khóa.

# \- Bước tiếp theo: bổ sung quality checks, clean layer,

# &#x20; Parquet và chuẩn bị dữ liệu cho ALS.

