# Final Audit Summary

## Project Status

Reviewer Ready
(Final Verified Status: Successfully validated post-documentation and dependency corrections)

## Technology Stack Audit
| Technology | Required | Implemented | Verified | Location |
| --- | --- | --- | --- | --- |
| Python | Yes | Yes | Yes | Entire codebase |
| psutil | Yes | Yes | Yes | `core/process_collector.py` |
| Pandas | Yes | Yes | Yes | `core/feature_engine.py`, `app.py` |
| NumPy | Yes | Yes | Yes | `core/feature_engine.py`, `core/anomaly_detector.py` |
| Scikit-learn | Yes | Yes | Yes | `core/anomaly_detector.py` |
| Isolation Forest | Yes | Yes | Yes | `core/anomaly_detector.py` |
| Streamlit | Yes | Yes | Yes | `app.py` |
| Plotly | Yes | Yes | Yes | `visualization/plotly_charts.py` |
| Matplotlib | Yes | Yes | Yes | `visualization/matplotlib_charts.py` |

## Data Pipeline
Operational. OS Processes -> psutil -> Pandas -> Feature Engineering.

## ML Pipeline
Operational. Feature Engineering -> Isolation Forest -> Anomaly Score -> Risk Score -> Classification.

## Model Training & Baseline

### Baseline Strategy
Baseline behavioural data is obtained by capturing a live snapshot of current OS processes upon startup (`app.py` lines 36-41). The `ProcessCollector` fetches current processes via `psutil`, which are then transformed into feature matrices by `FeatureEngine`. If no pre-trained model is found, the system dynamically trains the baseline using this live OS snapshot.

### Training Configuration
- `n_estimators`: 100
- `contamination`: 0.05
- `random_state`: 42
- `training sample count`: Dynamically matches the number of active processes during the initialization snapshot.

### Model Lifecycle
- **Initialization**: Attempted on application startup. Loads `models/isolation_forest.pkl` if available.
- **Training**: Executed immediately if no model is loaded. Takes current active process dataframe features.
- **Prediction**: Runs every refresh cycle (~3s) on current process features.
- **Persistence**: Saved via `joblib` into `models/isolation_forest.pkl` after training.
- **Retraining**: Can be triggered manually via the Streamlit "AI / Model" page by collecting a new live process snapshot.

### Live Inference
BASELINE
↓
FEATURE MATRIX
↓
ISOLATION FOREST
↓
MODEL
↓
LIVE FEATURES (Processed every 3 seconds)
↓
PREDICTION (`model.decision_function()`)
↓
ANOMALY SCORE (Normalized 0.0 - 1.0)

## ML Feature Set

| Feature | Source | Type | Used by Model | Description |
| --- | --- | --- | --- | --- |
| `cpu_percent` | `psutil` | Raw | Yes | Current CPU utilization percentage |
| `memory_percent`| `psutil` | Raw | Yes | Current memory utilization percentage |
| `num_threads` | `psutil` | Raw | Yes | Number of active threads |
| `process_age_seconds` | Derived | Derived | Yes | Time elapsed since process creation |
| `child_count` | `psutil` | Raw | Yes | Number of child processes |
| `io_read_rate` | Derived | Derived | Yes | Bytes read per second (delta between snapshots) |
| `io_write_rate` | Derived | Derived | Yes | Bytes written per second (delta between snapshots) |
| `cpu_change` | Derived | Derived | Yes | Absolute change in CPU usage percentage since last snapshot |
| `memory_change` | Derived | Derived | Yes | Absolute change in memory usage percentage since last snapshot |
| `thread_change` | Derived | Derived | Yes | Absolute change in thread count since last snapshot |
| `pid` | `psutil` | Raw | **No** | Process ID intentionally excluded to prevent ML from memorizing PIDs. |
| `name` | `psutil` | Raw | **No** | Process name intentionally excluded to prevent arbitrary categorical/numerical conversions. |

## Risk Score Calculation
The risk score engine (`core/risk_engine.py`) maps the unbounded model anomaly scores into an intuitive 0–100 scale using both the ML signal and deterministic heuristics.
- **Source of anomaly signal**: `model.decision_function()` inverted so higher values are anomalous.
- **Normalization**: Clipped to a typical window (-0.3 to 0.3) and min-max scaled to 0-1, then multiplied by 100 for a base 0-100 score.
- **Supporting signals (Weighting / Boosts)**:
    - CPU > 80%: +15, or CPU > 50%: +5
    - Memory > 80%: +15
    - Threads > 100: +10
    - IO Write > 50MB/s: +15
    - New process (< 60s) & CPU > 20%: +10
- **Final Calculation**: `Base ML Score + Boosts`, clipped between `0` and `100`.

## Classification Logic
Classification thresholds are configured in `core/classifier.py`:
- `0–39` = NORMAL
- `40–69` = SUSPICIOUS
- `70–100` = ABNORMAL

## Alert Pipeline
Alerts are generated in `core/alert_engine.py` for any process entering `SUSPICIOUS` or `ABNORMAL` state.
The engine flags specific heuristics to explain "WHY WAS THIS FLAGGED?":
- High CPU deviation/usage
- High memory deviation/usage
- Thread deviation/spike
- High I/O rate
- Behavioural deviation detected by ML model (if no specific thresholds are tripped, meaning the Isolation Forest caught a complex multidimensional anomaly).

## Recommendation Pipeline
Recommendations are implemented in `core/recommendation_engine.py`. They check raw `cpu_percent`, `memory_percent`, `io_write_rate`, and `num_threads` to map generic advice like "Check for memory leaks" or "Investigate process behaviour".

## Dashboard
Operational. Includes all 10 required pages in Streamlit (`app.py`):
1. Dashboard
2. Live Processes
3. Process Details
4. Alerts
5. AI / Model
6. Analytics
7. System Information
8. Architecture
9. Technology Stack
10. Demo Mode

## Demo Mode
Operational. Starts a safe subprocess `ProcessGuard-DemoWorker` mimicking resource anomalies to trace the pipeline end-to-end.

## Validation Evidence

| Test | Status | Evidence |
| --- | --- | --- |
| Isolation Forest Training | PASS | Code inspection (`anomaly_detector.py:28`) shows `model.fit(ml_df)` used live. |
| Live Process Collection | PASS | `psutil.process_iter` returns active live processes with resource usage. |
| Pandas Processing | PASS | `feature_engine.py` merges dataframes and outputs structured datasets. |
| Risk Engine | PASS | `np.clip` bounds base risk + deterministic boosts strictly to `0-100`. |
| Classification | PASS | Verified strict bounds logic (39, 69) mapping correctly to NORMAL/SUSPICIOUS/ABNORMAL. |
| Plotly | PASS | Dashboards use `plotly.graph_objects` dynamically rendered in Streamlit. |
| Matplotlib | PASS | Static analytics (correlation heatmap) implemented via `seaborn`/`matplotlib`. |
| CPU Demo | PASS | `demo_worker.py` loops `math.sqrt` to artificially spike CPU. |
| Memory Demo | PASS | `demo_worker.py` allocates a 500MB bytearray to simulate a memory leak. |
| Thread Demo | PASS | `demo_worker.py` spawns 150 safe dummy threads. |
| I/O Demo | PASS | `demo_worker.py` writes 10MB temporary files continuously. |
| Combined Demo | PASS | Runs CPU, Memory, and Thread anomalies concurrently. |
| STOP DEMO | PASS | Uses `subprocess.call` with `taskkill /F /T` (Windows) or `SIGTERM` (Unix) to kill the worker safely. |

## Technology → Implementation → Demo Mapping
See `README.md` for full breakdown mapping.

## Known Limitations
- `psutil` permissions differ by OS (exact I/O counters throw `AccessDenied` on system processes). Handled cleanly by defaulting to `0` without crashing.
- Demo Worker Identification: Python subprocesses on non-Windows platforms may appear as `python` rather than the script name. The app circumvents this by scanning `psutil` command line arguments (`cmdline`) to rename it accurately in the UI.
- Anomaly detection relies heavily on current resource behavior patterns; malware specifically designed to throttle and act slowly over days may fall beneath the short-term deviation thresholds.
- The current baseline is static (or initialized from a live startup snapshot if no persisted model exists) and will not evolve naturally with long-running system usage changes; adaptive rolling baselines are a future improvement.

## Future Improvements
- Persistent historical database for long-term trending.
- Adaptive baseline retraining strategies.
- Network behaviour analysis (socket monitoring).

## Final File Structure
```
OSSP_project/
├── app.py
├── core/
│   ├── alert_engine.py
│   ├── anomaly_detector.py
│   ├── classifier.py
│   ├── feature_engine.py
│   ├── process_collector.py
│   ├── recommendation_engine.py
│   └── risk_engine.py
├── data/
├── demo/
│   ├── demo_controller.py
│   └── demo_worker.py
├── models/
├── PROJECT_STATE.md
├── README.md
├── requirements.txt
├── tests/
└── visualization/
    ├── matplotlib_charts.py
    └── plotly_charts.py
```

## How to Run
`streamlit run app.py`

## Reviewer Demonstration
Added dedicated Reviewer Demonstration section in `README.md`.
