import uuid
import datetime

class AlertEngine:
    def __init__(self):
        self.alerts = []
        
    def generate_alerts(self, df):
        """
        Generates alerts for ABNORMAL or SUSPICIOUS processes.
        """
        if df is None or df.empty:
            return []
            
        new_alerts = []
        
        # Filter only suspicious and abnormal
        flagged = df[df['classification'].isin(['SUSPICIOUS', 'ABNORMAL'])]
        
        for _, row in flagged.iterrows():
            severity = "High" if row['classification'] == "ABNORMAL" else "Medium"
            
            # Determine reasons
            reasons = []
            if row.get('cpu_change', 0) > 20 or row.get('cpu_percent', 0) > 50:
                reasons.append("High CPU deviation/usage")
            if row.get('memory_change', 0) > 20 or row.get('memory_percent', 0) > 50:
                reasons.append("High memory deviation/usage")
            if row.get('thread_change', 0) > 20 or row.get('num_threads', 0) > 100:
                reasons.append("Thread deviation/spike")
            if row.get('io_write_rate', 0) > 1024*1024*10 or row.get('io_read_rate', 0) > 1024*1024*10:
                reasons.append("High I/O rate")
                
            if not reasons:
                reasons.append("Behavioural deviation detected by ML model")
                
            alert = {
                "alert_id": str(uuid.uuid4())[:8],
                "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
                "process": row['name'],
                "pid": row['pid'],
                "risk_score": row['risk_score'],
                "severity": severity,
                "reason": ", ".join(reasons)
            }
            new_alerts.append(alert)
            
            # Add to history, keeping max 100
            self.alerts.insert(0, alert)
            
        self.alerts = self.alerts[:100]
        return new_alerts
        
    def get_recent_alerts(self):
        return self.alerts
