class RecommendationEngine:
    @staticmethod
    def get_recommendation(row):
        """
        Returns a recommended action based on process stats and classification.
        """
        if row.get('classification') == 'NORMAL':
            return "No action required."
            
        recs = []
        if row.get('cpu_percent', 0) > 80:
            recs.append("Process is consuming excessive CPU. Consider terminating if unresponsive.")
        if row.get('memory_percent', 0) > 80:
            recs.append("High memory usage detected. Check for memory leaks.")
        if row.get('io_write_rate', 0) > 1024*1024*20:
            recs.append("High disk write activity. Monitor for potential ransomware or heavy logging.")
        if row.get('num_threads', 0) > 150:
            recs.append("Unusually high thread count. Investigate process behaviour.")
            
        if not recs:
            recs.append("Investigate the process and verify whether the activity is authorized.")
            
        return " ".join(recs)
