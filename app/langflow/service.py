from typing import Dict, Any, List
import json
import os
import asyncio
from datetime import datetime, timezone

# Try to import langchain components, but provide fallbacks for Cloudflare
try:
    from langchain.llms import Ollama
    from langchain.prompts import ChatPromptTemplate
    from langchain.chains import LLMChain
    from langchain.agents import Tool, AgentExecutor, LLMSingleActionAgent
    from langchain.schema import AgentAction, AgentFinish
    LANGCHAIN_AVAILABLE = True
except ImportError:
    # Fallback for Cloudflare environment
    LANGCHAIN_AVAILABLE = False

from .config import config

class LangflowService:
    def __init__(self):
        self.templates = {}
        self.flows = {}

        # Initialize LLMs if available
        if LANGCHAIN_AVAILABLE:
            # Replace OpenAI and Anthropic with Ollama models
            self.llm_llama = Ollama(
                model="llama2",
                temperature=config.model_configs["llama2"]["temperature"],
                url=config.ollama_base_url
            )

            self.llm_mistral = Ollama(
                model="mistral",
                temperature=config.model_configs["mistral"]["temperature"],
                url=config.ollama_base_url
            )

            self._load_templates()
            self._load_flows()
        else:
            # For Cloudflare environment, we'll use a simplified approach
            self._init_cloudflare_mode()

    def _init_cloudflare_mode(self):
        """Initialize in Cloudflare-compatible mode"""
        # We'll use predefined templates and flows instead of loading from disk
        self.templates = {
            "restaurant_analysis": {
                "template": "Analyze the restaurant performance for {{restaurant_id}} over {{timeframe}}. Focus on these metrics: {{metrics}}."
            },
            "competitor_analysis": {
                "template": "Compare restaurant {{restaurant_id}} with competitors {{competitor_ids}} over {{timeframe}}."
            },
            "menu_optimization": {
                "template": "Optimize the menu for restaurant {{restaurant_id}} based on the provided menu items and sales data."
            }
        }

    def _load_templates(self):
        """Load prompt templates from the templates directory"""
        self.templates = {}
        try:
            for template_file in os.listdir(config.templates_dir):
                if template_file.endswith(".json"):
                    with open(os.path.join(config.templates_dir, template_file), "r") as f:
                        self.templates[template_file[:-5]] = json.load(f)
        except (FileNotFoundError, PermissionError):
            # Fallback to default templates
            self._init_cloudflare_mode()

    def _load_flows(self):
        """Load flow configurations from the flows directory"""
        self.flows = {}
        try:
            for flow_file in os.listdir(config.flows_dir):
                if flow_file.endswith(".json"):
                    with open(os.path.join(config.flows_dir, flow_file), "r") as f:
                        self.flows[flow_file[:-5]] = json.load(f)
        except (FileNotFoundError, PermissionError):
            # Flows will be loaded from KV in Cloudflare environment
            pass

    async def run_flow(self, flow_id: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Run a specific flow with the given inputs"""
        # In Cloudflare, flow_id is the actual ID, not the name
        # We need to get the flow from KV
        from app.apis.langflow import kv_get

        flow_data = await kv_get(flow_id)
        if not flow_data:
            raise ValueError(f"Flow {flow_id} not found")

        # Extract flow name if available, otherwise use a default
        flow_name = flow_data.get("name", "default_flow")

        # Check if we have a config for this flow
        if flow_name in config.flow_configs:
            flow_config = config.flow_configs[flow_name]

            # Validate inputs against schema if possible
            if "input_schema" in flow_config:
                self._validate_inputs(inputs, flow_config["input_schema"])

            # Get output schema if available
            output_schema = flow_config.get("output_schema", {})
        else:
            # Use a default output schema
            output_schema = {
                "analysis": "str",
                "recommendations": "list"
            }

        # Process the flow
        if LANGCHAIN_AVAILABLE:
            # Use LangChain if available
            # Get the appropriate LLM based on the flow
            llm = self._get_llm_for_flow(flow_name)

            # Create the prompt template
            prompt = self._create_prompt(flow_name, inputs)

            # Create and run the chain
            chain = LLMChain(llm=llm, prompt=prompt)
            result = await chain.arun(inputs)
        else:
            # Simplified processing for Cloudflare
            # This is a placeholder - in a real implementation, you would
            # call an external API or use a Cloudflare-compatible AI service
            result = json.dumps({
                "analysis": f"Analysis for {flow_id} with inputs {inputs}",
                "recommendations": ["Recommendation 1", "Recommendation 2"]
            })

        # Parse and validate the output
        output = self._parse_output(result, output_schema)

        return output

    def _validate_inputs(self, inputs: Dict[str, Any], schema: Dict[str, str]):
        """Validate inputs against the schema"""
        for key, expected_type in schema.items():
            if key not in inputs:
                raise ValueError(f"Missing required input: {key}")

            actual_type = type(inputs[key]).__name__
            if expected_type != actual_type:
                raise ValueError(f"Type mismatch for {key}: expected {expected_type}, got {actual_type}")

    def _get_llm_for_flow(self, flow_name: str):
        """Get the appropriate LLM for the flow"""
        # Update model selection based on flow requirements
        if flow_name in ["restaurant_analysis", "menu_optimization"]:
            return self.llm_llama
        else:
            return self.llm_mistral

    def _create_prompt(self, flow_name: str, inputs: Dict[str, Any]) -> ChatPromptTemplate:
        """Create a prompt template for the flow"""
        template = self.templates.get(flow_name, {}).get("template", "")
        return ChatPromptTemplate.from_template(template)

    def _parse_output(self, result: str, schema: Dict[str, str]) -> Dict[str, Any]:
        """Parse and validate the output against the schema"""
        try:
            output = json.loads(result)
        except json.JSONDecodeError:
            # If the output is not valid JSON, try to extract structured data
            output = self._extract_structured_data(result, schema)

        # Validate output against schema
        for key, expected_type in schema.items():
            if key not in output:
                raise ValueError(f"Missing required output: {key}")

            actual_type = type(output[key]).__name__
            if expected_type != actual_type:
                raise ValueError(f"Type mismatch for {key}: expected {expected_type}, got {actual_type}")

        return output

    def _extract_structured_data(self, text: str, schema: Dict[str, str]) -> Dict[str, Any]:
        """Extract structured data from text using LLM"""
        prompt = f"""Extract the following information from the text and return it as JSON:
        {json.dumps(schema, indent=2)}

        Text:
        {text}
        """

        # Use llama2 for extraction instead of OpenAI
        result = self.llm_llama.predict(prompt)
        return json.loads(result)

# Create a singleton instance
langflow_service = LangflowService()