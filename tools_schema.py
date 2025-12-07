"""
This module defines the tool schemas (function definitions) passed to the LLM.
These schemas allow the model to understand available capabilities and required parameters.
"""

light_tool_def = {
    "type": "function",
    "function": {
        "name": "control_light",
        "description": "Use this tool ONLY to physically turn the ambient light on or off via GPIO. Do NOT use this for answering questions about lights or general topics.",
        "parameters": {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "description": "The desired state: 'on' to power up the light, 'off' to power it down.",
                    "enum": ["on", "off"],
                }
            },
            "required": ["status"],
        },
    },
}

temp_tool_def = {
    "type": "function",
    "function": {
        "name": "get_environment_metrics",
        "description": "Reads the current temperature and humidity from the sensors. Use this when the user asks about the weather, heat, cold, or air quality inside the room.",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The specific room or area to check (e.g., 'indoor', 'kitchen').",
                    "default": "indoor",
                }
            },
            "required": [],
        },
    },
}


toca_musica_def = {
    "type": "function",
    "function": {
        "name": "tocar_musica",
        "description": "Plays music from a YouTube search or URL. Use this when the user asks to listen to something.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The name of the song or link to play.",
                }
            },
            "required": ["query"],
        },
    },
}

pausar_retomar_def = {
    "type": "function",
    "function": {
        "name": "pausar_retomar",
        "description": "Pauses or resumes the current music.",
        "parameters": {"type": "object", "properties": {}, "required": []},
    },
}

parar_musica_def = {
    "type": "function",
    "function": {
        "name": "parar_musica",
        "description": "Stops playback completely and closes the player.",
        "parameters": {"type": "object", "properties": {}, "required": []},
    },
}

detect_music_def = {
    "type": "function",
    "function": {
        "name": "detect_music",
        "description": "Starts the music identification process when the user requests to identify a song.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
}


# List of all available tools to be imported by the inference engine
available_tools_definitions = [
    light_tool_def,
    temp_tool_def,
    toca_musica_def,
    pausar_retomar_def,
    parar_musica_def,
    detect_music_def,
]
