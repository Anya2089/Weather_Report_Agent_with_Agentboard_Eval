import boto3
import json
import logging
import time
from typing import Tuple, List, Dict, Any
from common.registry import registry

logger = logging.getLogger(__name__)

@registry.register_llm("bedrock_claude")
class BedrockClaudeLLM:
    """
    Bedrock Claude LLM implementation for AgentBoard
    Supports Claude 3.7 Sonnet via AWS Bedrock
    """
    
    def __init__(self, config: Dict[str, Any]):
        # Basic configuration
        self.config = config
        
        # Engine attribute for compatibility with AgentBoard
        self.engine = "claude"  # This helps agents identify it as a Claude model
        
        # XML split attribute for compatibility with AgentBoard agents
        self.xml_split = {
            "example": ["<example>", "</example>"],
            "text": ["<text>", "</text>"],
            "rule": ["<rule>", "</rule>"],
            "system_msg": ["<system>", "</system>"],
            "instruction": ["<instruction>", "</instruction>"],
            "goal": ["<goal>", "</goal>"]
        }
        
        # Bedrock specific configuration
        self.model_id = config.get("model_id", "us.anthropic.claude-3-7-sonnet-20250219-v1:0")
        self.region = config.get("region", "us-east-1")
        self.max_tokens = config.get("max_tokens", 4096)
        self.temperature = config.get("temperature", 0.0)
        self.top_p = config.get("top_p", 1.0)
        self.retry_delays = config.get("retry_delays", 10)
        self.max_retry_iters = config.get("max_retry_iters", 15)
        
        # Override context length for Claude 3.7
        self.context_length = config.get("context_length", 200000)
        
        # Initialize Bedrock client
        try:
            self.bedrock_client = boto3.client(
                service_name='bedrock-runtime',
                region_name=self.region
            )
            logger.info(f"Initialized Bedrock client for region: {self.region}")
        except Exception as e:
            logger.error(f"Failed to initialize Bedrock client: {str(e)}")
            raise
    
    def generate(self, system_message: str, user_message: str) -> Tuple[bool, str]:
        """
        Generate response using Bedrock Claude 3.7
        
        Args:
            system_message: System prompt/instruction
            user_message: User input message
            
        Returns:
            Tuple of (success: bool, response: str)
        """
        
        for attempt in range(self.max_retry_iters):
            try:
                # Construct messages in Claude 3 format
                messages = [
                    {
                        "role": "user",
                        "content": user_message
                    }
                ]
                
                # Construct request body for Bedrock
                body = {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": self.max_tokens,
                    "temperature": self.temperature,
                    "top_p": self.top_p,
                    "messages": messages
                }
                
                # Add system message if provided
                if system_message and system_message.strip():
                    body["system"] = system_message
                
                logger.debug(f"Bedrock request body: {json.dumps(body, indent=2)}")
                
                # Call Bedrock API
                response = self.bedrock_client.invoke_model(
                    modelId=self.model_id,
                    body=json.dumps(body),
                    contentType='application/json'
                )
                
                # Parse response
                response_body = json.loads(response['body'].read())
                logger.debug(f"Bedrock response: {json.dumps(response_body, indent=2)}")
                
                # Extract generated text
                if 'content' in response_body and len(response_body['content']) > 0:
                    generated_text = response_body['content'][0]['text']
                    logger.info(f"Successfully generated response with {len(generated_text)} characters")
                    return True, generated_text
                else:
                    logger.error(f"Unexpected response format: {response_body}")
                    return False, f"Error: Unexpected response format from Bedrock"
                    
            except Exception as e:
                logger.warning(f"Bedrock API call failed (attempt {attempt + 1}/{self.max_retry_iters}): {str(e)}")
                
                if attempt < self.max_retry_iters - 1:
                    # Wait before retry
                    time.sleep(self.retry_delays)
                else:
                    # Final attempt failed
                    logger.error(f"All Bedrock API attempts failed: {str(e)}")
                    return False, f"Error: Bedrock API failed after {self.max_retry_iters} attempts: {str(e)}"
        
        return False, "Error: Unexpected failure in Bedrock API calls"
    
    def num_tokens_from_messages(self, messages: List[Dict[str, str]]) -> int:
        """
        Estimate token count for messages
        Claude 3 uses approximately 1 token per 4 characters
        
        Args:
            messages: List of message dictionaries
            
        Returns:
            Estimated token count
        """
        total_text = ""
        for message in messages:
            if isinstance(message, dict):
                total_text += message.get("content", "")
            else:
                total_text += str(message)
        
        # Rough estimation: 1 token ≈ 4 characters for Claude
        estimated_tokens = len(total_text) // 4
        logger.debug(f"Estimated tokens: {estimated_tokens} for text length: {len(total_text)}")
        
        return estimated_tokens
    
    def test_connection(self) -> bool:
        """
        Test Bedrock connection with a simple request
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            success, response = self.generate("You are a helpful assistant.", "Hello, please respond with 'Connection successful'")
            if success and "successful" in response.lower():
                logger.info("Bedrock connection test passed")
                return True
            else:
                logger.error(f"Bedrock connection test failed: {response}")
                return False
        except Exception as e:
            logger.error(f"Bedrock connection test error: {str(e)}")
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get model information
        
        Returns:
            Dictionary with model details
        """
        return {
            "model_id": self.model_id,
            "region": self.region,
            "context_length": self.context_length,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "provider": "AWS Bedrock",
            "model_family": "Claude 3.7 Sonnet"
        }
    
    @classmethod
    def from_config(cls, config: Dict[str, Any]):
        """
        Create BedrockClaudeLLM instance from configuration
        
        Args:
            config: Configuration dictionary
            
        Returns:
            BedrockClaudeLLM instance
        """
        return cls(config)
