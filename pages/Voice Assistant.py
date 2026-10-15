import os
import io
import json
import base64
import re
import requests
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv
from gtts import gTTS

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from theme import apply_chart_theme, get_colors

# -----------------------------------------------------------------------------
# Configuration & Environment
# -----------------------------------------------------------------------------

# Load environment variables
current_dir = os.path.dirname(os.path.abspath(__file__))
code_dir = os.path.dirname(current_dir)
project_dir = os.path.dirname(code_dir)

env_candidates = [
    os.path.join(code_dir, ".env"),
    os.path.join(project_dir, ".env"),
    os.path.join(current_dir, ".env")
]

for env_path in env_candidates:
    if os.path.exists(env_path):
        load_dotenv(env_path)
        break

api_key = os.getenv("gemini_api") or os.getenv("GEMINI_API_KEY")

# -----------------------------------------------------------------------------
# Dataset Loading
# -----------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def load_data():
    parquet_candidates = [
        os.path.join(code_dir, "Cleaned data.parquet"),
        os.path.join(project_dir, "Code", "Cleaned data.parquet"),
        os.path.join(current_dir, "Cleaned data.parquet"),
        "/Users/menna/Python/EDA/Final Project/Code/Cleaned data.parquet"
    ]
    for p in parquet_candidates:
        if os.path.exists(p):
            try:
                df = pd.read_parquet(p)
                return df, p
            except Exception as e:
                st.error(f"Error loading parquet file at {p}: {e}")
    return None, None

df, dataset_path = load_data()

# -----------------------------------------------------------------------------
# Gemini API Helpers
# -----------------------------------------------------------------------------
CANDIDATE_MODELS = [
    "gemini-3.8-flash",
    "gemini-3.5-flash",
    "gemini-3.1-flash-lite",
    "gemini-flash-latest"
]

def call_gemini_api(payload, candidate_models=CANDIDATE_MODELS, current_key=api_key):
    """
    Calls Google Gemini REST API with automatic model fallback in case of high demand / rate limits.
    """
    if not current_key:
        return None, "Gemini API key is not configured. Please check your .env file."

    last_error = ""
    for model in candidate_models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={current_key}"
        try:
            headers = {"Content-Type": "application/json"}
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            if response.status_code == 200:
                data = response.json()
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts:
                        text_res = parts[0].get("text", "")
                        return text_res, None
            elif response.status_code in [404, 503, 429]:
                last_error = f"Model {model} returned status {response.status_code}: {response.text[:200]}"
                continue  # Fallback to next model
            else:
                last_error = f"API Error ({response.status_code}): {response.text[:200]}"
                continue
        except Exception as e:
            last_error = f"Request exception on {model}: {str(e)}"
            continue

    return None, f"Failed to get response from Gemini models. Details: {last_error}"


def transcribe_audio_with_gemini(audio_bytes, mime_type="audio/wav", current_key=api_key):
    """
    Transcribes spoken voice audio to English text using Gemini multimodal input.
    """
    audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
    payload = {
        "contents": [
            {
                "parts": [
                    {"inline_data": {"mime_type": mime_type, "data": audio_b64}},
                    {
                        "text": (
                            "Listen carefully to this audio recording. "
                            "Transcribe the user's spoken question into clear English text. "
                            "If spoken in another language, translate it directly into English. "
                            "Output ONLY the transcribed question text without any markdown or conversational filler."
                        )
                    }
                ]
            }
        ]
    }
    result, err = call_gemini_api(payload, current_key=current_key)
    if err:
        return None, err
    return result.strip() if result else "", None


def generate_tts_audio(text_content):
    """
    Converts English text into an MP3 audio buffer using gTTS.
    """
    try:
        # Clean text for smoother speech
        clean_text = re.sub(r"[\*#_`>\[\]\(\)]", "", text_content)
        clean_text = re.sub(r"https?://\S+", "", clean_text)
        clean_text = clean_text.strip()
        if not clean_text:
            return None

        # Truncate very long speech to prevent excessively large audio files
        if len(clean_text) > 800:
            clean_text = clean_text[:800] + "..."

        tts = gTTS(text=clean_text, lang="en")
        audio_fp = io.BytesIO()
        tts.write_to_fp(audio_fp)
        audio_fp.seek(0)
        return audio_fp.getvalue()
    except Exception as e:
        return None


# -----------------------------------------------------------------------------
# Data Analysis & Safe Code Execution Engine
# -----------------------------------------------------------------------------
def analyze_question_with_dataset(question, dataframe, current_key=api_key):
    """
    Generates and executes pandas code to analyze 'Cleaned data.parquet' strictly.
    Returns:
        dict: {
            'is_relevant': bool,
            'answer': str,
            'code': str,
            'data_result': any,
            'chart': plotly Figure or None,
            'error': str or None
        }
    """
    columns_info = list(dataframe.columns)
    departments = list(dataframe["Department"].unique()) if "Department" in dataframe else []
    sample_records = dataframe.head(2).to_dict(orient="records")

    system_prompt = f"""
You are an expert HR Data Analyst. You have access to a pandas DataFrame named `df` loaded from 'Cleaned data.parquet'.

Dataset Metadata:
- Total Records: {len(dataframe)}
- Columns: {columns_info}
- Available Departments: {departments}
- Date Range: Jan 2026 to Sep 2026

CRITICAL STRICT RULES:
1. You must answer ONLY using the data in `df` from 'Cleaned data.parquet'.
2. If the user question is NOT related to the HR / payroll data in this file (e.g., general knowledge, unrelated companies, external news, creative writing, programming tutorials), set "is_relevant" to false and provide a polite refusal in English stating: "I can only answer questions based strictly on the provided payroll dataset ('Cleaned data.parquet')."
3. If the question IS relevant, write safe, efficient Python/pandas code that operates on `df` and assigns the final calculation or summarized table to a variable named `result`.
4. The variable `result` can be a scalar number, a string, a pandas Series, or a pandas DataFrame.
5. If the user asks for comparison across categories (e.g. departments, months, job titles), group the data appropriately in `result`.
6. Return your response strictly as valid JSON with keys:
   - "is_relevant": (boolean) true if answerable from the data, false otherwise
   - "code": (string) Python code to compute `result` using `df`
   - "explanation": (string) Brief English description of the calculation
"""

    prompt = f"User Question: \"{question}\"\nAnalyze the dataset and respond in strict JSON."

    payload = {
        "contents": [
            {"parts": [{"text": f"{system_prompt}\n\n{prompt}"}]}
        ],
        "generationConfig": {"response_mime_type": "application/json"}
    }

    raw_response, err = call_gemini_api(payload, current_key=current_key)
    if err:
        return {"error": err, "is_relevant": False, "answer": err}

    try:
        parsed = json.loads(raw_response)
    except Exception:
        # Extract json chunk if raw string contains formatting
        match = re.search(r"\{.*\}", raw_response, re.DOTALL)
        if match:
            try:
                parsed = json.loads(match.group(0))
            except Exception as e:
                return {"error": f"Failed to parse model JSON: {e}", "is_relevant": False}
        else:
            return {"error": "Invalid response format from Gemini.", "is_relevant": False}

    is_relevant = parsed.get("is_relevant", False)
    if not is_relevant:
        refusal_msg = parsed.get("explanation") or (
            "I can only answer questions based strictly on the provided payroll dataset ('Cleaned data.parquet'). "
            "Your question appears to be outside the scope of this file."
        )
        return {
            "is_relevant": False,
            "answer": refusal_msg,
            "code": "",
            "data_result": None,
            "chart": None,
            "error": None
        }

    code = parsed.get("code", "")
    data_result = None
    chart_obj = None

    # Execute generated code
    if code:
        local_scope = {"df": dataframe.copy(), "pd": pd, "np": np}
        try:
            exec(code, {}, local_scope)
            data_result = local_scope.get("result")
        except Exception as exec_err:
            return {
                "is_relevant": True,
                "answer": f"An error occurred while calculating the result: {exec_err}",
                "code": code,
                "data_result": None,
                "chart": None,
                "error": str(exec_err)
            }

    # Synthesize English final answer from exact calculated result
    result_repr = str(data_result)
    if isinstance(data_result, pd.DataFrame):
        result_repr = data_result.head(10).to_markdown()
    elif isinstance(data_result, pd.Series):
        result_repr = data_result.head(10).to_string()

    synthesis_prompt = f"""
You are an expert HR Data Analyst. 
A user asked: "{question}"
We executed the analysis code on 'Cleaned data.parquet' and obtained this exact result:
{result_repr}

Write a clear, professional, direct English answer summarizing the findings.
Include exact figures (currency, counts, averages, or percentages) appropriately formatted.
Keep the answer concise and grounded strictly in this result. Do not speculate.
"""

    synth_payload = {
        "contents": [{"parts": [{"text": synthesis_prompt}]}]
    }

    final_text, synth_err = call_gemini_api(synth_payload, current_key=current_key)
    if synth_err or not final_text:
        final_text = f"Calculation Result:\n\n{result_repr}"

    # Auto-generate a Plotly chart if result is a categorical/aggregated table
    if isinstance(data_result, pd.DataFrame) and len(data_result) > 1 and len(data_result.columns) >= 2:
        try:
            num_cols = data_result.select_dtypes(include=[np.number]).columns
            cat_cols = data_result.select_dtypes(exclude=[np.number]).columns
            if len(num_cols) > 0 and len(cat_cols) > 0:
                chart_obj = px.bar(
                    data_result,
                    x=cat_cols[0],
                    y=num_cols[0],
                    title=f"{num_cols[0]} by {cat_cols[0]}",
                    text_auto=True,
                    template="plotly_white"
                )
                apply_chart_theme(chart_obj)
        except Exception:
            chart_obj = None

    return {
        "is_relevant": True,
        "answer": final_text.strip(),
        "code": code,
        "data_result": data_result,
        "chart": chart_obj,
        "error": None
    }


# -----------------------------------------------------------------------------
# Streamlit UI
# -----------------------------------------------------------------------------

# Sidebar
with st.sidebar:
    st.subheader("AI assistant settings", icon=":material/tune:")

    # Dataset Status
    if df is not None:
        st.success("Dataset connected", icon=":material/check_circle:")
        st.caption(f":material/folder: `Cleaned data.parquet` ({len(df):,} rows)")
    else:
        st.error("Dataset not found", icon=":material/error:")
        st.caption("Please ensure `Cleaned data.parquet` is present in the `Code` folder.")

    # API Key Status
    if api_key:
        st.success("Gemini API key active", icon=":material/check_circle:")
    else:
        st.warning("Gemini API key missing", icon=":material/warning:")
        api_input = st.text_input("Enter Gemini API key:", type="password")
        if api_input:
            api_key = api_input
            st.rerun()

    st.subheader("Dataset overview", icon=":material/database:")
    if df is not None:
        st.metric("Total records", f"{len(df):,}")
        st.metric("Unique employees", f"{df['Employee ID'].nunique():,}")
        st.metric("Departments", f"{df['Department'].nunique():,}")
        if "Month" in df.columns:
            st.caption(f":material/calendar_today: Period: {df['Month'].min().strftime('%b %Y')} – {df['Month'].max().strftime('%b %Y')}")

    if st.button("Clear chat history", icon=":material/delete:", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

# Main Page Header
st.header("AI payroll assistant", icon=":material/smart_toy:")
st.caption("Ask questions using **voice** or **text**. All responses are computed strictly from the payroll database.")

if df is None:
    st.error("`Cleaned data.parquet` could not be located. Please check the project directory.", icon=":material/error:")
    st.stop()

# Initialize Session State
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {
            "role": "assistant",
            "content": "Hello! I am your AI Payroll Analyst. You can speak to me or type your question in English. I will analyze `Cleaned data.parquet` and answer using only the data in the file.",
            "code": None,
            "data_result": None,
            "chart": None,
            "audio_bytes": None
        }
    ]

# Sample questions shortcuts
st.subheader("Suggested questions", icon=":material/lightbulb:")
cols = st.columns(4)
sample_prompts = [
    "What is the total gross salary by department?",
    "Which 5 employees have the highest penalties?",
    "What is the average net salary across departments?",
    "How many employees were hired each year?"
]

selected_prompt = None
for i, col in enumerate(cols):
    if col.button(sample_prompts[i], key=f"sample_{i}", use_container_width=True):
        selected_prompt = sample_prompts[i]

# Voice Input Section
voice_col1, voice_col2 = st.columns([1, 2])
with voice_col1:
    st.subheader("Voice agent", icon=":material/mic:")
    audio_record = st.audio_input("Record your question in English:")

# Process Voice Input
voice_query = None
if audio_record is not None:
    # Check if this audio has already been processed in session
    audio_bytes = audio_record.read()
    audio_hash = hash(audio_bytes)
    if st.session_state.get("last_processed_audio") != audio_hash:
        st.session_state.last_processed_audio = audio_hash
        with st.spinner("Listening & transcribing voice input..."):
            transcribed_text, trans_err = transcribe_audio_with_gemini(
                audio_bytes,
                mime_type=audio_record.type or "audio/wav",
                current_key=api_key
            )
            if trans_err:
                st.error(f"Voice Transcription Error: {trans_err}")
            elif transcribed_text:
                st.success(f"Heard: *\"{transcribed_text}\"*", icon=":material/record_voice_over:")
                voice_query = transcribed_text

# Text Chat Input
text_query = st.chat_input("Type your question about payroll data in English...")

# Determine active user input
active_input = selected_prompt or voice_query or text_query

# Render Conversation History
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"], avatar=":material/person:" if msg["role"] == "user" else ":material/smart_toy:"):
        st.markdown(msg["content"])

        # Display Code & Result if present
        if msg.get("code"):
            with st.expander("View pandas analysis code", icon=":material/code:"):
                st.code(msg["code"], language="python")

        if msg.get("data_result") is not None:
            res = msg["data_result"]
            if isinstance(res, pd.DataFrame):
                st.dataframe(res, use_container_width=True)
            elif isinstance(res, pd.Series):
                st.dataframe(res.to_frame(), use_container_width=True)

        if msg.get("chart") is not None:
            st.plotly_chart(msg["chart"], use_container_width=True)

        # Audio Output Player
        if msg.get("audio_bytes"):
            st.caption(":material/volume_up: Spoken answer:")
            st.audio(msg["audio_bytes"], format="audio/mp3")

# Handle New User Input
if active_input:
    # Append user question
    st.session_state.chat_history.append({
        "role": "user",
        "content": active_input
    })
    with st.chat_message("user", avatar=":material/person:"):
        st.markdown(active_input)

    # Generate Assistant Response
    with st.chat_message("assistant", avatar=":material/smart_toy:"):
        with st.spinner("Analyzing payroll data with Gemini..."):
            analysis = analyze_question_with_dataset(active_input, df, current_key=api_key)

            answer_text = analysis["answer"]
            st.markdown(answer_text)

            if analysis.get("code"):
                with st.expander("View pandas analysis code", icon=":material/code:"):
                    st.code(analysis["code"], language="python")

            if analysis.get("data_result") is not None:
                res = analysis["data_result"]
                if isinstance(res, pd.DataFrame):
                    st.dataframe(res, use_container_width=True)
                elif isinstance(res, pd.Series):
                    st.dataframe(res.to_frame(), use_container_width=True)

            if analysis.get("chart") is not None:
                st.plotly_chart(analysis["chart"], use_container_width=True, key=f'analysis_chart_{id(analysis["chart"])}')

            # Generate Speech Audio
            audio_bytes = None
            if analysis.get("is_relevant", False):
                with st.spinner("Generating voice audio..."):
                    audio_bytes = generate_tts_audio(answer_text)
                    if audio_bytes:
                        st.caption(":material/volume_up: Spoken answer:")
                        st.audio(audio_bytes, format="audio/mp3")

            # Store in session state
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": answer_text,
                "code": analysis.get("code"),
                "data_result": analysis.get("data_result"),
                "chart": analysis.get("chart"),
                "audio_bytes": audio_bytes
            })
