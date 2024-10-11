import streamlit as st
from audio_recorder_streamlit import audio_recorder
import os
import json
from io import BytesIO
from texttoreport import format_assessment_report, format_exercise_plan
from voicetotext import transcribe_audio
from createreport import create_physiotherapy_report, save_as_docx, create_exercise_plan_report
import base64

# Create the 'recordings' folder if it doesn't exist
recordings_folder = 'voicerecordings'
if not os.path.exists(recordings_folder):
    os.makedirs(recordings_folder)

def get_image_as_base64(path):
    with open(path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

def display_title():
    logo_base64 = get_image_as_base64("PTIcon.jpg.crdownload.jpg")
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@700&display=swap');
        .custom-h1 {{ font-size: 24px; color: #002366 !important; font-family: 'Montserrat', sans-serif; font-weight: bold; }}
        .custom-p {{ color: #002244; font-family: 'Arial', sans-serif; font-size: 12px; }}
        .stButton>button {{ background-color: #4CAF50; color: white; border: none; padding: 10px 24px; margin: 10px 0; border-radius: 4px; cursor: pointer; }}
        .stButton>button:hover {{ background-color: #45a049; }}
        .step-title {{ font-size: 18px; color: #002366; font-weight: bold; margin: 20px 0 10px; }}
        .expander-title {{ font-size: 16px; color: #004488; font-weight: bold; }}
        .section-title {{ font-size: 20px; color: #006699; font-weight: bold; margin-top: 20px; }}
        </style>
        <div style="display: flex; align-items: center;">
            <img src="data:image/png;base64,{logo_base64}" style="width:40px; margin-right:15px; vertical-align: middle;">
            <div>
                <h1 class="custom-h1">PhysioAI - Automated Therapist Assistant</h1>
                <p class="custom-p">A digital tool that streamlines physiotherapy assessments by automating transcription, report generation, and personalized exercise planning</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

def initialize_session_variables():
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
    if 'final_message_shown' not in st.session_state:
        st.session_state.final_message_shown = False
    if 'assessment_report_downloaded' not in st.session_state:
        st.session_state.assessment_report_downloaded = False
    if 'exercise_plan_downloaded' not in st.session_state:
        st.session_state.exercise_plan_downloaded = False

initialize_session_variables()

st.sidebar.title("Options")
record_option = st.sidebar.radio("Select Input Method", ("Upload Voice Note", "Record Voice Note"), on_change=lambda: reset_state())

def reset_state():
    st.session_state.transcription_done = False
    st.session_state.assessment_report_done = False
    st.session_state.exercise_plan_done = False
    st.session_state.transcribed_text = None
    st.session_state.assessment_report = None
    st.session_state.exercise_plan = None
    st.session_state.recorded_audio_path = None
    st.session_state.final_message_shown = False
    st.session_state.assessment_report_downloaded = False
    st.session_state.exercise_plan_downloaded = False

display_title()

if record_option == "Upload Voice Note":
    audio_file = st.file_uploader("Upload a voice note (MP3, WAV, M4A)", type=["mp3", "wav", "m4a"])
    if audio_file is not None:
        with st.spinner('Saving uploaded audio...'):
            file_extension = audio_file.name.split('.')[-1].lower()
            temp_audio_path = os.path.join(recordings_folder, f"temp_audio_file.{file_extension}")
            with open(temp_audio_path, "wb") as f:
                f.write(audio_file.read())
            st.session_state.recorded_audio_path = temp_audio_path
            st.success(f"Audio file saved: {temp_audio_path}")

elif record_option == "Record Voice Note":
    audio_bytes = audio_recorder(pause_threshold=2.0, sample_rate=41000, text="", recording_color="#e8b62c", neutral_color="#6aa36f", icon_name="microphone", icon_size="4x")
    if audio_bytes:
        wav_audio_path = os.path.join(recordings_folder, "latest_recording.wav")
        with open(wav_audio_path, "wb") as f:
            f.write(audio_bytes)
        st.session_state.recorded_audio_path = wav_audio_path
        st.audio(wav_audio_path, format="audio/wav")
        st.success("Recording saved. Click 'Submit for Transcription' to proceed.")

# Display previous outputs
if st.session_state.transcribed_text:
    st.markdown("<div class='section-title'>Transcribed Text</div>", unsafe_allow_html=True)
    text_area_height = st.slider("Adjust Transcribed Text Height", 100, 500, 200)
    st.text_area('', st.session_state.transcribed_text, height=text_area_height)

if st.session_state.assessment_report:
    st.markdown("<div class='section-title'>Assessment Report</div>", unsafe_allow_html=True)
    report_area_height = st.slider("Adjust Assessment Report Height", 100, 500, 200)
    for key, value in st.session_state.assessment_report.items():
        if isinstance(value, dict):
            st.text(f"{key.capitalize()}:")
            for subkey, subvalue in value.items():
                st.text(f"  {subkey.capitalize()}: {subvalue}")
        else:
            st.text(f"{key.capitalize()}: {value}")

if st.session_state.exercise_plan:
    st.markdown("<div class='section-title'>Exercise Plan</div>", unsafe_allow_html=True)
    exercise_area_height = st.slider("Adjust Exercise Plan Height", 100, 500, 200)
    for key, value in st.session_state.exercise_plan.items():
        if isinstance(value, dict):
            st.text(f"{key.capitalize()}:")
            for subkey, subvalue in value.items():
                st.text(f"  {subkey.capitalize()}: {subvalue}")
        else:
            st.text(f"{key.capitalize()}: {value}")

# Processing buttons
if st.session_state.recorded_audio_path and not st.session_state.transcription_done:
    if st.button("Submit for Transcription"):
        with st.spinner('Transcribing audio...'):
            try:
                st.session_state.transcribed_text = transcribe_audio(st.session_state.recorded_audio_path)
                st.session_state.transcription_done = True
            except Exception as e:
                st.error(f"An error occurred during transcription: {e}")

if st.session_state.transcription_done and not st.session_state.assessment_report_done:
    st.markdown("<div class='step-title'>Generate Assessment Report</div>", unsafe_allow_html=True)
    if st.button("Generate Assessment Report"):
        with st.spinner('Generating assessment report...'):
            try:
                report_json_string = format_assessment_report(st.session_state.transcribed_text)
                st.session_state.assessment_report = json.loads(report_json_string)
                st.session_state.assessment_report_done = True
            except Exception as e:
                st.error(f"An error occurred: {e}")

if st.session_state.assessment_report_done:
    st.markdown("<div class='step-title'>Download Assessment Report</div>", unsafe_allow_html=True)
    buffer = save_as_docx(st.session_state.assessment_report, 'headerpic.png')
    downloaded = st.download_button(
        "Download Assessment Report",
        data=buffer,
        file_name="physiotherapy_report.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
    if downloaded:
        st.session_state.assessment_report_downloaded = True

    if st.session_state.assessment_report_downloaded:
        st.success("Assessment report downloaded successfully.")

if st.session_state.assessment_report_done and not st.session_state.exercise_plan_done:
    st.markdown("<div class='step-title'>Generate Exercise Plan</div>", unsafe_allow_html=True)
    if st.button("Generate Exercise Plan"):
        with st.spinner('Generating exercise plan...'):
            try:
                exercise_plan_data = format_exercise_plan(st.session_state.assessment_report)
                if isinstance(exercise_plan_data, str):
                    st.session_state.exercise_plan = json.loads(exercise_plan_data)
                elif isinstance(exercise_plan_data, dict):
                    st.session_state.exercise_plan = exercise_plan_data
                else:
                    raise ValueError("Invalid format: exercise_plan must be a dictionary or a JSON string.")
                st.session_state.exercise_plan_done = True
            except Exception as e:
                st.error(f"An error occurred: {e}")

if st.session_state.exercise_plan_done:
    st.markdown("<div class='step-title'>Download Exercise Plan</div>", unsafe_allow_html=True)
    buffer = BytesIO()
    doc = create_exercise_plan_report(st.session_state.exercise_plan, logo_path='headerpic.png')
    doc.save(buffer)
    buffer.seek(0)
    downloaded = st.download_button(
        "Download Exercise Plan Report",
        data=buffer,
        file_name="exercise_plan_report.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
    if downloaded:
        st.session_state.exercise_plan_downloaded = True

    if st.session_state.exercise_plan_downloaded:
        st.success("Exercise plan report downloaded successfully.")

if st.session_state.final_message_shown:
    st.markdown("Thank you for using PhysioAI! 😊", unsafe_allow_html=True)
