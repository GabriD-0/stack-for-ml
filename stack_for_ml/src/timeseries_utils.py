"""Reusable helpers for the Stack Overflow time-series assignment.

The functions here are intentionally small and notebook-friendly: they keep the
report reproducible while leaving the narrative and plots in the notebook.
"""

from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass
import json
import re
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.tree import DecisionTreeRegressor
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.tsa.holtwinters import ExponentialSmoothing, Holt
from statsmodels.tsa.statespace.sarimax import SARIMAX


TARGET = "daily_questions"
DEFAULT_FEATURES = [
    "lag1",
    "lag7",
    "lag14",
    "rolling7",
    "rolling14",
    "dow_sin",
    "dow_cos",
    "month_sin",
    "month_cos",
    "is_weekend",
    "trend",
]


@dataclass(frozen=True)
class ForecastResult:
    """Standard container for forecasts used in comparisons."""

    name: str
    y_pred: pd.Series
    metrics: dict[str, float]
    params: dict[str, object]


def load_questions(csv_path: str | Path) -> pd.DataFrame:
    """Load the Stack Overflow ML dataset with parsed datetimes."""

    df = pd.read_csv(csv_path)
    df["creation_date"] = pd.to_datetime(df["creation_date"], errors="coerce")
    if "last_activity_date" in df.columns:
        df["last_activity_date"] = pd.to_datetime(
            df["last_activity_date"], errors="coerce"
        )
    return df


def build_daily_series(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate question rows into a complete daily time series."""

    if df["creation_date"].isna().any():
        raise ValueError("creation_date contains invalid timestamps.")

    daily = (
        df.assign(date=df["creation_date"].dt.floor("D"))
        .groupby("date")
        .size()
        .rename(TARGET)
        .to_frame()
        .sort_index()
    )
    full_index = pd.date_range(daily.index.min(), daily.index.max(), freq="D")
    daily = daily.reindex(full_index)
    daily.index.name = "date"
    return daily


def quality_diagnostic(raw_df: pd.DataFrame, daily: pd.DataFrame) -> pd.DataFrame:
    """Build the quality diagnostic required by the assignment."""

    complete_index = pd.date_range(daily.index.min(), daily.index.max(), freq="D")
    missing_dates = complete_index.difference(daily.dropna().index)

    rows = []
    for col in [TARGET]:
        series = daily[col]
        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        outliers = int(((series < lower) | (series > upper)).sum())
        rows.append(
            {
                "coluna": col,
                "nulos": int(series.isna().sum()),
                "datas_duplicadas": int(daily.index.duplicated().sum()),
                "gaps_datas": int(len(missing_dates)),
                "outliers_iqr": outliers,
                "acao": "manter; representam picos/quedas reais de atividade",
            }
        )

    rows.append(
        {
            "coluna": "creation_date",
            "nulos": int(raw_df["creation_date"].isna().sum()),
            "datas_duplicadas": "n/a em granularidade de pergunta",
            "gaps_datas": int(len(missing_dates)),
            "outliers_iqr": "n/a",
            "acao": "usar para agregacao diaria",
        }
    )
    return pd.DataFrame(rows)


def add_time_features(daily: pd.DataFrame) -> pd.DataFrame:
    """Create lags, rolling means and cyclic calendar features."""

    df = daily.copy()
    df["lag1"] = df[TARGET].shift(1)
    df["lag7"] = df[TARGET].shift(7)
    df["lag14"] = df[TARGET].shift(14)
    df["rolling7"] = df[TARGET].shift(1).rolling(7).mean()
    df["rolling14"] = df[TARGET].shift(1).rolling(14).mean()

    dow = df.index.dayofweek
    month = df.index.month
    df["dow_sin"] = np.sin(2 * np.pi * dow / 7)
    df["dow_cos"] = np.cos(2 * np.pi * dow / 7)
    df["month_sin"] = np.sin(2 * np.pi * month / 12)
    df["month_cos"] = np.cos(2 * np.pi * month / 12)
    df["is_weekend"] = (dow >= 5).astype(int)
    df["trend"] = np.arange(len(df))
    return df.dropna()


def temporal_split(df: pd.DataFrame, train_size: float = 0.8) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split a time-series frame without shuffling."""

    split_idx = int(len(df) * train_size)
    return df.iloc[:split_idx].copy(), df.iloc[split_idx:].copy()


def regression_metrics(y_true: Iterable[float], y_pred: Iterable[float]) -> dict[str, float]:
    """Compute MAE, RMSE and MAPE for positive-count series."""

    y_true_s = pd.Series(y_true, dtype=float)
    y_pred_s = pd.Series(y_pred, dtype=float)
    mae = mean_absolute_error(y_true_s, y_pred_s)
    rmse = float(np.sqrt(mean_squared_error(y_true_s, y_pred_s)))
    non_zero = y_true_s != 0
    mape = np.nan
    if non_zero.any():
        mape = float(np.mean(np.abs((y_true_s[non_zero] - y_pred_s[non_zero]) / y_true_s[non_zero])) * 100)
    return {"mae_teste": float(mae), "rmse_teste": float(rmse), "mape_teste": float(mape)}


def baseline_persistence(train: pd.Series, test: pd.Series) -> ForecastResult:
    """Naive baseline: each day repeats the previous observed value."""

    history = pd.concat([train.iloc[[-1]], test.iloc[:-1]])
    pred = pd.Series(history.to_numpy(), index=test.index, name="baseline_persistencia")
    return ForecastResult(
        name="baseline_persistencia",
        y_pred=pred,
        metrics=regression_metrics(test, pred),
        params={"strategy": "previous_observed_value"},
    )


def baseline_moving_average(train: pd.Series, test: pd.Series, window: int = 7) -> ForecastResult:
    """Rolling mean baseline with recursive updates from observed test values."""

    history = list(train.astype(float).to_numpy())
    predictions = []
    for actual in test.astype(float).to_numpy():
        predictions.append(float(np.mean(history[-window:])))
        history.append(actual)
    pred = pd.Series(predictions, index=test.index, name=f"baseline_media_movel_{window}")
    return ForecastResult(
        name=f"baseline_media_movel_{window}",
        y_pred=pred,
        metrics=regression_metrics(test, pred),
        params={"window": window},
    )


def fit_sarimax_grid(
    train: pd.Series,
    test: pd.Series,
    orders: list[tuple[int, int, int]] | None = None,
    seasonal_orders: list[tuple[int, int, int, int]] | None = None,
) -> tuple[ForecastResult, pd.DataFrame, object]:
    """Fit a compact SARIMAX grid and return the lowest-AIC model."""

    if orders is None:
        orders = [(0, 0, 1), (1, 0, 0), (1, 0, 1), (2, 0, 1), (1, 1, 1), (2, 1, 1)]
    if seasonal_orders is None:
        seasonal_orders = [(0, 0, 0, 0), (1, 0, 1, 7), (0, 1, 1, 7)]

    rows = []
    best_fit = None
    best_spec = None
    best_aic = np.inf

    for order in orders:
        for seasonal_order in seasonal_orders:
            try:
                model = SARIMAX(
                    train,
                    order=order,
                    seasonal_order=seasonal_order,
                    enforce_stationarity=False,
                    enforce_invertibility=False,
                )
                fit = model.fit(disp=False)
                aic = float(fit.aic)
                rows.append({"order": order, "seasonal_order": seasonal_order, "aic": aic, "status": "ok"})
                if aic < best_aic:
                    best_aic = aic
                    best_fit = fit
                    best_spec = (order, seasonal_order)
            except Exception as exc:  # pragma: no cover - diagnostic table captures failures.
                rows.append(
                    {
                        "order": order,
                        "seasonal_order": seasonal_order,
                        "aic": np.nan,
                        "status": f"erro: {type(exc).__name__}",
                    }
                )

    if best_fit is None or best_spec is None:
        raise RuntimeError("No SARIMAX specification converged.")

    forecast = best_fit.get_forecast(steps=len(test)).predicted_mean
    forecast.index = test.index
    order, seasonal_order = best_spec
    result = ForecastResult(
        name=f"sarimax_{order}_{seasonal_order}",
        y_pred=forecast.rename("sarimax"),
        metrics=regression_metrics(test, forecast),
        params={"order": order, "seasonal_order": seasonal_order, "aic": best_aic},
    )
    return result, pd.DataFrame(rows).sort_values("aic", na_position="last"), best_fit


def fit_exponential_smoothing(train: pd.Series, test: pd.Series) -> tuple[ForecastResult, object]:
    """Fit Holt-Winters with weekly seasonality, falling back to Holt if needed."""

    params: dict[str, object]
    try:
        model = ExponentialSmoothing(
            train,
            trend="add",
            seasonal="add",
            seasonal_periods=7,
            initialization_method="estimated",
        )
        fit = model.fit(optimized=True)
        params = {"family": "Holt-Winters", "trend": "add", "seasonal": "add", "seasonal_periods": 7}
        name = "holtwinters_add_weekly"
    except Exception:
        model = Holt(train, initialization_method="estimated")
        fit = model.fit(optimized=True)
        params = {"family": "Holt", "trend": "add", "seasonal": None}
        name = "holt_linear"

    pred = fit.forecast(len(test))
    pred.index = test.index
    return (
        ForecastResult(name=name, y_pred=pred.rename(name), metrics=regression_metrics(test, pred), params=params),
        fit,
    )


def fit_ml_model(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    features: list[str] | None = None,
    complex_model: bool = False,
) -> tuple[ForecastResult, object, dict[str, float]]:
    """Fit a tabular ML model for the engineered time-series features."""

    if features is None:
        features = DEFAULT_FEATURES

    X_train = train_df[features]
    y_train = train_df[TARGET]
    X_test = test_df[features]
    y_test = test_df[TARGET]

    if complex_model:
        model = DecisionTreeRegressor(max_depth=None, min_samples_leaf=1, random_state=42)
        name = "decision_tree_complexa"
        params = {"model": "DecisionTreeRegressor", "max_depth": None, "min_samples_leaf": 1, "features": features}
    else:
        model = GradientBoostingRegressor(
            n_estimators=120,
            learning_rate=0.05,
            max_depth=2,
            min_samples_leaf=5,
            random_state=42,
        )
        name = "gradient_boosting"
        params = {
            "model": "GradientBoostingRegressor",
            "n_estimators": 120,
            "learning_rate": 0.05,
            "max_depth": 2,
            "min_samples_leaf": 5,
            "features": features,
        }

    model.fit(X_train, y_train)
    pred = pd.Series(model.predict(X_test), index=y_test.index, name=name)
    train_pred = pd.Series(model.predict(X_train), index=y_train.index)
    train_metrics = {
        "mae_treino": regression_metrics(y_train, train_pred)["mae_teste"],
        "rmse_treino": regression_metrics(y_train, train_pred)["rmse_teste"],
    }
    return ForecastResult(name=name, y_pred=pred, metrics=regression_metrics(y_test, pred), params=params), model, train_metrics


def residual_diagnostics(residuals: pd.Series, lags: int = 14) -> pd.DataFrame:
    """Run Ljung-Box diagnostics for champion residuals."""

    return acorr_ljungbox(residuals.dropna(), lags=[min(lags, max(1, len(residuals.dropna()) // 2))], return_df=True)


def walk_forward_sarimax(
    series: pd.Series,
    order: tuple[int, int, int],
    seasonal_order: tuple[int, int, int, int],
    initial_window: int = 120,
    step: int = 7,
) -> pd.DataFrame:
    """Walk-forward validation with periodic SARIMAX refits."""

    rows = []
    for start in range(initial_window, len(series), step):
        train = series.iloc[:start]
        test = series.iloc[start : start + step]
        if len(test) == 0:
            break
        model = SARIMAX(
            train,
            order=order,
            seasonal_order=seasonal_order,
            enforce_stationarity=False,
            enforce_invertibility=False,
        )
        fit = model.fit(disp=False)
        pred = fit.get_forecast(steps=len(test)).predicted_mean
        pred.index = test.index
        metrics = regression_metrics(test, pred)
        rows.append(
            {
                "inicio_teste": test.index.min(),
                "fim_teste": test.index.max(),
                "n_teste": len(test),
                **metrics,
            }
        )
    return pd.DataFrame(rows)


def log_wandb_run(
    name: str,
    metrics: dict[str, float],
    params: dict[str, object],
    y_true: pd.Series,
    y_pred: pd.Series,
    project: str = "stack-overflow-timeseries-n3",
) -> None:
    """Log one experiment to wandb, defaulting to offline mode."""

    os.environ.setdefault("WANDB_MODE", "offline")
    local_wandb_dir = Path(os.environ.get("WANDB_DIR", Path.cwd() / "wandb"))
    local_tmp_dir = Path(os.environ.get("TMP", Path.cwd() / ".tmp_wandb"))
    local_wandb_dir.mkdir(exist_ok=True)
    local_tmp_dir.mkdir(exist_ok=True)
    os.environ.setdefault("WANDB_DIR", str(local_wandb_dir))
    os.environ.setdefault("WANDB_CACHE_DIR", str(local_wandb_dir / "cache"))
    os.environ.setdefault("WANDB_CONFIG_DIR", str(local_wandb_dir / "config"))
    os.environ.setdefault("WANDB_DATA_DIR", str(local_wandb_dir / "data"))
    os.environ.setdefault("TMP", str(local_tmp_dir))
    os.environ.setdefault("TEMP", str(local_tmp_dir))
    os.environ.setdefault("TMPDIR", str(local_tmp_dir))
    tempfile.tempdir = str(local_tmp_dir)
    try:
        import wandb
    except ImportError:
        print(f"wandb nao instalado; run '{name}' nao foi logado.")
        return

    def write_fallback(reason: str) -> None:
        fallback_dir = local_wandb_dir / "offline-fallback-runs"
        fallback_dir.mkdir(parents=True, exist_ok=True)
        safe_name = re.sub(r"[^A-Za-z0-9_.-]+", "_", name).strip("_")
        payload = {
            "project": project,
            "name": name,
            "metrics": metrics,
            "params": {key: str(value) for key, value in params.items()},
            "reason": reason,
            "predictions": [
                {"date": str(idx.date()), "y_true": float(y_true.loc[idx]), "y_pred": float(y_pred.loc[idx])}
                for idx in y_true.index.intersection(y_pred.index)
            ],
        }
        (fallback_dir / f"{safe_name}.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")

    try:
        with wandb.init(
            project=project,
            name=name,
            config=params,
            dir=str(local_wandb_dir),
            reinit=True,
        ) as run:
            run.log(metrics)
            comparison = pd.DataFrame(
                {
                    "date": y_true.index.astype(str),
                    "y_true": y_true.to_numpy(),
                    "y_pred": y_pred.reindex(y_true.index).to_numpy(),
                }
            )
            run.log({"previsao_teste": wandb.Table(dataframe=comparison)})
    except Exception as exc:  # pragma: no cover - environment-dependent fallback.
        write_fallback(f"{type(exc).__name__}: {exc}")
        print(f"wandb fallback local para run '{name}'; metricas salvas em wandb/offline-fallback-runs.")
