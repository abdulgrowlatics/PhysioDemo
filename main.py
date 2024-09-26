from fastapi import FastAPI, UploadFile, File, HTTPException
from voicetotext import transcribe_audio
from texttoreport import format_assessment_report, format_exercise_plan
import os
import shutil
from dotenv import load_dotenv
from sse_starlette.sse import EventSourceResponse
import asyncio

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

# Directory to save uploaded files
UPLOAD_DIR = "uploaded_audios"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# Generator for processing each step and sending data in parts
async def process_audio_steps(file_path):
    try:
        # Step 1: Transcribe the audio
        transcribed_text = transcribe_audio(file_path)
        if "Error" in transcribed_text:
            yield {"event": "error", "data": transcribed_text}
            return
        yield {"event": "transcription", "data": transcribed_text}
        await asyncio.sleep(1)  # Simulating a small delay for demonstration purposes

        # Step 2: Generate the assessment report from the transcription
        formatted_report = format_assessment_report(transcribed_text)
        if "Error" in formatted_report:
            yield {"event": "error", "data": formatted_report}
            return
        yield {"event": "formatted_report", "data": formatted_report}
        await asyncio.sleep(1)  # Simulating a small delay for demonstration purposes

        # Step 3: Generate the exercise plan from the formatted report
        exercise_plan = format_exercise_plan(formatted_report)
        if "Error" in exercise_plan:
            yield {"event": "error", "data": exercise_plan}
            return
        yield {"event": "exercise_plan", "data": exercise_plan}

    except Exception as e:
        yield {"event": "error", "data": f"An error occurred: {str(e)}"}


@app.post("/process_audio/")
async def process_audio(file: UploadFile = File(...)):
    try:
        # Save the uploaded audio file to a directory
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Return an EventSourceResponse to stream results step-by-step
        return EventSourceResponse(process_audio_steps(file_path))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
