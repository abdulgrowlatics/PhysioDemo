
import streamlit as st
from st_audiorec import st_audiorec
import os
import json
from io import BytesIO
from datetime import datetime
from texttoreport import format_assessment_report, format_exercise_plan
from voicetotext import transcribe_audio
from createreport import create_physiotherapy_report, save_as_docx, create_exercise_plan_report  # Replace with the actual import path
import base64
# Create the 'recordings' folder if it doesn't exist
recordings_folder = 'voicerecordings'
if not os.path.exists(recordings_folder):
    os.makedirs(recordings_folder)


def get_image_as_base64(path):
    with open(path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

def display_title():
    # Read your local image to get the base64 encoded version
    logo_base64 = get_image_as_base64("PTIcon.jpg.crdownload")
    
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@700&display=swap');
        
        .custom-h1 {{
            font-size: 24px;
            color: #002366 !important;  /* Dark navy blue with !important rule */
            font-family: 'Montserrat', sans-serif;
            font-weight: bold;
        }}
        .custom-p {{
            color: #002244;  /* Dark navy blue */
            font-family: 'Arial', sans-serif;
            font-size: 12px;
        }}
        </style>
        <div style="display: flex; align-items: center;">
            <img src="data:image/png;base64,{logo_base64}" style="width:40px; margin-right:15px; vertical-align: middle;">
            <div>
                <h1 class="custom-h1">PhysioAI - Automated Therapist Assistant</h1>
                <p class="custom-p">A digital tool that streamlines physiotherapy assessments by automating transcription, report generation, and personalized exercise planning</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
    """
    <style>
        .subheader-style {
            font-size: 16px;
            color: #002366;  /* Dark navy blue */
            font-family: 'Poppins', sans-serif;
            font-weight: bold;
            padding: 10px 0;
            border-bottom: 2px solid #EAECEE;  /* Slight bottom border for separation */
        }
    </style>
    """,
    unsafe_allow_html=True,
    )
# Streamlit UI Styling
st.markdown(
    """
    <style>
        .main {
            background-color: #f9f9f9;
            padding: 20px;
        }
        .stButton button {
            background-color: #4CAF50;
            color: white;
            width: 100%;
            border: none;
            padding: 10px;
            text-align: center;
            display: inline-block;
            font-size: 16px;
            margin: 10px 0;
            cursor: pointer;
        }
        .stButton button:hover {
            background-color: #45a049;
        }
        .header-title {
            font-size: 2em;
            color: #333;
            text-align: center;
            margin-bottom: 30px;
        }
        .step-title {
            font-size: 1.5em;
            color: #333;
            margin: 20px 0 10px 0;
        }
        .sidebar .sidebar-content {
            width: 300px;
            height: 100%;
            padding: 20px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Initialize session state variables
if 'transcribed_text' not in st.session_state:
    st.session_state.transcribed_text = None
if 'assessment_report' not in st.session_state:
    st.session_state.assessment_report = None
if 'exercise_plan' not in st.session_state:
    st.session_state.exercise_plan = None
if 'recorded_audio_path' not in st.session_state:
    st.session_state.recorded_audio_path = None
if 'transcription_done' not in st.session_state:
    st.session_state.transcription_done = False
if 'assessment_report_done' not in st.session_state:
    st.session_state.assessment_report_done = False
if 'exercise_plan_done' not in st.session_state:
    st.session_state.exercise_plan_done = False
if 'is_recording' not in st.session_state:
    st.session_state.is_recording = False

# Streamlit Sidebar
st.sidebar.title("Options")
record_option = st.sidebar.radio(
    "Select Input Method",
    ("Upload Voice Note", "Record Voice Note")
)
display_title()
# Streamlit UI
#st.markdown("<div class='header-title'>Physio AI - Physiotherapy Assessment Tool</div>", unsafe_allow_html=True)

# Step 1: Upload or Record Audio
if record_option == "Upload Voice Note":
    audio_file = st.file_uploader("Upload a voice note (MP3, WAV, M4A)", type=["mp3", "wav", "m4a"])
    if audio_file is not None:
        with st.spinner('Saving uploaded audio...'):
            # Save the uploaded file
            file_extension = audio_file.name.split('.')[-1].lower()
            temp_audio_path = os.path.join(recordings_folder, f"temp_audio_file.{file_extension}")
            with open(temp_audio_path, "wb") as f:
                f.write(audio_file.read())
            st.session_state.recorded_audio_path = temp_audio_path
            st.success(f"Audio file saved: {temp_audio_path}")

elif record_option == "Record Voice Note":
    # Record Voice Note with explicit control
    if not st.session_state.is_recording:
        if st.button("Start Recording"):
            st.session_state.is_recording = True
            st.write("Recording... Click 'Download Recording' when done.")
            audio_data = st_audiorec()  # This component manages the recording interface

    else:
        audio_data = st_audiorec()
        if st.button("Download Recording"):
            with st.spinner('Saving recorded audio...'):
                st.session_state.is_recording = False
                if audio_data is not None:
                    try:
                        # Save the recording to a fixed file for latest recording
                        wav_audio_path = os.path.join(recordings_folder, "latest_recording.wav")
                        
                        # Save the recorded audio as WAV in the 'recordings' folder
                        with open(wav_audio_path, "wb") as f:
                            f.write(audio_data)
                        
                        # The path of the saved audio file
                        st.session_state.recorded_audio_path = wav_audio_path
                        st.write(f"Audio recording saved at: {wav_audio_path}")
                        
                        # Provide a download link for the recorded audio file
                        with open(wav_audio_path, "rb") as file:
                            st.download_button(
                                label="Download Recorded Audio",
                                data=file,
                                file_name="latest_recording.wav",
                                mime="audio/wav"
                            )

                        st.audio(wav_audio_path, format="audio/wav")  # Play the WAV audio for verification
                        st.success(f"Audio recording saved. Click 'Submit for Transcription' to process.")

                    except Exception as e:
                        st.error(f"Error saving audio file: {e}")

# Display "Submit for Transcription" button if recording or file upload is completed and transcription is not done
if st.session_state.recorded_audio_path and not st.session_state.transcription_done:
    if st.button("Submit for Transcription"):
        with st.spinner('Transcribing audio...'):
            try:
                if os.path.exists(st.session_state.recorded_audio_path):
                    # Use the specified audio file
                    st.session_state.transcribed_text = transcribe_audio(st.session_state.recorded_audio_path)
                    st.session_state.transcription_done = True  # Mark transcription as done
                else:
                    st.error("Audio file not found.")
                
                st.markdown("<div class='step-title'>Transcription:</div>", unsafe_allow_html=True)
                st.text_area("Transcribed Text", st.session_state.transcribed_text, height=200)
            except FileNotFoundError as e:
                st.error(f"File not found error during transcription: {e}")
            except Exception as e:
                st.error(f"An error occurred during transcription: {e}")

# Step 2: Generate Assessment Report if transcription is done and report is not generated
if st.session_state.transcription_done and not st.session_state.assessment_report_done:
    st.markdown("<div class='step-title'>Step 2: Generate Assessment Report</div>", unsafe_allow_html=True)
    if st.button("Generate Assessment Report"):
        with st.spinner('Generating assessment report...'):
            try:
                report_json_string = format_assessment_report(st.session_state.transcribed_text)
                # Parse the JSON string into a dictionary
                st.session_state.assessment_report = json.loads(report_json_string)
                st.session_state.assessment_report_done = True  # Mark report generation as done
                
                st.success("Assessment report generated successfully!")
            except json.JSONDecodeError as e:
                st.error(f"Error decoding JSON: {e}")
            except Exception as e:
                st.error(f"An error occurred during report generation: {e}")

# Step 3: Download Report if assessment report is done
if st.session_state.assessment_report_done:
    st.markdown("<div class='step-title'>Step 3: Download Report</div>", unsafe_allow_html=True)
    st.success("The report is generated successfully. Click the button below to download.")
    if st.button("Download Report"):
        with st.spinner('Generating Word document...'):
            try:
                # Generate and save the DOCX file
                buffer = save_as_docx(st.session_state.assessment_report, 'headerpic.png')  
                # Provide download button
                st.download_button(
                    label="Download Physiotherapy Report",
                    data=buffer,
                    file_name="physiotherapy_report.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
            except FileNotFoundError as e:
                st.error(f"File not found error during document generation: {e}")
            except Exception as e:
                st.error(f"An error occurred during document generation: {e}")


if st.session_state.assessment_report_done and not st.session_state.exercise_plan_done:
    st.markdown("<div class='step-title'>Step 4: Generate Exercise Plan</div>", unsafe_allow_html=True)
    if st.button("Generate Exercise Plan"):
        with st.spinner('Generating exercise plan...'):
            try:
                # Generate exercise plan in dictionary format
                exercise_plan_data = format_exercise_plan(st.session_state.assessment_report)
                
                # Check if exercise_plan_data is a JSON string and convert to dictionary
                if isinstance(exercise_plan_data, str):
                    st.session_state.exercise_plan = json.loads(exercise_plan_data)
                elif isinstance(exercise_plan_data, dict):
                    st.session_state.exercise_plan = exercise_plan_data
                else:
                    raise ValueError("Invalid format: exercise_plan must be a dictionary or a JSON string.")
                    
                st.session_state.exercise_plan_done = True  # Mark exercise plan as done
                st.success("Exercise plan created successfully!")

                # Generate the Word document for the exercise plan
                buffer = BytesIO()
                doc = create_exercise_plan_report(st.session_state.exercise_plan, logo_path='headerpic.png')
                doc.save(buffer)
                buffer.seek(0)

                # Provide download button for the exercise plan Word document
                st.download_button(
                    label="Download Exercise Plan Report",
                    data=buffer,
                    file_name="exercise_plan_report.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
            except json.JSONDecodeError as e:
                st.error(f"Error decoding JSON: {e}")
            except Exception as e:
                st.error(f"An error occurred during exercise plan generation: {e}")









