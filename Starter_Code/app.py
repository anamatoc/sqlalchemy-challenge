# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt
from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
measurement=Base.classes.measurement
station=Base.classes.station

# Create our session (link) from Python to the DB
session=Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    return (
        f'''
        <H1> Welcome to my Weather App!! </H1>
        Available Routes:<br/>
        /api/v1.0/precipitation<br/>
        /api/v1.0/stations<br/>
        /api/v1.0/tobs<br/>
        /api/v1.0/temp/start<br/>
        /api/v1.0/temp/start/end<br/>
''')

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    year=dt.date(2017,8,23)-dt.timedelta(days=365)
    data=session.query(measurement.date,measurement.prcp).filter(measurement.date>=year).all()
    
    session.close()
    
    #Convert list to Json
    total_precipitation = []
    for date, prcp in data:
        precipitation_dict = {}
        precipitation_dict[date] = prcp
        total_precipitation.append(precipitation_dict)
    return jsonify(total_precipitation)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    active_stations = session.query(measurement.station, func.count(measurement.station)).group_by(
        measurement.station).order_by(func.count(measurement.station).desc()).all()
    session.close()

    # Convert list to Json
    station_list = list(np.ravel(active_stations))
    return jsonify(station_list)

# Tobs
@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    date=session.query(func.max(measurement.date)).first()
    year=dt.date(2017,8,23)-dt.timedelta(days=365)
    results = data=session.query(measurement.tobs).filter(
        measurement.station=="USC00519281").filter(measurement.date>=year).all()
    # Close session
    session.close()

    # Convert to Json
    all_temp = []
    for tobs, date in results:
        tobs_dict = {}
        tobs_dict['date'] = date
        tobs_dict['tobs'] = tobs
        all_temp.append(tobs_dict)
    return jsonify(all_temp)

#Return Min, Max, Ave
@app.route("/api/v1.0/temp/start")
def start_temp(start):
    session = Session(engine)

    tempstart_result = session.query(func.min(
        measurement.tobs),func.max(measurement.tobs),
        func.avg(measurement.tobs)).\
        filter(measurement.date >= start).all()
    
    session.close()

    temp_start = []
    temp_start["Min_Temp"] = tempstart_result[0][0]
    temp_start["Avg_Temp"] = tempstart_result[0][1]
    temp_start["Max_Temp"] = tempstart_result[0][2]
    return jsonify(temp_start)


# Return min temp, average temp and the maxtemp
@app.route("/api/v1.0/temp/start/end")
def temp_start_end(start, end):
    #Link session
    session = Session(engine)

    results = session.query(func.min(
        measurement.tobs),func.max(measurement.tobs),
        func.avg(measurement.tobs)).\
        filter(measurement.date >= start).filter(
        measurement.date <= end).all()
    session.close()

    temp_sten = []
    temp_sten["Min_Temp"] = results[0][0]
    temp_sten["Avg_Temp"] = results[0][1]
    temp_sten["Max_Temp"] = results[0][2]
    return jsonify(results)


if __name__ == '__main__':
    app.run()
