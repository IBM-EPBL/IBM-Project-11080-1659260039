import flask
import numpy as np
import pandas as pd
from flask import Flask, request, render_template, url_for, session, redirect
import pickle
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

app = flask.Flask(__name__,static_folder='')
model = pickle.load(open('./CKD.pkl','rb'))

@app.route('/')
def homePage():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html',name=session['username'])

@app.route('/prediction', methods=['POST','GET'])
def predictCKD():
    return render_template('predict.html')
'''
@app.route('/home', methods=['POST'])
def home():
    return render_template('index.html')
'''

@app.route('/predict', methods=['POST','GET'])
def predict():
    input_features = [float(x) for x in request.form.values()]
    features_value = [np.array(input_features)]
    features_name = ['blood_urea', 'blood_glucose_random', 'anemia', 'coronary_artery_disease','pus_cell','diabetes_mellitus','red_blood_cells','pedal_edema']
    df = pd.DataFrame(features_value, columns=features_name)
    output = model.predict(df)
    if(output==0):
        text="Oops! You are detected with Chronic Kidney Disease."
    else:
        text="Hurray! You are not affected by Chronic Kidney Disease"
    return render_template('result.html',prediction_text=text)

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


"""
elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers !'
        elif not username or not password or not email:
            msg = 'Please fill out the form !' 
elif request.method == 'POST':
        msg = 'Please fill out the form !' """