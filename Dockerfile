FROM python:3.9

WORKDIR /code

# 依存パッケージのインストール
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# アプリケーションファイルをコピー
COPY ./app /code/app

# サーバ起動
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

