# IESTI05 Final Project ALEXA

**Course:** IESTI05 - Edge AI Engineering  
**University:** UNIFEI  

## 📋 Project Overview

This is the final project for the IESTI05 class. It demonstrates the implementation of a local "Alexa-like" voice assistant running entirely on Edge hardware. The system uses a Small Language Model (SLM) to process natural language, control hardware peripherals, play music, and perform Retrieval-Augmented Generation (RAG) for music identification.

## 🛠️ Hardware Requirements

* **Edge Device:** Raspberry Pi 5 (8 GB RAM)
* **Audio:** Headset (Microphone & Speaker connected via USB/Jack)
* **Input:** Push Button (GPIO 20)
* **Actuators:** LED (Simulating ambient light control)
* **Sensors:** Temperature Sensor

## 💻 Software & Tech Stack

* **Language:** Python 3.x
* **LLM Inference:** Ollama (running Llama 3.2)
* **Speech-to-Text:** Groq API (Whisper-large-v3-turbo)
* **Orchestration:** LangChain
* **Vector Database:** ChromaDB (for RAG music identification)
* **Music Playback:** `yt-dlp` and `mpv`
* **Hardware Control:** `gpiozero`

## 🧠 AI Model Details

* **Reasoning & Tool Calling:** Llama 3.2 (via Ollama)
  * Handles intent classification and function selection (Light, Music, Weather, RAG).
* **Transcription:** Whisper (via Groq Cloud)
* **Embeddings:** `nomic-embed-text` (for vector store)

## ⚙️ Architecture

1. **Input:** User presses the physical button to record audio via the headset microphone.
2. **STT:** Audio is sent to Groq API for fast transcription.
3. **Inference:** Transcribed text is sent to the local Llama 3.2 model via Ollama.
4. **Tool Execution:** The model determines if a tool is needed:
    * **Control Light:** Toggles LED.
    * **Environment:** Reads temperature sensor.
    * **Music Player:** Searches YouTube and plays audio via `mpv`.
    * **Music Detection:** Uses RAG to match sung lyrics against a local ChromaDB database of songs.
5. **Response:** The system executes the action and generates a text response.

## 🚀 Installation & Setup

### Prerequisites

1. Raspberry Pi 5 setup with Python environment.
2. Ollama installed and running (`ollama serve`).
3. Pull the model: `ollama pull llama3.2`.
4. Groq API Key.

### Steps

1. Clone the repository:

    ```bash
    git clone https://github.com/your-username/Final_Project_IESTI-5_ALEXA.git
    ```

2. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3. Create a `.env` file with your API keys:

    ```
    GROQ_API_KEY=your_key_here
    ```

4. (Optional) Build the vector database for music detection:

    ```bash
    python create_vector_database.py
    ```

5. Run the assistant:

    ```bash
    python main.py
    ```

## 👥 Team

* [Student Name 1]
* [Student Name 2]
