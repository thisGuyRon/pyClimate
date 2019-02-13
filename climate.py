#-------------------------------------------------------
#import packages
#-------------------------------------------------------
from flask import Flask, jsonify
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, and_
import datetime as dt
#-------------------------------------------------------
#Database setup
#-------------------------------------------------------
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station
# Create our session (link) from Python to the DB
session = Session(engine)
app=Flask(__name__)


@app.route("/")
def home():
    "Home Page opening"
    return (
        #Loading all pages for Flask with instructions where necessary
        f"Home page for Hawaii temperature lookup<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"</br>"
        f"/api/v1.0/<start><br/>"
        f"(add start date ex: 2015-01-01, YYYY-MM-YY)<br/>"
        f"</br>"
        f"/api/v1.0/<start><end><br/>"
        f"(add start/end date, ex: /api/v1.0/2015-01-01/2016-01-01)"
    )

@app.route("/api/v1.0/precipitation")
def precip():
    "Loading participation dataset"
    #loads entire list of participation in json format
    precip = session.query(Measurement.date, Measurement.prcp).all()
    precip_list=[]
    for precip in precip:
        precip_dict={}
        precip_dict["date"]=precip.date
        precip_dict["precipitation"]=precip.prcp
        precip_list.append(precip_dict)

    return jsonify(precip_list)

@app.route("/api/v1.0/stations")
def station():
    "Loading station dataset"
    #loads all station data in json format
    stations = session.query(Station.station, Station.name).all()
    stations_list=[]
    for station in stations:
        precip_dict={}
        precip_dict["serial number"]=station.station
        precip_dict["name"]=station.name
        stations_list.append(precip_dict)
    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    "Loading temperature dataset"
    #loads temperature for the last year in json format
    last_date=str(session.query(Measurement.date).order_by(Measurement.date.desc()).first())
    last_date2=dt.datetime.strptime(last_date, "('%Y-%m-%d',)") - dt.timedelta(days=365)
    tobs_all=session.query(Measurement.date, Measurement.tobs).filter(Measurement.date>last_date2).all()
    tobs_list=[]
    for tobs in tobs_all:
        tobs_dict={}
        tobs_dict["date"]=tobs.date
        tobs_dict["Temperature"]=tobs.tobs
        tobs_list.append(tobs_dict)
    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def start(start):
    "Loading temperature dataset from a specific day"
    #loads all days from a specific date up to present date(latest date)
    start_tobs=session.query(Measurement.date,func.min(Measurement.tobs).label("MinTemp"),\
         func.avg(Measurement.tobs).label("TempAvg"), func.max(Measurement.tobs).label("MaxTemp")\
             ).filter(Measurement.date>=start).group_by(Measurement.date).all()
    tobs_date_list=[]
    for tobs in start_tobs:
        tobs_date_dict={}
        tobs_date_dict["date"]=tobs.date
        tobs_date_dict["min"]=tobs.MinTemp
        tobs_date_dict["avg"]=tobs.TempAvg
        tobs_date_dict["max"]=tobs.MaxTemp
        tobs_date_list.append(tobs_date_dict)
    return jsonify(tobs_date_list)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    "Loading dataset for a date range"
    #loads temperature for a specific range of dates
    se_tobs=session.query(\
        Measurement.date\
        ,func.min(Measurement.tobs).label("MinTemp")\
        ,func.avg(Measurement.tobs).label("TempAvg")\
        , func.max(Measurement.tobs).label("MaxTemp"))\
        .filter(and_(Measurement.date>=start, Measurement.date<=end))\
        .group_by(Measurement.date).all()

    se_tobs_list=[]
    for tobs in se_tobs:
        se_tobs_dict={}
        se_tobs_dict["date"]=tobs.date
        se_tobs_dict["min"]=tobs.MinTemp
        se_tobs_dict["avg"]=tobs.TempAvg
        se_tobs_dict["max"]=tobs.MaxTemp
        se_tobs_list.append(se_tobs_dict)
    return jsonify(se_tobs_list)

if __name__=="__main__":
    app.run(debug=True)