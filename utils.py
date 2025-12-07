import sounddevice as sd
from scipy.io.wavfile import write
import numpy as np
import os
import tempfile
from groq import Groq
from dotenv import load_dotenv
import yt_dlp
import subprocess
import os
import socket
import json
import time
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_chroma import Chroma
import queue

load_dotenv()

# Setup for Local RAG
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PERSIST_DIRECTORY = os.path.join(BASE_DIR, "chroma_db")

# Initialize Local LLM (Ollama)
llm = ChatOllama(model="llama3.2", temperature=0.1)


def load_retriever():
    """Load the vector store from disk and create a retriever"""
    if not os.path.exists(PERSIST_DIRECTORY):
        print(f"Warning: Database directory {PERSIST_DIRECTORY} not found.")
        return None

    print("Loading existing vector store...")

    embedding_function = OllamaEmbeddings(model="nomic-embed-text")
    vectorstore = Chroma(
        collection_name="rag-edgeai-eng-chroma",
        embedding_function=embedding_function,
        persist_directory=PERSIST_DIRECTORY,
    )

    retriever = vectorstore.as_retriever(k=3)
    return retriever


def record_audio(button=None, duration=10, sample_rate=44100):
    """
    Record audio from the microphone.
    If button is provided, records until button is released.
    Otherwise, records for fixed duration.

    Args:
        button: gpiozero Button object (optional).
        duration (int): Duration of recording in seconds (used if button is None).
        sample_rate (int): Sample rate of the recording.

    Returns:
        str: Path to the temporary audio file.
    """
    if button:
        print("Recording... Release button to stop.")
        q = queue.Queue()

        def callback(indata, frames, time, status):
            if status:
                print(status)
            q.put(indata.copy())

        try:
            with sd.InputStream(samplerate=sample_rate, channels=1, callback=callback):
                while button.is_pressed:
                    sd.sleep(50)  # Wait 50ms

            print("Recording finished.")

            data_chunks = []
            while not q.empty():
                data_chunks.append(q.get())

            if not data_chunks:
                return None

            recording = np.concatenate(data_chunks, axis=0)

            # Create a temporary file
            fd, path = tempfile.mkstemp(suffix=".wav")

            # Write the recording to the file
            # Convert to 16-bit PCM
            data = (recording * 32767).astype(np.int16)
            write(path, sample_rate, data)

            # Close the file descriptor
            os.close(fd)

            return path

        except Exception as e:
            print(f"Error recording audio: {e}")
            return None

    else:
        print(f"Recording for {duration} seconds... Sing now!")

        try:
            # Record audio
            recording = sd.rec(
                int(duration * sample_rate), samplerate=sample_rate, channels=1
            )
            sd.wait()  # Wait until recording is finished
            print("Recording finished.")

            # Create a temporary file
            fd, path = tempfile.mkstemp(suffix=".wav")

            # Write the recording to the file
            # Convert to 16-bit PCM
            data = (recording * 32767).astype(np.int16)
            write(path, sample_rate, data)

            # Close the file descriptor
            os.close(fd)

            return path

        except Exception as e:
            print(f"Error recording audio: {e}")
            return None


def transcribe_audio(audio_file_path):
    """
    Transcribe audio file using Groq's Whisper model.

    Args:
        audio_file_path (str): Path to the audio file.

    Returns:
        str: Transcribed text.
    """
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    if not os.path.exists(audio_file_path):
        raise FileNotFoundError(f"Audio file not found: {audio_file_path}")

    try:
        with open(audio_file_path, "rb") as file:
            transcription = client.audio.transcriptions.create(
                file=(os.path.basename(audio_file_path), file.read()),
                model="whisper-large-v3-turbo",
                response_format="json",
                language="en",
                temperature=0.0,
            )
            return transcription.text
    except Exception as e:
        print(f"Error during transcription: {e}")
        return None


class MusicPlayer:
    def __init__(self):
        self.process = None
        self.socket_path = "/tmp/mpv_socket"
        self.ydl_opts = {
            "format": "bestaudio/best",
            "noplaylist": True,
            "quiet": True,
            "default_search": "ytsearch1:",
        }

    def _send_command(self, command_list):
        """Função auxiliar para enviar JSON para o socket do MPV"""
        if not os.path.exists(self.socket_path):
            print("[Erro] O player não parece estar rodando (socket não encontrado).")
            return

        try:
            client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            client.connect(self.socket_path)

            payload = json.dumps({"command": command_list}) + "\n"

            client.send(payload.encode("utf-8"))
            client.close()
        except Exception as e:
            print(f"[Erro] Falha ao comunicar com MPV: {e}")

    def play(self, query):
        self.stop()

        if os.path.exists(self.socket_path):
            os.remove(self.socket_path)

        print(f"\n[Sistema] Buscando: '{query}'...")

        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            try:
                info = ydl.extract_info(query, download=False)
                if "entries" in info:
                    info = info["entries"][0]

                url = info["url"]
                title = info["title"]
                print(f"[Sistema] Tocando: {title}")

                self.process = subprocess.Popen(
                    [
                        "mpv",
                        "--no-video",
                        f"--input-ipc-server={self.socket_path}",
                        "--idle",
                        url,
                    ],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                time.sleep(0.5)

            except Exception as e:
                print(f"[Erro] Falha ao tocar: {e}")

    def pause_toggle(self):
        print("[Sistema] Alternando Pause...")
        self._send_command(["cycle", "pause"])

    def stop(self):
        if self.process:
            self._send_command(["quit"])
            try:
                self.process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.process.terminate()

            self.process = None

            if os.path.exists(self.socket_path):
                os.remove(self.socket_path)

            print("[Sistema] Parado.")
        else:
            print("[Aviso] Já está parado.")


player = MusicPlayer()


def tocar_musica(query: str):
    player.play(query)


def pausar_retomar():
    player.pause_toggle()


def parar_musica():
    player.stop()


def detect_music():
    """
    Tool function to detect music.
    Handles recording, transcription, and identification internally.
    """
    try:
        # 1. Prompt and Record
        print("\n[System] Please sing the song you want to identify (10 seconds)...")
        audio_path = record_audio(duration=10)

        if not audio_path:
            return "Failed to record audio."

        # 2. Transcribe
        print("[System] Transcribing...")
        sung_lyrics = transcribe_audio(audio_path)

        # Cleanup audio file
        try:
            os.remove(audio_path)
        except OSError:
            pass

        if not sung_lyrics:
            return "Could not transcribe audio."

        # 3. RAG Identification
        # Load the retriever
        retriever = load_retriever()
        if not retriever:
            return "Database not found. Cannot identify music."

        start_time = time.time()

        print(f"[System] Detecting music from lyrics: '{sung_lyrics}'")
        print("[System] Retrieving documents...")
        docs = retriever.invoke(sung_lyrics)

        # Include metadata in context
        docs_content = "\n\n".join(
            f"Music Name: {doc.metadata.get('music_name', 'Unknown')}\nLyrics content: {doc.page_content}"
            for doc in docs
        )

        # Custom prompt for music identification
        template = """You are a music expert helper. Your task is to identify which song the following lyrics belong to.
        Use the provided context which contains lyrics and their associated music names.
        
        Context:
        {context}
        
        User Input Text: {question}
        
        Based on the context, identify the song name. If the input text matches the lyrics in the context, return ONLY the Music Name.
        If no match is found, return "Music not found".
        """

        rag_prompt = ChatPromptTemplate.from_template(template)
        rag_chain = rag_prompt | llm | StrOutputParser()
        identified_music = rag_chain.invoke(
            {"context": docs_content, "question": sung_lyrics}
        )

        end_time = time.time()
        latency = end_time - start_time

        result_msg = f"I identified the song as: {identified_music.strip()} (Time: {latency:.2f}s)"
        print(f"[System] {result_msg}")

        return result_msg

    except Exception as e:
        print(f"Error in detect_music: {e}")
        return f"An error occurred during music detection: {str(e)}"
