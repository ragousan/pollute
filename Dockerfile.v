# set base image (host OS)
FROM python:3.8

# set the working directory in the container
WORKDIR /app

ADD post_pollute.py .

# copy the dependencies file to the working directory
COPY requirements_flask.txt .

# install dependencies
RUN pip install -r requirements_flask.txt

# command to run on container start
CMD [ "python", "post_pollute.py" ]