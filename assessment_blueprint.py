from flask import Blueprint, render_template, request, url_for, redirect, session
import re 
from datetime import datetime
import os

from werkzeug.utils import secure_filename

from conn_database import connect_db
db = connect_db()



cursor = db.cursor() 

assessment_blueprint=Blueprint("assessment_blueprint", __name__, static_folder="static", template_folder="templates")


#view all ungraded submissions
@assessment_blueprint.route('/assessment', methods =['GET']) 
def assessment():

    
    if 'loggedin' in session:
        if session['level']=="admin": 

          cursor.execute('SELECT * FROM assignment_submission WHERE teacher_score="" ') 
          
        elif session['level']=="teacher":
          subject_id = session['subject']
          class_id = session['class']
          
          cursor.execute('SELECT lesson_id, lesson_title  FROM lesson_td WHERE subject = "'+subject_id+'" AND class_id = "'+class_id+'"')  
          row = cursor.fetchone() 
          lesson_id = row[0]
          lesson_title = row[1]

         
          cursor.execute(f'SELECT * FROM assignment_submission WHERE  teacher_score="" AND lesson_id = "{lesson_id}"') 
        
        elif session['level']=="student":
          
          class_id = session['class']
          
          cursor.execute('SELECT lesson_id, lesson_title  FROM lesson_td WHERE class_id = "'+class_id+'"')  
          row = cursor.fetchone() 
          lesson_id = row[0]
          lesson_title = row[1]

          user_type = session['level']  
          user_id = session['id'] 
         
          cursor.execute(f'SELECT * FROM assignment_submission WHERE  teacher_score="" AND user_type="{user_type}" AND user_id="{user_id}" ') 

        else:
          return redirect(url_for('auth'))

        data_assessment = cursor.fetchall()
        num_of_data_assessment=len(data_assessment)  


        #----------------------------------------

        assessment_record = []
        for row in data_assessment:
          submission_id = row[0]
          user_id = row[3]
          user_type = row[4]
          lesson_id = row[5]
          date_submitted = row[8]


          if user_type == 'admin':
              cursor.execute(f'SELECT username FROM accounts WHERE id="{user_id}" ')
              user_rec = cursor.fetchone() 
              user_name = user_rec[0]

          elif user_type == 'teacher': 
              cursor.execute(f'SELECT surname, other_names FROM teacher_tb WHERE teacher_id="{user_id}" ')
              user_rec = cursor.fetchone() 
              surname = user_rec[0]
              othernames = user_rec[1]
              user_name=f"{surname} {othernames}"


          elif user_type == 'student':   
              cursor.execute(f'SELECT surname, other_names FROM student_tb WHERE student_id="{user_id}" ')
              user_rec = cursor.fetchone() 
              surname = user_rec[0]
              othernames = user_rec[1]
              user_name=f"{surname} {othernames}"

          #-----------------------
          cursor.execute(f'SELECT * FROM lesson_td WHERE lesson_id="{lesson_id}" ')
          lesson = cursor.fetchone()
          
          lesson_title = lesson[1]
          lesson_subject_id = lesson[3]
          lesson_class_id = lesson[4]
          lesson_term_id = lesson[5]
          lesson_week = lesson[6]


          cursor.execute(f'SELECT * FROM class_tb WHERE id="{lesson_class_id}" ')
          class_record = cursor.fetchone()
          class_val = class_record[1]


          cursor.execute(f'SELECT subject_name FROM subjects_tb WHERE subject_id="{lesson_subject_id}" ')
          subject_rec = cursor.fetchone()
          subject_name = subject_rec[0]

          

          cursor.execute(f'SELECT term FROM terms_tb WHERE id="{lesson_term_id}" ')
          term_rec = cursor.fetchone()
          term_name = term_rec[0]

          assessment_record.append([submission_id, user_name, user_type, class_val, subject_name, term_name, lesson_week, date_submitted, lesson_title, lesson_id])
        #-----------------------------------------------------------


    else:
        return redirect(url_for('login'))
    
    #return render_template('assessment.html', num_of_data_assessment=num_of_data_assessment, data_assessment=data_assessment, data_week=data_week , data_lesson=data_lesson, data_subject=data_subject, data_class=data_class, data_term=data_term)     
	  
    return render_template('assessment.html', num_of_data_assessment=num_of_data_assessment, assessment_record=assessment_record)     
	  




#view all ungraded submissions
@assessment_blueprint.route('/assessment_all', methods =['GET']) 
def assessment_all():

    
    if 'loggedin' in session:
        if session['level']=="admin": 

          cursor.execute('SELECT * FROM assignment_submission WHERE teacher_score <> "" ') 
          
        elif session['level']=="teacher":
          subject_id = session['subject']
          class_id = session['class']
          
          cursor.execute('SELECT lesson_id, lesson_title  FROM lesson_td WHERE subject = "'+subject_id+'" AND class_id = "'+class_id+'"')  
          row = cursor.fetchone() 
          lesson_id = row[0]
          lesson_title = row[1]

         
          cursor.execute(f'SELECT * FROM assignment_submission WHERE teacher_score <> "" AND lesson_id = "{lesson_id}"') 
        
        elif session['level']=="student":
          
          class_id = session['class']

          user_type = session['level']  
          user_id = session['id'] 
          
          cursor.execute('SELECT lesson_id, lesson_title  FROM lesson_td WHERE class_id = "'+class_id+'"')  
          
          row = cursor.fetchone() 
          lesson_id = row[0]
          lesson_title = row[1]

         
          #cursor.execute(f'SELECT * FROM assignment_submission WHERE teacher_score <> "" AND lesson_id = "{lesson_id}"') 
          cursor.execute(f'SELECT * FROM assignment_submission WHERE  teacher_score <> "" AND user_type="{user_type}" AND user_id="{user_id}" ')   

        data_assessment = cursor.fetchall()
        num_of_data_assessment=len(data_assessment)  


        #----------------------------------------

        assessment_record2 = []

        for row in data_assessment:
          submission_id = row[0]
          user_id = row[3]
          user_type = row[4]
          lesson_id = row[5]
          date_submitted = row[8]
          teacher_score = row[2]


          if user_type == 'admin':
              cursor.execute(f'SELECT username FROM accounts WHERE id={user_id} ')
              user_rec = cursor.fetchone() 
              user_name = user_rec[0]

          elif user_type == 'teacher': 
              cursor.execute(f'SELECT surname, other_names FROM teacher_tb WHERE teacher_id={user_id} ')
              user_rec = cursor.fetchone() 
              surname = user_rec[0]
              othernames = user_rec[1]
              user_name=f"{surname} {othernames}"


          elif user_type == 'student':   
              cursor.execute(f'SELECT surname, other_names FROM student_tb WHERE student_id={user_id} ')
              user_rec = cursor.fetchone() 
              surname = user_rec[0]
              othernames = user_rec[1]
              user_name=f"{surname} {othernames}"

          #-----------------------
          cursor.execute(f'SELECT * FROM lesson_td WHERE lesson_id={lesson_id} ')
          lesson = cursor.fetchone()
          
          lesson_title = lesson[1]
          lesson_subject_id = lesson[3]
          lesson_class_id = lesson[4]
          lesson_term_id = lesson[5]
          lesson_week = lesson[6]

          cursor.execute(f'SELECT subject_name FROM subjects_tb WHERE subject_id={lesson_subject_id} ')
          subject_rec = cursor.fetchone()
          subject_name = subject_rec[0]

          cursor.execute(f'SELECT class_name FROM class_tb WHERE id={lesson_class_id} ')
          class_rec = cursor.fetchone()
          class_name = class_rec[0]

          cursor.execute(f'SELECT term FROM terms_tb WHERE id={lesson_term_id} ')
          term_rec = cursor.fetchone()
          term_name = term_rec[0]

          assessment_record2.append([submission_id, user_name, user_type, class_name, subject_name, term_name, lesson_week, date_submitted, lesson_title, lesson_id, teacher_score])
        #-----------------------------------------------------------


    else:
        return redirect(url_for('login'))
    
    #return render_template('assessment.html', num_of_data_assessment=num_of_data_assessment, data_assessment=data_assessment, data_week=data_week , data_lesson=data_lesson, data_subject=data_subject, data_class=data_class, data_term=data_term)     
	  
    return render_template('assessment_all.html', num_of_data_assessment=num_of_data_assessment, assessment_record2=assessment_record2)     
	  






@assessment_blueprint.route('/assessment_input', methods=['GET', 'POST']) 
def assessment_input(): 

  
  if request.method == 'POST': 
    submission_id = request.form['submission_id'] 
   

    view_from = request.form['view_from'] 

    cursor.execute(f'SELECT expected_score, lesson_id, date_submitted, user_id, user_type, your_answer, your_upload, teacher_score, teacher_note FROM assignment_submission WHERE submit_id = "{submission_id}" ') 
    submit_rec = cursor.fetchone()

    expected_score = submit_rec[0]
    lesson_id = submit_rec[1]
    date_submitted=submit_rec[2]
    user_id=submit_rec[3]
    user_type=submit_rec[4]

    your_answer=submit_rec[5]
    your_upload=submit_rec[6]

    teacher_score=submit_rec[7]
    teacher_note=submit_rec[8]


    if user_type == 'admin':
        cursor.execute(f'SELECT username FROM accounts WHERE id={user_id} ')
        user_rec = cursor.fetchone() 
        user_name = user_rec[0]

    elif user_type == 'teacher': 
        cursor.execute(f'SELECT surname, other_names FROM teacher_tb WHERE teacher_id={user_id} ')
        user_rec = cursor.fetchone() 
        surname = user_rec[0]
        othernames = user_rec[1]
        user_name=f"{surname} {othernames}"


    elif user_type == 'student':   
        cursor.execute(f'SELECT surname, other_names FROM student_tb WHERE student_id={user_id} ')
        user_rec = cursor.fetchone() 
        surname = user_rec[0]
        othernames = user_rec[1]
        user_name=f"{surname} {othernames}"


    cursor.execute(f'SELECT assignment_title, detail FROM lesson_assignment WHERE lesson_id={lesson_id} ')
    red_assignment = cursor.fetchone()
    assignment_title = red_assignment[0]
    assignment_detail = red_assignment[1]

    cursor.execute(f'SELECT * FROM lesson_td WHERE lesson_id={lesson_id} ')
    lesson = cursor.fetchone()
    
    lesson_title = lesson[1]
    lesson_subject_id = lesson[3]
    lesson_class_id = lesson[4]
    lesson_term_id = lesson[5]
    lesson_week = lesson[6]

    cursor.execute(f'SELECT subject_name FROM subjects_tb WHERE subject_id={lesson_subject_id} ')
    subject_rec = cursor.fetchone()
    subject_name = subject_rec[0]

    cursor.execute(f'SELECT class_name FROM class_tb WHERE id={lesson_class_id} ')
    class_rec = cursor.fetchone()
    class_name = class_rec[0]

    cursor.execute(f'SELECT term FROM terms_tb WHERE id={lesson_term_id} ')
    term_rec = cursor.fetchone()
    term_name = term_rec[0]

     
    assessment_record = []
    assessment_record.append([expected_score, submission_id, user_name, user_type, class_name, subject_name, term_name, lesson_week, date_submitted, lesson_title, lesson_id, your_answer, your_upload, assignment_title, assignment_detail, teacher_score, teacher_note])
        
    return render_template('assessment_input.html', assessment_record=assessment_record, view_from=view_from) 





@assessment_blueprint.route('/assessment_process', methods=['GET', 'POST']) 
def assessment_process(): 

  
  if request.method == 'POST': 

    submission_id = request.form['submission_id'] 
    view_from = request.form['view_from'] 

    if request.form['process']=="Delete Score":        
        
        cursor.execute('UPDATE assignment_submission SET teacher_score="", teacher_note="" WHERE submit_id = ?', (submission_id))              
        db.commit()

        action_done = 'clear'

    elif request.form['process']=="Save":

        teacher_score = request.form['teacher_score'] 
        teacher_note = request.form['teacher_note']  
                
        cursor.execute('UPDATE assignment_submission SET teacher_score=?, teacher_note=? WHERE submit_id = ?', (teacher_score, teacher_note, submission_id))              
        db.commit()

        action_done = 'saved'
   
    # ---------------------------------------------------------------

    cursor.execute(f'SELECT expected_score, lesson_id, date_submitted, user_id, user_type, your_answer, your_upload FROM assignment_submission WHERE submit_id = "{submission_id}" ') 
    submit_rec = cursor.fetchone()
    expected_score = submit_rec[0]
    lesson_id = submit_rec[1]
    date_submitted=submit_rec[2]
    user_id=submit_rec[3]
    user_type=submit_rec[4]

    your_answer=submit_rec[5]
    your_upload=submit_rec[6]


    if user_type == 'admin':
        cursor.execute(f'SELECT username FROM accounts WHERE id={user_id} ')
        user_rec = cursor.fetchone() 
        user_name = user_rec[0]

    elif user_type == 'teacher': 
        cursor.execute(f'SELECT surname, other_names FROM teacher_tb WHERE teacher_id={user_id} ')
        user_rec = cursor.fetchone() 
        surname = user_rec[0]
        othernames = user_rec[1]
        user_name=f"{surname} {othernames}"


    elif user_type == 'student':   
        cursor.execute(f'SELECT surname, other_names FROM student_tb WHERE student_id={user_id} ')
        user_rec = cursor.fetchone() 
        surname = user_rec[0]
        othernames = user_rec[1]
        user_name=f"{surname} {othernames}"


    cursor.execute(f'SELECT assignment_title, detail FROM lesson_assignment WHERE lesson_id={lesson_id} ')
    red_assignment = cursor.fetchone()
    assignment_title = red_assignment[0]
    assignment_detail = red_assignment[0]

    cursor.execute(f'SELECT * FROM lesson_td WHERE lesson_id={lesson_id} ')
    lesson = cursor.fetchone()
    
    lesson_title = lesson[1]
    lesson_subject_id = lesson[3]
    lesson_class_id = lesson[4]
    lesson_term_id = lesson[5]
    lesson_week = lesson[6]

    cursor.execute(f'SELECT subject_name FROM subjects_tb WHERE subject_id={lesson_subject_id} ')
    subject_rec = cursor.fetchone()
    subject_name = subject_rec[0]

    cursor.execute(f'SELECT class_name FROM class_tb WHERE id={lesson_class_id} ')
    class_rec = cursor.fetchone()
    class_name = class_rec[0]

    cursor.execute(f'SELECT term FROM terms_tb WHERE id={lesson_term_id} ')
    term_rec = cursor.fetchone()
    term_name = term_rec[0]

     
    assessment_record = []
    assessment_record.append([expected_score, submission_id, user_name, user_type, class_name, subject_name, term_name, lesson_week, date_submitted, lesson_title, lesson_id, your_answer, your_upload, assignment_title, assignment_detail])
        
    return render_template('assessment_input.html', assessment_record=assessment_record, action_done=action_done, view_from=view_from) 



'''
@assessment_blueprint.route('/assessment_clear_score', methods=['GET', 'POST']) 
def assessment_clear_score():
  if 'loggedin' in session and session['level']=="admin" or session['level']=="teacher":

      if request.method == 'POST':       
        submission_id = request.form['submission_id'] 
        view_from = request.form['view_from'] 
   
    args = request.args
    sel_id = args.get('value')
    lesson_id = args.get('lesson_id')
   
   
    cursor.execute('DELETE FROM lesson_assignment WHERE assignment_id = "'+sel_id+'"')              
    db.commit()
   
      

    return redirect(url_for('lesson_assignment_blueprint.assignment', value=lesson_id)) 

    

  else:
    return redirect(url_for('login')) 
 '''
