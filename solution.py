from datetime import datetime
from datetime import timedelta

import csv
import sys
import json

################################
# Peter Utekal
# Command line example => python3 solution.py example/example0.csv RFZ WIW
################################

# Arguments and global variables

csv_file = sys.argv[1]

origin = sys.argv[2]
destination = sys.argv[3]

final_response = []
dataset = []
   
# Function to turn date string to unix timestamp for easier travel time calculation

def stringDateToTimestamp(str):
    split = str.split('T')

    date = split[0]
    time = split[1]

    date_split = date.split('-')
    time_split = time.split(':')

    year = int(date_split[0])
    month = int(date_split[1])
    day = int(date_split[2])

    hour = int(time_split[0])
    minute = int(time_split[1])
    second = int(time_split[2])

    response = datetime(year, month, day, hour, minute, second)

    return datetime.timestamp(response)

# Function to build a response item

def buildArrayItem(rows):

    response = {
        "flights":[],
        "bags_allowed": 0,
        "bags_count": 0,
        "destination": '',
        "origin": '',
        "total_price": 0,
        "travel_time": ''
    }
    total_duration = 0
    total_price = 0

    if len(rows) > 1:

        for row in rows:
            response['flights'].append({
                "flight_no":row[0],
                "origin":row[1],
                "destination":row[2],
                "departure":row[3],
                "arrival":row[4],
                "base_price":row[5],
                "bag_price":row[6],
                "bags_allowed":row[7]
            })

            departure_timestamp = stringDateToTimestamp(row[3])
            arrival_timestamp = stringDateToTimestamp(row[4])

            duration = arrival_timestamp - departure_timestamp

            total_duration = total_duration + duration

            total_price = total_price + (int(float(row[5])) + int(row[6]))

        response['bags_allowed'] = 2
        response['bags_count'] = 1
        response['destination'] = destination
        response['origin'] = origin
        response['total_price'] = total_price
        response['travel_time'] = str(timedelta(seconds=total_duration))
    else:

        departure_timestamp = stringDateToTimestamp(rows[0][3])
        arrival_timestamp = stringDateToTimestamp(rows[0][4])

        duration = arrival_timestamp - departure_timestamp

        result = str(timedelta(seconds=duration))

        response = {
            "flights":[
                {
                    "flight_no":rows[0][0],
                    "origin":rows[0][1],
                    "destination":rows[0][2],
                    "departure":rows[0][3],
                    "arrival":rows[0][4],
                    "base_price":rows[0][5],
                    "bag_price":rows[0][6],
                    "bags_allowed":rows[0][7]
                }
            ],
            "bags_allowed": rows[0][7],
            "bags_count": 1,
            "destination": rows[0][2],
            "origin": rows[0][1],
            "total_price": int(float(rows[0][5])) + int(rows[0][6]),
            "travel_time": result
        }

    return response

# 1. Filter (straight flights without transit)

def filterStraightFlights():
    response = []

    for row in dataset:
        if row[1] == origin:
            if row[2] == destination:
                arr = []
                arr.append(row)
                arr_item = buildArrayItem(arr)
                final_response.append(arr_item)
            else:
                response.append(row)
        else: 
            continue
    
    return response

# 2. Filter (flights with transit)

def filterTransitFlights(flights):

    response = []

    for row in dataset:
        for flight in flights:
            if flight[2] == row[1]:
                if row[2] == destination:
                    # departure of row must be more than arrival of flights
                    departure_timestamp = stringDateToTimestamp(row[3])
                    arrival_timestamp = stringDateToTimestamp(flight[4])

                    if departure_timestamp > arrival_timestamp:
                        arr = []
                        arr.append(row)
                        arr.append(flight)
                        final_response.append(buildArrayItem(arr))

    return response

# Main CSV manipulation

with open(csv_file, mode = 'r') as file:
    csvFile = csv.reader(file)

    for row in csvFile:
        dataset.append(row)

    # 1. Filter dataset and get all straight flights (save to final_response)

    flights_to_filter = filterStraightFlights()

    # 2. Filter for transit flights (saving empty response to variable for (possibly) additional filters)

    transit_flights = filterTransitFlights(flights_to_filter)

    sorted_response = sorted(final_response, key=lambda k: k['total_price']) 

    print(json.dumps(sorted_response))