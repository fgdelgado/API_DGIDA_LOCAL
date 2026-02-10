FROM public.ecr.aws/lambda/python:3.11

WORKDIR /build

# Instalamos zip
RUN yum install -y zip && yum clean all

# Copiamos requirements
COPY app/requirements.txt requirements.txt

# INSTALAR DEPENDENCIAS EN LA RAÍZ
RUN pip install --no-cache-dir -r requirements.txt -t .

# Copiamos el código de la app
COPY app/ .

# Limpiamos cosas innecesarias
RUN rm -rf lambda_build \
           docker-compose.yml \
           Dockerfile \
           __pycache__ \
           *.pyc

# Creamos el zip final
RUN zip -r /build/lambda.zip .
