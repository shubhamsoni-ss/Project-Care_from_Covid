# Importing necessary modules
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import os
import mysql.connector
import pymysql
from SDIndex import SOCIALDISTANCINGINDEX
from flask_mail import Mail, Message
from check_symptoms import symptomsChecker
import smtplib
from collections import Counter

# Initializing flask
app=Flask(__name__)

# Configurations to be include into the program if you are using mysql.connector for database handling instead of pymysql
''' app.secret_key = 'major_project_2020'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '12345'
app.config['MYSQL_DB'] = 'major_project_2020'

mysql = MySQL(app)'''

# Setting up email configurations
app.config.update(dict(
            MAIL_SERVER = 'smtp.googlemail.com',
            MAIL_PORT = 465,
            MAIL_USE_TLS = False,
            MAIL_USE_SSL = True,
            MAIL_USERNAME = 'your gmail account address',
            MAIL_PASSWORD = 'your gmail account password'
            ))

mail = Mail(app)

# Adding upload folder path i.e. the path where the program will look to store the output video (change it according to you computer's filesystem)
app.config['UPLOAD_FOLDER']='C:/Users/lenovo/OneDrive/Desktop/care_from_covid/uploadedvideos'

# Function to return the covid infection status of logged-in user
def checkCovidStatus():
    try:
        if('id' in session):
            conn = pymysql.connect('localhost','root','12345','major_project_2020')
            cur = conn.cursor()
            cur.execute('select * from user where user_id = "%s"'%(session['id']))
            account = cur.fetchone()
            conn.commit()
            conn.close()
            return account[8]
    except Exception as ex:
        return render_template('not.html', msg = ex)
    
# Function to update the covid infection status of logged-in user into the database
def updateCovidStatus(status):
    try:
        if('id' in session):
            conn = pymysql.connect('localhost','root','12345','major_project_2020')
            cur = conn.cursor()
            n = cur.execute('update user set covid_status = "%s" where user_id = "%s"'%(status,session['id']))
            conn.commit()
            conn.close()
    except Exception as ex:
        return render_template('not.html', msg = ex)

# Function to return details of the disease from the database which has been predicted by the symptoms checker
def getDiseaseData(disease):
    try:
        if('id' in session):
            conn = pymysql.connect('localhost','root','12345','major_project_2020')
            cur = conn.cursor()
            n = cur.execute('select * from diseasedatabase where disease = "%s"'%(disease))
            if(n):
                data = cur.fetchone()
            conn.commit()
            conn.close()
            return data[1],data[2]
    except Exception as ex:
        return render_template('not.html', msg = ex)

# Function to send email alert using the database records to all those persons who have visited the same place at same date and approximately same time where the covid infected person visited
def traceContacts():
    try:
        conn = pymysql.connect('localhost','root','12345','major_project_2020')
        cur = conn.cursor()
        n = cur.execute('select country,state,city,landmark,year(date),month(date),day(date),hour(time),minute(time),second(time) from contacttracing where user_id = "%s"'%(session['id']))
        conn.commit()
        if(n):
            user_details = cur.fetchall()
            details = list(user_details)
            country = []
            state = []
            city = []
            landmark = []
            year = []
            month = []
            day = []
            hour = []
            minute = []
            second = []
            for i in details:
                country.append(i[0])
                state.append(i[1])
                city.append(i[2])
                landmark.append(i[3])
                year.append(i[4])
                month.append(i[5])
                day.append(i[6])
                hour.append(i[7])
                minute.append(i[8])
                second.append(i[9])
            n1 = cur.execute('select user_id,country,state,city,landmark,year(date),month(date),day(date),hour(time),minute(time),second(time) from contacttracing where user_id != "%s"'%(session['id']))
            conn.commit()
            all_details = cur.fetchall()
            alldetails = list(all_details)
            result = []
            for i in alldetails:
                if(i[1] in country and i[2] in state and i[3] in city and i[4] in landmark and i[5] in year and i[6] in month and i[7] in day and i[8] in hour):
                    result.append(i)
            if(len(result)!=0):
                for i in result:
                    msgg = Message('Contact Tracing Result', sender='your email address', recipients=[i[0]])
                    msgg.html = '<b>Take precautions, someone of your recent contacts may be tested covid positive </b>'+'<br><br><b>Visited country: </b><br>'+i[1]+'<br><br><b>Visited state: </b><br>'+i[2]+'<br><br><b>Visited city: </b><br>'+i[3]+'<br><br><b>Visited landmark: </b><br>'+i[4]+'<br><br><b>Visited date: </b><br>'+str(i[5])+'-'+str(i[6])+'-'+str(i[7])
                    mail.send(msgg)
            '''dt = []
            for i in user_details:
                dt.append(i[5])
            a = cur.execute('select * from contacttracing where date in ({0});'.format(dt))
            conn.commit()
            b = cur.fetchall()
            '''
            # msg = result
            conn.close()
            # return msg
    except Exception as ex:
        return render_template("not.html",msg = ex)

# Creating an app route for home or index page
@app.route('/')
def homepage():
    msg = '' 
    msg1 = ''
    msg2 = ''
    if(checkCovidStatus() == "positive"):
        msg1 = "Be cautious!, you may be at a risk of covid infection"
    elif(checkCovidStatus() == "negative"):
        msg2 = "Hurray!, you are not at a risk of covid infection"
    return render_template('index.html',msg = msg, msg1 = msg1, msg2 = msg2)

# Creating an app route for signup page
@app.route('/signup', methods=['POST','GET'])
def signup():
    return render_template("signup.html")

# Creating an app route for login page
@app.route('/contact_us', methods=['POST','GET'])
def contact_us():
    return render_template("contact_us.html")

# Creating an app route for healthrecord page
@app.route('/healthrecord', methods=['POST','GET'])
def healthrecord():
    msg = ''
    try:
        conn = pymysql.connect('localhost','root','12345','major_project_2020')
        cur = conn.cursor()
        n = cur.execute('select * from healthrecord where user_id="%s"'%(session['id']))
        conn.commit()
        if(n):
            data = cur.fetchall()
            total = len(data)
            data = list(data)
            alltime_disease = []
            alltime_symps = []
            for i in data:
                alltime_disease.append(i[2])
                alltime_symps.extend(i[1].split(','))
            #set_dis = set(alltime_disease)
            #set_symps = set(alltime_symps)
            count_diseases = Counter(alltime_disease)
            count_symps = Counter(alltime_symps)
            scount_diseases = dict(sorted(count_diseases.items(),key = lambda x: x[1],reverse = True))
            scount_symps = dict(sorted(count_symps.items(),key = lambda x: x[1],reverse = True))
            '''alltime_disease = i[2]
                alltime_symps = i[1]'''
            return render_template("healthrecord.html",data = data,total = total,count_diseases = scount_diseases,count_symps = scount_symps)
        else:
            msg = "You don't have any health record yet"
            return render_template("symptoms_checker.html",msg = msg)
        conn.close()
    except Exception  as ex:
        return render_template("not.html",msg = ex)

# Creating an app route for symptoms checker page
@app.route('/symptoms_checker', methods=['POST','GET'])
def symptoms_checker():
    msg = '___'
    msg1 = '___'
    msg2 = '___'
    msg3 = '___'
    msg4 = '___'
    symp = []
    try:
        if('id' in session):
            if request.method == 'POST' and 'symptoms' in request.form:
                symp = request.form.getlist('symptoms')
                symptoms_list = ','.join(map(str,symp))
                disease, accuracy = symptomsChecker(symp)
                conn = pymysql.connect('localhost','root','12345','major_project_2020')
                cur = conn.cursor()
                n = cur.execute('INSERT INTO healthrecord(user_id,symptoms,predicted_disease) VALUES(% s, % s, % s)',(session['id'],symptoms_list,disease))
                #msg = n
                conn.commit()
                conn.close()
                if(disease == "Severe Covid Infection"):
                    updateCovidStatus("positive")
                    traceContacts()
                    ret = 1
                else:
                    updateCovidStatus("negative")
                    #traceContacts()
                    ret = 0
                details = getDiseaseData(disease)
                msgg = Message('Your Symptoms Checker Result', sender='your email address', recipients=[session['id']])
                if(ret == 1):
                    #msgg.html = '<b> DISEASE: </b>'+disease+'<br><b>PRECAUTIONS:</b><br>'+details[1]
                    msgg.html = '<b>DISEASE NAME: </b>'+disease+'<br><br><b>PRECAUTIONS: </b><br>'+details[1]
                else:
                    msgg.html = '<b>DISEASE NAME: </b>'+disease+'<br><br><b>PRECAUTIONS: </b><br>'+details[1]
                mail.send(msgg)
                return render_template("symptoms_checker.html",msg1 = disease, msg2 = accuracy*100,msg = "yes",msg3 = details[0],msg4 = details[1])
            elif(request.method == 'POST'):
                return render_template("symptoms_checker.html",msg = "Please, fill out the form") 
            else:
                 return render_template("symptoms_checker.html",msg = msg,msg1 = msg1,msg2 = msg2,msg3 = msg3,msg4 = msg4)
        else:
            return render_template("dologin.html",msg = "Please, login to continue")
    except Exception as ex:
            return render_template("symptoms_checker.html",msg=ex)  

# Creating an app route for social distancing index calculator page
@app.route('/socialdistancingindex', methods=['POST','GET'])
def socialdistancingindex():
    if('id' in session):
        return render_template("socialdistancingindex.html")
    else:
        return render_template("dologin.html",msg = "Please, login to continue")

# Creating an app route for uploader page
@app.route('/uploader', methods = [ 'GET','POST'])
def upload_file():
   if request.method == 'POST':
      f = request.files['file']
      try:
        f.save(os.path.join(app.root_path,app.config['UPLOAD_FOLDER'],secure_filename(f.filename)))
        greenSDI, redSDI, orangeSDI, Greenline, Redline, Totalline,totalframe=SOCIALDISTANCINGINDEX()
        return render_template('uploaded.html',GreenSocialDistancingIndex=greenSDI,RedSocialDistancingIndex=redSDI,OrangeSocialDistancingIndex=orangeSDI, max=30, labels=totalframe, redvalues=Redline, greenvalues=Greenline, totalvalues=Totalline)
      except FileNotFoundError:
        return render_template("not.html",msg = "file not found")   

# Creating an app route for contactus page
@app.route('/contactus', methods=['POST','GET'])
def contactus():
    msg = ''
    msg1 = ''
    msg2 = ''
    try:
        if request.method == 'POST' and 'username' in request.form and 'email' in request.form and 'message' in request.form :
            username = request.form['username'] 
            email = request.form['email'] 
            message = request.form['message']
            conn = pymysql.connect('localhost','root','12345','major_project_2020')
            cur = conn.cursor()
            n =  cur.execute('INSERT INTO contact_us VALUES (% s, % s, % s)',(username,email,message))
            conn.commit()
            if(n!=0):
                    msg2 = "Feedback sent successfully"
                    return render_template('contact_us.html', msg2 = msg2)
            else:
                msg1 = "Unable to send your feedback"
                return render_template('contact_us.html', msg1 = msg1)
            conn.close()
        elif request.method == 'POST': 
            msg = 'Please fill out the form !'
            return render_template('contact_us.html', msg = msg)
    except Exception as ex:
            return render_template("contact_us.html",msg = ex)

# Creating an app route to perform signup functionality
@app.route('/register', methods =['GET', 'POST']) 
def register(): 
    msg = '' 
    try:
        if request.method == 'POST' and 'fullname' in request.form and 'password' in request.form and 'email' in request.form and 'phone' in request.form and 'gender' in request.form and 'state' in request.form and 'countrya' in request.form and 'district' in request.form: 
            username = request.form['fullname'] 
            password = request.form['password'] 
            email = request.form['email']
            phone = request.form['phone']
            #phone = int(phone)
            gender = request.form['gender']
            country = request.form['state'] 
            state = request.form['countrya'] 
            city = request.form['district'] 
            conn = pymysql.connect('localhost','root','12345','major_project_2020')
            cur = conn.cursor()
            cur.execute('select * from user where user_id = "%s" and mobile_number = "%s"'%(email,phone))
            account = cur.fetchone()
            if account:
                msg = 'Account already exists !'
                return render_template('signup.html', msg = msg)
            else:
                status = "negative"
                n =  cur.execute('INSERT INTO user VALUES (% s, % s, % s, % s, % s, % s, % s, % s, % s)',(email,username,password,phone,gender,country,state,city,status))
                conn.commit()
                if(n!=0):
                    msg = "You have successfully registered"
                    return render_template('dologin.html', msg = msg)
                else:
                    msg = "You are not successfully registered"
                    return render_template('signup.html', msg = msg)
                conn.close()
        elif request.method == 'POST': 
            msg = 'Please fill out the form !'
            return render_template('signup.html', msg = msg)
    except Exception as ex:
        return render_template('signup.html', msg = ex)

# Creating an app route to perform contact tracing functionality
@app.route('/contacttracing', methods =['GET', 'POST']) 
def contacttracing(): 
    msg = '' 
    msg1 = ''
    msg2 = ''
    try:
        if('id' in session):
            if request.method == 'POST' and 'country' in request.form and 'state' in request.form and 'city' in request.form and 'landmark' in request.form and 'date' in request.form and 'time' in request.form:  
                country = request.form['country'] 
                state = request.form['state'] 
                city = request.form['city'] 
                landmark = request.form['landmark']
                date = request.form['date']
                time = request.form['time']
                conn = pymysql.connect('localhost','root','12345','major_project_2020')
                cur = conn.cursor()
                #cur.execute('select * from user where user_id = "%s"'%(email))
                #account = cur.fetchone()
            #if account:
                n =  cur.execute('INSERT INTO contacttracing VALUES (% s, % s, % s, % s, % s, % s, % s)', (session['id'],country,state,city,landmark,date,time))
                if(n!=0):
                    msg = "Data stored successfully"
                else:
                    msg = "Failed to store the data"
                conn.commit()
                conn.close()
            elif request.method == 'POST': 
                msg = 'Please fill out the form !'
            if(checkCovidStatus() == "positive"):
                msg1 = "Be cautious, you are at a risk of covid infection"
            elif(checkCovidStatus() == "negative"):
                msg2 = "Hurray!, currently you are not at a risk of covid infection"
            return render_template('contacttracing.html', msg = msg, msg1 = msg1, msg2 = msg2) 
        else:
            return render_template('dologin.html', msg = "Please, login to continue")
    except Exception as ex:
        return render_template('not.html', msg = ex)

# Creating an app route to perform login functionality
@app.route('/dologin', methods =['GET', 'POST']) 
def dologin(): 
    msg = '' 
    msg1 = ''
    msg2 = ''
    if('id' not in session):
        if request.method == 'POST' and 'email' in request.form and 'password' in request.form: 
            userid = request.form['email'] 
            password = request.form['password'] 
            conn = pymysql.connect("localhost","root","12345","major_project_2020")
            cur = conn.cursor()
            cur.execute('SELECT * FROM user WHERE user_id = % s AND password = % s',(userid, password)) 
            conn.commit()
            account = cur.fetchone() 
            if account: 
                session['loggedin'] = True
                session['id'] = account[0] 
                session['username'] = account[1] 
                msg = 'Logged in successfully !'
                if(checkCovidStatus() == "positive"):
                    msg1 = "Be cautious!, you may be at a risk of covid infection"
                    msgg = Message('Your COVID Status', sender='your email address', recipients=[session['id']])
                    msgg.body = 'Be cautious!, you have a risk of covid infection. Consult to your doctor immediately'
                    mail.send(msgg)
                else:
                    msg2 = "Hurray!, you are not at a risk of covid infection"
                return render_template('index.html', msg = msg, msg1 = msg1 ,msg2 = msg2) 
            else: 
                msg = 'Incorrect username / password !'
        return render_template('dologin.html', msg = msg)
    else:
        if(checkCovidStatus() == "positive"):
            msg1 = "Be cautious!, you may be at a risk of covid infection"
        elif(checkCovidStatus() == "negative"):
            msg2 = "Hurray!, you are not at a risk of covid infection"
        return render_template('index.html', msg = session['username']+", You are already loggedin",msg1 = msg1,msg2 = msg2)

# Creating an app route to perform logout functionality
@app.route('/logout') 
def logout(): 
    if('id' in session):
        session.pop('loggedin', None) 
        session.pop('id', None) 
        session.pop('username', None) 
        #return redirect(url_for('dologin'))
        return render_template('dologin.html', msg = "Logged out")
    else:
        return render_template('dologin.html', msg = "Already logged out")

# Creating an app route to perform forgot password functionality
@app.route('/forgotpassword', methods =['GET', 'POST']) 
def forgotpassword(): 
    msg = '' 
    if request.method == 'POST' and 'email' in request.form and 'password1' in request.form and 'password2' in request.form: 
        email = request.form['email'] 
        password1 = request.form['password1'] 
        password2 = request.form['password2']
        conn = pymysql.connect("localhost","root","12345","major_project_2020")
        cur = conn.cursor()
        cur.execute('SELECT * FROM user WHERE user_id = % s',(email)) 
        account = cur.fetchone() 
        if account: 
            if(password1 == password2):
                cur.execute('UPDATE user SET password = %s where user_id = %s',(password2,email))
                return render_template('dologin.html', msg = "Password has reset successfully") 
            else:
                return render_template("forgotpassword.html", msg = "passwords are not matched")
        else: 
            msg = 'Incorrect email!'
            return render_template('forgotpassword.html', msg = msg)
    return render_template("forgotpassword.html")

# Running the Flask app    
if __name__=="__main__":
    app.debug=True
    app.run() 
