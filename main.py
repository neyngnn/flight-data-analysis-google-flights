import mysql.connector
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objs as go
from datetime import datetime
import requests
import matplotlib.pyplot as plt
from scipy import stats
import string as str

WEATHERAPI_KEY = 'c2b9a0d6382f4a178a2163812243011'

def get_weather(city, date):
    """
    Fetch weather information for a specific city and date using WeatherAPI
    
    Args:
        city (str): Name of the city
        date (datetime.date): Date to fetch weather for
    
    Returns:
        dict: Weather information or None if not found
    """
    try:
        # WeatherAPI forecast endpoint
        weather_url = f"http://api.weatherapi.com/v1/forecast.json?key={WEATHERAPI_KEY}&q={city}&dt={date.strftime('%Y-%m-%d')}"
        
        # Send request to WeatherAPI
        response = requests.get(weather_url)
        weather_data = response.json()
        
        # Extract relevant weather information
        if 'forecast' in weather_data and 'forecastday' in weather_data['forecast']:
            forecast_day = weather_data['forecast']['forecastday'][0]
            return {
                'temperature': forecast_day['day']['avgtemp_c'],
                'max_temp': forecast_day['day']['maxtemp_c'],
                'min_temp': forecast_day['day']['mintemp_c'],
                'condition': forecast_day['day']['condition']['text'],
                'icon': f"https:{forecast_day['day']['condition']['icon']}",
                'humidity': forecast_day['day']['avghumidity'],
                'max_wind': forecast_day['day']['maxwind_kph']
            }
        
        return None
    
    except Exception as e:
        st.error(f"Lỗi khi tìm nạp thời tiết: {e}")
        return None

# Styling and background
def set_advanced_styling():
    """Advanced custom styling for Streamlit application"""
    st.markdown("""
    <style>
    /* Global Application Styling */
    .stApp {
        background: linear-gradient(135deg, #f9fcff, #e4f1ff);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* Refined Header Styling */
    h1 {
        color: #2c3e50;
        text-align: center;
        font-weight: 700;
        background: linear-gradient(90deg, #3498db, #2980b9);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 20px;
        letter-spacing: -1px;
    }

    /* Enhanced Sidebar Styling */
    .css-1aumxhk {
        background: linear-gradient(to right, #ffffff, #f0f5fa);
        border-radius: 15px;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.08);
        padding: 20px;
        border: 1px solid rgba(0, 123, 255, 0.1);
    }

    /* Sophisticated Card and Container Styling */
    .stDataFrame, .stMetric, .stCard {
        background-color: white;
        border-radius: 12px;
        box-shadow: 0 6px 15px rgba(0, 0, 0, 0.08);
        padding: 15px;
        margin-bottom: 15px;
        border: 1px solid rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
    }

    .stDataFrame:hover, .stMetric:hover, .stCard:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
    }

    /* Elegant Button Styling */
    .stButton > button {
        background: linear-gradient(45deg, #4a90e2, #3498db);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    .stButton > button:hover {
        background: linear-gradient(45deg, #3498db, #2980b9);
        transform: scale(1.05);
        box-shadow: 0 6px 10px rgba(0, 0, 0, 0.15);
    }

    /* Refined Metric Styling */
    .stMetric {
        background-color: #f8fafc;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        border: 1px solid rgba(0, 123, 255, 0.1);
    }

    .metric-label {
        color: #7f8c8d;
        font-size: 0.9em;
        text-transform: uppercase;
    }

    .metric-value {
        color: #2c3e50;
        font-weight: bold;
    }

    /* Expander Styling */
    .stExpander {
        border-radius: 10px;
        background-color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    }
    </style>
    """, unsafe_allow_html=True)


# Kết nối đến cơ sở dữ liệu MySQL
def connect_to_database():
    return mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="Ptn.1910",
        database="all_flights"
    )

# Lấy danh sách thành phố dựa trên id_departure và id_arrival
def get_cities(conn, column_name):
    query = f"SELECT DISTINCT {column_name} FROM merge;"
    cursor = conn.cursor()
    cursor.execute(query)
    cities = [row[0] for row in cursor.fetchall()]
    cursor.close()
    return cities

# Lấy dữ liệu chuyến bay theo điểm đi, điểm đến và ngày bay
def get_flights(conn, source, destination, date, travel_class):
    query = """
        SELECT
            airline AS "Hãng hàng không",
            departure_datetime AS "Thời gian khởi hành",
            arrival_datetime AS "Thời gian đến", 
            price AS "Giá vé",
            travel_class AS "Hạng ghế",
            is_nonstop AS "Chuyến bay trực tiếp" 
        FROM merge
        WHERE id_departure = %s 
            AND id_arrival = %s 
            AND DATE(departure_datetime) = %s 
            AND travel_class = %s
            AND scrape_date = (
                SELECT MAX(scrape_date) 
                FROM merge
            )
        ORDER BY price ASC
    """

    cursor = conn.cursor()
    cursor.execute(query, (source, destination, date, travel_class))
    result = cursor.fetchall()
    column_names = [desc[0] for desc in cursor.description]
    cursor.close()
    
    # Convert result to DataFrame
    if result:
        flight_data = pd.DataFrame(result, columns=column_names)
        return flight_data
    return pd.DataFrame()  # Return empty DataFrame if no results

# Lấy lịch sử thay đổi giá vé của chuyến bay
def get_flight_price_history(conn, source, destination, departure_datetime, travel_class, airline):
    query = f"""
    SELECT scrape_date, price, airline
    FROM merge
    WHERE id_departure = %s 
        AND id_arrival = %s 
        AND departure_datetime = %s
        AND travel_class = %s
        AND airline = %s
    ORDER BY scrape_date DESC;
    """
    cursor = conn.cursor()
    cursor.execute(query, (source, destination, departure_datetime, travel_class, airline))
    price_history = cursor.fetchall()
    cursor.close()

    # Chuyển đổi kết quả thành DataFrame để dễ dàng xử lý và hiển thị
    df_price_history = pd.DataFrame(price_history, columns=["Ngày cào", "Giá vé", "Hãng hàng không"])
    return df_price_history


def analyze_flight_prices(conn, source, destination, travel_class, airline, departure_datetime):
    """
    Phân tích giá vé máy bay dựa trên các tiêu chí cụ thể
    
    Args:
        conn: Kết nối cơ sở dữ liệu
        source (str): Điểm xuất phát
        destination (str): Điểm đến
        travel_class (str): Hạng vé
        airline (str): Hãng hàng không
        departure_datetime (str): Chuỗi thời gian (ví dụ: "22:00")
        
    Returns:
        tuple: Hai đầu của khoảng giá vé trung bình (lower_price, upper_price)
    """
    # Truy vấn để lấy các chuyến bay phù hợp
    query = """
    SELECT price 
    FROM merge 
    WHERE id_departure = %s 
    AND id_arrival = %s 
    AND travel_class = %s 
    AND airline = %s 
    AND departure_datetime LIKE %s
    """
    
    try:
        # Thực thi truy vấn
        cursor = conn.cursor()
        cursor.execute(query, (source, destination, travel_class, airline, f"%{departure_datetime}%"))
        results = cursor.fetchall()

        # Kiểm tra nếu không có kết quả
        if not results:
            return (0, 0)

        # Chuyển đổi kết quả sang DataFrame
        df_prices = pd.DataFrame(results, columns=['price'])

        # Sử dụng phương pháp IQR để xác định giá trị ngoại lai
        Q1 = df_prices['price'].quantile(0.25)
        Q3 = df_prices['price'].quantile(0.75)
        IQR = Q3 - Q1

        # Xác định ngưỡng giá trị ngoại lai
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR

        # Lọc bỏ các giá trị ngoại lai
        df_normal_prices = df_prices[(df_prices['price'] >= lower_bound) & 
                                     (df_prices['price'] <= upper_bound)]

        # Tính toán hai đầu của khoảng giá vé trung bình
        lower_price = df_normal_prices['price'].quantile(0.25)
        upper_price = df_normal_prices['price'].quantile(0.75)
    
    except Exception as e:
        print(f"Lỗi khi phân tích giá vé: {e}")
        return (0, 0)
    
    finally:
        # Đóng con trỏ để giải phóng tài nguyên
        cursor.close()

    return (lower_price, upper_price)


def create_price_comparison_chart(lower_price, upper_price, current_price):
    """
    Tạo biểu đồ đường thẳng chia 3 phần màu sắc và hiển thị giá hiện tại bằng chấm tròn màu xanh dương.

    Args:
        lower_price (float): Giá vé thấp của khoảng
        upper_price (float): Giá vé cao của khoảng
        current_price (float): Giá vé hiện tại
    """
    # Xử lý trường hợp dữ liệu không hợp lệ
    if not all(isinstance(x, (int, float)) and x >= 0 for x in [lower_price, upper_price, current_price]):
        st.warning("Dữ liệu giá không hợp lệ để tạo biểu đồ.")
        return

    # Tạo figure
    fig = go.Figure()

    # Vùng màu xanh lá (0 đến lower_price)
    fig.add_trace(go.Scatter(
        x=[0, lower_price],
        y=[0, 0],
        mode='lines',
        line=dict(color='rgba(144, 238, 144, 0.8)', width=6),  # Độ dày nhỏ hơn
        name='Giá thấp hơn'
    ))

    # Vùng màu vàng (lower_price đến upper_price)
    fig.add_trace(go.Scatter(
        x=[lower_price, upper_price],
        y=[0, 0],
        mode='lines',
        line=dict(color='rgba(255, 223, 0, 0.8)', width=6),  # Độ dày nhỏ hơn
        name='Giá trung bình'
    ))

    # Vùng màu đỏ (upper_price trở lên)
    fig.add_trace(go.Scatter(
        x=[upper_price, upper_price + (upper_price - lower_price)],  # Mở rộng thêm để minh họa
        y=[0, 0],
        mode='lines',
        line=dict(color='rgba(255, 99, 71, 0.8)', width=6),  # Độ dày nhỏ hơn
        name='Giá cao hơn'
    ))

    # Giá hiện tại (chấm tròn màu xanh dương)
    fig.add_trace(go.Scatter(
        x=[current_price],
        y=[0],
        mode='markers+text',
        marker=dict(color='rgba(0, 102, 255, 0.9)', size=12, symbol='circle'),  # Kích thước nhỏ hơn
        name='Giá hiện tại',
        text=[f'{current_price:,.0f} VND'],
        textposition='top center',
        hoverinfo='text',
        hovertext=f'Giá hiện tại: {current_price:,.0f} VND'
    ))

    # Cấu hình layout
    fig.update_layout(
        title=dict(
            text='📊 So sánh giá vé với khoảng vé trung bình',
            x=0.5,
            xanchor="center",
            font=dict(size=18, color='rgba(50, 50, 50, 0.9)')
        ),
        xaxis=dict(
            title='Giá vé (VND)',
            showgrid=False,
            zeroline=False,
            linecolor='rgba(200, 200, 200, 0.8)',
            linewidth=1
        ),
        yaxis=dict(
            visible=False  # Ẩn trục Y vì không cần thiết
        ),
        legend=dict(
            x=0.5,  # Đặt chú thích ở giữa
            y=2.5,  # Dời chú thích lên trên
            orientation='h',  # Chuyển sang bố cục ngang
            xanchor="center",
            font=dict(size=12),
        ),
        plot_bgcolor='white',
        margin=dict(l=30, r=30, t=70, b=30),  # Thu nhỏ margin
        height=120  # Giảm chiều cao biểu đồ để gọn hơn
    )

    # Hiển thị biểu đồ
    st.plotly_chart(fig, use_container_width=True)


# Hàm chính Streamlit để hiển thị giao diện người dùng
def main():
    # Áp dụng custom styling
    set_advanced_styling()

    # Kết nối cơ sở dữ liệu MySQL
    conn = connect_to_database()

    # Tiêu đề chính
    st.markdown("<h1 style='text-align: center; color: #2c3e50;'>✈️ Flight Booking Explorer ✈️</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #7f8c8d;'>Khám phá chuyến bay với thông tin chi tiết và lịch sử giá</p>", unsafe_allow_html=True)

    # Tạo các cột cho giao diện sidebar
    col1, col2 = st.columns([1, 1])

    with col1:
        # Sidebar trái - Chọn điểm đi
        source = st.selectbox(
            "🛫 Điểm khởi hành", 
            get_cities(conn, "id_departure"),
            help="Chọn thành phố xuất phát của bạn"
        )

    with col2:
        # Sidebar phải - Chọn điểm đến
        destination = st.selectbox(
            "🛬 Điểm đến", 
            get_cities(conn, "id_arrival"),
            help="Chọn thành phố bạn muốn đến"
        )

    # Tạo các cột cho ngày bay và hạng ghế
    col3, col4 = st.columns([1, 1])

    with col3:
        # Chọn ngày bay
        date = st.date_input(
            "📅 Ngày khởi hành", 
            datetime.today(), 
            help="Chọn ngày bạn muốn bay"
        )

    with col4:
        # Chọn hạng ghế
        travel_class = st.selectbox(
            "💺 Hạng ghế", 
            ["Economy", "Business"],
            help="Chọn hạng ghế phù hợp với nhu cầu của bạn"
        )

    # Nút tìm kiếm
    # search_button = st.button("🔍 Tìm chuyến bay", key="search_flights")

    # Xử lý tìm kiếm chuyến bay
    if source and destination and date and travel_class:
        flight_data = get_flights(conn, source, destination, date, travel_class)
        
        
        if not flight_data.empty:
            # Hiển thị tiêu đề kết quả
            st.markdown(f"### 🛩️ Chuyến bay từ {source} đến {destination}")
            
            # Hiển thị bảng chuyến bay
            # st.dataframe(flight_data, use_container_width=True)
            st.dataframe(
                flight_data.style.set_properties(**{
                    'background-color': '#f9f9f9',
                    'color': '#333333',
                    'border': '1px solid #ddd',
                    'text-align': 'center'
                }).set_table_styles([{
                    'selector': 'th',
                    'props': [('background-color', '#3498db'), ('color', 'white'), ('font-weight', 'bold')]
                }])
            )


            # Cho phép người dùng chọn chuyến bay
            flight_index = st.selectbox(
                "Chọn một chuyến bay để xem chi tiết",
                flight_data.index
                #format_func=lambda x: f"{flight_data.loc[x, 'Hãng hàng không']} - {flight_data.loc[x, 'Thời gian khởi hành']}"
            )

            # Hiển thị thông tin chi tiết của chuyến bay đã chọn
            selected_flight = flight_data.loc[flight_index]

            # Tạo các cột để hiển thị thông tin chi tiết
            col_left, col_right = st.columns([3, 2])

            with col_left:
                # Hiển thị thông tin chi tiết
                st.metric("🏢 Hãng hàng không", selected_flight['Hãng hàng không'])
                # st.metric("🛬 Thời gian đến", selected_flight['Thời gian đến'].split(" ")[1])


            with col_right:
                st.metric("💺 Hạng ghế", selected_flight['Hạng ghế'])
                # st.metric("🕒 Thời gian khởi hành", selected_flight['Thời gian khởi hành'])

                # st.metric("💰 Giá vé", f"{selected_flight['Giá vé']:,.0f} VND")
                # st.metric("🛫 Chuyến bay trực tiếp", "Có" if selected_flight['Chuyến bay trực tiếp'] else "Không")
                
            col_left, col_right = st.columns([1, 1])

            with col_left:
                # Hiển thị thông tin chi tiết
                st.metric("🕒 Thời gian khởi hành", selected_flight['Thời gian khởi hành'].split(" ")[1])
                st.metric("🛬 Thời gian đến", selected_flight['Thời gian đến'].split(" ")[1])

                st.metric("💰 Giá vé", f"{selected_flight['Giá vé']:,.0f} VND")

            with col_right:
                st.metric("🕒 Ngày khởi hành", selected_flight['Thời gian khởi hành'].split(" ")[0])
                st.metric("🛬 Ngày đến", selected_flight['Thời gian đến'].split(" ")[0])


                st.metric("🛫 Chuyến bay trực tiếp", "Có" if selected_flight['Chuyến bay trực tiếp'] else "Không")           
            
            
            # Lấy lịch sử thay đổi giá vé
            flight_history = get_flight_price_history(
                conn,
                source,
                destination,
                selected_flight['Thời gian khởi hành'],
                selected_flight['Hạng ghế'],
                selected_flight['Hãng hàng không']
            )

            # Hiển thị lịch sử thay đổi giá vé và phân tích giá
            if not flight_history.empty:
                # Tính toán khoảng giá và so sánh
                price_range = analyze_flight_prices(
                    conn,
                    source, 
                    destination, 
                    selected_flight['Hạng ghế'],
                    selected_flight['Hãng hàng không'],
                    selected_flight['Thời gian khởi hành'].split(' ', 1)[1]
                )
                        
                # Hiển thị thông báo so sánh giá
                # Tính toán độ chênh lệch giá
                current_price = selected_flight['Giá vé']
                if price_range[0] > 0 and price_range[1] > 0:
                    avg_price = (price_range[0] + price_range[1]) / 2
                    price_difference = avg_price - current_price

                    if price_difference > 0:
                        # Nếu giá hiện tại thấp hơn giá trung bình
                        st.info(f"{current_price:,.0f} ₫ là mức giá **thấp** cho {selected_flight['Hạng ghế']}, "
                                f"rẻ hơn bình thường {price_difference:,.0f} ₫", icon="📉")
                    elif price_difference < 0:
                        # Nếu giá hiện tại cao hơn giá trung bình
                        st.info(f"{current_price:,.0f} ₫ là mức giá **cao** cho {selected_flight['Hạng ghế']}, "
                                f"đắt hơn bình thường {abs(price_difference):,.0f} ₫", icon="📈")
                    else:
                        # Nếu giá hiện tại gần như bằng giá trung bình
                        st.info(f"{current_price:,.0f} ₫ là mức giá **trung bình** cho {selected_flight['Hạng ghế']}", icon="🔍")
                                    
                # Vẽ biểu đồ khoảng giá
                create_price_comparison_chart(
                    price_range[0],  # lower_price
                    price_range[1],  # upper_price
                    selected_flight['Giá vé']  # current_price
                )
                
                st.markdown("#### 📊 Biểu đồ lịch sử giá vé")
                
                # Chuyển đổi cột Ngày cào sang datetime
                flight_history['Ngày cào'] = pd.to_datetime(flight_history['Ngày cào'])
                
                # Tạo biểu đồ đường sử dụng Plotly
                fig = px.line(
                    flight_history, 
                    x='Ngày cào', 
                    y='Giá vé', 
                    title=f"Lịch sử thay đổi giá của chuyến bay khởi hành {selected_flight['Thời gian khởi hành']} của hãng hàng không {selected_flight['Hãng hàng không']}",
                    labels={'Ngày cào': 'Ngày', 'Giá vé': 'Giá vé (VND)'}
                )
                
                # Tùy chỉnh giao diện biểu đồ
                fig.update_layout(
                    xaxis_title="Ngày",
                    yaxis_title="Giá vé (VND)",
                    hovermode="x unified",
                    plot_bgcolor='rgba(240,240,240,0.8)',
                    paper_bgcolor='rgba(0,0,0,0)'
                )
                
                # Hiển thị biểu đồ
                st.plotly_chart(fig, use_container_width=True)
                
        #       # Hiển thị bảng lịch sử giá
        #         st.subheader("Lịch sử giá vé")
        #         st.dataframe(flight_history.style.format({"Giá vé": "{:,.0f}"}))
        #     else:
        #         st.warning("Không có dữ liệu lịch sử giá vé.")      
        # else:
        #     st.warning("Không có chuyến bay nào phù hợp với tiêu chí tìm kiếm.")     

            
            # # Lấy lịch sử thay đổi giá vé
            # flight_history = get_flight_price_history(
            #     conn,
            #     source,
            #     destination,
            #     selected_flight['Thời gian khởi hành'],
            #     selected_flight['Hạng ghế'],
            #     selected_flight['Hãng hàng không']
                
            # )
             # Add a section for weather information
            # Thêm phần thời tiết điểm đi và điểm đến
            with st.expander("🌦️ Thông tin thời tiết cho chuyến bay", expanded=True):
                # Tạo hai cột ngang để hiển thị thông tin thời tiết
                col_departure, col_arrival = st.columns(2)
                
                # Thông tin thời tiết tại điểm khởi hành
                with col_departure:
                    st.markdown("### ⛅ Điểm khởi hành")
                    departure_date = pd.to_datetime(selected_flight['Thời gian khởi hành']).date()
                    departure_weather_info = get_weather(source, departure_date)
                    
                    if departure_weather_info:
                        # Hiển thị thông tin thời tiết điểm khởi hành
                        st.markdown(f"**🌡️ Nhiệt độ TB:** {departure_weather_info['temperature']:.1f}°C")
                        st.markdown(f"**🌞 Cao nhất:** {departure_weather_info['max_temp']:.1f}°C")
                        st.markdown(f"**🌡️ Thấp nhất:** {departure_weather_info['min_temp']:.1f}°C")
                        st.markdown(f"**🌬️ Gió:** {departure_weather_info['max_wind']} km/h")
                        st.markdown(f"**💧 Độ ẩm:** {departure_weather_info['humidity']}%")
                        st.image(departure_weather_info['icon'], width=50, caption="Biểu tượng thời tiết")
                        st.caption(f"**Mô tả:** {departure_weather_info['condition']}")
                    else:
                        st.warning("Không thể tải thông tin thời tiết tại điểm khởi hành.")
                
                # Thông tin thời tiết tại điểm đến
                with col_arrival:
                    st.markdown("### ⛅ Điểm đến")
                    arrival_date = pd.to_datetime(selected_flight['Thời gian đến']).date()
                    arrival_weather_info = get_weather(destination, arrival_date)
                    
                    if arrival_weather_info:
                        # Hiển thị thông tin thời tiết điểm đến
                        st.markdown(f"**🌡️ Nhiệt độ TB:** {arrival_weather_info['temperature']:.1f}°C")
                        st.markdown(f"**🌞 Cao nhất:** {arrival_weather_info['max_temp']:.1f}°C")
                        st.markdown(f"**🌡️ Thấp nhất:** {arrival_weather_info['min_temp']:.1f}°C")
                        st.markdown(f"**🌬️ Gió:** {arrival_weather_info['max_wind']} km/h")
                        st.markdown(f"**💧 Độ ẩm:** {arrival_weather_info['humidity']}%")
                        st.image(arrival_weather_info['icon'], width=50, caption="Biểu tượng thời tiết")
                        st.caption(f"**Mô tả:** {arrival_weather_info['condition']}")
                    else:
                        st.warning("Không thể tải thông tin thời tiết tại điểm đến.")





                        
    conn.close()
 
if __name__ == "__main__":
    main()