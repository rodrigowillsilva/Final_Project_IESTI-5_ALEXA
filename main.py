import os
import sys
import inference
import utils
from gpiozero import Button

SYSTEM_PROMPT = {
    "role": "AI Assistant",
    "content": (
        "You are a local AI assistant running on a Raspberry Pi that acts like Alexa. "
        "### RULES FOR INTERACTIONS: \n"
        "when the user asks to turn on or off the light, use the 'control_light'.\n"
        "when the user asks about temperature or humidity, use the 'get_environment_metrics'.\n"
        "when the user asks to play (NOT IDENTIFY), pause, resume, or stop music, use 'tocar_musica', 'pausar_retomar', or 'parar_musica' respectively.\n"
        "when the user asks to identify a song, use the 'detect_music' function.\n"
    ),
}


def main():
    """
    Main application loop.
    Simulates the STT -> Inference -> TTS pipeline in the terminal.
    """
    history = [SYSTEM_PROMPT]

    # Initialize Button
    button = Button(20)

    print("\n--- Local Alexa (Edge AI Prototype) Initialized ---")
    print("Press the BUTTON (GPIO 20) to start recording.")
    print("Press Ctrl+C to stop.\n")

    # print("\n--- Audio Recording Test ---")

    # audio_path = utils.record_audio(duration=5)
    # print(f"Audio recorded and saved to: {audio_path}")

    # transcribed_text = utils.transcribe_audio(audio_path)
    # print(f"Transcribed text: {transcribed_text}")

    # os.remove(audio_path)

    # # play the recorded audio
    # import sounddevice as sd
    # from scipy.io.wavfile import read

    # sample_rate, data = read(audio_path)
    # sd.play(data, sample_rate)
    # sd.wait()  # Wait until playback is finished

    while True:
        try:
            # Wait for Button to start recording
            print("Waiting for button press...")
            button.wait_for_press()

            # Record while button is held
            audio_path = utils.record_audio(button=button)
            print(f"Audio recorded and saved to: {audio_path}")

            user_text = utils.transcribe_audio(audio_path)
            print(f"Transcribed text: {user_text}")

            # cleanup
            try:
                os.remove(audio_path)
            except OSError:
                pass

            if not user_text or not user_text.strip():
                continue

            # Core Inference
            ai_response = inference.run_inference(user_text, history)

            # Output Simulation (This will be replaced by the TTS module later)
            print(f"ALEXA: {ai_response}\n")

        except KeyboardInterrupt:
            print("\nForced shutdown.")
            sys.exit(0)


if __name__ == "__main__":
    main()
