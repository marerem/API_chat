from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from . import models, schema, utils
from .database import engine, get_db
from .routers import post, user, auth, vote
from .config import setting
from fastapi import Form
from pydantic import BaseModel , EmailStr, conint
from fastapi.responses import JSONResponse
from typing import Dict
from fastapi import FastAPI, File, UploadFile, HTTPException
from typing import Dict
from io import BytesIO
from typing import Annotated
app = FastAPI()
templates = Jinja2Templates(directory="app/templates")  

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)

@app.get('/')
def root(request: Request):
    return templates.TemplateResponse("index.html",{"request": request})

@app.get('/signin')
def root(request: Request):
    return templates.TemplateResponse("lg.html", {"request": request})

@app.get('/create_user')
def root(request: Request):
    return templates.TemplateResponse("cr.html",{"request": request})

@app.get('/main')
def root(request: Request):
    return templates.TemplateResponse("main.html",{"request": request})

@app.get('/main/info')
def root(request: Request):
    return templates.TemplateResponse("info.html",{"request": request})

@app.get('/main/create_motor_model')
def root(request: Request):
    return templates.TemplateResponse("create_motor_model.html",{"request": request})


import flask
from flask import Flask, request, jsonify
from fastapi import Body, FastAPI, Response, status, HTTPException,Depends, APIRouter
import pandas as pd

import sys, os
import logging
from logging.handlers import TimedRotatingFileHandler
import configparser
import json
import socket
import influxdb_client
## Import time to handle time parsing functions
import time

## Importiere Lib zum Handeln von Unix Timestamps und Datumsfunktionen generell
import datetime

## Import copy for the creation and handling of DataFrame Dictionaries
import copy

## import HTTP request list
import requests
import urllib3

## import InfluxDB Client
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

### import PYMSSQL Client
#import pymssql

## Import pickle to save data_frames so that we don't have to rebuilt it all the time.
import pickle

## import PYMSSQL Client
#import pymssql

## Import glob for all the cvs files
import glob

## Import Path
from pathlib import Path
import numpy as np
import pandas as pd

import time


appp = Flask(__name__)


def split_data_by_id(data, test_percent,sim=None):
    if sim is not None:
        sim_df = data.dropna()
        #exclude sim signal
        data = pd.DataFrame(sim_df[~sim_df['id'].str.contains('Sim')])
        with_sim_df = pd.DataFrame(sim_df[sim_df['id'].str.contains('Sim')])

    unique_ids = data['id'].unique()
    np.random.shuffle(unique_ids)
    num_test_groups = int(test_percent*len(unique_ids))
    test_ids = unique_ids[:num_test_groups]

    train_data = []
    test_data = []

    for id in unique_ids:
        id_data = data[data['id'] == id]
        if id in test_ids:
            test_data.append(id_data)
        else:
            train_data.append(id_data)
    if sim is not None:
        train_data.append(with_sim_df)

    train_data = pd.concat(train_data, ignore_index=True)
    test_data = pd.concat(test_data, ignore_index=True)

    test_data.to_csv('test_data.csv', index=False)
    train_data.to_csv('train_data.csv', index=False)

# Function to process data and perform calculations
def process_data(df):
    #change column '_time' as datatime

    #time_columns = [col for col in df.columns if isinstance(col, str) and '_time' in col.lower()]
    print(df._time)
    
    # Assuming you have a list of column names called time_columns
    df['_time'] = pd.to_datetime(df['_time'],format='mixed')
    #df['_time'] = pd.to_datetime(df['_time'])
    m = df["_time"] - df["_time"].min()
    df["_time"] = pd.to_timedelta(m.astype(str)).dt.total_seconds()
      # Convert the column to datetime with 'coerce' option to handle invalid values
     
    print(df._time)


    # Automatically select columns with names containing 'value' and 'time'
    selected_columns = [col for col in df.columns if isinstance(col, str) and ('_value' in col.lower() or '_time' in col.lower())]
    selected_df = df[selected_columns]

    # Print the head of the selected DataFrame
    #print("\nHead of the selected DataFrame:")
    #print(selected_df.head())

    # Check if the user wants to calculate unique values for a specific column
    #calculate_unique = input("\nDo you want to calculate the size of unique values for a specific column? Always say : y  (y): ")

    #if calculate_unique.lower() == 'y':
    id_columns = [col for col in df.columns if isinstance(col, str) and 'id' in col.lower()]
    if id_columns:
        print("\nPotential columns with 'ID' in their name:")
        for idx, column in enumerate(id_columns, start=1):
            print(f"{idx}. {column}")

        column_name = 'Test Cycle ID'

        if column_name in id_columns:
            filter_value = '64ca'

            if filter_value:
                #filtered_values = df[~df[column_name].str.startswith(filter_value)][column_name].unique()
                filtered_values = df[~df[column_name].apply(lambda x: str(x).startswith(filter_value))][column_name].unique()

            else:
                filtered_values = df[column_name].unique()

            num_unique_values = len(filtered_values)
            #print(f"\nSize of unique values in '{column_name}': {num_unique_values}")
          #  else:
               # print("Invalid column name.")
       # else:
           # print("No columns with 'ID' in their name found.")
    #else:
            #print("Skipping unique value calculation.")
    #Check if the user wants to add the 'label' column

    # Check if the user wants to add the 'label' column
    #add_label = input("\nDo you want to add the 'label' column based on specific conditions? (y/n): ")

    #if add_label.lower() == 'y':
    selected_df['label'] = 0

    # condition of labels assigned
    dict_condition = {
    'Spike Start Time [ms]': ('==', 0),
    'Spike Torque [mNm]': ('<=', 148)
}

    conditions = []
    for col_name, (col_sign, col_threshold) in dict_condition.items():
        conditions.append(f"(df['{col_name}'].astype(float) {col_sign} {col_threshold})")

    condition_string = " & ".join(conditions)

    selected_df['label'] = np.where(eval(condition_string), 1, selected_df['label'])

    print("\nHead of the updated DataFrame:")
    print(selected_df.head())

    # Add unique IDs and calculate amounts for labels 1 and 0

    selected_df['id'] = df[column_name]
    print(selected_df)
    final_selected_df = selected_df[selected_df['id'].isin(filtered_values)]
    selected_df_one = final_selected_df[final_selected_df.label == 1]
    selected_df_zero = final_selected_df[final_selected_df.label == 0]
    print("\nCondition used for lablening",condition_string)
    print("\nAmount of label 1:", selected_df_one['id'].unique().size)
    print("Amount of label 0:", selected_df_zero['id'].unique().size)

    #else:
        #print("Exiting without adding 'label' column.")

    print("\nfinal_selected_df DataFrame:")
    print(final_selected_df)
    final_selected_df.to_csv('retrived_df.csv', index=False)
    split_data_by_id(final_selected_df, 0.2)

# Function to query data from InfluxDB
def query_influxdb():
    # ...
    # cread from influx DB
    ## Create the influx DB client - query_api and write_api
    ifx_org         = 'maxon'
    ifx_bucket      = 'backup_12092023'
    ifx_token       = 'ZgBSDkbY-EwSFrxL4n-Bg0sF7zHqHVwcQ9VxEmQDsjmd-K_6ZpavNdYlJyb01UM7ADcKngmjYwRirlF6yxQxHA=='
    ifx_url         = 'http://srvmint000072:8086'
    ifx_client      = InfluxDBClient(url=ifx_url, token=ifx_token, org=ifx_org)




    # -------- Init -------- //<editor-fold desc="Init">
    write_api = ifx_client.write_api(write_options=SYNCHRONOUS)
    query_api = ifx_client.query_api()
    delete_api = ifx_client.delete_api()


    tic = time.perf_counter()
    starting_cycle_id = "65004c50"  # Replace with the desired cycle ID

    # Modify the Flux query to filter data for cycles occurring after the starting cycle ID
    query = f'from(bucket: "{ifx_bucket}")' \
            f'|> range(start: 1970-01-01T00:00:00.000Z, stop: 1970-01-01T00:00:03.978Z)' \
            f'|> filter(fn: (r) => r._measurement == "B7E92AAEB086")' \
            f'|> filter(fn: (r) => r["Additional Test Config"] =~ /BlackBlock-MWM0[0-3][0-9]/)'  \
            f'|> filter(fn: (r) => r._field == "Act Current [mA]")' \





    result = query_api.query(query, org=ifx_org)
    print(result)
    toc = time.perf_counter()
    print(f"Time taken for querying the entire InfluxDB: {toc-tic:2f} s")
    datas = []
    for table in result:
        datas.append(table)

        # Create an empty dictionary to hold column names and records
    data = {}

    # Assuming you can access the column names and records using methods
    for flux_table in datas:

        # Sample data in FluxTable format (output from previous question)
        flux_table_columns = flux_table.columns

        flux_table_records = flux_table.records



        # Extract column names from flux_table_columns
        column_names = [column.label for column in flux_table_columns]

        # Iterate through the flux_table_records and extract data
        for record in flux_table_records:
            for key, value in record.values.items():
                if key not in data:
                    data[key] = []
                data[key].append(value)


    # Create a Pandas DataFrame
    df = pd.DataFrame(data)

    # Assuming you have the 'df' DataFrame from the query
    process_data(df)

# Function to read data from a CSV file and perform operations
def read_csv_and_process(file_content: bytes) -> pd.DataFrame:
    df = pd.read_csv(BytesIO(file_content))
    #file_path= input("\nFile path .csv format (exmaple : black_influxdb_data.csv ): ")
    #df = pd.read_csv(file_path)

    print(pd.DataFrame(df.head().iloc[:4,:10])) # for exmaple
    search_value = 'Additional Test Config'
    # Find the index of the row containing the value 'BlackBlockTest'
    start_index = df[df.apply(lambda row: search_value in row.values, axis=1)].index[0]
    # Switch column names to match the values in the start_index row
    df.columns = df.iloc[start_index]

    # Update the DataFrame to start from the found row and reset the index
    df = df.iloc[start_index+1:].reset_index(drop=True)

    df = pd.DataFrame(df)
    process_data(df)
    return True, df

@app.post("/process_csv")
async def create_file(file: Annotated[bytes, File(description="A file read as bytes")]):
    if not file:
        return {"message": "No file sent"}   
    else:
        #contents = await file.read()
        success, df = read_csv_and_process(file)
        return {"file_size": len(df)}

@app.get('/process_csv/model')
def root(request: Request):
    return templates.TemplateResponse("model_chose.html", {"request": request})
