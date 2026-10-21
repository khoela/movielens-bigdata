from pyspark.sql import SparkSession

# 1. Khởi động Spark trên máy tính của bạn
spark = SparkSession.builder \
    .master("local[2]") \
    .appName("KiemTraSpark") \
    .getOrCreate()

# 2. In phiên bản Spark
print("Phien ban Spark:", spark.version)

# 3. Tạo dữ liệu thử gồm 1 triệu dòng
du_lieu = spark.range(1000000)

# 4. Đếm số dòng bằng Spark
so_dong = du_lieu.count()
print("So dong:", so_dong)

# 5. Kiểm tra kết quả
if so_dong == 1000000:
    print("ENV CHECK: PASS")
else:
    raise RuntimeError("So dong khong dung")

# 6. Đóng Spark
spark.stop()