import ollama
import logging
from typing import List, Dict, Any, Optional
import hardware
import tools_schema
import utils
import os

# Configuration
MODEL_NAME = "llama3.2"  # Ensure this model is pulled: `ollama pull llama3.2`

# Logger setup
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - [INFERENCE] - %(message)s"
)
logger = logging.getLogger(__name__)

# Function Mapping: Connects string names from LLM to actual Python functions
AVAILABLE_FUNCTIONS = {
    "control_light": hardware.control_light,
    "get_environment_metrics": hardware.get_environment_metrics,
    "tocar_musica": utils.tocar_musica,
    "pausar_retomar": utils.pausar_retomar,
    "parar_musica": utils.parar_musica,
    "detect_music": utils.detect_music,
}


def run_inference(user_input: str, conversation_history: List[Dict[str, Any]]) -> str:
    """
    Orchestrates the conversation flow: User Input -> LLM -> Tool Execution -> Final Response.

    Args:
        user_input (str): The text input from the user (or STT system).
        conversation_history (List[Dict]): The context/history of the session.

    Returns:
        str: The final natural language response from the Assistant.
    """

    # 1. Append user input to history
    conversation_history.append({"role": "user", "content": user_input})
    logger.info(f"Processing user input: {user_input}")

    try:
        # 2. First Call to LLM: Intent Classification & Tool Selection
        response = ollama.chat(
            model=MODEL_NAME,
            messages=conversation_history,
            tools=tools_schema.available_tools_definitions,
        )

        message = response["message"]

        # 3. Check for Tool Calls
        if message.get("tool_calls"):
            logger.info("Tool usage detected by the model.")

            # Append the model's intent to history (critical for context)
            conversation_history.append(message)

            # 4. Execute Tools
            for tool in message["tool_calls"]:
                function_name = tool["function"]["name"]
                arguments = tool["function"]["arguments"]

                logger.info(f"Executing tool: {function_name} with args: {arguments}")

                function_to_call = AVAILABLE_FUNCTIONS.get(function_name)

                if function_to_call:
                    # Execute the actual hardware function
                    function_response = function_to_call(**arguments)  # type: ignore

                    # SPECIAL CASE: If detect_music was called, return immediately.
                    # The user wants to "kill" the inference loop here and use the hardcoded response.
                    if function_name == "detect_music":
                        return str(function_response)

                    # 5. Feed the result back to the model
                    conversation_history.append(
                        {
                            "role": "tool",
                            "content": str(function_response),
                        }
                    )
                else:
                    logger.error(f"Function {function_name} not found in function map.")
                    conversation_history.append(
                        {
                            "role": "tool",
                            "content": f"Error: Tool {function_name} implementation missing.",
                        }
                    )

            # 6. Second Call to LLM: Generate Final Natural Language Response
            final_response = ollama.chat(
                model=MODEL_NAME,
                messages=conversation_history,
            )
            return final_response["message"]["content"]

        else:
            # No tool needed, return direct text response
            content = message["content"]

            # Filtro de segurança simples: Se começar com chave {, provavelmente é alucinação de JSON
            if content.strip().startswith("{") and "parameters" in content:
                return "I'm sorry, I tried to access a tool that doesn't exist. Could you try rephrasing? (Internal Error)"

            conversation_history.append(message)
            return message["content"]

    except Exception as e:
        logger.error(f"Inference pipeline failed: {e}")
        return "I encountered an internal error while processing your request."
