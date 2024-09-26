
# PhysioAI - Automated Therapist Assistant

A digital tool that streamlines physiotherapy assessments by automating transcription, report generation, and personalized exercise planning.

## FastAPI
This FastAPI application allows for uploading an audio file and processing it sequentially for transcription, report generation, and exercise plan creation. The results are streamed in real-time using Server-Sent Events (SSE).

## Features

- Transcribes audio using OpenAI's Whisper model.
- Generates a physiotherapy assessment report.
- Creates a physiotherapy exercise plan.
- Returns responses in real-time using Server-Sent Events (SSE).

## Installation

### Step 1: Create and activate a virtual environment

Using Conda (optional):

```bash
conda create --name physiodemo python=3.8
conda activate physiodemo
```

Or use `venv`:

```bash
python -m venv env
source env/bin/activate  # On Windows: .\env\Scripts\activate
```

### Step 2: Install dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Set up environment variables

Create a `.env` file in the root directory and add your OpenAI API key:

```bash
OPENAI_API_KEY=your_openai_api_key_here
```

## Running the Application

Start the FastAPI server:

```bash
uvicorn main:app --reload
```

## API Endpoints

### POST `/process_audio/`

Uploads an audio file, processes it sequentially, and returns responses in real-time.

#### Request

```bash
POST /process_audio/
Content-Type: multipart/form-data
```

#### Example using `curl`:

```bash
curl -X 'POST'   'http://127.0.0.1:8000/process_audio/'   -H 'accept: text/event-stream'   -H 'Content-Type: multipart/form-data'   -F 'file=@/path/to/audiofile.mp3'
```

#### Response Stream:

- Transcription of the audio file.
- Generated physiotherapy assessment report.
- Created exercise plan.

## Real-time Response Handling

Each result (transcription, report, exercise plan) will be sent in sequence using Server-Sent Events.

Example JavaScript code to listen to responses:

```javascript
const eventSource = new EventSource('http://127.0.0.1:8000/process_audio/');

eventSource.addEventListener('transcription', function(event) {
  console.log('Transcription:', event.data);
});

eventSource.addEventListener('formatted_report', function(event) {
  console.log('Report:', event.data);
});

eventSource.addEventListener('exercise_plan', function(event) {
  console.log('Exercise Plan:', event.data);
});
```

## Requirements

```txt
fastapi==0.115.0
openai==0.28.0
python-docx==1.1.2
python-dotenv==1.0.1
python-multipart==0.0.9
sse-starlette==2.1.3
streamlit==1.38.0
streamlit-audiorec==0.1.3
streamlit-webrtc==0.47.9
uvicorn==0.30.6
```

## License

This project is licensed under the MIT License.
