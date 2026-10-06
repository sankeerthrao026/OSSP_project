import streamlit as st
import time
import pandas as pd
import psutil

# Core modules
from core.process_collector import ProcessCollector
from core.feature_engine import FeatureEngine
from core.anomaly_detector import AnomalyDetector
from core.risk_engine import RiskEngine
from core.classifier import Classifier
from core.alert_engine import AlertEngine
from core.recommendation_engine import RecommendationEngine
from demo.demo_controller import DemoController

# Visualizations
from visualization.plotly_charts import plot_realtime_cpu_memory, plot_risk_distribution, plot_process_history
from visualization.matplotlib_charts import plot_anomaly_distribution, plot_feature_correlation

st.set_page_config(page_title="AI ProcessGuard", layout="wide", initial_sidebar_state="expanded")

# --- Initialize session state ---
if 'collector' not in st.session_state:
    st.session_state.collector = ProcessCollector()
    st.session_state.feature_engine = FeatureEngine()
    st.session_state.anomaly_detector = AnomalyDetector()
    st.session_state.risk_engine = RiskEngine()
    st.session_state.classifier = Classifier()
    st.session_state.alert_engine = AlertEngine()
    st.session_state.demo_controller = DemoController()
    st.session_state.process_history = []
    st.session_state.system_history = []
    st.session_state.is_monitoring = False
    
    # Attempt initial training if model isn't trained
    if not st.session_state.anomaly_detector.is_trained:
        st.info("Training initial baseline model...")
        df = st.session_state.collector.collect_processes()
        _, ml_df = st.session_state.feature_engine.create_features(df)
        st.session_state.anomaly_detector.train(ml_df)
        st.success("Initial baseline trained.")
        time.sleep(1)

# --- Sidebar Navigation ---
st.sidebar.title("🛡️ AI ProcessGuard")
st.sidebar.markdown("Real-Time Intelligent Process Anomaly Detection")

pages = ["Dashboard", "Live Processes", "Process Details", "Alerts", "AI / Model", "Analytics", "System Information", "Architecture", "Technology Stack", "Demo Mode"]
page = st.sidebar.radio("Navigation", pages)

# --- Refresh Control ---
st.sidebar.markdown("---")
auto_refresh = st.sidebar.checkbox("Auto-Refresh (3s)", value=True)

# --- Processing Pipeline ---
def run_pipeline():
    # 1. Collect Processes
    sys_metrics = st.session_state.collector.collect_system_metrics()
    st.session_state.system_history.append(sys_metrics)
    if len(st.session_state.system_history) > 100:
        st.session_state.system_history.pop(0)
        
    df = st.session_state.collector.collect_processes()
    
    # Demo worker might show up as python.exe. We rename it for UI if we find commandline args containing demo_worker.
    # psutil cmdline can throw access denied, so we wrap it.
    for p in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmd = p.info.get('cmdline', [])
            if cmd and 'demo_worker.py' in ' '.join(cmd):
                # Update name in our df
                df.loc[df['pid'] == p.pid, 'name'] = 'ProcessGuard-DemoWorker'
        except:
            pass

    # 2. Feature Engine
    features_df, ml_df = st.session_state.feature_engine.create_features(df)
    
    # 3. ML Anomaly Score
    anomaly_scores = st.session_state.anomaly_detector.predict(ml_df)
    
    # 4. Risk Score
    risk_scores = st.session_state.risk_engine.calculate_risk(features_df, anomaly_scores)
    features_df['risk_score'] = risk_scores
    
    # 5. Classification
    classifications = st.session_state.classifier.classify_list(risk_scores)
    features_df['classification'] = classifications
    
    # 6. Alerts & Recommendations
    st.session_state.alert_engine.generate_alerts(features_df)
    
    # Save a slice for process history (limit size to prevent memory leak)
    # Only save top risky ones to history to save memory, plus demo worker
    top_risky = features_df.sort_values(by='risk_score', ascending=False).head(50)
    demo_worker_df = features_df[features_df['name'] == 'ProcessGuard-DemoWorker']
    history_slice = pd.concat([top_risky, demo_worker_df]).drop_duplicates(subset=['pid'])
    
    st.session_state.process_history.append(history_slice)
    if len(st.session_state.process_history) > 50:
        st.session_state.process_history.pop(0)
        
    return sys_metrics, features_df

sys_metrics, current_df = run_pipeline()

# --- Page Content ---
if page == "Dashboard":
    st.title("📊 Dashboard")
    
    # Top metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    total_procs = len(current_df)
    normal = len(current_df[current_df['classification'] == 'NORMAL'])
    suspicious = len(current_df[current_df['classification'] == 'SUSPICIOUS'])
    abnormal = len(current_df[current_df['classification'] == 'ABNORMAL'])
    
    col1.metric("Total Processes", total_procs)
    col2.metric("Normal", normal)
    col3.metric("Suspicious", suspicious, delta_color="off")
    col4.metric("Abnormal", abnormal, delta_color="inverse")
    col5.metric("System CPU", f"{sys_metrics['cpu_usage_percent']}%")
    
    # Charts
    st.markdown("### System Resource Usage")
    sys_df = pd.DataFrame(st.session_state.system_history)
    st.plotly_chart(plot_realtime_cpu_memory(sys_df), use_container_width=True)
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("### Top Risky Processes")
        top_df = current_df.sort_values(by='risk_score', ascending=False).head(5)
        st.dataframe(top_df[['pid', 'name', 'risk_score', 'classification', 'cpu_percent']], use_container_width=True)
    with col_b:
        st.markdown("### Recent Alerts")
        alerts = st.session_state.alert_engine.get_recent_alerts()[:5]
        if alerts:
            for alert in alerts:
                if alert['severity'] == 'High':
                    st.error(f"{alert['process']} (PID: {alert['pid']}) - Risk: {alert['risk_score']}")
                else:
                    st.warning(f"{alert['process']} (PID: {alert['pid']}) - Risk: {alert['risk_score']}")
        else:
            st.info("No active alerts.")

elif page == "Live Processes":
    st.title("🔬 Live Process Monitor")
    
    search = st.text_input("Search by Process Name or PID:")
    
    display_df = current_df[['pid', 'name', 'status', 'cpu_percent', 'memory_percent', 'num_threads', 'io_read_rate', 'io_write_rate', 'risk_score', 'classification']]
    
    if search:
        display_df = display_df[display_df['name'].str.contains(search, case=False) | display_df['pid'].astype(str).str.contains(search)]
        
    st.dataframe(display_df.style.apply(
        lambda x: ['background: rgba(255,0,0,0.2)' if x['classification'] == 'ABNORMAL' 
                   else ('background: rgba(255,165,0,0.2)' if x['classification'] == 'SUSPICIOUS' else '') for i in x], 
        axis=1
    ), use_container_width=True, height=600)

elif page == "Process Details":
    st.title("🔎 Process Details")
    
    pid_to_check = st.number_input("Enter PID to investigate:", min_value=0, step=1)
    
    if pid_to_check > 0:
        process_data = current_df[current_df['pid'] == pid_to_check]
        if not process_data.empty:
            row = process_data.iloc[0]
            st.subheader(f"Details for {row['name']} (PID: {row['pid']})")
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Risk Score", f"{row['risk_score']}/100")
            col2.metric("Classification", row['classification'])
            col3.metric("CPU %", f"{row['cpu_percent']:.1f}%")
            col4.metric("Memory %", f"{row['memory_percent']:.1f}%")
            
            col5, col6, col7, col8 = st.columns(4)
            col5.metric("Status", row['status'])
            col6.metric("Threads", row['num_threads'])
            col7.metric("Process Age", f"{row['process_age_seconds']:.0f}s")
            col8.metric("I/O Write Rate", f"{row['io_write_rate']/1024/1024:.2f} MB/s")
            
            st.markdown("### WHY WAS THIS FLAGGED?")
            if row['classification'] == 'NORMAL':
                st.success("This process is behaving normally.")
            else:
                reasons = []
                if row.get('cpu_change', 0) > 20 or row.get('cpu_percent', 0) > 50:
                    reasons.append(f"High CPU deviation/usage (Currently {row['cpu_percent']:.1f}%)")
                if row.get('memory_change', 0) > 20 or row.get('memory_percent', 0) > 50:
                    reasons.append(f"High memory deviation/usage (Currently {row['memory_percent']:.1f}%)")
                if row.get('thread_change', 0) > 20 or row.get('num_threads', 0) > 100:
                    reasons.append(f"Thread deviation/spike (Currently {row['num_threads']} threads)")
                if row.get('io_write_rate', 0) > 1024*1024*10:
                    reasons.append(f"High I/O rate (Currently {row['io_write_rate']/1024/1024:.2f} MB/s)")
                
                if not reasons:
                    reasons.append("Behavioural deviation detected by ML Isolation Forest model across multiple combined features.")
                    
                for r in reasons:
                    st.error(f"- {r}")
                    
            st.markdown("### Recommended Action")
            rec = RecommendationEngine.get_recommendation(row)
            st.info(rec)
            
            st.markdown("### Historical Behaviour")
            if st.session_state.process_history:
                hist_df = pd.concat(st.session_state.process_history)
                st.plotly_chart(plot_process_history(hist_df, pid_to_check), use_container_width=True)
        else:
            st.warning("Process not found or no longer active.")

elif page == "Alerts":
    st.title("🚨 Alerts")
    alerts = st.session_state.alert_engine.get_recent_alerts()
    if alerts:
        alerts_df = pd.DataFrame(alerts)
        st.dataframe(alerts_df, use_container_width=True)
    else:
        st.success("No alerts generated yet.")

elif page == "AI / Model":
    st.title("🧠 AI / ML Engine")
    
    st.markdown("""
    ### Framework: Scikit-learn
    ### Algorithm: Isolation Forest
    ### Learning: Unsupervised Anomaly Detection
    """)
    
    st.markdown("### Features Extracted for ML:")
    cols = ['cpu_percent', 'memory_percent', 'num_threads', 'process_age_seconds', 'child_count', 'io_read_rate', 'io_write_rate', 'cpu_change', 'memory_change', 'thread_change']
    st.write(cols)
    
    st.markdown("### Model Status:")
    detector = st.session_state.anomaly_detector
    
    col1, col2 = st.columns(2)
    col1.metric("Is Trained", "Yes" if detector.is_trained else "No")
    col1.metric("Training Samples", detector.training_samples)
    col2.metric("Estimators", detector.model.n_estimators)
    col2.metric("Contamination", detector.model.contamination)
    
    st.text(f"Last Training Time: {detector.last_training_time}")
    
    if st.button("Retrain Baseline Now"):
        st.info("Collecting current processes and retraining...")
        df = st.session_state.collector.collect_processes()
        _, ml_df = st.session_state.feature_engine.create_features(df)
        st.session_state.anomaly_detector.train(ml_df)
        st.success("Retraining complete!")

elif page == "Analytics":
    st.title("📈 Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.plotly_chart(plot_risk_distribution(current_df), use_container_width=True)
        
    with col2:
        st.pyplot(plot_anomaly_distribution(current_df))
        
    st.markdown("### Feature Correlation")
    st.pyplot(plot_feature_correlation(current_df))

elif page == "System Information":
    st.title("💻 System Information")
    
    col1, col2 = st.columns(2)
    col1.metric("Operating System", sys_metrics['os_name'])
    col1.metric("CPU Count", sys_metrics['cpu_count'])
    col1.metric("Boot Time", sys_metrics['boot_time'])
    col1.metric("System Uptime (s)", f"{sys_metrics['uptime_seconds']:.0f}")
    
    col2.metric("Total Memory (GB)", f"{sys_metrics['total_memory_gb']:.2f}")
    col2.metric("Available Memory (GB)", f"{sys_metrics['available_memory_gb']:.2f}")
    col2.metric("Memory Usage %", f"{sys_metrics['memory_usage_percent']}")
    col2.metric("CPU Usage %", f"{sys_metrics['cpu_usage_percent']}")

elif page == "Architecture":
    st.title("🏗️ System Architecture")
    
    st.code("""
OS PROCESSES
       ↓
PSUTIL
       ↓
PANDAS
       ↓
FEATURE ENGINEERING
       ↓
SCIKIT-LEARN
       ↓
ISOLATION FOREST
       ↓
ANOMALY SCORE
       ↓
RISK ENGINE
       ↓
CLASSIFICATION (NORMAL / SUSPICIOUS / ABNORMAL)
       ↓
ALERTS + RECOMMENDATIONS
       ↓
STREAMLIT
       ↓
PLOTLY + MATPLOTLIB
       ↓
BROWSER
    """)

elif page == "Technology Stack":
    st.title("⚙️ Technology Stack")
    
    st.markdown("""
    - **PYTHON** → Core application
    - **PSUTIL** → Real OS/process monitoring
    - **PANDAS** → DataFrames and data processing
    - **NUMPY** → Numerical processing
    - **SCIKIT-LEARN** → Machine Learning
    - **ISOLATION FOREST** → Unsupervised anomaly detection
    - **PLOTLY** → Interactive visualization
    - **MATPLOTLIB** → Analytical visualization
    - **STREAMLIT** → Web dashboard
    - **BROWSER** → Dashboard access
    """)

elif page == "Demo Mode":
    st.title("🧪 Demo Mode")
    st.markdown("### CONTROLLED DEMONSTRATION")
    st.warning("This safely generates resource anomalies to demonstrate the AI ProcessGuard detection pipeline.")
    
    anomaly_type = st.selectbox("Select Anomaly Scenario", ['cpu', 'memory', 'thread', 'io', 'combined'])
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("START DEMO", type="primary"):
            pid = st.session_state.demo_controller.start_demo(anomaly_type)
            st.success(f"Demo started! ProcessGuard-DemoWorker spawned with PID: {pid}. Wait a few seconds for the ML to detect it.")
    with col2:
        if st.button("STOP DEMO"):
            st.session_state.demo_controller.stop_demo()
            st.success("Demo stopped.")
            
    st.markdown("---")
    st.markdown("### Pipeline Review")
    st.markdown("""
    When Demo is running, observe:
    1. ProcessGuard-DemoWorker appears in Live Processes
    2. Risk Score goes up as Isolation Forest detects deviation
    3. Classification moves NORMAL → SUSPICIOUS → ABNORMAL
    4. Alert is generated
    5. Check Process Details page for 'WHY WAS THIS FLAGGED?'
    """)
    
    demo_active = current_df[current_df['name'] == 'ProcessGuard-DemoWorker']
    if not demo_active.empty:
        st.subheader("⚠️ Demo Worker Active")
        st.dataframe(demo_active[['pid', 'name', 'risk_score', 'classification', 'cpu_percent', 'memory_percent', 'num_threads', 'io_write_rate']])
    else:
        st.info("Demo worker is currently inactive.")

if auto_refresh:
    time.sleep(3)
    st.rerun()
