# Skill: Time Series Forecasting

## Purpose
To predict future values based on previously observed time-ordered data, considering trends, seasonality, and exogenous variables.

## When to Use
- When forecasting sales, inventory, stock prices, or resource demand
- When identifying anomalies in system metrics over time
- When working with IoT sensor data

## Procedure

### 1. Identify the Time Series Characteristics
Analyze the data for:
- **Trend**: Long-term upward or downward movement.
- **Seasonality**: Repeating patterns at fixed intervals (daily, weekly, yearly).
- **Stationarity**: Whether statistical properties (mean, variance) change over time.

### 2. Choose the Forecasting Model
Select an appropriate algorithm based on data complexity:
- **ARIMA / SARIMA**: Traditional statistical models. Best for univariate data with clear seasonality.
- **Prophet (by Meta)**: Excellent for business time series with daily observations and strong seasonal effects.
- **XGBoost / LightGBM**: Effective for tabular time series with many exogenous features.
- **LSTMs / Transformers (e.g., Temporal Fusion Transformer)**: Best for complex, non-linear relationships and long sequences.

### 3. Prophet Implementation Example

**Setup and Fitting**:
```python
from prophet import Prophet
import pandas as pd

# Data must have 'ds' (datestamp) and 'y' (target) columns
df = pd.read_csv('sales_data.csv')
df.rename(columns={'date': 'ds', 'sales': 'y'}, inplace=True)

# Initialize Prophet model
m = Prophet(
    yearly_seasonality=True,
    weekly_seasonality=True,
    daily_seasonality=False
)

# Add custom holidays or exogenous variables if necessary
m.add_country_holidays(country_name='US')

# Fit the model
m.fit(df)
```

**Forecasting**:
```python
# Create future dates
future = m.make_future_dataframe(periods=365)

# Predict future values
forecast = m.predict(future)

# Plotting results
fig1 = m.plot(forecast)
fig2 = m.plot_components(forecast)
```

### 4. Evaluation Metrics
Use appropriate error metrics for time series:
- **MAE (Mean Absolute Error)**: Easy to interpret, robust to outliers.
- **RMSE (Root Mean Squared Error)**: Penalizes large errors heavily.
- **MAPE (Mean Absolute Percentage Error)**: Useful for comparing relative performance across different scales.

```python
from sklearn.metrics import mean_absolute_error, mean_squared_error
import numpy as np

mae = mean_absolute_error(y_true, y_pred)
rmse = np.sqrt(mean_squared_error(y_true, y_pred))
```

### 5. Cross-Validation
Do not use standard K-Fold cross-validation. Use Time Series Split to respect temporal order.

```python
from sklearn.model_selection import TimeSeriesSplit

tscv = TimeSeriesSplit(n_splits=5)
for train_index, test_index in tscv.split(X):
    X_train, X_test = X[train_index], X[test_index]
    y_train, y_test = y[train_index], y[test_index]
    # Train and evaluate model
```

## Best Practices
- Always plot your data before modeling. Visual inspection reveals obvious anomalies or structural breaks.
- Use baseline models (like naive forecasting or moving average) to establish a performance floor before moving to complex models.
- Handle missing values carefully; avoid interpolating over large gaps without justification.