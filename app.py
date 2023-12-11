# app.py
import glob
import os
from openai_api import information_extraction
import streamlit as st
import tempfile

from collections import deque

from tafrigh.cli import farrigh, Config


st.markdown("""
<style>
        p, div, input, label {
        unicode-bidi:bidi-override;
        direction: RTL;
        text-align: right;
        }
</style>
    """, unsafe_allow_html=True)

# Streamlit app title and description
st.markdown("# تطبيق عطاي")
st.markdown("#### هذا التطبيق يساعدك على تفريغ المقاطع الصوتية وتلخيص النصوص")



# Function to transcribe video from YouTube URL
def transcribe_video(urls):
    min_words_per_segment = 1
    wit_api_key = "ZGIVS4TB3GBUKWAQ5GHHDRMBJTCRCB77"
    max_cutting_duration = 15
    language = "ar"
    # Setup directories.
    output_dir = "output"
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    # Start Tafrigh.
    if wit_api_key:
        print("جارٍ تحويل المواد إلى نصوص باستخدام تقنيات wit.ai.")
    else:
        print("جارٍ تحويل المواد إلى نصوص باستخدام نماذج Whisper.")

    config = Config(
        urls_or_paths=list(map(str.strip, urls.split(" ")))
        if len(urls.strip())
        else ["."],
        skip_if_output_exist=False,
        playlist_items="",
        verbose=False,
        model_name_or_path="",
        task="transcribe",
        language=language,
        use_faster_whisper=True,
        beam_size=5,
        ct2_compute_type="default",
        wit_client_access_tokens=[wit_api_key],
        max_cutting_duration=max_cutting_duration,
        min_words_per_segment=min_words_per_segment,
        save_files_before_compact=False,
        save_yt_dlp_responses=False,
        output_sample=0,
        output_formats=["txt", "srt"],
        output_dir=output_dir,
    )

    deque(farrigh(config), maxlen=0)

    # Download all txt and srt files.

    txt_files = glob.glob(f"{output_dir}/*.txt")
    srt_files = glob.glob(f"{output_dir}/*.srt")
    audio_files = glob.glob(f"{output_dir}/*.wav")
    # st.text(f"تجد الملفات تحت هذا المكان \n {output_dir}")
    try:
        txt_files.remove("output/archive.txt")
    except ValueError:
        pass
    # Display audio files
    for audio_file in audio_files:
        audio_file_bytes = open(audio_file, "rb")
        st.audio(audio_file_bytes)
    # Download transcription file
    if txt_files:
        file_name = txt_files[0]
        with open(file_name, "r") as f:
            file_contents = f.read()
        st.download_button(
            label="تحميل نص التفريغ",
            data=file_contents,
            file_name=file_name,
            mime='text/txt',
        )
    # st.text(transcribed_text)


def summarize_text(input_text):
    
    try:
        prompt = f"لخص لي هذا النص الآتي:\n\n{input_text}\n\nقدم ملخصًا موجزًا من جملة إلى ثلاث جمل، مع تسليط الضوء على النقاط الرئيسية."

        response = information_extraction(prompt)
        st.markdown(response)
        # with st.expander("إقرأ التلخيص"):
        #     st.code(response)
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")


# Video transcription section
st.markdown("### التفريغ")
col1, col2 = st.columns(2)
with col1:
    urls = st.text_input("أدخل رابط المقطع على يوتيوب:")
with col2:
    audio_file = st.file_uploader(
        label="تحميل ملف الصوت",
        type=["mp4", "mp3", "wav"],
    )
if st.button("فرِّغ", type="primary"):
    progress_text_transcribe = st.markdown("**تفريغ :hourglass_flowing_sand:**")
    if urls:
        transcribe_video(urls)
    elif audio_file:
        with col2:
            st.audio(audio_file, format='audio/wav')
            temp_dir = tempfile.mkdtemp()
            audio_file_path = os.path.join(temp_dir, audio_file.name)
            with open(audio_file_path, "wb") as f:
                f.write(audio_file.getbuffer())
            transcribe_video(str(audio_file_path))
    progress_text_transcribe.empty()
# Display a stylish horizontal line using HTML and CSS
st.markdown(
    """
    <div style="width: 75%; margin: 20px auto;height: 2px; background-color: #ff4c4b;"></div>
    """
    , unsafe_allow_html=True
)
# Text summarization section
st.markdown("### تلخيص النص")
col3, col4 = st.columns(2)
with col3:
    text_input = st.text_area("أدخل النص هنا:", height=270)
with col4:
    text_file = st.file_uploader(
        label="تحميل ملف وورد",
        type=["txt", "docx"],
    )
if st.button("لخِّص", type="primary"):
    progress_text_summary = st.markdown("**تلخيص النص :hourglass_flowing_sand:**")
    if text_input:
        summarize_text(text_input)
    elif text_file:
        summarize_text(text_file.read().decode('utf-8'))
    progress_text_summary.empty()
