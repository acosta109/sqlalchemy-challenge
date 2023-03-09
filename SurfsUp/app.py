import pandas as pd
import datetime as dt

# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#Set up the database. 
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(autoload_with=engine)
measurement = Base.classes.measurement
station = Base.classes.station


#Flask set up
app = Flask(__name__)

@app.route("/")
def welcome():
    """List all available api routes."""
    return(
        f"Available Routes:<br/>"
        f'Look at the precipitaion data for the past year: /api/v1.0/precipitation <br/>'
        f'Look at a list of the stations: /api/v1.0/stations <br/>'
        f'Look at the temperature for the past year: /api/v1.0/tobs <br/>'
        f'To find the min, max, and avg temperature from a certain date: /api/v1.0/YYYY-MM-DD <br/>'
        f'To find the min, max, and avg temperature between specific dates: /api/v1.0/YYYY-MM-DD/YYYY-MM-DD'
    )
@app.route('/api/v1.0/precipitation')
def precipitation():
    """Jsonify precipitation data for one year."""
    session = Session(engine)
    #Find the most recent date
    last_date = session.query(func.max(measurement.date)).scalar()
    # Calculate the date one year from the last date in data set.
    date_one_yr_ago_dt = dt.datetime.strptime(last_date, '%Y-%m-%d') - dt.timedelta(days=365)
    query_date = date_one_yr_ago_dt.strftime('%Y-%m-%d')
    # Perform a query to retrieve the date and precipitation scores
    last_year = session.query(measurement.date, measurement.prcp).\
            filter(measurement.date >= query_date).all()
    results = []
    for date, prcp in last_year:
        result_dict = {}
        result_dict["date"] = date
        result_dict["prcp"] = prcp
        results.append(result_dict)
    # Close Session
    session.close()
    # Return the results as a JSON dictionary
    return jsonify(results)

@app.route('/api/v1.0/stations')
def stations():
    """Jsonify a list of the stations"""
    session = Session(engine)
    results = session.query(station.station).all()
    session.close()

    station_list = [result[0] for result in results]
    station_dict = {i: station_list[i] for i in range(0, len(station_list))}

    return jsonify(station_dict)
    

@app.route('/api/v1.0/tobs')
def tobs():
    """Return the temperatures from the most active station. """
    session = Session(engine)
    #Find the dates to query
    latest_string = session.query(measurement.date).order_by(measurement.date.desc()).first()[0]
    latest_date_tob = dt.datetime.strptime(latest_string, '%Y-%m-%d')
    query_date_tob = dt.date(latest_date_tob.year -1, latest_date_tob.month, latest_date_tob.day)

    active_stations = session.query(measurement.station,func.count(measurement.id)).\
        group_by(measurement.station).\
        order_by(func.count(measurement.id).desc()).first()
    most_active = active_stations[0]
    #Set up query to get temperature
    query_result = session.query(measurement.date, measurement.tobs).\
        filter(measurement.date >= query_date_tob).\
        filter(measurement.station == most_active).all()
    session.close()

    temp_results = []

    for date, tobs in query_result:
        temp_dict = {}
        temp_dict["date"] = date
        temp_dict["tobs"] = tobs
        temp_results.append(temp_dict)
    return jsonify(temp_results)

@app.route('/api/v1.0/<start>')
def start(start):
    """Jsonify temperature data from a singular date."""
    session = Session(engine)
    #Temp dictionaries and results to jsonify
    start_date_temp_results = []
    start_date_temp_dict = {}
    #Find the max temperature
    max_temp = session.query(func.max(measurement.tobs)).\
        filter(measurement.date >= start).scalar()
    start_date_temp_dict['max temp'] = max_temp
    #Find the min temperature
    min_temp = session.query(func.min(measurement.tobs)).\
        filter(measurement.date >= start).scalar()
    start_date_temp_dict['min temp'] = min_temp
    #Find the avg temperature
    avg_temp = session.query(func.avg(measurement.tobs)).\
        filter(measurement.date >= start).scalar() 
    start_date_temp_dict['avg temp'] = avg_temp
    start_date_temp_results.append(start_date_temp_dict)

    return jsonify(start_date_temp_results)

@app.route('/api/v1.0/<start>/<end>')
def start_and_end(start, end):
    """Jsonify temperature data for a between two date."""
    session = Session(engine)
    #Temp dictionaries and results to jsonify
    start_date_end_date_temp_results = []
    start_date_end_date_temp_dict = {}
    #Find the max temperature
    max_temp = session.query(func.max(measurement.tobs)).\
        filter(measurement.date >= start).\
         filter(measurement.date <= end).scalar()
    start_date_end_date_temp_dict['max temp'] = max_temp
    #Find the min temperature
    min_temp = session.query(func.min(measurement.tobs)).\
        filter(measurement.date >= start).\
         filter(measurement.date <= end).scalar()
    start_date_end_date_temp_dict['min temp'] = min_temp
    #Find the avg temperature
    avg_temp = session.query(func.avg(measurement.tobs)).\
        filter(measurement.date >= start).\
         filter(measurement.date <= end).scalar()
    start_date_end_date_temp_dict['avg temp'] = avg_temp

    start_date_end_date_temp_results.append(start_date_end_date_temp_dict)
    return jsonify(start_date_end_date_temp_results)

if __name__ == "__main__":
    app.run(debug=True)