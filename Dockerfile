FROM python:3.9-slim

WORKDIR /app
COPY requirement.txt.
RUN pip install --no--cache--dir -r requirements.txt

COPY ..
EXPOSE 8501
HEALTHCHECK CMD curl--fail http://localhost:8501/
_stcore/health ||exist1

ENTRYPOINT ["streamlit", "run","app.py", "--server.port=8501", "--server.address=0.0.0.0"]