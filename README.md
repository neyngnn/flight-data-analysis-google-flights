# Flight Booking Explorer - Streamlit & Power BI Dashboard

## Mô tả dự án

**Flight Booking Explorer** là một ứng dụng web được xây dựng bằng **Streamlit** giúp người dùng tìm kiếm và phân tích các chuyến bay từ cơ sở dữ liệu MySQL. Ứng dụng cung cấp thông tin chi tiết về chuyến bay, bao gồm hãng hàng không, thời gian khởi hành, giá vé, và hạng ghế. Người dùng có thể phân tích giá vé dựa trên dữ liệu lịch sử, so sánh với giá vé trung bình và xem biểu đồ thay đổi giá theo thời gian.

Bên cạnh đó, dự án còn cung cấp thông tin thời tiết tại điểm đi và điểm đến vào ngày bay thông qua API WeatherAPI, giúp người dùng đưa ra quyết định bay hợp lý.

**Dự án còn được kết hợp với một dashboard Power BI** để phân tích dữ liệu chuyến bay và rút ra các insights về xu hướng giá vé, hãng hàng không phổ biến, và các yếu tố ảnh hưởng đến sự lựa chọn chuyến bay.

## Các tính năng chính
- **Tìm kiếm chuyến bay**: Cho phép người dùng tìm kiếm chuyến bay từ một điểm khởi hành đến điểm đến với thông tin chi tiết như hãng hàng không, giá vé và thời gian khởi hành.
- **Phân tích giá vé**: Tính toán giá vé trung bình, so sánh giá vé hiện tại với giá vé trung bình và đưa ra các nhận định về mức giá.
- **Lịch sử giá vé**: Hiển thị biểu đồ lịch sử thay đổi giá vé của các chuyến bay.
- **Thông tin thời tiết**: Cung cấp thông tin về thời tiết tại điểm đi và điểm đến vào ngày bay.

## Cấu trúc thư mục
```
📂streamlit_app
├──📂.streamlit
├──📂.vscode
├──📂__pycache__
├──📂data
│   ├──📜all_flights.csv
│   ├──📜merge.csv
│   ├──📜EDA.ipynb
│   ├──📜README.md
│   ├──📜dashboard_flight.pbix
│   ├──📜dashboard_flight_link.txt
│   ├──📜main.py
│   └──📜preprocessingdata.py

```


## Công nghệ sử dụng
- **Streamlit**: Xây dựng giao diện web tương tác cho việc tìm kiếm và phân tích chuyến bay.
- **MySQL**: Cơ sở dữ liệu chứa thông tin về chuyến bay.
- **WeatherAPI**: API cung cấp dữ liệu thời tiết cho các điểm đến và điểm đi.
- **Power BI**: Sử dụng để tạo và phân tích dashboard cho các chuyến bay và giá vé.

## Hướng dẫn cài đặt

1. **Clone Repository**
```
git clone https://github.com/neyngnn/flight-data-analysis-google-flights.git
```
2. **Cài đặt các thư viện yêu cầu**
```
pip install -r requirements.txt
```

3. **Chạy ứng dụng Streamlit**


4. **Xem dashboard Power BI**
Mở tệp `dashboard_flight.pbix` trong Power BI Desktop để phân tích thêm dữ liệu.

## Tệp liên quan

- **`EDA.ipynb`**: Phân tích dữ liệu khám phá (EDA) về các chuyến bay và giá vé.
- **`dashboard_flight.pbix`**: Tệp Power BI Dashboard chứa các báo cáo và phân tích dữ liệu chuyến bay.
- **`preprocessingdata.py`**: Tiền xử lý dữ liệu trước khi sử dụng cho phân tích.




![Screenshot 2025-02-14 091033](https://github.com/user-attachments/assets/917c10b7-1cda-4cea-bdca-4bcd19f62c42)

![Screenshot 2025-02-14 091208](https://github.com/user-attachments/assets/3d07c4ec-7d0c-4735-8add-8fc36edd5ac0)

![Screenshot 2025-02-14 091229](https://github.com/user-attachments/assets/323525a8-3bea-491c-a8cb-65791e50cc54)
