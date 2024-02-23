FROM python:3.8
EXPOSE 8080
WORKDIR /app
COPY . ./
RUN pip install -r requirements.txt
ENTRYPOINT ["streamlit", "run", "app_main.py", "--server.port=8080", "--server.address=0.0.0.0", "--server.enableCORS=false", "--browser.gatherUsageStats=false"]