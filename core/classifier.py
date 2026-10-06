class Classifier:
    def __init__(self, normal_max=39, suspicious_max=69):
        self.normal_max = normal_max
        self.suspicious_max = suspicious_max
        
    def classify(self, risk_score):
        if risk_score <= self.normal_max:
            return "NORMAL"
        elif risk_score <= self.suspicious_max:
            return "SUSPICIOUS"
        else:
            return "ABNORMAL"
            
    def classify_list(self, risk_scores):
        return [self.classify(score) for score in risk_scores]
