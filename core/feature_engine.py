import pandas as pd
import numpy as np

class FeatureEngine:
    def __init__(self):
        self.previous_df = None
        
    def create_features(self, current_df):
        """
        Creates ML features from the raw DataFrame.
        Maintains history to calculate rates if previous_df exists.
        """
        if current_df is None or current_df.empty:
            return pd.DataFrame()
            
        features_df = current_df.copy()
        
        # We need to compute I/O rates and changes
        if self.previous_df is not None and not self.previous_df.empty:
            # Merge with previous df to calculate rates
            merged = features_df.merge(self.previous_df, on='pid', how='left', suffixes=('', '_prev'))
            
            # Calculate time difference
            dt = np.maximum(merged['timestamp'] - merged['timestamp_prev'], 0.1) # avoid div by zero
            
            # I/O rates
            features_df['io_read_rate'] = (merged['read_bytes'] - merged['read_bytes_prev'].fillna(0)) / dt
            features_df['io_write_rate'] = (merged['write_bytes'] - merged['write_bytes_prev'].fillna(0)) / dt
            
            # Behaviour deviations
            features_df['cpu_change'] = (merged['cpu_percent'] - merged['cpu_percent_prev'].fillna(0)).abs()
            features_df['memory_change'] = (merged['memory_percent'] - merged['memory_percent_prev'].fillna(0)).abs()
            features_df['thread_change'] = (merged['num_threads'] - merged['num_threads_prev'].fillna(0)).abs()
            
        else:
            features_df['io_read_rate'] = 0.0
            features_df['io_write_rate'] = 0.0
            features_df['cpu_change'] = 0.0
            features_df['memory_change'] = 0.0
            features_df['thread_change'] = 0.0
            
        # Update history
        self.previous_df = current_df[['pid', 'timestamp', 'read_bytes', 'write_bytes', 'cpu_percent', 'memory_percent', 'num_threads']].copy()
        
        # Replace negative values with 0 (can happen if counters reset)
        features_df['io_read_rate'] = features_df['io_read_rate'].clip(lower=0)
        features_df['io_write_rate'] = features_df['io_write_rate'].clip(lower=0)
        
        # Select final ML features
        # DO NOT include pid or name in the features dataset for ML
        ml_feature_columns = [
            'cpu_percent',
            'memory_percent',
            'num_threads',
            'process_age_seconds',
            'child_count',
            'io_read_rate',
            'io_write_rate',
            'cpu_change',
            'memory_change',
            'thread_change'
        ]
        
        # Fill NA with 0 for safety
        features_df.fillna(0, inplace=True)
        
        # We return both the full dataframe with new columns and the ML-specific dataframe
        ml_df = features_df[ml_feature_columns]
        
        return features_df, ml_df
