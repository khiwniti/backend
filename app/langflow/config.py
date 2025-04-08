from typing import Dict, Any
import os

class LangflowConfig:
    def __init__(self):
        self.flows_dir = os.path.join(os.path.dirname(__file__), "flows")
        self.templates_dir = os.path.join(os.path.dirname(__file__), "templates")
        self.models_dir = os.path.join(os.path.dirname(__file__), "models")
        
        # Ensure directories exist
        os.makedirs(self.flows_dir, exist_ok=True)
        os.makedirs(self.templates_dir, exist_ok=True)
        os.makedirs(self.models_dir, exist_ok=True)
        
        # Replace API keys with Ollama configuration
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        
        # Model configurations - replacing with Ollama models
        self.model_configs: Dict[str, Any] = {
            "llama2": {
                "temperature": 0.7,
                "max_tokens": 2000,
                "top_p": 1.0,
                "frequency_penalty": 0.0,
                "presence_penalty": 0.0
            },
            "mistral": {
                "temperature": 0.7,
                "max_tokens": 2000,
                "top_p": 1.0
            }
        }
        
        # Flow configurations
        self.flow_configs: Dict[str, Any] = {
            "restaurant_analysis": {
                "description": "Analyzes restaurant performance and provides insights",
                "input_schema": {
                    "restaurant_id": "str",
                    "timeframe": "str",
                    "metrics": "list"
                },
                "output_schema": {
                    "analysis": "str",
                    "recommendations": "list",
                    "metrics": "dict"
                }
            },
            "competitor_analysis": {
                "description": "Analyzes competitor restaurants and provides insights",
                "input_schema": {
                    "restaurant_id": "str",
                    "competitor_ids": "list",
                    "timeframe": "str"
                },
                "output_schema": {
                    "comparison": "dict",
                    "strengths": "list",
                    "weaknesses": "list",
                    "opportunities": "list"
                }
            },
            "menu_optimization": {
                "description": "Optimizes restaurant menu based on performance data",
                "input_schema": {
                    "restaurant_id": "str",
                    "menu_items": "list",
                    "sales_data": "dict"
                },
                "output_schema": {
                    "optimized_menu": "list",
                    "recommendations": "list",
                    "projected_impact": "dict"
                }
            }
        }

config = LangflowConfig() 