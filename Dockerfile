#using lightweight python image
FROM python:3.13
#setting working directory inside the container
WORKDIR /app
#copying the requirements.txt and installing the dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create model directory inside the container
RUN mkdir -p model

# Copy the model file into the container's model directory
COPY c1_flight_xgb.pkl model/

#copy the rest of the program files
COPY . .


# expose port 5000 for the flask app
EXPOSE 5000

#run the python app
CMD ["python", "app.py"]