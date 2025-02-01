FROM python:3.10-slim
WORKDIR /app

# Install the application dependencies
COPY ./requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy in the source code
COPY . /app

EXPOSE 8000

CMD ["python", "bot.py"]