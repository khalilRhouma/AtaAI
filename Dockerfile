# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# installing ffmpeg and yt-dlp dependencies
RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get install -y ffmpeg curl
RUN curl -L https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -o /usr/local/bin/yt-dlp
RUN chmod a+rx /usr/local/bin/yt-dlp
# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port that Streamlit will run on
EXPOSE 8501

# Run streamlit when the container launches
CMD ["streamlit", "run", "app.py"]
