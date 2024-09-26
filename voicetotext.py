import os
import openai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Now you can access the variables like this:
openai_api_key = os.getenv('OPENAI_API_KEY')


# Define a function to handle audio transcription
def transcribe_audio(file_path):
    """
    Transcribe an audio file using OpenAI's Whisper model.

    Args:
        file_path (str): The path to the audio file to be transcribed.

    Returns:
        str: The transcribed text from the audio file.
    """
    try:
        # Initialize OpenAI client with the API key
        openai.api_key = openai_api_key
        
        if openai_api_key is None:
            raise ValueError("OpenAI API key not found. Set the 'OPENAI_API_KEY' environment variable.")

        # Open the audio file
        with open(file_path, "rb") as audio_file:
            # Transcribe the audio file using the correct method
            transcription = openai.Audio.transcribe(
                model="whisper-1", 
                file=audio_file
            )

        # Return the transcribed text
        return transcription['text']

    except FileNotFoundError:
        return f"Error: The file '{file_path}' was not found."
    except openai.OpenAIError as e:  # Correct error handling
        return f"OpenAI API error: {str(e)}"
    except Exception as e:
        return f"An error occurred: {str(e)}"

# Example usage
# if __name__ == "__main__":
#     file_path = r"AudioFile\WhatsApp Audio 2024-09-18 at 4.18.12 PM (online-audio-converter.com).mp3"
#     transcribed_text = transcribe_audio(file_path)
#     print(transcribed_text)
