FROM python
WORKDIR /app
COPY app/main.py /app
COPY app/requirements.txt /app
RUN pip install -r requirements.txt
CMD ["python", "main.py"]
