# backtesting.py

import os
import argparse
import json
from strategy import run_strategy
from evaluate import sharpe_ratio, maximum_drawdown
from data import load_data
from matplotlib import pyplot as plt

default_params = {
    "sma_window": 100,
    "rsi_lower": 25.0,
    "rsi_upper": 75.0
}

def run_backtest(data, params):
    """
    Chạy backtest với các tham số đã cho và hiển thị kết quả.
    
    Args:
        params (dict): Dictionary chứa các tham số tốt nhất từ quá trình optimize.
        data (DataFrame): Dataset để backtest.
    """
    final_asset, asset_over_time_df = run_strategy(data, **params)

    print("\nBacktesting Evaluation:")
    print(f"  Final Asset Value: {final_asset}")
    print(f"  Sharpe Ratio: {sharpe_ratio(asset_over_time_df):.4f}")
    print(f"  Maximum Drawdown: {maximum_drawdown(asset_over_time_df):.2f}%")

    # Vẽ biểu đồ tài sản theo thời gian
    asset_over_time_df.plot(kind='line', figsize=(10, 5), title="Asset Over Time (Backtest)")
    plt.ylabel("Asset Value")
    plt.xlabel("Date")
    plt.gca().spines[['top', 'right']].set_visible(False)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run backtest with default or optimized params")
    parser.add_argument("--use-optimized", action="store_true", help="Use best_params from optimize step")
    args = parser.parse_args()
    
    # Load data
    in_sample_df, out_sample_df = load_data()

    # best_params = {
    #     "sma_window": 100,
    #     "rsi_lower": 25.0,
    #     "rsi_upper": 75.0
    # }
    if args.use_optimized:
        if os.path.exists("best_params.json"):
            with open("best_params.json", "r") as f:
                best_params = json.load(f)
            print("📈 Sử dụng best_params từ optimize:")
            print(best_params)
        else:
            print("⚠️ Không tìm thấy best_params.json! Sử dụng best_params mặc định.")
            best_params = default_params
    else:
        print("▶️ Sử dụng best_params mặc định.")
        best_params = default_params
    # best_params = {
    #     "sma_window": 200,
    #     "rsi_lower": 29.140662837219445,
    #     "rsi_upper": 65.00361398539523
    # }

    # Chạy trên out-sample
    run_backtest(out_sample_df, best_params)
