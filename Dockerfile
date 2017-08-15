# Dockerfile for the TuCluster main server
FROM python:3.6

RUN mkdir -p /tucluster

# Create a user
RUN adduser --disabled-password --gecos '' wwwuser

# Copy the requirements file so we can install deps. in the container
COPY requirements_dev.txt /tucluster/
COPY requirements.txt /tucluster/

# Install any needed packages specified in requirements.txt
RUN pip install -r /tucluster/requirements_dev.txt


# Set the working directory to /app
WORKDIR /tucluster

# Make port 80 available to the world outside this container
EXPOSE 8000

# Run app.py when the container launches
CMD ["gunicorn", "--reload", "-w", "4", "-b", ":8000", "tucluster.app"]


