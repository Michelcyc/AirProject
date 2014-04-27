#Git: 

#!flask/bin/python
from flask import Flask , jsonify, abort, make_response, request, url_for
import datetime
import os
import pymongo
from pymongo import MongoClient

#Setting addresses of the DB
#Remote
dbIp = os.environ['DB_PORT_27017_TCP_ADDR']
dbPort = os.environ['DB_PORT_27017_TCP_PORT']
#Local
#dbIp = 'localhost'
#dbPort = 27017

client = MongoClient(dbIp,dbPort)
db = client.FplDB
dbFpls = db.fplCollection                #dbFpls is the collection that will handle all the plans

#Setting database variables


#-----------------------------
app = Flask(__name__)

#Creating memory array
globalAirport = ''
airportList = []
airport = [{}]
airportDictionary = {'dublinAirport': airport }
airportList.append(airportDictionary)

#Getting all airports flight plans
@app.route('/', methods = ['GET'])
def get_airports_flight_plans():
    return jsonify( { 'flightPlans': airportList } )

#Creating a airport
@app.route('/', methods = ['POST'])
def create_airport():
    new_airport = { request.json['airportName']: [{}] } 
    airportList.append(new_airport)
    return jsonify( { 'airport': new_airport } ), 201

#Getting all flight plans from a specific airport
@app.route('/<airportName>/', methods = ['GET'])
def get_flight_plans(airportName):
    expectedAirport = searchAirport(airportList, airportName)
    return jsonify( { airportName: expectedAirport } )

#Finding airport in a list
def searchAirport(airportList, airportName):
    for item in airportList:
        if item.get(airportName):
            return item[airportName]

#Finding flightplan in a list
def searchFlightPlan(fplList, fplId):
    for item in fplList:
        if item.get('id')==fplId:
            return item;

#Posting a Flight Plan
@app.route('/<airportName>/', methods = ['POST'])
def create_plans(airportName):
    if not request.json: #handle errors
        abort(400)
    expectedAirport = searchAirport(airportList, airportName);
    #here two lines of code just to get the {} off of the new airports, because now will be some content there
    if expectedAirport[0]=={}:
      expectedAirport.remove({})
    #
    flightPlan = {
        #'id': len(expectedAirport) + 1,             //Sincronize part
        'id': request.json['id'],
        'aircraft': request.json['aircraft'],
        'origin': request.json['origin'],
        'destination': request.json['destination'],
        'departure': request.json.get('departure'),
        'route': request.json.get('route')
    }
    expectedAirport.append(flightPlan)          #Adding in the list
    #MONGODB
    post = dbFpls.insert(flightPlan)                   #Adding in the MongoDB
    ##
    #return jsonify( { 'flightPlan': flightPlan } ), 201
    #return JSONEncoder().encode( { 'flightPlan': flightPlan } )
    return jsonify( { 'result': 'true' } )

  
#Getting a specific Flight Plan
@app.route('/<airportName>/<int:fpl_id>/', methods = ['GET'])
def get_fpl(airportName,fpl_id):
    expectedAirport = searchAirport(airportList, airportName)
    flightPlan = searchFlightPlan(expectedAirport,fpl_id)
    return jsonify( { 'flightPlan': flightPlan } )

#Changing a flightPlan
@app.route('/<airportName>/<int:fpl_id>/', methods = ['PUT'])
def update_fpl(airportName,fpl_id):
    expectedAirport = searchAirport(airportList, airportName);
    flightPlan = searchFlightPlan(expectedAirport,fpl_id);
    if not request.json:
        abort(400)
    if 'aircraft' in request.json and type(request.json['aircraft']) != unicode:
        abort(400)
    if 'departure' in request.json and type(request.json['departure']) is not unicode:
        abort(400)
    if 'origin' in request.json and type(request.json['origin']) is not unicode:
        abort(400)
    if 'destination' in request.json and type(request.json['destination']) is not unicode:
        abort(400)
    if 'route' in request.json and type(request.json['route']) is not unicode:
        abort(400)

    flightPlan['aircraft'] = request.json.get('aircraft', flightPlan['aircraft'])
    flightPlan['origin'] = request.json.get('origin', flightPlan['origin'])
    flightPlan['destination'] = request.json.get('destination', flightPlan['destination'])
    flightPlan['departure'] = request.json.get('departure', flightPlan['departure'])
    flightPlan['route'] = request.json.get('route', flightPlan['route'])
    return jsonify( { 'flightPlan': flightPlan } )

#Deleting a Flight Plan
@app.route('/<airportName>/<int:fpl_id>/', methods = ['DELETE'])
def delete_fpl(airportName,fpl_id):
    expectedAirport = searchAirport(airportList, airportName)
    flightPlan = searchFlightPlan(expectedAirport,fpl_id)
    expectedAirport.remove(flightPlan)
    if (len(expectedAirport)==0):
        expectedAirport.append({})
    return jsonify( { 'result': True } )

@app.route('/<airportName>/', methods = ['DELETE'])
def delete_airport(airportName):
    y = len(airportList)
    for x in range(0,y):
      if airportList[x].get(airportName):
        airportList.pop(x)
        fail = False
        break
      else:
        fail = True
    if ( (y==0) or (fail) ):
        return jsonify( { 'result': False } )
    else:
        return jsonify( { 'result': True } )
  
#Handling error returning JSON
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify( { 'error': 'Not found' } ), 404)

if __name__ == '__main__':
    app.run(debug = True)