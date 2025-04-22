# optimize.py

import optuna
from optuna.samplers import TPESampler

from data import load_data
from strategy import run_strategy
from evaluate import sharpe_ratio, maximum_drawdown
from utils import plot_all_optuna

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

    return best_params, asset_df

if __name__ == "__main__":
    in_sample_df, out_sample_df = load_data()
    
    print("🔍 Running Optimization...")
    study = run_optimization(out_sample_df, n_trials=12, seed=710)

    best_params, asset_df = evaluate_best_strategy(study, out_sample_df)

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
