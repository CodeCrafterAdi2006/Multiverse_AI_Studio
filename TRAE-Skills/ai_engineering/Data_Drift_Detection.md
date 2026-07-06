# Skill: Data Drift Detection

## Purpose
To monitor production machine learning models for performance degradation caused by changes in the statistical properties of the input data (data drift) or the relationship between features and the target variable (concept drift) over time.

## When to Use
- When deploying models to production environments where data changes frequently (e.g., e-commerce, fraud detection, recommendation systems)
- When establishing a continuous training pipeline (MLOps)
- When debugging silent failures in model accuracy without corresponding system errors

## Procedure

### 1. Identify Drift Types
Distinguish between the types of drift occurring in the data:
- **Covariate Shift (Data Drift)**: The distribution of input features ($P(X)$) changes, but the relationship with the target remains the same.
- **Prior Probability Shift**: The distribution of the target variable ($P(Y)$) changes.
- **Concept Drift**: The relationship between features and the target ($P(Y|X)$) changes (e.g., a new type of fraud emerges).

### 2. Choose Detection Methods
Select appropriate statistical tests to compare a reference dataset (usually the training data) with the current production data:
- **Numerical Features**: Kolmogorov-Smirnov (K-S) test, Wasserstein distance, Population Stability Index (PSI).
- **Categorical Features**: Chi-Square test, Jensen-Shannon distance.
- **Multivariate**: Domain Classifier (train a model to distinguish between reference and current data).

### 3. Implementation Example (Evidently AI)
Evidently is an open-source library for monitoring ML models.

**Installation**:
```bash
pip install evidently
```

**Generate a Data Drift Report**:
```python
import pandas as pd
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset

# Load reference data (e.g., training set) and current data (e.g., last week's production data)
reference_data = pd.read_csv('train.csv')
current_data = pd.read_csv('production_week1.csv')

# Initialize the report with the DataDriftPreset
data_drift_report = Report(metrics=[DataDriftPreset()])

# Calculate metrics
data_drift_report.run(reference_data=reference_data, current_data=current_data)

# Save report as HTML
data_drift_report.save_html('data_drift_report.html')

# Get JSON output for programmatic integration (e.g., Airflow, Prefect)
drift_json = data_drift_report.json()
print(drift_json)
```

**Custom Tests and Thresholds**:
You can define specific tests for different features:
```python
from evidently.test_suite import TestSuite
from evidently.tests import TestNumberOfDriftedColumns, TestShareOfDriftedColumns
from evidently.tests.base_test import generate_column_tests
from evidently.tests import TestColumnDrift

suite = TestSuite(tests=[
    TestNumberOfDriftedColumns(lt=3), # Fail if more than 2 columns drift
    TestShareOfDriftedColumns(lt=0.3), # Fail if >30% of columns drift
    generate_column_tests(TestColumnDrift, columns=['age', 'income'])
])

suite.run(reference_data=reference_data, current_data=current_data)
suite.save_html('test_suite.html')
```

### 4. Alerting and Retraining Strategy
Establish a workflow when drift is detected:
1. **Alerting**: Send notifications via Slack, PagerDuty, or email when drift metrics exceed thresholds.
2. **Investigation**: Data scientists analyze the report to determine if the drift is benign (e.g., seasonal change) or harmful.
3. **Retraining**: Trigger a CI/CD pipeline to retrain the model on the new data, validate the new model against a holdout set, and deploy it if it outperforms the current model.

## Best Practices
- **Define a Baseline**: Always establish a solid baseline using the training dataset or a validated holdout set.
- **Choose the Right Window Size**: The timeframe for the "current" data depends on the business context. Daily, weekly, or monthly windows are common.
- **Monitor the Monitor**: Ensure the drift detection system itself is robust and doesn't generate excessive false positive alerts (alert fatigue).