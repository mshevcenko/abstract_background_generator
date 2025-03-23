FROM python:3.11-slim
RUN apt-get update && apt-get install -y \
    build-essential \
    libcairo2-dev \
    pkg-config \
    python3-dev \
    cmake \
 && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt


#ARG WFC_VERSION=wfc_cpp-0.1.0-cp311-cp311-linux_x86_64.whl
#COPY wfc_whls/$WFC_VERSION /app/wheelhouse/
#RUN pip install /app/wheelhouse/$WFC_VERSION
#RUN rm /app/wheelhouse/$WFC_VERSION

COPY . .

RUN pip install ./wfc_whls/wfc_cpp/
RUN rm -r ./wfc_whls

EXPOSE 8000
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
