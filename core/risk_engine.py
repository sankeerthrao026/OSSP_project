import pandas as pd
import numpy as np

class RiskEngine:
    def __init__(self):
        pass
        
    def calculate_risk(self, df, anomaly_scores):
        """
        Calculates a 0-100 risk score based on the ML anomaly score and deterministic signals.
        """
        if df is None or df.empty:
            return []
            
        risk_scores = []
        
        for i in range(len(df)):
            row = df.iloc[i]
            base_score = anomaly_scores[i] * 100  # Convert 0-1 to 0-100
            
            # Boost score based on extreme deterministic signals to ensure we catch bad actors 
            # even if ML is still adjusting
            boost = 0
            
            # CPU > 80%
            if row.get('cpu_percent', 0) > 80:
                boost += 15
            elif row.get('cpu_percent', 0) > 50:
                boost += 5
                
            # High memory usage
            if row.get('memory_percent', 0) > 80:
                boost += 15
                
            # Thread spikes (assuming > 100 threads is unusual for most, adjust as needed)
            if row.get('num_threads', 0) > 100:
                boost += 10
                
            # High IO
            if row.get('io_write_rate', 0) > 1024*1024*50: # 50 MB/s
                boost += 15
                
            # Process Age (new processes doing lots of stuff are riskier)
            if row.get('process_age_seconds', 0) < 60 and row.get('cpu_percent', 0) > 20:
                boost += 10
                
            # Calculate final score and clamp to 0-100
            final_score = base_score + boost
            final_score = np.clip(final_score, 0, 100)
            
            risk_scores.append(int(final_score))
            
        return risk_scores
