"""ModelDrift client for logging predictions and ground truth labels."""
import requests
from typing import Dict, Any, Optional


class ModelDriftClient:
    """
    Client for sending predictions and ground truth labels to ModelDrift backend.
    
    Example:
        client = ModelDriftClient(base_url="http://localhost:8000")
        
        client.log_prediction(
            model_name="credit_risk",
            model_version="v1",
            prediction_id="pred_001",
            input_features={"feature1": 0.5, "feature2": 100},
            prediction="high_risk",
            confidence=0.91
        )
        
        client.log_ground_truth(
            prediction_id="pred_001",
            actual_label="default"
        )
    """
    
    def __init__(self, base_url: str = "http://localhost:8000", timeout: int = 10):
        """
        Initialize the ModelDrift client.
        
        Args:
            base_url: Base URL of the ModelDrift API (default: http://localhost:8000)
            timeout: Request timeout in seconds (default: 10)
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
    
    def log_prediction(
        self,
        model_name: str,
        model_version: str,
        prediction_id: str,
        input_features: Dict[str, Any],
        prediction: str,
        confidence: float
    ) -> Dict[str, Any]:
        """
        Log a model prediction to the backend.
        
        Args:
            model_name: Name of the model (e.g., "credit_risk")
            model_version: Version of the model (e.g., "v1")
            prediction_id: Unique identifier for this prediction
            input_features: Dictionary of input features (supports nested structures)
            prediction: Predicted label or value
            confidence: Confidence score between 0.0 and 1.0
            
        Returns:
            Response dictionary with status and prediction_id
            
        Raises:
            ConnectionError: If backend is unavailable
            ValueError: If API returns non-200 response
        """
        url = f"{self.base_url}/api/v1/predictions"
        
        payload = {
            "model_name": model_name,
            "model_version": model_version,
            "prediction_id": prediction_id,
            "input_features": input_features,
            "prediction": prediction,
            "confidence": confidence
        }
        
        try:
            response = self.session.post(url, json=payload, timeout=self.timeout)
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(
                f"Failed to connect to ModelDrift backend at {url}. "
                f"Is the backend running? Error: {str(e)}"
            )
        except requests.exceptions.Timeout as e:
            raise TimeoutError(
                f"Request to ModelDrift backend timed out after {self.timeout}s. Error: {str(e)}"
            )
        
        if response.status_code != 200:
            try:
                error_detail = response.json()
            except:
                error_detail = response.text
            
            raise ValueError(
                f"ModelDrift API returned {response.status_code}: {error_detail}"
            )
        
        return response.json()
    
    def log_ground_truth(
        self,
        prediction_id: str,
        actual_label: str
    ) -> Dict[str, Any]:
        """
        Log ground truth label for a prediction.
        
        Args:
            prediction_id: Unique identifier of the prediction
            actual_label: Actual label or outcome
            
        Returns:
            Response dictionary with status and prediction_id
            
        Raises:
            ConnectionError: If backend is unavailable
            ValueError: If API returns non-200 response
        """
        url = f"{self.base_url}/api/v1/labels"
        
        payload = {
            "prediction_id": prediction_id,
            "actual_label": actual_label
        }
        
        try:
            response = self.session.post(url, json=payload, timeout=self.timeout)
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(
                f"Failed to connect to ModelDrift backend at {url}. "
                f"Is the backend running? Error: {str(e)}"
            )
        except requests.exceptions.Timeout as e:
            raise TimeoutError(
                f"Request to ModelDrift backend timed out after {self.timeout}s. Error: {str(e)}"
            )
        
        if response.status_code != 200:
            try:
                error_detail = response.json()
            except:
                error_detail = response.text
            
            raise ValueError(
                f"ModelDrift API returned {response.status_code}: {error_detail}"
            )
        
        return response.json()
    
    def close(self):
        """Close the underlying session."""
        self.session.close()
