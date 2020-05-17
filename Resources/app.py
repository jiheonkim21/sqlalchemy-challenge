import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

last_date = dt.date(2017,8,23)
one_year_back = last_date - dt.timedelta(days=365)
one_year_back_formatted = one_year_back.strftime("%Y-%m-%d")
print(one_year_back)

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f'Available Routes:<br/><br/>'
        f'/api/v1.0/precipitation<br/><br/>'
        f'/api/v1.0/stations<br/><br/>'
        f'/api/v1.0/tobs<br/><br/>'
        f'/api/v1.0/start<br/><br/>'
        f'/api/v1.0/start/end'

    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of date and amounto of precipitation for the last 12 months"""
    # Query all stations
    results = session.query(Measurement.date, func.sum(Measurement.prcp)).\
            group_by(Measurement.date).\
            filter(Measurement.date>one_year_back).\
            order_by((Measurement.date).desc()).all()

    session.close()

    # Create a dictionary from the row data and append to a list of all_precipitation
    all_precipitation = []
    for date, prcp in results:
        precipitation_dict = {}
        precipitation_dict["date"] = date
        precipitation_dict["prcp"] = prcp
        all_precipitation.append(precipitation_dict)

    return jsonify(all_precipitation)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all station names"""
    # Query all stations
    results = session.query(Station.name).all()

    session.close()

    # Convert list of tuples into normal list
    all_names = list(np.ravel(results))

    return jsonify(all_names)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of date and temperature for the last 12 months for station USC00519281"""
    # Query all stations
    results = session.query(Measurement.date, Measurement.tobs).\
            filter(Measurement.station=="USC00519281").\
            filter(Measurement.date>one_year_back).all()

    session.close()

    # Convert list of tuples into normal list
    all_temps = list(np.ravel(results))

    return jsonify(all_temps)

@app.route("/api/v1.0/<start>")
def tobs_start(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of date and temperature for all dates past the start date for station USC00519281"""

    # Query all stations
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start).all()
    session.close()

    results_dict = {"Minimum Temp":results[0][0],"Average Temp":results[0][1],"Maximum Temp":results[0][2]}
    return jsonify(results_dict)

@app.route("/api/v1.0/<start>/<end>")
def tobs_startend(start, end):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of date and temperature for all dates between the start and end date for station USC00519281"""
    
    # Query all stations
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close

    results_dict = {"Minimum Temp":results[0][0],"Average Temp":results[0][1], "Maximum Temp":results[0][2]}
    return jsonify(results_dict)

if __name__ == '__main__':
    app.run(debug=True)
