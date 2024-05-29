from flask import Blueprint, render_template, request, url_for, redirect, session
import re 

from conn_database import connect_db
db = connect_db()
cursor = db.cursor() 

lesson_blueprint=Blueprint("lesson_blueprint", __name__, static_folder="static", template_folder="templates")

#load form


@lesson_blueprint.route('/lesson', methods =['GET']) 
def lesson():
  
    if 'loggedin' in session and session['level']=="admin":
        cursor.execute('SELECT * FROM lesson_td')
        data_lesson = cursor.fetchall()
    elif 'loggedin' in session and session['level']=="teacher":
        teacher_subject = session['subject']
        teacher_class = session['class']

        cursor.execute(f'SELECT * FROM lesson_td WHERE subject={teacher_subject} AND class_id={teacher_class} ')
        data_lesson = cursor.fetchall()
    
    elif 'loggedin' in session and session['level']=="student":
        student_class = session['class']

        cursor.execute(f'SELECT * FROM lesson_td WHERE class_id={student_class} ')
        data_lesson = cursor.fetchall()
    else:
        #user not login 
        return redirect(url_for('login')) 

    cursor.execute('SELECT * FROM subjects_tb')
    data_subject = cursor.fetchall()

    cursor.execute('SELECT * FROM class_tb')
    data_class = cursor.fetchall()

    cursor.execute('SELECT * FROM terms_tb')
    data_term = cursor.fetchall()

    cursor.execute('SELECT * FROM week_tb')
    data_week = cursor.fetchall()

    #args = request.args
    #lesson_id = args.get('id')
    
    cursor.execute('SELECT lesson_id FROM lesson_assignment')
    data_assignment = cursor.fetchall()


    cursor.execute('SELECT lesson_id FROM  lesson_upload_td')
    data_media = cursor.fetchall()

    return render_template('lesson_list.html', data_week=data_week , data_lesson=data_lesson, data_subject=data_subject, data_class=data_class, data_term=data_term, data_assignment=data_assignment, data_media=data_media)     
	  



#process the student add
@lesson_blueprint.route('/lesson_input', methods=['GET', 'POST']) 
def lesson_input(): 

  cursor = db.cursor()

  if request.method == 'POST': 

    lesson_title = request.form['lesson_title'] 
    lesson_detail = request.form['lesson_detail'] 

    subject = request.form['class_subject']  
    term = request.form['term'] 
    week = request.form['week'] 


    cursor.execute('SELECT class_id  FROM subjects_tb WHERE subject_id = "'+subject+'"')  
    row = cursor.fetchone() 
    class_id = row[0]

    
    if "edit_id" in request.form: # Edit Record
      edit_id = request.form['edit_id'] 
      #cursor.execute('UPDATE lesson_td SET lesson_title="'+lesson_title+'", lesson_detail="'+lesson_detail+'", class_id="'+class_id+'", subject="'+subject+'", term="'+term+'", week="'+week+'" WHERE lesson_id = "'+edit_id+'"')              
      
      cursor.execute('UPDATE lesson_td SET lesson_title=?, lesson_detail=?, class_id=?, subject=?, term=?, week=? WHERE lesson_id = ?', (lesson_title, lesson_detail, class_id, subject, term, week, edit_id))              
      
      
      db.commit()
        
      return redirect('lesson?task=edit&value='+edit_id+'&done=1')

    else: #Add  Record 
      cursor.execute('INSERT INTO lesson_td (lesson_title, lesson_detail, class_id, subject, term, week) VALUES (?,?,?,?,?,?)',(lesson_title, lesson_detail, class_id, subject, term, week)) 
      #cursor.execute(f"INSERT INTO lesson_td (lesson_title, lesson_detail, class_id, subject, term, week) VALUES ('{lesson_title}', '{lesson_detail}', '{class_id}', '{subject}', '{term}', '{week}')")
      db.commit() 
    
     
      #return render_template('lesson_list.html', msg=output) 
      return redirect('lesson?add=1')
  else:

    #loadm form in edit mode
    args = request.args
    msg=''
    if 'task' in args: #check if in edit mode    
      sel_id = args.get('value')  

      cursor.execute('SELECT * FROM lesson_td WHERE lesson_id = "'+sel_id+'"')  
      data_preview = cursor.fetchone()            
      msg="Edit"


      
      cursor = db.cursor()
     
      cursor.execute('SELECT * FROM lesson_td')
      data_lesson = cursor.fetchall()
    
      if 'loggedin' in session and session['level']=="admin":

          cursor.execute('SELECT * FROM subjects_tb')
          data_subject = cursor.fetchall()

          cursor.execute('SELECT * FROM class_tb')
          data_class = cursor.fetchall()

      elif 'loggedin' in session and session['level']=="teacher":
          teacher_subject = session['subject']
          teacher_class = session['class']

          cursor.execute(f'SELECT * FROM subjects_tb WHERE subject_id={teacher_subject}')
          data_subject = cursor.fetchall()

          cursor.execute(f'SELECT * FROM class_tb  WHERE id={teacher_class}')
          data_class = cursor.fetchall()
      else:
          return redirect(url_for('login')) 

      cursor.execute('SELECT * FROM terms_tb')
      data_term = cursor.fetchall()

      cursor.execute('SELECT * FROM week_tb')
      data_week = cursor.fetchall()



      return render_template('lesson_input.html', preview=data_preview, data_week=data_week , data_lesson=data_lesson, data_subject=data_subject, data_class=data_class, data_term=data_term)

    else:
      #load form in add mode
      cursor = db.cursor()
      cursor.execute('SELECT * FROM lesson_td')
      data_lesson = cursor.fetchall()
    
     

      if 'loggedin' in session and session['level']=="admin":

          cursor.execute('SELECT * FROM subjects_tb')
          data_subject = cursor.fetchall()

          cursor.execute('SELECT * FROM class_tb ORDER BY class_name')
          data_class = cursor.fetchall()

      elif 'loggedin' in session and session['level']=="teacher":
          teacher_subject = session['subject']
          teacher_class = session['class']

          cursor.execute(f'SELECT * FROM subjects_tb WHERE subject_id={teacher_subject}')
          data_subject = cursor.fetchall()

          cursor.execute(f'SELECT * FROM class_tb  WHERE id={teacher_class} ORDER BY class_name' )
          data_class = cursor.fetchall()


      cursor.execute('SELECT * FROM terms_tb')
      data_term = cursor.fetchall()

      cursor.execute('SELECT * FROM week_tb')
      data_week = cursor.fetchall() 

      return render_template('lesson_input.html', data_week=data_week , data_lesson=data_lesson, data_subject=data_subject, data_class=data_class, data_term=data_term) 





@lesson_blueprint.route('/delete_lesson', methods =['GET'])
def delete_lesson():
  if 'loggedin' in session and session['level']=="admin" or session['level']=="teacher":
    args = request.args
    sel_id = args.get('value')
   
   
    cursor.execute('DELETE FROM lesson_td WHERE lesson_id = "'+sel_id+'"')              
    db.commit()
    
    #returning back to seestudents 
    
    return redirect('lesson?delete=1')
  else:
    return redirect(url_for('login')) 