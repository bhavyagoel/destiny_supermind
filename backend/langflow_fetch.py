import json
import requests
import os
import logging
from typing import Optional, Dict, Any
from requests.exceptions import RequestException, Timeout

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('LangflowClient')

class LangflowError(Exception):
    """Base exception class for Langflow client errors"""
    pass

class LangflowAPIError(LangflowError):
    """Exception raised for API-related errors"""
    def __init__(self, message: str, status_code: Optional[int] = None, response: Optional[dict] = None):
        self.status_code = status_code
        self.response = response
        super().__init__(message)

class LangflowConfigError(LangflowError):
    """Exception raised for configuration-related errors"""
    pass

class LangflowClient:
    def __init__(self, application_token: Optional[str] = None, endpoint: Optional[str] = None):
        self.base_api_url = os.environ.get('BASE_API_URL')
        self.langflow_id = os.environ.get('LANGFLOW_ID')
        self.flow_id = os.environ.get('FLOW_ID')
        self.application_token = application_token or os.environ.get('APPLICATION_TOKEN')
        self.endpoint = endpoint or self.flow_id

        self._validate_config()
        logger.info(f"LangflowClient initialized with langflow_id: {self.langflow_id}")

    def _validate_config(self) -> None:
        """Validate the configuration parameters"""
        missing_params = []
        for param_name, param_value in [
            ('BASE_API_URL', self.base_api_url),
            ('LANGFLOW_ID', self.langflow_id),
            ('FLOW_ID', self.flow_id)
        ]:
            if not param_value:
                missing_params.append(param_name)

        if missing_params:
            error_msg = f"Missing required configuration parameters: {', '.join(missing_params)}"
            logger.error(error_msg)
            raise LangflowConfigError(error_msg)

    def run_flow(self, message: str, output_type: str = "chat", 
                 input_type: str = "chat", tweaks: Optional[dict] = None) -> dict:
        """
        Run a flow with a given message and optional tweaks.

        Args:
            message: The message to send to the flow
            output_type: The output type
            input_type: The input type
            tweaks: Optional tweaks to customize the flow

        Returns:
            dict: The JSON response from the flow

        Raises:
            LangflowAPIError: If the API request fails
            RequestException: If there's a network-related error
        """
        api_url = f"{self.base_api_url}/lf/{self.langflow_id}/api/v1/run/{self.endpoint}"
        
        payload = {
            "input_value": message,
            "output_type": output_type,
            "input_type": input_type,
        }
        if tweaks:
            payload["tweaks"] = tweaks

        headers = {}
        if self.application_token:
            headers["Authorization"] = f"Bearer {self.application_token}"
            headers["Content-Type"] = "application/json"

        try:
            logger.debug(f"Sending request to {api_url} with payload: {json.dumps(payload)}")
            response = requests.post(
                api_url,
                json=payload,
                headers=headers,
                timeout=30  # Add timeout
            )
            
            response.raise_for_status()
            return response.json()

        except Timeout:
            error_msg = "Request timed out while connecting to Langflow API"
            logger.error(error_msg)
            raise LangflowAPIError(error_msg)

        except RequestException as e:
            error_msg = f"Failed to connect to Langflow API: {str(e)}"
            logger.error(error_msg)
            raise LangflowAPIError(error_msg)

        except json.JSONDecodeError as e:
            error_msg = f"Failed to parse API response: {str(e)}"
            logger.error(error_msg)
            raise LangflowAPIError(error_msg)

    def prepare_tweaks(self, message: str) -> Dict[str, Any]:
        """
        Prepare the tweaks based on the message.

        Args:
            message: The message to split and customize the flow components

        Returns:
            dict: A dictionary of tweaks

        Raises:
            LangflowConfigError: If required environment variables are missing
        """
        try:
            gemini_api_key = os.environ.get('GEMINI_API_KEY')
            gemini_prompt = os.environ.get('GEMINI_PROMPT')
            gemini_prompt_2 = os.environ.get('GEMINI_PROMPT_2')

            if not all([gemini_api_key, gemini_prompt, gemini_prompt_2]):
                raise LangflowConfigError("Missing required Gemini configuration parameters")

            message_parts = message.split('-')
            tweaks = {
                "AstraDB-EKNPh": {},
                "TextInput-IA62h": {
                    "input_value": message_parts[0].strip()
                },
                "CombineText-dpoVZ": {
                    "first_text": gemini_prompt,
                    "delimiter": "\\n"
                },
                "CombineText-XnSUA": {
                    "first_text": gemini_prompt_2,
                    "delimiter": "\\n"
                },
                "ParseData-bB1wW": {},
                "ChatOutput-XJAAL": {},
                "GoogleGenerativeAIModel-Tdtr3": {
                    "model": "gemini-1.5-flash",
                    "google_api_key": gemini_api_key
                },
                "TextInput-QOITS": {
                    "input_value": message_parts[1] if len(message_parts) > 1 else ''
                }
            }
            return tweaks

        except Exception as e:
            error_msg = f"Error preparing tweaks: {str(e)}"
            logger.error(error_msg)
            raise LangflowError(error_msg)

    def execute_flow(self, message: str, output_type: str = "chat", 
                    input_type: str = "chat") -> Dict[str, Any]:
        """
        Execute the flow with the given message.

        Args:
            message: The message to send to the flow
            output_type: The output type
            input_type: The input type

        Returns:
            dict: The response from the flow

        Raises:
            LangflowError: If there's an error executing the flow
        """
        try:
            logger.info(f"Executing flow with message: {message}")
            tweaks = self.prepare_tweaks(message)
            response = self.run_flow(message, output_type, input_type, tweaks)
            
            if not response.get("outputs"):
                raise LangflowError("Invalid response format: missing 'outputs' key")
            
            text_response = response["outputs"][0]["outputs"][0]["results"]["message"]["data"]["text"]
            return {"response": text_response}

        except (KeyError, IndexError) as e:
            error_msg = f"Error parsing flow response: {str(e)}"
            logger.error(error_msg)
            raise LangflowError(error_msg)

def getInsightsFromLangflow(username: str, query: str, client: LangflowClient) -> Dict[str, str]:
    """
    Get insights from Langflow.

    Args:
        username: The username
        query: The query string
        client: LangflowClient instance

    Returns:
        dict: The response containing insights

    Raises:
        LangflowError: If there's an error getting insights
    """
    try:
        logger.info(f"Getting insights for user: {username}")
        message = f"{username} - {query}"
        return client.execute_flow(message=message, output_type="chat", input_type="chat")

    except Exception as e:
        error_msg = f"Error getting insights: {str(e)}"
        logger.error(error_msg)
        raise LangflowError(error_msg)