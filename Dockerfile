FROM python:3.10-slim

# Install system deps
RUN apt-get update && apt-get install -y gcc g++

WORKDIR /app
COPY . .

# Install requirements
RUN pip install -r requirements.txt

# Download spacy models

RUN python -m spacy download xx_ent_wiki_sm

# Expose Hugging Face's default port
EXPOSE 7860

CMD ["python", "app.py"]