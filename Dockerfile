# Pull base image
FROM python:3.11.2

# Set environment varibles
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /code

# Copy project
COPY . /code/

# Install dependencies
RUN apt-get update -y
RUN apt-get upgrade -y

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN rm -rf /code/main/migrations/*.*

# Create superuser
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
COPY telegram_bot.sh /telegram_bot.sh
RUN chmod +x /telegram_bot.sh
ENTRYPOINT ["/entrypoint.sh", "/telegram_bot.sh"]
