# utils.py

import matplotlib.pyplot as plt
from optuna.visualization import (
    plot_optimization_history,
    plot_parallel_coordinate,
    plot_contour,
    plot_slice,
    plot_param_importances
)

def plot_price_with_sma(df, sma_col="SMA100"):
    plt.figure(figsize=(10, 5))
    plt.plot(df["Close"], label="Close Price")
    plt.plot(df[sma_col], label=sma_col)
    plt.title("Close Price with SMA")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.legend()
    plt.tight_layout()
    plt.show()
    plt.close()

def plot_rsi(df):
    plt.figure(figsize=(10, 3))
    plt.plot(df["RSI"], label="RSI", color="purple")
    plt.axhline(70, linestyle='--', color='red', label="RSI Upper")
    plt.axhline(30, linestyle='--', color='green', label="RSI Lower")
    plt.title("RSI Over Time")
    plt.ylabel("RSI")
    plt.legend()
    plt.tight_layout()
    plt.show()
    plt.close()

def plot_drawdown(df):
    peak = df["Asset"].cummax()
    drawdown = (df["Asset"] - peak) / peak
    plt.figure(figsize=(10, 3))
    plt.plot(drawdown, color="red")
    plt.title("Drawdown Over Time")
    plt.ylabel("Drawdown")
    plt.tight_layout()
    plt.show()
    plt.close()

def plot_asset_over_time(df, title="Asset Over Time"):
    df.plot(kind='line', figsize=(10, 5), title=title)
    plt.ylabel("Asset Value")
    plt.xlabel("Date")
    plt.gca().spines[['top', 'right']].set_visible(False)
    plt.tight_layout()
    plt.show()
    plt.close()

def plot_all_optuna(study):
    """
    Hàm này vẽ các biểu đồ đánh giá tối ưu hóa từ Optuna.
    """
    # Biểu đồ quá trình tối ưu hóa
    plot_optimization_history(study).show()

    # Biểu đồ biểu diễn các tham số trong quá trình tối ưu hóa
    plot_parallel_coordinate(study).show()

    # Biểu đồ Contour để thấy sự tương quan giữa các tham số
    plot_contour(study).show()

    # Biểu đồ phân đoạn của quá trình tối ưu hóa
    plot_slice(study).show()

    # Biểu đồ quan trọng của các tham số
    plot_param_importances(study).show()
