# set base image (host OS)
FROM python:3.8

# set the working directory in the container
WORKDIR /code

ADD air_polute.py .

# copy the dependencies file to the working directory
COPY requirements.txt .

# install dependencies
RUN pip install -r requirements.txt

# command to run on container start
CMD [ "python", "air_polute.py" ]





