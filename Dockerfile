FROM python:3-slim

# Additional dependencies required to support Snappy compression:
RUN apt-get update && apt-get install -y --no-install-recommends \
        libsnappy-dev \
        g++ \
        git \
	&& rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/access

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN pip install .

CMD crawldb


