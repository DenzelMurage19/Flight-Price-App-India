from flask import Flask  
from flask import request
import requests
from flask import render_template
from flask_cors import cross_origin
import sklearn
import pickle
import os
import pandas as pd



app = Flask(__name__)  # initializes the flask application
model_path = os.path.join('model', 'c1_flight_xgb.pkl')
with open(model_path, 'rb') as file:
    model = pickle.load(file)  # loading the pre-trained ML model

API_KEY = '422653b5ebc261f39d9d9427'
BASE_URL = 'https://v6.exchangerate-api.com/v6/422653b5ebc261f39d9d9427/latest/INR'

@app.route("/")  # Flask route decorator for mapping a specific URL (/) to the function home. URL is the root of the web app
@cross_origin()  # allows cross_origin requests. server can respond to requests from different origins (e.g. diff domains)
def home():
    return render_template(r"home.html")  # Use raw string to avoid escape issues

@app.route("/predict", methods=['GET', 'POST'])  # Another URL that handles POST (Submit data) and GET (fetch data and render pages) requests. it will handle user inputs (features).
@cross_origin()
def predict():
    if request.method == "POST":
        # Date_of_journey
        date_dep = request.form['Dep_Time']  # Retrieves form data sent by user Dep_time field in form where user provides date and time for trip
        journey_day = int(pd.to_datetime(date_dep, format="%Y-%m-%dT%H:%M").day)
        journey_month = int(pd.to_datetime(date_dep, format="%Y-%m-%dT%H:%M").month)

        # Departure
        dep_hour = int(pd.to_datetime(date_dep, format='%Y-%m-%dT%H:%M').hour)
        dep_min = int(pd.to_datetime(date_dep, format="%Y-%m-%dT%H:%M").minute)

        # Arrival
        date_arr = request.form["Arrival_Time"]
        arrival_hour = int(pd.to_datetime(date_arr, format="%Y-%m-%dT%H:%M").hour)
        arrival_min = int(pd.to_datetime(date_arr, format="%Y-%m-%dT%H:%M").minute)

        # Duration
        Duration_hour = abs(arrival_hour - dep_hour)
        Duration_mins = abs(arrival_min - dep_min)

        # Total Stops
        Total_Stops = int(request.form["stops"])

        airline = request.form['airline']
        # Airline encoding
        Airline_AirIndia = Airline_GoAir = Airline_IndiGo = Airline_JetAirways = 0
        Airline_MultipleCarriers = Airline_SpiceJet = Airline_Vistara = Airline_Other = 0

        if airline == 'Jet Airways':
            Airline_JetAirways = 1
        elif airline == 'IndiGo':
            Airline_IndiGo = 1
        elif airline == 'Air India':
            Airline_AirIndia = 1
        elif airline == 'Multiple carriers':
            Airline_MultipleCarriers = 1
        elif airline == 'SpiceJet':
            Airline_SpiceJet = 1
        elif airline == 'Vistara':
            Airline_Vistara = 1
        elif airline == 'GoAir':
            Airline_GoAir = 1
        else:
            Airline_Other = 1

        Source = request.form["Source"]
        Source_Delhi = Source_Kolkata = Source_Mumbai = Source_Chennai = 0
        if Source == 'Delhi':
            Source_Delhi = 1
        elif Source == 'Kolkata':
            Source_Kolkata = 1
        elif Source == 'Mumbai':
            Source_Mumbai = 1
        elif Source == 'Chennai':
            Source_Chennai = 1

        # Destination
        Destination_Cochin = Destination_Delhi = Destination_Hyderabad = Destination_Kolkata = 0
        Source = request.form['Destination']
        if Source == 'Cochin':
            Destination_Cochin = 1
        elif Source == 'Delhi':
            Destination_Delhi = 1
        elif Source == 'Hyderabad':
            Destination_Hyderabad = 1
        elif Source == 'Kolkata':
            Destination_Kolkata = 1

        prediction=model.predict([[
            Total_Stops,
            journey_day,
            journey_month,
            dep_hour,
            dep_min,
            arrival_hour,
            arrival_min,
            Duration_hour,
            Duration_mins,
            Airline_AirIndia,
            Airline_GoAir,
            Airline_IndiGo,
            Airline_JetAirways,
            Airline_MultipleCarriers,
            Airline_Other,
            Airline_SpiceJet,
            Airline_Vistara,
            Source_Chennai,
            Source_Kolkata,
            Source_Mumbai,
            Source_Delhi,
            Destination_Cochin,
            Destination_Delhi,
            Destination_Hyderabad,
            Destination_Kolkata,
        ]])

        output = round(prediction[0],2)

        #currency coversion
        selected_currency = request.form['currency']
        converted_price = output
    
        if selected_currency != 'INR':
             try:
                response = requests.get(BASE_URL)
            
                # Check if the request was successful
                if response.status_code == 200:
                    data = response.json()
                
                    # Retrieve the exchange rate for the selected currency
                    rates = data['conversion_rates']  # Dictionary of rates with keys as currency codes
                    if selected_currency in rates:
                        exchange_rate = rates[selected_currency]
                        converted_price = round(output * exchange_rate, 2)
                    else:
                        print(f"Error: Currency {selected_currency} not found in the response data.")

                else:
                    print(f"Error: {response.status_code} - {response.text}")

             except requests.exceptions.RequestException as e:
                    print(f"Request error: {e}")
             except Exception as e:
                print(f"An unexpected error occurred: {e}")

        return render_template(r"home.html", prediction_text= f"Your Flight Price is {converted_price:.2f} {selected_currency}.")
    return render_template(r"home.html")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

