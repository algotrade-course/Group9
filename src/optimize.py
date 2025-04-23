# optimize.py

import optuna
from optuna.samplers import TPESampler
import json
from src.data import load_data
from src.strategy import run_strategy
from src.evaluate import sharpe_ratio, maximum_drawdown, holding_period_return
from src.utils import plot_all_optuna

def objective(trial, data):
    sma_window = trial.suggest_int("sma_window", 50, 200)
    rsi_lower = trial.suggest_float("rsi_lower", 20.0, 35.0)
    rsi_upper = trial.suggest_float("rsi_upper", 65.0, 80.0)

    final_asset, _ = run_strategy(data, sma_window, rsi_lower, rsi_upper)
    return final_asset

def run_optimization(data, n_trials=20, seed=42):
    sampler = TPESampler(seed=seed)
    study = optuna.create_study(direction="maximize", sampler=sampler)

    study.optimize(lambda trial: objective(trial, data), n_trials=n_trials, show_progress_bar=True)

    return study

def evaluate_best_strategy(study, data):
    best_params = study.best_params
    final_asset, asset_df = run_strategy(data, **best_params)

    print(f"\nBest Trial:")
    print(f"  Final Asset: {final_asset}")
    for key, val in best_params.items():
        print(f"    {key}: {val}")

    print("\nEvaluation on Full Sample:")
    print(f"  Sharpe Ratio: {sharpe_ratio(asset_df):.4f}")
    print(f"  Maximum Drawdown: {maximum_drawdown(asset_df):.2f}%")
    print(f"  Accumulated return rate: {holding_period_return(asset_df):.2f}%")
    return best_params, asset_df

if __name__ == "__main__":
    in_sample_df, out_sample_df = load_data()
    
    print("🔍 Running Optimization...")

    # study = run_optimization(out_sample_df, n_trials=5, seed=710)
    # study = run_optimization(out_sample_df, n_trials=80, seed=710)
    study = run_optimization(in_sample_df, n_trials=80, seed=710)

    best_params, asset_df = evaluate_best_strategy(study, in_sample_df)

    # Sau khi evaluate_best_strategy()
    with open("best_params.json", "w") as f:
        json.dump(best_params, f, indent=4)
        print("✅ Đã lưu best_params vào best_params.json")

    # Vẽ biểu đồ asset và biểu đồ Optuna
    import matplotlib.pyplot as plt

    asset_df.plot(kind='line', figsize=(10, 5), title="Asset Over Time (Optimized)")
    plt.ylabel("Asset Value")
    plt.xlabel("Date")
    plt.gca().spines[['top', 'right']].set_visible(False)
    plt.tight_layout()
    plt.show()

    # Biểu đồ Optuna
    plot_all_optuna(study)
