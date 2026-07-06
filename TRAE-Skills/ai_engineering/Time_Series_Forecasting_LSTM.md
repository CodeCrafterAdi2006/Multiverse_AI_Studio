# Skill: Time Series Forecasting with LSTM Networks

## Purpose
To build accurate time series prediction models using Long Short-Term Memory (LSTM) neural networks.

## When to Use
- For stock price prediction
- When forecasting sales or demand
- For predicting energy consumption
- When analyzing financial markets
- For weather forecasting with sequential data

## Procedure

### 1. Data Preparation
Prepare time series data for LSTM.

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split

# Load sample data
df = pd.read_csv('time_series_data.csv', parse_dates=['date'], index_col='date')
data = df[['value']].values

# Normalize data
scaler = MinMaxScaler(feature_range=(0, 1))
scaled_data = scaler.fit_transform(data)

# Create sequences
def create_sequences(data, time_steps=60):
    X, y = [], []
    for i in range(time_steps, len(data)):
        X.append(data[i-time_steps:i, 0])
        y.append(data[i, 0])
    return np.array(X), np.array(y)

time_steps = 60
X, y = create_sequences(scaled_data, time_steps)

# Reshape for LSTM (samples, time steps, features)
X = np.reshape(X, (X.shape[0], X.shape[1], 1))

# Split into train and test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
```

### 2. Build LSTM Model
Create an LSTM model with Keras.

```python
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint

model = Sequential([
    LSTM(50, return_sequences=True, input_shape=(X_train.shape[1], 1)),
    Dropout(0.2),
    LSTM(50, return_sequences=False),
    Dropout(0.2),
    Dense(25),
    Dense(1)
])

model.compile(optimizer=Adam(learning_rate=0.001), loss='mean_squared_error')

model.summary()
```

### 3. Train the Model
Train the LSTM model.

```python
callbacks = [
    EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True),
    ModelCheckpoint('best_model.h5', monitor='val_loss', save_best_only=True)
]

history = model.fit(
    X_train, y_train,
    batch_size=32,
    epochs=100,
    validation_data=(X_test, y_test),
    callbacks=callbacks
)

# Plot training history
plt.figure(figsize=(12, 6))
plt.plot(history.history['loss'], label='Training Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.title('Model Loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend()
plt.show()
```

### 4. Make Predictions
Generate predictions with the trained model.

```python
# Predict on test data
predictions = model.predict(X_test)
predictions = scaler.inverse_transform(predictions)
y_test_actual = scaler.inverse_transform(y_test.reshape(-1, 1))

# Plot results
train = df[:-len(y_test)]
valid = df[-len(y_test):]
valid['Predictions'] = predictions

plt.figure(figsize=(16, 8))
plt.title('Time Series Prediction')
plt.xlabel('Date', fontsize=18)
plt.ylabel('Value', fontsize=18)
plt.plot(train['value'])
plt.plot(valid[['value', 'Predictions']])
plt.legend(['Training Data', 'Actual Value', 'Predicted Value'], loc='lower right')
plt.show()
```

### 5. Evaluate the Model
Calculate evaluation metrics.

```python
from sklearn.metrics import mean_squared_error, mean_absolute_error, mean_absolute_percentage_error

rmse = np.sqrt(mean_squared_error(y_test_actual, predictions))
mae = mean_absolute_error(y_test_actual, predictions)
mape = mean_absolute_percentage_error(y_test_actual, predictions)

print(f'RMSE: {rmse:.2f}')
print(f'MAE: {mae:.2f}')
print(f'MAPE: {mape:.2%}')
```

### 6. Multi-Step Forecasting
Predict multiple future time steps.

```python
def multi_step_forecast(model, last_sequence, steps, scaler, time_steps):
    forecast = []
    current_sequence = last_sequence.copy()
    
    for _ in range(steps):
        # Predict next step
        prediction = model.predict(current_sequence.reshape(1, time_steps, 1), verbose=0)
        
        # Store prediction
        forecast.append(prediction[0, 0])
        
        # Update sequence
        current_sequence = np.roll(current_sequence, -1)
        current_sequence[-1] = prediction[0, 0]
    
    # Inverse transform
    forecast = scaler.inverse_transform(np.array(forecast).reshape(-1, 1))
    return forecast.flatten()

# Get the last sequence from training data
last_sequence = X_test[-1]

# Forecast next 30 days
forecast_steps = 30
forecast = multi_step_forecast(model, last_sequence, forecast_steps, scaler, time_steps)

# Create future dates
last_date = df.index[-1]
future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=forecast_steps)

# Plot forecast
plt.figure(figsize=(16, 8))
plt.plot(df['value'], label='Historical Data')
plt.plot(future_dates, forecast, label='Forecast', linestyle='--')
plt.title('Multi-Step Time Series Forecast')
plt.xlabel('Date')
plt.ylabel('Value')
plt.legend()
plt.show()
```

### 7. Multivariate LSTM
Use multiple features for prediction.

```python
# Load data with multiple features
df = pd.read_csv('multivariate_data.csv', parse_dates=['date'], index_col='date')
features = ['value', 'feature1', 'feature2', 'feature3']
data = df[features].values

# Normalize all features
scaler = MinMaxScaler(feature_range=(0, 1))
scaled_data = scaler.fit_transform(data)

# Create sequences with multiple features
def create_multivariate_sequences(data, time_steps=60):
    X, y = [], []
    for i in range(time_steps, len(data)):
        X.append(data[i-time_steps:i, :])  # All features
        y.append(data[i, 0])  # Target is first feature
    return np.array(X), np.array(y)

time_steps = 60
X, y = create_multivariate_sequences(scaled_data, time_steps)

# Build multivariate LSTM model
model = Sequential([
    LSTM(100, return_sequences=True, input_shape=(X.shape[1], X.shape[2])),
    Dropout(0.3),
    LSTM(100, return_sequences=False),
    Dropout(0.3),
    Dense(50),
    Dense(1)
])

model.compile(optimizer=Adam(learning_rate=0.001), loss='mean_squared_error')
```

## Best Practices
- **Normalize/Standardize**: Always normalize time series data
- **Sequence Length**: Choose appropriate time step window
- **Validation**: Use walk-forward validation for time series
- **Regularization**: Use dropout to prevent overfitting
- **Early Stopping**: Stop training when validation loss stops improving
- **Feature Engineering**: Create meaningful features (lags, rolling stats)
- **Ensemble**: Combine with ARIMA, Prophet for better results
- **Hyperparameter Tuning**: Optimize layers, units, learning rate
- **Monitor**: Track performance on both train and validation sets
- **Update**: Retrain model periodically with new data
