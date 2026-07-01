import pandas as pd
from typing import List, Dict, Any
from sklearn.ensemble import IsolationForest
import numpy as np
from src.services.data_loader import data_loader

class AnomalyDetector:
    def __init__(self):
        pass

    def detect_anomalies(self) -> List[Dict[str, Any]]:
        df = data_loader.get_dataframe()
        anomalies = []

        # 1. Heuristic: Unresolved high-priority tickets older than 24 hours
        # Assume "current time" is the max created_at time in the dataset or a fixed point if needed.
        # Here we'll use the max created_at plus 1 day to simulate "now" if not real-time.
        current_time = df['created_at'].max() if pd.notnull(df['created_at'].max()) else pd.Timestamp.now()
        
        # 'Critical' and 'High' priority
        high_priority = df['priority'].isin(['High', 'Critical'])
        unresolved = df['status'].isin(['Open', 'Escalated'])
        
        # tickets older than 24h
        df['age_hours'] = (current_time - df['created_at']).dt.total_seconds() / 3600
        older_than_24h = df['age_hours'] > 24
        
        heuristic_anomalies = df[high_priority & unresolved & older_than_24h]
        for _, row in heuristic_anomalies.iterrows():
            anomalies.append({
                "ticket_id": row['ticket_id'],
                "type": "Heuristic",
                "reason": "Unresolved high-priority ticket older than 24 hours",
                "details": f"Priority: {row['priority']}, Age: {row['age_hours']:.1f} hrs"
            })

        # 2. Statistical / ML: Abnormally long resolution times
        resolved_df = df[df['resolution_time_hrs'].notnull()].copy()
        if not resolved_df.empty:
            # We can use IsolationForest on resolution time and response time
            features = resolved_df[['resolution_time_hrs']].fillna(0)
            
            # Simple IQR approach for 1D data is often more explainable, but IF is good too.
            # Let's use Isolation Forest as an ML approach
            iso = IsolationForest(contamination=0.05, random_state=42)
            preds = iso.fit_predict(features)
            
            resolved_df['is_anomaly'] = preds
            ml_anomalies = resolved_df[resolved_df['is_anomaly'] == -1]
            
            for _, row in ml_anomalies.iterrows():
                # Only flag as anomaly if it's exceptionally high (not exceptionally low)
                if row['resolution_time_hrs'] > features['resolution_time_hrs'].mean():
                    anomalies.append({
                        "ticket_id": row['ticket_id'],
                        "type": "Statistical",
                        "reason": "Abnormally long resolution time",
                        "details": f"Resolution time: {row['resolution_time_hrs']} hrs"
                    })

        return anomalies

anomaly_detector = AnomalyDetector()
