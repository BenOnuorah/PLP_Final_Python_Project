from flask import Blueprint, render_template, request, url_for, redirect, session
import re 
from datetime import datetime
import os

from werkzeug.utils import secure_filename

from conn_database import connect_db
db = connect_db()



cursor = db.cursor() 

lesson_assignment_blueprint=Blueprint("lesson_assignment_blueprint", __name__, static_folder="static", template_folder="templates")

@lesson_assignment_blueprint.route('/assignment', methods =['GET']) 
def assignment():

    args = request.args
    sel_id = args.get('value')

    if 'loggedin' in session and session['level']=="admin" or session['level']=="teacher":

        cursor.execute('SELECT lesson_title  FROM lesson_td WHERE lesson_id = "'+sel_id+'"')  
        row = cursor.fetchone() 
        lesson_title = row[0]
      
        cursor.execute('SELECT * FROM lesson_assignment WHERE lesson_id = "'+sel_id+'"') 
        data_lesson_assignment = cursor.fetchall()
        num_of_assignment=len(data_lesson_assignment)

    else:
        return redirect(url_for('login'))
    
    return render_template('assignment.html', num_of_assignment=num_of_assignment, data_lesson_assignment=data_lesson_assignment, lesson_title=lesson_title)     
	  



#process the student add
@lesson_assignment_blueprint.route('/assignment_input', methods=['GET', 'POST']) 
def assignment_input(): 

  
  if request.method == 'POST': 
    lesson_id = request.form['lesson_id'] 
    assignment_title = request.form['assignment_title'] 
    detail = request.form['detail']  
    max_score = request.form['max_score']  
   
    if "edit_id" in request.form: # Edit Record
      edit_id = request.form['edit_id'] 
      
      

      cursor.execute('UPDATE lesson_assignment SET lesson_id=?, assignment_title=?, detail=?, max_score=? WHERE assignment_id = ?', (lesson_id, assignment_title, detail, max_score, edit_id) )              
      

      db.commit()
        
      return redirect('assignment?task=edit&value='+lesson_id+'&done=1')

    else: #Add  Record 

      #cursor.execute(f"INSERT INTO lesson_assignment (lesson_id, assignment_title, detail, max_score) VALUES ('{lesson_id}', '{assignment_title}', '{detail}', '{max_score}')")
      
      cursor.execute("INSERT INTO lesson_assignment (lesson_id, assignment_title, detail, max_score) VALUES (?,?,?,?)", (lesson_id, assignment_title, detail, max_score) )

      db.commit() 
    
    
      output="Record saved"
      #return render_template('lesson_more.html', msg=output, value=lesson_id) 

      return redirect(url_for('lesson_assignment_blueprint.assignment', msg=output, value=lesson_id))  

  else:

    #loadm form in edit mode
    args = request.args
    msg=''
    if 'task' in args: #check if in edit mode    
      sel_id = args.get('assignment') 
      value = args.get('value') 

      cursor.execute('SELECT * FROM lesson_assignment WHERE assignment_id = "'+sel_id+'"')  
      data_preview = cursor.fetchone()            
      msg="Edit"

      cursor.execute('SELECT lesson_title  FROM lesson_td WHERE lesson_id = "'+value+'"')  
      row = cursor.fetchone() 
      lesson_title = row[0]

      return render_template('assignment_input.html', preview=data_preview, lesson_title=lesson_title)
      

      
     
    else:
      #load form in add mode
      args = request.args
      sel_id = args.get('value')
      
      cursor.execute('SELECT lesson_title  FROM lesson_td WHERE lesson_id = "'+sel_id+'"')  
      row = cursor.fetchone() 
      lesson_title = row[0]

     
      return render_template('assignment_input.html', lesson_title=lesson_title) 




@lesson_assignment_blueprint.route('/assignment_delete', methods =['GET'])
def assignment_delete():
  if 'loggedin' in session and session['level']=="admin" or session['level']=="teacher":
    args = request.args
    sel_id = args.get('value')
    lesson_id = args.get('lesson_id')
   
   
    cursor.execute('DELETE FROM lesson_assignment WHERE assignment_id = "'+sel_id+'"')              
    db.commit()
    
    #returning back to seestudents 
    #return redirect(url_for('lesson_more_blueprint.lesson_more')) 
  

    return redirect(url_for('lesson_assignment_blueprint.assignment', value=lesson_id)) 

  else:
    return redirect(url_for('login')) 



# assignment submission 
@lesson_assignment_blueprint.route('/assignment_submission', methods=['GET', 'POST']) 
def assignment_submission(): 
  if 'loggedin' in session:

    if request.method == 'POST': 
      expected_score = request.form['max_score']  
      user_id = session['id'] 
      user_type = session['level']      
      lesson_id = request.form['lesson_id']     
      your_answer = request.form['detail']  
      date_submitted = str(datetime.now())

       #-------------------- Upload File-------------------------
      filename=""
      file = request.files['image_file'] 

      if file:
          now = str(datetime.now())
          filename = secure_filename(now+file.filename)
          file.save(os.path.join("static/images_folder", filename)) 
      #----------------------------------------------------------

      your_upload = filename

      cursor.execute('INSERT INTO assignment_submission (expected_score, user_id, user_type, lesson_id, your_answer, your_upload, date_submitted) VALUES (?,?,?,?,?,?,?)',(expected_score, user_id, user_type, lesson_id, your_answer, your_upload, date_submitted)) 
      db.commit() 


      #-----------------------------------------------------------
      class_id = request.form['class_id'] 
      term = request.form['term'] 

      if term == "1":
          term_name = "1st Term"
      elif term == "2": 
          term_name = "2nd Term"
      elif term == "3":     
          term_name = "3rd Term"

      cursor.execute(f'SELECT class_name  FROM class_tb WHERE id = {class_id}')  
      row = cursor.fetchone() 
      class_name = row[0]

      cursor.execute(f'SELECT * FROM lesson_td WHERE class_id={class_id} AND term={term} ORDER BY week')
      data_lesson = cursor.fetchall()

      cursor.execute('SELECT * FROM subjects_tb')
      data_subject = cursor.fetchall()

      cursor.execute('SELECT lesson_id FROM lesson_assignment')
      data_assignment = cursor.fetchall()

      cursor.execute('SELECT lesson_id, teacher_score, expected_score FROM assignment_submission')
      data_submission = cursor.fetchall()

      return render_template('scheme_detail.html', data_submission=data_submission, data_assignment=data_assignment, data_lesson=data_lesson, class_name=class_name, data_subject=data_subject, term_name=term_name, assignment_submitted=1)   
    
    else:

      return redirect(url_for('login'))
