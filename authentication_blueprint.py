from fcntl import DN_DELETE
from logging.config import valid_ident
from flask import Blueprint, render_template, request, url_for, redirect, session
import re 
from datetime import datetime

regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'

from conn_database import connect_db
db = connect_db()

cursor = db.cursor() 

auth_bp=Blueprint("authentication_blueprint", __name__, static_folder="static", template_folder="templates")


@auth_bp.route('/register', methods =['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST':
        surname = request.form['surname']
        other_name = request.form['othernames']
        #address = request.form['address']
        email = request.form['email']
        password = request.form['password']

        gender = request.form['gender']
        phone = request.form['phone']
        class_id = request.form['class']
        dob = request.form['dob']
        now = str(datetime.now())
        

        
        cursor = db.cursor()
        cursor.execute(f"SELECT * FROM student_tb WHERE email = '{email}'  OR password = '{password}' ")
        record = cursor.fetchone()

        if record:
            msg = 'Email or password already registered try again!'
        elif not re.fullmatch(regex, email):
            msg = 'Invalid email address !'
        elif not surname or not other_name or not email or not password:
            msg = 'Please fill out the * form fields !'
        else:
            cursor.execute(f"INSERT INTO student_tb (phone, surname, other_names, gender, date_of_birth, email, password, class, date_reg) VALUES ('{phone}', '{surname}', '{other_name}', '{gender}', '{dob}', '{email}', '{password}', '{class_id}', '{now}')")
            db.commit()
            msg = 'You have successfully registered !'



        cursor = db.cursor()
        cursor.execute('SELECT * FROM class_tb')
        class_rec = cursor.fetchall()     

        return render_template('register.html', msg = msg, class_rec=class_rec)

    else:
        cursor = db.cursor()
        cursor.execute('SELECT * FROM class_tb')
        class_rec = cursor.fetchall()  

        return render_template('register.html', class_rec=class_rec)





@auth_bp.route('/teacher_register', methods =['GET', 'POST'])
def teacher_register():
    msg = ''
    if request.method == 'POST':
        surname = request.form['surname']
        other_name = request.form['othernames']
        #address = request.form['address']
        email = request.form['email']
        password = request.form['password']

        gender = request.form['gender']
        phone = request.form['phone']
        subject_id = request.form['class_subject']
        dob = request.form['dob']
        now = str(datetime.now())

        #-------------- 
        cursor = db.cursor()

        cursor.execute('SELECT class_id  FROM subjects_tb WHERE subject_id = "'+subject_id+'"')  
        row = cursor.fetchone() 
        class_id = row[0]

        cursor.execute(f"SELECT * FROM teacher_tb WHERE email = '{email}'  OR password = '{password}' ")
        record = cursor.fetchone()

        if record:
            msg = 'Email or password already registered try again!'
        elif not re.fullmatch(regex, email):
            msg = 'Invalid email address !'
        elif not surname or not other_name or not email or not password:
            msg = 'Please fill out the * form fields !'
        else:
            cursor.execute(f"INSERT INTO teacher_tb (phone, surname, other_names, gender, date_of_birth, email, password, subject, date_reg, class_id) VALUES ('{phone}', '{surname}', '{other_name}', '{gender}', '{dob}', '{email}', '{password}', '{subject_id}', '{now}', '{class_id}')")
            db.commit()
            msg = 'You have successfully registered teacher !'


        cursor = db.cursor()
        
        cursor.execute('SELECT * FROM subjects_tb')
        data_subject = cursor.fetchall()

        cursor.execute('SELECT * FROM class_tb ORDER BY class_name')
        data_class = cursor.fetchall()

        return render_template('teacher_register.html', msg = msg, data_class=data_class, data_subject=data_subject)        
      
       
    else:
        cursor = db.cursor()
        
        cursor.execute('SELECT * FROM subjects_tb')
        data_subject = cursor.fetchall()

        cursor.execute('SELECT * FROM class_tb ORDER BY class_name')
        data_class = cursor.fetchall()

        return render_template('teacher_register.html', data_class=data_class, data_subject=data_subject)        
      

@auth_bp.route('/login', methods =['GET', 'POST'])
def login():
    msg = ''
    
    if request.method == 'POST':
        login_id = request.form['username']
        password = request.form['password']
        login_as = request.form['login_as']

        cursor = db.cursor() 

        #email means user is student
        if re.fullmatch(regex, login_id ):
            if login_as=='student':
                cursor.execute(f"SELECT * FROM student_tb WHERE email = '{login_id}' AND password = '{password}' ")
            elif login_as=='teacher': 
                cursor.execute(f"SELECT * FROM teacher_tb WHERE email = '{login_id}' AND password = '{password}' ")   
        else:
            cursor.execute(f"SELECT * FROM accounts WHERE username = '{login_id}' AND password = '{password}' ")

        
        record = cursor.fetchone()
        if record:
            session['loggedin'] = True
            session['id'] = record[0]   
            
            #check if login id is email
            if re.fullmatch(regex, login_id):

                if login_as=='student':                   
                    session['level'] = "student"
                    session['class'] = record[7]

                     #get class name
                    cursor.execute('SELECT class_name  FROM class_tb WHERE id = "'+record[7]+'"')  
                    row = cursor.fetchone() 
                    session['class_name'] = row[0]

                elif login_as=='teacher':     
                    session['level'] = "teacher"
                    session['subject'] = record[7]
                    session['class'] = record[8]

                    #get subject name
                    cursor.execute('SELECT subject_name  FROM subjects_tb WHERE subject_id = "'+record[7]+'"')  
                    row = cursor.fetchone() 
                    session['subject_name'] = row[0]

                    #get class name
                    cursor.execute('SELECT class_name  FROM class_tb WHERE id = "'+record[8]+'"')  
                    row = cursor.fetchone() 
                    session['class_name'] = row[0]


                session['login_sname'] = record[1]
                session['login_oname'] = record[2]
                session['login_gender'] = record[3]
                session['login_dob'] = record[4]
                session['login_phone'] = record[6]
                
                session['login_id'] = record[5] #student email
               
            else:
              #user is an admin
                session['level'] = "admin"
                session['login_sname'] = record[1] #username
                
            
            #redirect to success login URL 
            return redirect(url_for('auth'))
        else:
          msg = 'Invalid credentials'
          return render_template('login.html', msg = msg)
    else:
      return render_template('login.html')


@auth_bp.route('/change_pw', methods =['GET', 'POST'])
def change_pw():  

    if request.method == 'POST':
        old_password = request.form['old_password']
        new_password = request.form['new_password']
        confirm_new_password = request.form['confirm_new_password']
        user_cat = request.form['user_cat']

        if user_cat == "Student":
            #
            cursor.execute(f"SELECT password FROM student_tb WHERE password = '{old_password}' ")

        elif user_cat == "Teacher": 
            #  
            cursor.execute(f"SELECT password FROM teacher_tb WHERE password = '{old_password}' ")   
        elif user_cat == "Admin": 
            # 
            cursor.execute(f"SELECT password FROM accounts WHERE password = '{old_password}' ") 

        row = cursor.fetchone()
        if row is None:
            return render_template('change_pw.html', msg='Error: Password not found!')
                   
        else:  

            if new_password != confirm_new_password:
                   
                return("Warning: New Password and Confirm New Password are not thesame!")
            else:    

                #validate before updating   
                if user_cat=="Admin":
                    cursor.execute(f"SELECT * FROM accounts WHERE password='{new_password}' ") 
                    row = cursor.fetchone()
                    if row is None: 
                        cursor.execute(f'UPDATE accounts SET password="{new_password}" WHERE password="{old_password}" ')
                        db.commit()
                        return render_template('change_pw.html', msg='Admin Password changed')
                       
                    else:  

                        return render_template('change_pw.html', msg='Error: New passord you tried to use is already existing!')
                                       

                elif user_cat=="Student":
                    cursor.execute(f'SELECT * FROM student_tb WHERE password="{new_password}" ') 
                    row = cursor.fetchone()
                    if row is None: 
                        cursor.execute(f'UPDATE student_tb SET password="{new_password}" WHERE password="{old_password}" ')
                        db.commit()
                        return render_template('change_pw.html', msg='Student Password changed')
                       
                        
                    else:  

                        return render_template('change_pw.html', msg='Error: New passord you tried to use is already existing!')
                        
    
                elif user_cat=="Teacher":
                    cursor.execute(f'SELECT * FROM teacher_tb WHERE password="{new_password}" ') 
                    row = cursor.fetchone()
                    if row is None: 
                        cursor.execute(f'UPDATE teacher_tb SET password="{new_password}" WHERE password="{old_password}" ')
                        db.commit()
                        return render_template('change_pw.html', msg='Teacher Password changed')
                        
                    else:  

                        return render_template('change_pw.html', msg='Error: New passord you tried to use is already existing!')
                       
                elif user_cat=="":
                     
                    return render_template('change_pw.html', msg='Error: Select a user category!')   


    return render_template('change_pw.html')    
      
@auth_bp.route('/logout')
def logout():
    msg = ''
    session.pop('loggedin', None)
    session.pop('login_id', None)
    session.pop('login_pw', None)
    session.pop('level', None)
    msg = 'You have logout now'
    #return redirect(url_for('login'))
    return render_template('login.html', msg = msg)