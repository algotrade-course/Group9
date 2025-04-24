import pandas as pd
import psycopg
import pandas as pd
import numpy as np
from decimal import Decimal
import matplotlib.pyplot as plt
from typing import List
import os

# ------------------------------
# 1. Data Acquisition from Database
# ------------------------------

# Database connection info
db_info = {
    "host": "api.algotrade.vn",
    "port": 5432,
    "database": "algotradeDB",
    "user": "intern_read_only",
    "password": "ZmDaLzFf8pg5"
}

# Connect to the algotrade database and fetch VN30INDEX data
def get_data_from_db():
    with psycopg.connect(
        host=db_info['host'],
        port=db_info['port'],
        dbname=db_info['database'],
        user=db_info['user'],
        password=db_info['password']
    ) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT m.datetime, m.tickersymbol, m.price
                FROM "quote"."matched" m
                LEFT JOIN "quote"."total" v
                ON m.tickersymbol = v.tickersymbol
                AND m.datetime = v.datetime
                WHERE m.datetime BETWEEN '2021-02-08' and '2025-03-20'
                AND m.tickersymbol LIKE 'VN30F%'
            """)
            result = cur.fetchall()

    # Create DataFrame
    df = pd.DataFrame(result, columns=['Date', 'TickerSymbol', 'Close'])
    return df

# ------------------------------
# 2. Data Preprocessing
# ------------------------------

def preprocess_data(df):
    # Làm lại index để xử lý
    df = df.reset_index()

    # Chuyển Date sang datetime nếu chưa (phòng trường hợp chưa chạy dòng này)
    df['Date'] = pd.to_datetime(df['Date'])

    # Bỏ các bản ghi trước 09:00 mỗi ngày
    df = df[df['Date'].dt.time >= pd.to_datetime("09:00:00").time()]

    # Làm tròn xuống đến phút (bỏ giây và microsecond)
    df['Minute'] = df['Date'].dt.floor('T')  # 'T' là phút

    # Lấy bản ghi đầu tiên cho mỗi phút
    df_minutely = df.sort_values('Date').groupby('Minute').first().reset_index()

    # Đổi tên lại cho gọn
    df_minutely.rename(columns={'Minute': 'Date'}, inplace=True)

    # Đổi tên cột để dễ xử lý (tránh trùng lặp)
    df_minutely.columns = ['Date_1', 'index', 'Date_2', 'TickerSymbol', 'Close']

    # Giữ lại cột 'Date_1' và các cột cần thiết khác
    df_minutely = df_minutely[['Date_1', 'TickerSymbol', 'Close']]

    # Đổi tên 'Date_1' thành lại 'Date nếu bạn muốn
    df_minutely.rename(columns={'Date_1': 'Date'}, inplace=True)
    
    return df_minutely

# ------------------------------
# 3. Split Data into In-sample and Out-sample
# ------------------------------

def split_data(df_minutely):
    df_minutely.set_index('Date', inplace=True)

    # Calculate number of rows for in-sample data (70% of the total rows)
    num_in_sample_rows = int(len(df_minutely) * 0.7)

    # Split the data using the number of rows
    in_sample_data = df_minutely.iloc[:num_in_sample_rows].copy()
    out_sample_data = df_minutely.iloc[num_in_sample_rows:].copy()

    # Ensure no overlap or gaps between the datasets
    # Check the max date of in-sample and min date of out-sample to see if they match
    print(f"In-sample period: {in_sample_data.index.min().date()} to {in_sample_data.index.max().date()}")
    print(f"Out-sample period: {out_sample_data.index.min().date()} to {out_sample_data.index.max().date()}")

    # Check the exact timestamps
    print("In-sample last timestamp:", in_sample_data.index[-1])
    print("Out-sample first timestamp:", out_sample_data.index[0])

    # If the last row of in-sample and the first row of out-sample have the same timestamp,
    # shift the start of the out-sample data by one row
    if in_sample_data.index[-1] == out_sample_data.index[0]:
        out_sample_data = out_sample_data.iloc[1:]

    print("Updated Out-sample Period:")
    print(f"Out-sample period: {out_sample_data.index.min().date()} to {out_sample_data.index.max().date()}")

    # Return the split datasets
    return in_sample_data, out_sample_data

# ------------------------------
# 4. Save Data to CSV
# ------------------------------

def save_data_to_csv(in_sample_data, out_sample_data):
    if not os.path.exists('data'):
        os.makedirs('data')

    # Export to CSV
    in_sample_data.to_csv("data/in_sample_data.csv")
    out_sample_data.to_csv("data/out_sample_data.csv")

    print("CSV files have been successfully saved.")

# ------------------------------
# 5. Load Data
# ------------------------------
def load_data(in_sample_path="data/in_sample_data.csv", out_sample_path="data/out_sample_data.csv"):
    """
    Load in-sample and out-of-sample datasets from CSV files.
    
    Returns:
        Tuple of DataFrames: (in_sample_df, out_sample_df)
    """
    if not os.path.exists(in_sample_path) or not os.path.exists(out_sample_path):
        print("Tệp dữ liệu chưa có. Đang tạo dữ liệu mới...")
        # Nếu không có tệp, chạy main để tạo chúng
        main()

    # in_sample_df = pd.read_csv(in_sample_path)
    in_sample_df = pd.read_csv(in_sample_path, parse_dates=True, index_col=0)
    out_sample_df = pd.read_csv(out_sample_path, parse_dates=True, index_col=0)
    return in_sample_df, out_sample_df

# Main Function to Execute All Steps
def main():
    # 1. Get Data
    df = get_data_from_db()

    # 2. Preprocess Data
    df_minutely = preprocess_data(df)

    # 3. Split Data into In-sample and Out-sample
    in_sample_data, out_sample_data = split_data(df_minutely)

    # 4. Save Data to CSV
    save_data_to_csv(in_sample_data, out_sample_data)

# Run the main function
if __name__ == "__main__":
    main()
