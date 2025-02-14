import pandas as pd

# Đọc dữ liệu từ file CSV
df = pd.read_csv('data\\all_flights.csv')

# Chuyển cột 'price' thành kiểu số (numeric), bỏ qua các giá trị không hợp lệ
df['price'] = pd.to_numeric(df['price'], errors='coerce')

# Nhóm dữ liệu theo các cột cần thiết và tính giá trị trung bình của price
df_grouped = df.groupby(
    ['scrape_date', 'id_departure', 'id_arrival', 'departure_datetime', 
     'arrival_datetime', 'airline', 'travel_class', 'is_nonstop'],
    as_index=False
).agg({'price': 'mean'})

# Lưu kết quả vào file mới (hoặc bạn có thể ghi đè lên file gốc)
df_grouped.to_csv('data\merge.csv', index=False)

# Hiển thị kết quả
print(df_grouped)
