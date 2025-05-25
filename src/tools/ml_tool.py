"""AI and Machine Learning tools for data analysis and model operations."""

import logging
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Union
import json
import pickle
import os
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import accuracy_score, mean_squared_error, classification_report
from sklearn.preprocessing import StandardScaler, LabelEncoder

from .base import Tool

logger = logging.getLogger(__name__)


class MLTool(Tool):
    """Tool for machine learning operations and data analysis."""

    name = "ml_tool"
    description = "Perform machine learning tasks, data analysis, and model operations"

    def __init__(self):
        """Initialize ML tool."""
        super().__init__(
            name="ml_tool",
            description="Perform machine learning tasks, data analysis, and model operations"
        )
        self.models_dir = "saved_models"
        os.makedirs(self.models_dir, exist_ok=True)

    def get_schema(self) -> Dict[str, Any]:
        """Get the JSON schema for ML tool parameters."""
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["analyze_data", "train_model", "predict", "save_model", "load_model", "feature_importance"],
                    "description": "The ML operation to perform"
                },
                "data_path": {
                    "type": "string",
                    "description": "Path to the data file (CSV, JSON, etc.)"
                },
                "data": {
                    "type": "object",
                    "description": "Direct data input as JSON object"
                },
                "target_column": {
                    "type": "string",
                    "description": "Name of the target column for training"
                },
                "model_type": {
                    "type": "string",
                    "enum": ["linear_regression", "logistic_regression", "random_forest", "random_forest_classifier"],
                    "default": "linear_regression",
                    "description": "Type of ML model to train"
                },
                "model_name": {
                    "type": "string",
                    "description": "Name for saving/loading the model"
                },
                "test_size": {
                    "type": "number",
                    "minimum": 0.1,
                    "maximum": 0.9,
                    "default": 0.2,
                    "description": "Fraction of data to use for testing"
                },
                "input_data": {
                    "type": "object",
                    "description": "Input data for making predictions"
                }
            },
            "required": ["action"],
            "additionalProperties": False
        }

    def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        """Execute ML operations."""
        try:
            if action == "analyze_data":
                return self._analyze_data(
                    data_path=kwargs.get('data_path'),
                    data=kwargs.get('data')
                )
            elif action == "train_model":
                return self._train_model(
                    data_path=kwargs.get('data_path'),
                    target_column=kwargs.get('target_column'),
                    model_type=kwargs.get('model_type', 'linear_regression'),
                    model_name=kwargs.get('model_name', 'default_model'),
                    test_size=kwargs.get('test_size', 0.2)
                )
            elif action == "predict":
                return self._predict(
                    model_name=kwargs.get('model_name'),
                    input_data=kwargs.get('input_data')
                )
            elif action == "save_model":
                return self._save_model(
                    model_name=kwargs.get('model_name'),
                    model=kwargs.get('model')
                )
            elif action == "load_model":
                return self._load_model(model_name=kwargs.get('model_name'))
            elif action == "feature_importance":
                return self._get_feature_importance(model_name=kwargs.get('model_name'))
            elif action == "data_preprocessing":
                return self._preprocess_data(
                    data_path=kwargs.get('data_path'),
                    operations=kwargs.get('operations', [])
                )
            else:
                return {"error": f"Unknown action: {action}"}

        except Exception as e:
            logger.error(f"Error in ML tool: {str(e)}")
            return {"error": f"ML tool error: {str(e)}"}

    def _analyze_data(self, data_path: str = None, data: Any = None) -> Dict[str, Any]:
        """Analyze dataset and provide insights."""
        try:
            if data_path:
                if data_path.endswith('.csv'):
                    df = pd.read_csv(data_path)
                elif data_path.endswith('.json'):
                    df = pd.read_json(data_path)
                else:
                    return {"error": "Unsupported file format. Use CSV or JSON."}
            elif data is not None:
                df = pd.DataFrame(data)
            else:
                return {"error": "No data provided"}

            analysis = {
                "shape": df.shape,
                "columns": df.columns.tolist(),
                "data_types": df.dtypes.to_dict(),
                "missing_values": df.isnull().sum().to_dict(),
                "summary_stats": df.describe().to_dict(),
                "memory_usage": df.memory_usage(deep=True).sum(),
                "categorical_columns": df.select_dtypes(include=['object']).columns.tolist(),
                "numerical_columns": df.select_dtypes(include=[np.number]).columns.tolist()
            }

            # Sample correlation matrix for numerical columns
            if len(analysis['numerical_columns']) > 1:
                corr_matrix = df[analysis['numerical_columns']].corr()
                analysis['correlation_matrix'] = corr_matrix.to_dict()

            return {
                "success": True,
                "message": f"📊 Data analysis complete for dataset with {df.shape[0]} rows and {df.shape[1]} columns",
                "analysis": analysis
            }

        except Exception as e:
            return {"error": f"Data analysis failed: {str(e)}"}

    def _train_model(self, data_path: str, target_column: str, model_type: str = 'linear_regression',
                     model_name: str = 'default_model', test_size: float = 0.2) -> Dict[str, Any]:
        """Train a machine learning model."""
        try:
            # Load data
            if data_path.endswith('.csv'):
                df = pd.read_csv(data_path)
            else:
                return {"error": "Only CSV files supported for training"}

            if target_column not in df.columns:
                return {"error": f"Target column '{target_column}' not found in dataset"}

            # Prepare features and target
            X = df.drop(columns=[target_column])
            y = df[target_column]

            # Handle categorical variables
            categorical_cols = X.select_dtypes(include=['object']).columns
            for col in categorical_cols:
                le = LabelEncoder()
                X[col] = le.fit_transform(X[col].astype(str))

            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=42
            )

            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)

            # Choose and train model
            if model_type == 'linear_regression':
                model = LinearRegression()
                model.fit(X_train_scaled, y_train)
                predictions = model.predict(X_test_scaled)
                score = mean_squared_error(y_test, predictions)
                metric_name = "MSE"
            elif model_type == 'logistic_regression':
                model = LogisticRegression()
                model.fit(X_train_scaled, y_train)
                predictions = model.predict(X_test_scaled)
                score = accuracy_score(y_test, predictions)
                metric_name = "Accuracy"
            elif model_type == 'random_forest_classifier':
                model = RandomForestClassifier(
                    n_estimators=100, random_state=42)
                model.fit(X_train, y_train)  # RF doesn't always need scaling
                predictions = model.predict(X_test)
                score = accuracy_score(y_test, predictions)
                metric_name = "Accuracy"
            elif model_type == 'random_forest_regressor':
                model = RandomForestRegressor(
                    n_estimators=100, random_state=42)
                model.fit(X_train, y_train)
                predictions = model.predict(X_test)
                score = mean_squared_error(y_test, predictions)
                metric_name = "MSE"
            else:
                return {"error": f"Unsupported model type: {model_type}"}

            # Save model and scaler
            model_data = {
                'model': model,
                'scaler': scaler,
                'feature_names': X.columns.tolist(),
                'model_type': model_type,
                'target_column': target_column
            }

            with open(f"{self.models_dir}/{model_name}.pkl", 'wb') as f:
                pickle.dump(model_data, f)

            return {
                "success": True,
                "message": f"🤖 Model '{model_name}' trained successfully",
                "model_type": model_type,
                "test_score": score,
                "metric": metric_name,
                "features_count": len(X.columns),
                "training_samples": len(X_train)
            }

        except Exception as e:
            return {"error": f"Model training failed: {str(e)}"}

    def _predict(self, model_name: str, input_data: Union[Dict, List]) -> Dict[str, Any]:
        """Make predictions using a trained model."""
        try:
            model_path = f"{self.models_dir}/{model_name}.pkl"
            if not os.path.exists(model_path):
                return {"error": f"Model '{model_name}' not found"}

            with open(model_path, 'rb') as f:
                model_data = pickle.load(f)

            model = model_data['model']
            scaler = model_data['scaler']
            feature_names = model_data['feature_names']

            # Prepare input data
            if isinstance(input_data, dict):
                df = pd.DataFrame([input_data])
            else:
                df = pd.DataFrame(input_data)

            # Ensure all required features are present
            missing_features = set(feature_names) - set(df.columns)
            if missing_features:
                return {"error": f"Missing features: {list(missing_features)}"}

            # Reorder columns to match training
            df = df[feature_names]

            # Handle categorical variables (simple approach)
            categorical_cols = df.select_dtypes(include=['object']).columns
            for col in categorical_cols:
                le = LabelEncoder()
                df[col] = le.fit_transform(df[col].astype(str))

            # Scale features if needed
            if model_data['model_type'] in ['linear_regression', 'logistic_regression']:
                X_scaled = scaler.transform(df)
                predictions = model.predict(X_scaled)
            else:
                predictions = model.predict(df)

            return {
                "success": True,
                "message": f"🔮 Predictions generated using model '{model_name}'",
                "predictions": predictions.tolist(),
                "input_samples": len(df)
            }

        except Exception as e:
            return {"error": f"Prediction failed: {str(e)}"}

    def _get_feature_importance(self, model_name: str) -> Dict[str, Any]:
        """Get feature importance for tree-based models."""
        try:
            model_path = f"{self.models_dir}/{model_name}.pkl"
            if not os.path.exists(model_path):
                return {"error": f"Model '{model_name}' not found"}

            with open(model_path, 'rb') as f:
                model_data = pickle.load(f)

            model = model_data['model']
            feature_names = model_data['feature_names']

            if hasattr(model, 'feature_importances_'):
                importance_scores = model.feature_importances_
                feature_importance = dict(
                    zip(feature_names, importance_scores))

                # Sort by importance
                sorted_importance = dict(sorted(feature_importance.items(),
                                                key=lambda x: x[1], reverse=True))

                return {
                    "success": True,
                    "message": f"📈 Feature importance extracted from '{model_name}'",
                    "feature_importance": sorted_importance,
                    "top_features": list(sorted_importance.keys())[:5]
                }
            else:
                return {"error": "Model doesn't support feature importance"}

        except Exception as e:
            return {"error": f"Feature importance extraction failed: {str(e)}"}

    def _preprocess_data(self, data_path: str, operations: List[str]) -> Dict[str, Any]:
        """Preprocess data with specified operations."""
        try:
            df = pd.read_csv(data_path)
            original_shape = df.shape

            for operation in operations:
                if operation == "remove_duplicates":
                    df = df.drop_duplicates()
                elif operation == "handle_missing":
                    # Fill numeric columns with mean, categorical with mode
                    numeric_cols = df.select_dtypes(
                        include=[np.number]).columns
                    categorical_cols = df.select_dtypes(
                        include=['object']).columns

                    for col in numeric_cols:
                        df[col].fillna(df[col].mean(), inplace=True)

                    for col in categorical_cols:
                        df[col].fillna(df[col].mode()[0] if not df[col].mode(
                        ).empty else 'Unknown', inplace=True)

                elif operation == "normalize":
                    numeric_cols = df.select_dtypes(
                        include=[np.number]).columns
                    scaler = StandardScaler()
                    df[numeric_cols] = scaler.fit_transform(df[numeric_cols])

            # Save preprocessed data
            output_path = data_path.replace('.csv', '_preprocessed.csv')
            df.to_csv(output_path, index=False)

            return {
                "success": True,
                "message": f"🔧 Data preprocessing complete",
                "original_shape": original_shape,
                "new_shape": df.shape,
                "output_path": output_path,
                "operations_applied": operations
            }

        except Exception as e:
            return {"error": f"Data preprocessing failed: {str(e)}"}
