FROM python:3.10.12

ADD app.py .
COPY requirements.txt requirements.txt
COPY ./ ./

RUN pip3 install -r requirements.txt

ENTRYPOINT [ "streamlit", "run" ]
CMD [ "app.py", "--server.headless", "true", "--server.fileWatcherType", "none", "--browser.gatherUsageStats", "false"]
