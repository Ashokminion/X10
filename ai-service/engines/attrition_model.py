"""
Attrition Prediction Model using Random Forest
Predicts employee turnover risk based on historical data
"""
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
import pandas as pd
import numpy as np
import joblib
import os
import logging
from typing import Dict, List
from datetime import date

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AttritionPredictor:
    """
    Random Forest model for predicting employee attrition risk
    """
    
    def __init__(self, model_path=None):
        if model_path is None:
            # Get absolute path to the 'models' directory relative to this file
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            model_path = os.path.join(base_dir, "models")
        
        self.model_path = model_path
        self.model = None
        self.scaler = None
        self.feature_names = [
            'overtime_hours_3m',
            'night_shifts_count_3m',
            'performance_score',
            'absenteeism_rate',
            'tenure_months'
        ]
        
        if not os.path.exists(model_path):
            os.makedirs(model_path, exist_ok=True)
        
        # Try to load existing model
        self.load_model()
        
        # If no model exists, create a pretrained one
        if self.model is None:
            self._create_pretrained_model()
    
    def train(self, training_data: pd.DataFrame, labels: pd.Series):
        """
        Train the Random Forest model
        
        Args:
            training_data: DataFrame with features
            labels: Series with 0 (no attrition) or 1 (attrition)
        """
        logger.info("Training attrition prediction model...")
        
        # Scale features
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(training_data[self.feature_names])
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, labels, test_size=0.2, random_state=42
        )
        
        # Train Random Forest
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=10,
            min_samples_leaf=5,
            random_state=42,
            class_weight='balanced'
        )
        
        self.model.fit(X_train, y_train)
        
        # Evaluate
        train_score = self.model.score(X_train, y_train)
        test_score = self.model.score(X_test, y_test)
        
        logger.info(f"Training accuracy: {train_score:.3f}, Test accuracy: {test_score:.3f}")
        
        # Save model
        self.save_model()
        
        return {
            'train_accuracy': train_score,
            'test_accuracy': test_score,
            'n_features': len(self.feature_names)
        }
    
    def predict(self, employee_data: Dict) -> Dict:
        """
        Predict attrition risk for a single employee
        
        Args:
            employee_data: Dict containing feature values
            
        Returns:
            Dictionary with risk_score, risk_level, and features used
        """
        if self.model is None:
            raise ValueError("Model not trained. Please train or load a model first.")
        
        # Extract features
        features = np.array([[
            employee_data.get('overtime_hours_3m', 0),
            employee_data.get('night_shifts_count_3m', 0),
            employee_data.get('performance_score', 70),
            employee_data.get('absenteeism_rate', 0),
            employee_data.get('tenure_months', 12)
        ]])
        
        # Scale
        features_scaled = self.scaler.transform(features)
        
        # Predict probability
        risk_probability = self.model.predict_proba(features_scaled)[0][1]  # Probability of class 1 (attrition)
        
        # Classify risk level
        if risk_probability > 0.7:
            risk_level = "HIGH"
        elif risk_probability > 0.4:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        logger.info(f"Attrition prediction: {risk_level} (score: {risk_probability:.4f})")
        
        return {
            'risk_score': float(risk_probability),
            'risk_level': risk_level,
            'model_version': '1.0.0',
            'features_used': employee_data
        }
    
    def predict_batch(self, employees_data: List[Dict]) -> List[Dict]:
        """
        Predict attrition risk for multiple employees
        """
        results = []
        for emp_data in employees_data:
            try:
                prediction = self.predict(emp_data)
                prediction['employee_id'] = emp_data.get('employee_id')
                results.append(prediction)
            except Exception as e:
                logger.error(f"Prediction failed for employee {emp_data.get('employee_id')}: {str(e)}")
                results.append({
                    'employee_id': emp_data.get('employee_id'),
                    'error': str(e)
                })
        
        return results
    
    def save_model(self):
        """Save model and scaler to disk"""
        model_file = os.path.join(self.model_path, 'attrition_model.pkl')
        scaler_file = os.path.join(self.model_path, 'attrition_scaler.pkl')
        
        joblib.dump(self.model, model_file)
        joblib.dump(self.scaler, scaler_file)
        
        logger.info(f"Model saved to {model_file}")
    
    def load_model(self):
        """Load model and scaler from disk"""
        model_file = os.path.join(self.model_path, 'attrition_model.pkl')
        scaler_file = os.path.join(self.model_path, 'attrition_scaler.pkl')
        
        if os.path.exists(model_file) and os.path.exists(scaler_file):
            self.model = joblib.load(model_file)
            self.scaler = joblib.load(scaler_file)
            logger.info("Model loaded successfully")
        else:
            logger.warning("No saved model found")
    
    def _create_pretrained_model(self):
        """
        Create a pre-trained model with synthetic data for demonstration
        In production, this would be replaced with real training data
        """
        logger.info("Creating pre-trained model with synthetic data...")
        
        # Generate synthetic training data
        np.random.seed(42)
        n_samples = 1000
        
        # Features
        overtime_hours = np.random.uniform(0, 50, n_samples)
        night_shifts = np.random.randint(0, 15, n_samples)
        performance = np.random.normal(75, 15, n_samples)
        absenteeism = np.random.uniform(0, 10, n_samples)
        tenure = np.random.randint(1, 120, n_samples)
        
        # Labels (attrition = 1, no attrition = 0)
        # Higher overtime, low performance, high absenteeism → higher attrition
        labels = ((overtime_hours > 30) & (performance < 60) | (absenteeism > 5)).astype(int)
        
        training_data = pd.DataFrame({
            'overtime_hours_3m': overtime_hours,
            'night_shifts_count_3m': night_shifts,
            'performance_score': performance,
            'absenteeism_rate': absenteeism,
            'tenure_months': tenure
        })
        
        self.train(training_data, pd.Series(labels))


# Singleton instance
attrition_predictor = AttritionPredictor()
