FROM python:3.12
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple
COPY . .
CMD ["/bin/bash","-c","./run.sh"]