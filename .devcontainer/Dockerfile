# For more information, please refer to https://aka.ms/vscode-docker-python
FROM mcr.microsoft.com/vscode/devcontainers/python:3.9
RUN pip install --upgrade pip
RUN pip install poetry
#RUN poetry install




# # Keeps Python from generating .pyc files in the container
# ENV PYTHONDONTWRITEBYTECODE=1

# # Turns off buffering for easier container logging
# ENV PYTHONUNBUFFERED=1

# # Install pip requirements
# #COPY requirements.txt .
# RUN poetry install

# WORKDIR /app
# COPY . /app

# # Creates a non-root user with an explicit UID and adds permission to access the /app folder
# # For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
# RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
# USER appuser

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
#CMD ["python", "validator903/validator.py"]
