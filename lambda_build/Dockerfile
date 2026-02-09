FROM public.ecr.aws/lambda/python:3.11

WORKDIR /build

# Copiamos requirements
COPY requirements.txt .

# Instalamos dependencias en /build/python
RUN pip install --no-cache-dir -r requirements.txt -t python

# Copiamos el código de la app
COPY . .

# Limpiamos cosas innecesarias
RUN rm -rf lambda_build \
           docker-compose.yml \
           Dockerfile \
           __pycache__ \
           *.pyc

# Creamos el zip final
RUN zip -r /build/lambda.zip .
