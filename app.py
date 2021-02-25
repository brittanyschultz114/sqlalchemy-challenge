import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
station = Base.classes.station
measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)

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
        f"Hawaii Climate <br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation <br/>"
        f"/api/v1.0/stations <br/>"
        f"/api/v1.0/tobs <br/>"
        f"/api/v1.0/<start> <br/>"
        f"/api/v1.0/<start>/<end> <br/>"
        )

@app.route("/api/v1.0/precipitation")
def percipitation():
# Calculate the date one year from the last date in data set.
    one_year = dt.date(2017,8,23) - dt.timedelta(days=365)
    # Filter and order by measurement data
    year_data=session.query(measurement.date, measurement.prcp).\
        filter(measurement.date>= one_year ).\
        order_by(measurement.date.desc()).all()
    session.close()

    # Convert list of tuples into normal list
    precip_data = list(np.ravel(year_data))

    return jsonify(precip_data)


@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)

    """Return a list of all Stations"""
    results = session.query(station.station).\
                order_by(station.station).all()

    session.close()

    all_stations = list(np.ravel(results))
    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    lateststr = session.query(measurement.date).order_by(measurement.date.desc()).first()[0]
    latestdate = dt.datetime.strptime(lateststr, '%Y-%m-%d')
    querydate = dt.date(latestdate.year -1, latestdate.month, latestdate.day)
    sel = [measurement.date,measurement.tobs]
    queryresult = session.query(*sel).filter(measurement.date >= querydate).all()

    session.close()

    tobsall = []
    for date, tobs in queryresult:
        tobs_dict = {}
        tobs_dict["Date"] = date
        tobs_dict["Tobs"] = tobs
        tobsall.append(tobs_dict)

    return jsonify(tobsall)


@app.route('/api/v1.0/<start>')
def start(start):
    session = Session(engine)

    sel = [measurement.date, func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)]

    results =  (session.query(*sel)
                    .filter(func.strftime("%Y-%m-%d", measurement.date) >= start)
                    .group_by(measurement.date)
                    .all())

    session.close()

    dates = []                       
    for result in results:
        date_dict = {}
        date_dict["Date"] = result[0]
        date_dict["Low Temp"] = result[1]
        date_dict["Avg Temp"] = result[2]
        date_dict["High Temp"] = result[3]
        dates.append(date_dict)

    return jsonify(dates)


@app.route('/api/v1.0/<start>/<end>')
def startEnd(start, end):
    session = Session(engine)

    sel = [measurement.date, func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)]

    results =  (session.query(*sel)
                    .filter(func.strftime("%Y-%m-%d", measurement.date) >= start)
                    .filter(func.strftime("%Y-%m-%d", measurement.date) <= end)
                    .group_by(measurement.date)
                    .all())

    session.close()

    dates = []                       
    for result in results:
        date_dict = {}
        date_dict["Date"] = result[0]
        date_dict["Low Temp"] = result[1]
        date_dict["Avg Temp"] = result[2]
        date_dict["High Temp"] = result[3]
        dates.append(date_dict)

    return jsonify(dates)

if __name__ == '__main__':
    app.run(debug=True)