from flask import Blueprint, render_template, request, url_for, redirect, session
import re 
from datetime import datetime
import os

from werkzeug.utils import secure_filename

from conn_database import connect_db
db = connect_db()



cursor = db.cursor() 

performance_blueprint=Blueprint("performance_blueprint", __name__, static_folder="static", template_folder="templates")


@performance_blueprint.route('/performance', methods =['GET']) 
def performance():

    
    args = request.args
    student_id = args.get('id')
    class_id = args.get('class_id')

    record_list = []

    if 'loggedin' in session:

        cursor.execute(f'SELECT surname, other_names FROM student_tb WHERE student_id="{student_id}" ') 
        rec_student = cursor.fetchone()

        #count_student = len(rec_student)  
        
        #student_fullname = ""

        if  len(rec_student) > 0:

            surname = rec_student[0]
            other_names = rec_student[1]
            student_fullname = f"{surname} {other_names}"
            

            if session['level']=="teacher":   
              teacher_subject = session['subject'] 
              #session['class'] 
              cursor.execute(f'SELECT * FROM lesson_td WHERE class_id="{class_id}" AND subject="{teacher_subject}" ') 
              rec_lesson = cursor.fetchall()
            else: 
              cursor.execute(f'SELECT * FROM lesson_td WHERE class_id="{class_id}" ') 
              rec_lesson = cursor.fetchall()

            
            for row in rec_lesson:

                  lesson_id = row[0]
                  lesson_title = row[1]
                  subject_id = row[3]
                  term = row[5]
                  week = row[6]

                  #get class name  
                  cursor.execute('SELECT class_name  FROM class_tb WHERE id = "'+class_id+'"')  
                  row1 = cursor.fetchone()
                  class_name = row1[0]

                  #get subject name  
                  cursor.execute('SELECT subject_name  FROM subjects_tb WHERE subject_id = "'+subject_id+'" AND class_id = "'+class_id+'"')  
                  row2 = cursor.fetchone()
                  subject_name = row2[0]

                  #get term name  
                  cursor.execute(f'SELECT term FROM terms_tb WHERE id="{term}" ')
                  term_rec = cursor.fetchone()
                  term_name = term_rec[0]

                  #get assignment detail 
                  cursor.execute(f'SELECT * FROM lesson_assignment WHERE lesson_id="{lesson_id}" ') 
                  rec_assignment = cursor.fetchall()


                  if len(rec_assignment) > 0: #has assigment

                            for row3 in rec_assignment:
                              assignment_id = row3[0]
                              assignment_lesson_id = row3[1]
                              assignment_title = row3[2]
                              max_score = row3[4]

                              cursor.execute(f'SELECT * FROM assignment_submission WHERE lesson_id="{assignment_lesson_id}" AND user_type="student" AND user_id="{student_id}" ') 
                              rec_submission = cursor.fetchall()

                              if len(rec_submission) > 0: # has done assigment
                                for row4 in rec_submission:
                                  submission_id = row4[0]
                                  expected_score = row4[1]
                                  teacher_score = row4[2]
                                  

                              else:    
                                submission_id='-'  
                                expected_score = max_score 
                                teacher_score='Not Done' 
                               
                              record_list.append([lesson_id, class_name, subject_name, lesson_title, term_name, week, assignment_id, assignment_title, submission_id, expected_score, teacher_score, student_id, class_id, subject_id])

        

        return render_template('performance.html', performance_record=record_list, student_fullname=student_fullname)     
        

    else:
        return redirect(url_for('login'))
    




@performance_blueprint.route('/performance_detail', methods=['GET']) 
def performance_detail():
  
    if 'loggedin' in session:

        args = request.args
        
        lesson_id = args.get('lesson_id')
        assignment_id = args.get('assignment_id')
        submission_id = args.get('submission_id')
        student_id = args.get('student_id')
        class_id = args.get('class_id')
        subject_id = args.get('subject_id')

        cursor.execute(f'SELECT surname, other_names FROM student_tb WHERE student_id="{student_id}" ') 
        rec_student = cursor.fetchone()
        surname = rec_student[0]
        other_names = rec_student[1]
        student_fullname = f"{surname} {other_names}"
        

        

        cursor.execute(f'SELECT * FROM lesson_td WHERE class_id="{class_id}" ') 
        rec_lesson = cursor.fetchall()


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

         #get term name  
        cursor.execute(f'SELECT term FROM terms_tb WHERE id="{term_id}" ')
        term_rec = cursor.fetchone()
        term_name = term_rec[0]

        cursor.execute(f'SELECT subject_name FROM subjects_tb WHERE subject_id ={subject_id}')
        row3 = cursor.fetchone()
        subject_name = row3[0]


        cursor.execute(f'SELECT * FROM lesson_upload_td WHERE lesson_id = {lesson_id} ') 
        data_media = cursor.fetchall()


        cursor.execute(f'SELECT * FROM lesson_assignment WHERE lesson_id = {lesson_id} ') 
        data_assignment = cursor.fetchall()
        
        user_id = student_id   
        user_type = "student"   
        cursor.execute(f'SELECT * FROM assignment_submission WHERE lesson_id = {lesson_id} AND user_type = "{user_type}" AND user_id = "{user_id}" ')
        data_submission = cursor.fetchall()

      
        return render_template('performance_detail.html', data_submission=data_submission, lesson_id=lesson_id, data_assignment=data_assignment, data_media=data_media, term_id=term_id, class_id=class_id, term_name=term_name, class_name=class_name, lesson_title=lesson_title, lesson_detail=lesson_detail, subject_name=subject_name, week=week, student_id=student_id, student_fullname=student_fullname)   


    else:

      return redirect(url_for('login'))    


