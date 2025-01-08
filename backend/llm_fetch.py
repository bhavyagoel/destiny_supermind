import google.generativeai as genai
import os
import logging
from dotenv import load_dotenv
from typing import Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('GeminiAPI')

@dataclass
class GeminiResponse:
    """Data class to store Gemini API response details"""
    text: str
    success: bool
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    timestamp: str = datetime.now().isoformat()

class GeminiAPIError(Exception):
    """Custom exception for Gemini API related errors"""
    pass

class GeminiClient:
    """Client class for interacting with the Gemini API"""
    
    def __init__(self, model_name: str = 'gemini-1.5-flash'):
        """
        Initialize the Gemini client
        
        Args:
            model_name (str): Name of the Gemini model to use
        """
        self.model_name = model_name
        self.model = None
        self._setup_metrics()
    
    def _setup_metrics(self):
        """Initialize metrics tracking"""
        self.metrics = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'last_error': None
        }
    
    def initialize(self) -> bool:
        """
        Initialize the Gemini API with credentials
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        try:
            # Load environment variables
            if not load_dotenv():
                raise GeminiAPIError("Failed to load .env file")
            
            # Validate API key
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                raise GeminiAPIError("GEMINI_API_KEY not found in environment variables")
            
            # Configure the API
            genai.configure(api_key=api_key)
            
            # Initialize the model
            self.model = genai.GenerativeModel(self.model_name)
            
            logger.info(f"Successfully initialized Gemini API with model: {self.model_name}")
            return True
            
        except Exception as e:
            error_msg = f"Failed to initialize Gemini API: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.metrics['last_error'] = error_msg
            return False

    def get_response(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_retries: int = 3,
        **kwargs
    ) -> GeminiResponse:
        """
        Get a response from Gemini for a given prompt
        
        Args:
            prompt (str): The input prompt
            temperature (float): Controls response randomness (0.0 to 1.0)
            max_retries (int): Maximum number of retry attempts
            **kwargs: Additional parameters for generation config
            
        Returns:
            GeminiResponse: Object containing response details
        """
        if not prompt.strip():
            return GeminiResponse(
                text="Empty prompt provided",
                success=False,
                error="Prompt cannot be empty"
            )
        
        self.metrics['total_requests'] += 1
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                # Ensure model is initialized
                if not self.model and not self.initialize():
                    raise GeminiAPIError("Failed to initialize model")
                
                # Validate temperature
                if not 0 <= temperature <= 1:
                    raise ValueError("Temperature must be between 0 and 1")
                
                # Generate response
                generation_config = genai.types.GenerationConfig(
                    temperature=temperature,
                    **kwargs
                )
                
                start_time = datetime.now()
                response = self.model.generate_content(
                    prompt,
                    generation_config=generation_config
                )
                
                # Calculate response time
                response_time = (datetime.now() - start_time).total_seconds()
                
                # Log success
                logger.info(f"Successfully generated response in {response_time:.2f} seconds")
                self.metrics['successful_requests'] += 1
                
                return GeminiResponse(
                    text=response.text,
                    success=True,
                    metadata={
                        'response_time': response_time,
                        'model': self.model_name,
                        'temperature': temperature,
                        'retry_count': retry_count
                    }
                )
                
            except Exception as e:
                retry_count += 1
                error_msg = f"Error generating response (attempt {retry_count}/{max_retries}): {str(e)}"
                logger.error(error_msg, exc_info=True)
                
                if retry_count == max_retries:
                    self.metrics['failed_requests'] += 1
                    self.metrics['last_error'] = error_msg
                    
                    return GeminiResponse(
                        text="Failed to generate response",
                        success=False,
                        error=error_msg
                    )
                
                # Wait before retrying (exponential backoff)
                wait_time = 2 ** retry_count
                logger.info(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics and statistics"""
        success_rate = (
            (self.metrics['successful_requests'] / self.metrics['total_requests'] * 100)
            if self.metrics['total_requests'] > 0
            else 0
        )
        
        return {
            **self.metrics,
            'success_rate': f"{success_rate:.2f}%"
        }
    
    def save_metrics(self, filename: str = 'gemini_metrics.json'):
        """Save current metrics to a JSON file"""
        try:
            with open(filename, 'w') as f:
                json.dump(self.get_metrics(), f, indent=2)
            logger.info(f"Metrics saved to {filename}")
        except Exception as e:
            logger.error(f"Failed to save metrics: {str(e)}", exc_info=True)

def main():
    # Example usage
    client = GeminiClient()
    
    prompt = "Explain the concept of quantum computing in simple terms"
    logger.info(f"Sending prompt: {prompt}")
    
    response = client.get_response(prompt)
    
    if response.success:
        print("\nPrompt:", prompt)
        print("\nResponse:", response.text)
        print("\nMetadata:", response.metadata)
    else:
        print("\nError:", response.error)
    
    # Save metrics at the end
    client.save_metrics()

if __name__ == "__main__":
    main()