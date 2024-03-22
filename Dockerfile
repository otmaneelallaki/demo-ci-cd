FROM public.ecr.aws/lambda/python:3.11

# Set the working directory in the container
WORKDIR /var/task

# Copy Lambda function code
COPY python_lambda_template/* ./

# Install dependencies
COPY pyproject.toml poetry.lock ./
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev

# Remove Poetry cache
RUN rm -rf /tmp/poetry_cache

# Command to run the Lambda function
CMD ["index.handler"]
