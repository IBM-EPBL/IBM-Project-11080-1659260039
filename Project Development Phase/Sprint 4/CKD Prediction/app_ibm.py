import requests
import flask
import numpy as np
import pandas as pd
from flask import Flask, request, render_template, url_for, session, redirect

from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

# NOTE: you must manually set API_KEY below using information retrieved from your IBM Cloud account.
API_KEY = "I1JHnBDQ7KxJ_pRHg948Nit3rjLLPZGz0bdhTKSTizAU"
token_response = requests.post('https://iam.cloud.ibm.com/identity/token', data={"apikey":
 API_KEY, "grant_type": 'urn:ibm:params:oauth:grant-type:apikey'})
mltoken = token_response.json()["access_token"]

header = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + mltoken}

app = flask.Flask(__name__,static_folder='')


@app.route('/')
def homePage():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html',name=session['username'])

@app.route('/prediction', methods=['POST','GET'])
def predictCKD():
    return render_template('predict.html')

@app.route('/predict', methods=['POST','GET'])
def predict():
    input_features = [float(x) for x in request.form.values()]
    features_name = ['blood_urea', 'blood_glucose_random', 'anemia', 'coronary_artery_disease','pus_cell','diabetes_mellitus','red_blood_cells','pedal_edema']
    payload_scoring = {"input_data": [{"fields": ['blood_urea', 'blood_glucose_random', 'anemia', 'coronary_artery_disease','pus_cell','diabetes_mellitus','red_blood_cells','pedal_edema'], "values": [input_features]}]}

    response_scoring = requests.post('https://us-south.ml.cloud.ibm.com/ml/v4/deployments/fcd0538f-628a-4e12-94af-b523e0495be5/predictions?version=2022-11-11', json=payload_scoring,
    headers={'Authorization': 'Bearer ' + mltoken})
    print("Scoring response")
    predictions=response_scoring.json()   
    print(predictions)      
    output = predictions['predictions'][0]['values'][0][0]
    if(output==0):
        text="Oops! You are detected with Chronic Kidney Disease."
    else:
        text="Hurray! You are not affected by Chronic Kidney Disease"
    return render_template('result.html',prediction_text=text)

#extra code
app.secret_key = '123'
 
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'user'
 
mysql = MySQL(app)
 
@app.route('/login', methods =['GET', 'POST'])
def login():
    msg = ''
    #if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
    username = request.form['username']
    password = request.form['password']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM accounts WHERE username = % s AND password = % s', (username, password, ))
    account = cursor.fetchone()
    if account:
        session['loggedin'] = True
        session['id'] = account['id']
        session['username'] = account['username']
        msg = 'Logged in successfully !'
        return render_template('dashboard.html', msg = msg, name=username)
    else:
        msg = 'Incorrect username / password !'
    return render_template('index.html', msg = msg)
 
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect('/')
 
@app.route('/register', methods =['GET', 'POST'])
def register():
    msg = ''
    #if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form :
    username = request.form['username']
    password = request.form['password']
    email = request.form['email']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM accounts WHERE username = % s', (username, ))
    account = cursor.fetchone()
    if account:
        msg = 'Username already exists !'
        return render_template('index.html', msg = msg)
    else:
        cursor.execute('INSERT INTO accounts VALUES (NULL, % s, % s, % s)', (username, password, email ))
        mysql.connection.commit()
        msg = 'You have successfully registered !'
        return render_template('dashboard.html', msg = msg, name=username)


if __name__ == '__main__':
    app.run(debug=True)
