# AI ProcessGuard

## Project Title
AI ProcessGuard: An Intelligent Real-Time Process Anomaly Detection and Resource Monitoring System

## Project Objective
The objective of this project is to build an Operating Systems mini project that monitors OS processes in real-time and detects anomalies using Machine Learning (Isolation Forest). It goes beyond simple thresholds by analyzing process behavior patterns.

## Problem Statement
Traditional operating system task managers provide raw metrics (CPU, Memory, Threads) but lack the intelligence to automatically flag suspicious processes based on behavioural patterns. A normal process might have high CPU usage, while a suspicious one might have unusual thread spiking combined with disk I/O, which goes unnoticed by standard task managers.

## Proposed Solution
AI ProcessGuard uses a machine learning pipeline to learn the baseline behaviour of system processes and apply an Unsupervised Learning algorithm (Isolation Forest) to detect anomalies in real-time. It maps these anomalies to a Risk Score (0-100) and categorizes processes as NORMAL, SUSPICIOUS, or ABNORMAL.

## Architecture
```
REAL OS PROCESSES
       ↓
PSUTIL
       ↓
PANDAS DATAFRAME
       ↓
FEATURE ENGINEERING
       ↓
ISOLATION FOREST
       ↓
ANOMALY OUTPUT
       ↓
RISK ENGINE
       ↓
CLASSIFICATION (NORMAL / SUSPICIOUS / ABNORMAL)
       ↓
ALERT + RECOMMENDATION
       ↓
STREAMLIT
       ↓
PLOTLY / MATPLOTLIB
       ↓
BROWSER
```

**Architecture Explanation:**
- **Collection**: `psutil` accesses raw operating system properties to gather live resource consumption parameters for every active PID.
- **Processing**: The data is loaded into `Pandas` dataframes where missing values are handled and delta features (like I/O rates and usage changes) are computed dynamically.
- **Machine Learning Engine**: These structured features are passed to the `Isolation Forest` model (either loaded from a persisted file or trained live at startup), which computes a normalized anomaly score. This is fed to the Risk Engine where specific thresholds boost the risk rating to output a final 0-100 score, dictating classifications. The result is then surfaced through `Streamlit` incorporating live analytics via `Plotly` and `Matplotlib`.

## Technology Stack & Demonstration Map

| Technology | Actual Implementation | What Reviewer Should See |
| --- | --- | --- |
| Python | Core backend execution | System running via `app.py` |
| psutil | `core/process_collector.py` | Live system and process data on Dashboard |
| Pandas | `core/feature_engine.py` / `app.py` | Tabular grids under Live Processes |
| NumPy | `core/feature_engine.py` / `core/anomaly_detector.py` | Handled bounds and normalized risk scores |
| Scikit-learn | `core/anomaly_detector.py` | Model status metrics on AI / Model page |
| Isolation Forest | `core/anomaly_detector.py` | Risk score fluctuations reflecting anomalies |
| Streamlit | `app.py` | Entire web UI layout and refresh logic |
| Plotly | `visualization/plotly_charts.py` | Interactive timeline charts in Dashboard |
| Matplotlib | `visualization/matplotlib_charts.py` | Heatmaps and distribution in Analytics |

## Installation

1. Clone or download the repository to `OSSP_project/`
2. Open a terminal in the `OSSP_project` directory.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running Instructions
Run the Streamlit application:
```bash
streamlit run app.py
```

## ML Approach & Baseline
We use **Isolation Forest** with 100 estimators and 5% contamination. 
- **Baseline Strategy**: The system attempts to load a persisted model on startup. If no persisted model is found, the system immediately grabs a live snapshot of all active processes and fits the Isolation Forest to establish a fresh baseline.
- **Features Used**: CPU/Memory utilisation, Thread Count, Process Age, Child Process count, IO Read/Write rate, and delta deviations. We strictly drop PIDs and Names before predicting to prevent the ML from identifying processes instead of behavioral anomalies.

## Real-time Monitoring & "Why Was This Flagged?"
The system runs a continuous loop gathering snapshots of all active OS processes every ~3 seconds. 
Alerts are generated for SUSPICIOUS or ABNORMAL processes with specific tags derived from underlying metrics:
- *High CPU deviation/usage*
- *High memory deviation/usage*
- *Thread deviation/spike*
- *High I/O rate*
- *Behavioural deviation detected by ML model* (for multi-dimensional anomalies where the model isolates a process but hard-thresholds aren't specifically triggered).

## Reviewer Demonstration Guide
To effectively demonstrate this implementation to a reviewer, follow this sequence:
1. **Start Application:** `streamlit run app.py`
2. **Dashboard Overview:** Point out real system metrics (Total processes, CPU, RAM).
3. **Live Processes:** Navigate to Live Processes to show the `psutil` + `Pandas` dataframe in action.
4. **AI / Model Page:** Display the ML parameters. Highlight the Isolation Forest integration and click **Retrain Baseline Now**.
5. **Analytics:** Show the interactive Plotly graphs and Matplotlib Heatmaps processing the live snapshot.
6. **Demo Mode:** Start a **CPU** or **Combined** anomaly.
7. **Observe Detection:** Show the newly spawned `ProcessGuard-DemoWorker`. Observe its features spike, then watch as the Risk Score rapidly climbs.
8. **Classification Shift:** Emphasize the transition from `NORMAL` → `SUSPICIOUS` → `ABNORMAL`.
9. **Alert System:** Open the generated alert, and click into **Process Details** using the Demo Worker's PID.
10. **Explainability:** Show the *WHY WAS THIS FLAGGED?* reasoning and the provided recommendation.
11. **Clean up:** Navigate back to Demo Mode and safely stop it via **STOP DEMO**. 

## Known Limitations
- `psutil` exact I/O byte counts can throw `AccessDenied` on system processes depending on OS execution privileges; these default cleanly to zero.
- Python subprocesses representing the DemoWorker may appear differently (`python.exe` vs `python3`) across OSs; we employ `cmdline` scanning to detect and forcefully label it in the UI.
- The Isolation Forest detects behaviour snapshots; very slow, deliberate throttled malware falls outside the scope of current immediate-deviation heuristics.

## Future Improvements
- Persistent historical data storage layer (e.g. SQLite/PostgreSQL) instead of session buffers.
- Adaptive rolling baselines for the ML model over time.
- Integrated Network socket behaviour analysis.
