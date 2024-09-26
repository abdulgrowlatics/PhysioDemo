
import os
import openai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Now you can access the variables like this:
openai_api_key = os.getenv('OPENAI_API_KEY')

def format_assessment_report(text):
    try:
        var1 = "Given the following physiotherapy assessment transcription--- "
        var2 = text
        var3 = """--- Using only the information provided above, 

        Please extract and format the content into the following sections. Do not add any information that is not explicitly mentioned in the transcription:
        1. Patient Name
        2. Date of Visit
        3. Subjective Findings (including chief complaint, pain rating, onset, location, aggravating/alleviating factors, and functional limitations)
        4. Objective Findings (including posture, range of motion, palpation, muscle strength, special tests, etc.)
        5. Assessment (including diagnosis and problem list)
        6. Plan (including short-term goals, long-term goals, interventions, home exercise program, and frequency of treatment)
        7. Next Appointment (date and time)
        8. Instructions to Patient
        9. Clinic Information (Clinic Name, address, phone, email, website)

        Format the response using the following structure in JSON format. Include a key only if relevant information is present in the transcription.
        """

        prompt = var1 + var2 + var3

        response = openai.ChatCompletion.create(
            model="gpt-4o",  # Assuming this is the correct model name
            messages=[
                {"role": "system", "content": "You are a physiotherapy report generator. Only use the information provided by the user."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=4090,
            n=1,
            stop=None,
            temperature=0.2
        )

        # Extract the response text
        response_text = response['choices'][0]['message']['content'].strip()

        # Clean up any triple backticks (```json) that may surround the response
        if response_text.startswith('```json'):
            response_text = response_text[7:]  # Remove ```json
        if response_text.endswith('```'):
            response_text = response_text[:-3]  # Remove closing ```

        # Now parse the cleaned JSON string into actual JSON
        return response_text

    except openai.OpenAIError as e:
        return f"OpenAI API error: {str(e)}"
    except Exception as e:
        return f"An error occurred: {str(e)}"


def format_exercise_plan(response_text):
    try:
        prompt = f"""
        Based on the provided assessment findings:

        {response_text}

        Please create a detailed exercise plan strictly using the provided findings. Do not suggest exercises or details not supported by the findings. Use the following structure:
        1. Exercise Name
        2. Frequency/Repetitions
        3. Description (description of the exercise)
        
        Format the response in JSON format. Include a key only if relevant information is present in the findings.
        """

        response = openai.ChatCompletion.create(
            model="gpt-4o",  # Assuming this is the correct model name
            messages=[
                {"role": "system", "content": "You are an exercise plan generator for physiotherapy. Only use the provided assessment findings to generate the plan."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=4000,
            n=1,
            stop=None,
            temperature=0.2
        )

        # Extract the response text
        response_text = response['choices'][0]['message']['content'].strip()

        # Clean up any triple backticks (```json) that may surround the response
        if response_text.startswith('```json'):
            response_text = response_text[7:]  # Remove ```json
        if response_text.endswith('```'):
            response_text = response_text[:-3]  # Remove closing ```

        # Now parse the cleaned JSON string into actual JSON
        return response_text

    except openai.OpenAIError as e:
        return f"OpenAI API error: {str(e)}"
    except Exception as e:
        return f"An error occurred: {str(e)}"



