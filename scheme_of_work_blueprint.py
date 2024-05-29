from flask import Blueprint, render_template, request, url_for, redirect, session
import re 
from datetime import datetime
import os

from werkzeug.utils import secure_filename

from conn_database import connect_db
db = connect_db()



cursor = db.cursor() 

scheme_of_work_blueprint=Blueprint("scheme_of_work_blueprint", __name__, static_folder="static", template_folder="templates")


@scheme_of_work_blueprint.route('/scheme', methods =['GET']) 
def scheme():

    

    if 'loggedin' in session and session['level']=="admin":
       
        cursor.execute('SELECT * FROM class_tb ORDER BY class_name')
        data_class = cursor.fetchall()

        cursor.execute('SELECT class_id FROM lesson_td WHERE term="1"')
        data_topic1 = cursor.fetchall()

        cursor.execute('SELECT class_id FROM lesson_td WHERE term="2"')
        data_topic2 = cursor.fetchall()

        cursor.execute('SELECT class_id FROM lesson_td WHERE term="3"')
        data_topic3 = cursor.fetchall()

    elif 'loggedin' in session and session['level']=="teacher":
        teacher_subject = session['subject']
        teacher_class = session['class']

        cursor.execute(f'SELECT class_id FROM lesson_td WHERE term="1" AND subject="{teacher_subject}" AND class_id="{teacher_class}" ')
        data_topic1 = cursor.fetchall()

        cursor.execute(f'SELECT class_id FROM lesson_td WHERE term="2" AND subject="{teacher_subject}" AND class_id="{teacher_class}" ')
        data_topic2 = cursor.fetchall()

        cursor.execute(f'SELECT class_id FROM lesson_td WHERE term="3" AND subject="{teacher_subject}" AND class_id="{teacher_class}" ')
        data_topic3 = cursor.fetchall()

        cursor.execute(f'SELECT * FROM class_tb  WHERE id={teacher_class} ORDER BY class_name' )
        data_class = cursor.fetchall()

    elif 'loggedin' in session and session['level']=="student":
       
        class_id = session['class']

        cursor.execute(f'SELECT class_id FROM lesson_td WHERE term="1" AND class_id="{class_id}" ')
        data_topic1 = cursor.fetchall()

        cursor.execute(f'SELECT class_id FROM lesson_td WHERE term="2" AND class_id="{class_id}" ')
        data_topic2 = cursor.fetchall()

        cursor.execute(f'SELECT class_id FROM lesson_td WHERE term="3" AND class_id="{class_id}" ')
        data_topic3 = cursor.fetchall()

        cursor.execute(f'SELECT * FROM class_tb  WHERE id={class_id} ORDER BY class_name' )
        data_class = cursor.fetchall()    
    
    else:
        return redirect(url_for('auth')) 

    return render_template('scheme.html', data_topic3= data_topic3, data_topic2=data_topic2, data_class=data_class, data_topic1=data_topic1)   




@scheme_of_work_blueprint.route('/detail', methods=['GET', 'POST']) 
def detail():
  
    if 'loggedin' in session:

        if request.method == 'POST': 

            class_id = request.form['class_id'] 
            term = request.form['term'] 
      
        elif request.method == 'GET': 
            args = request.args
            class_id = args.get('class_id')
            term = args.get('term')
       
       #---------------------------
        if term == "1":
            term_name = "1st Term"
        elif term == "2": 
            term_name = "2nd Term"
        elif term == "3":     
            term_name = "3rd Term"


        if session['level']=="admin":
            cursor.execute(f'SELECT class_name  FROM class_tb WHERE id = {class_id}')  
            row = cursor.fetchone() 
            class_name = row[0]

            cursor.execute(f'SELECT * FROM lesson_td WHERE class_id={class_id} AND term={term} ORDER BY week')
            data_lesson = cursor.fetchall()

            cursor.execute('SELECT * FROM subjects_tb')
            data_subject = cursor.fetchall()

            cursor.execute('SELECT lesson_id FROM lesson_assignment')
            data_assignment = cursor.fetchall()

            cursor.execute('SELECT lesson_id,  teacher_score, expected_score FROM assignment_submission')
            data_submission = cursor.fetchall()

        elif session['level']=="teacher":
            teacher_subject = session['subject']
            teacher_class = session['class']

            cursor.execute(f'SELECT class_name  FROM class_tb WHERE id = "{teacher_class}" ')  
            row = cursor.fetchone() 
            class_name = row[0]

            cursor.execute(f'SELECT * FROM lesson_td WHERE class_id="{teacher_class}" AND subject="{teacher_subject}" AND term="{term}" ORDER BY week')
            data_lesson = cursor.fetchall()

            cursor.execute(f'SELECT * FROM subjects_tb WHERE subject_id="{teacher_subject}" ')
            data_subject = cursor.fetchall()

            cursor.execute('SELECT lesson_id FROM lesson_assignment')
            data_assignment = cursor.fetchall()

            cursor.execute('SELECT lesson_id,  teacher_score, expected_score FROM assignment_submission')
            data_submission = cursor.fetchall()


        elif session['level']=="student":
           
            class_id = session['class']
            student_id = session['id']

            cursor.execute(f'SELECT class_name  FROM class_tb WHERE id = "{class_id}" ')  
            row = cursor.fetchone() 
            class_name = row[0]

            cursor.execute(f'SELECT * FROM lesson_td WHERE class_id="{class_id}" AND term="{term}" ORDER BY week')
            data_lesson = cursor.fetchall()

            cursor.execute(f'SELECT * FROM subjects_tb WHERE class_id ="{class_id}" ')
            data_subject = cursor.fetchall()

            cursor.execute('SELECT lesson_id FROM lesson_assignment')
            data_assignment = cursor.fetchall()

            cursor.execute('SELECT lesson_id,  teacher_score, expected_score FROM assignment_submission WHERE user_id="{student_id}" AND user_type="student" ')
            data_submission = cursor.fetchall() 

        else:
            return redirect(url_for('auth'))       

        return render_template('scheme_detail.html', data_submission=data_submission, data_assignment=data_assignment, data_lesson=data_lesson, class_name=class_name, data_subject=data_subject, term_name=term_name)   



        #return redirect(url_for('auth')) 
    else:
      return redirect(url_for('login')) 





@scheme_of_work_blueprint.route('/learn', methods=['GET', 'POST']) 
def learn():
  
    if 'loggedin' in session:

        if request.method == 'POST': 

            class_id = request.form['class_id'] 
            lesson_id = request.form['lesson_id'] 
            subject_id = request.form['subject_id']
            term_name = request.form['term_name'] 

           

            cursor.execute(f'SELECT class_name  FROM class_tb WHERE id = {class_id}')  
            row1 = cursor.fetchone() 
            class_name = row1[0]

            cursor.execute(f'SELECT * FROM lesson_td WHERE lesson_id ={lesson_id}')
            row2 = cursor.fetchone()
            lesson_id = row2[0]
            lesson_title = row2[1]
            lesson_detail = row2[2]
            week = row2[6]
            term_id = row2[5]

            cursor.execute(f'SELECT subject_name FROM subjects_tb WHERE subject_id ={subject_id}')
            row3 = cursor.fetchone()
            subject_name = row3[0]


            cursor.execute(f'SELECT * FROM lesson_upload_td WHERE lesson_id = {lesson_id} ') 
            data_media = cursor.fetchall()


            cursor.execute(f'SELECT * FROM lesson_assignment WHERE lesson_id = {lesson_id} ') 
            data_assignment = cursor.fetchall()
            
            user_id = session['id']   
            user_type = session['level']   
            cursor.execute(f'SELECT * FROM assignment_submission WHERE lesson_id = {lesson_id} AND user_type = "{user_type}" AND user_id = "{user_id}" ')
            data_submission = cursor.fetchall()

          
            return render_template('scheme_learn.html', data_submission=data_submission, lesson_id=lesson_id, data_assignment=data_assignment, data_media=data_media, term_id=term_id, class_id=class_id, term_name=term_name, class_name=class_name, lesson_title=lesson_title, lesson_detail=lesson_detail, subject_name=subject_name, week=week)   



        return redirect(url_for('auth')) 

    return redirect(url_for('login')) 




