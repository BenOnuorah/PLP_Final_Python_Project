from flask import Blueprint, render_template, request, url_for, redirect, session
import re 
from datetime import datetime
import os

from werkzeug.utils import secure_filename

from conn_database import connect_db
db = connect_db()



cursor = db.cursor() 

lesson_more_blueprint=Blueprint("lesson_more_blueprint", __name__, static_folder="static", template_folder="templates")

UPLOAD_FOLDER = 'static/images_folder'
allowed_file = set(['pdf', 'png', 'jpg', 'jpeg', 'gif'])


@lesson_more_blueprint.route('/lesson_more', methods =['GET']) 
def lesson_more():

    args = request.args
    sel_id = args.get('value')
    
    cursor.execute('SELECT lesson_title  FROM lesson_td WHERE lesson_id = "'+sel_id+'"')  
    row = cursor.fetchone() 
    lesson_title = row[0]
  
    if 'loggedin' in session and session['level']=="admin" or session['level']=="teacher":

        cursor.execute('SELECT * FROM lesson_upload_td WHERE lesson_id = "'+sel_id+'"') 
        data_lesson_more = cursor.fetchall()

    else:
        return redirect(url_for('login')) 
    
    return render_template('lesson_more.html', data_lesson_more=data_lesson_more, lesson_title=lesson_title)     
	  



#process the student add
@lesson_more_blueprint.route('/lesson_more_input', methods=['GET', 'POST']) 
def lesson_more_input(): 

  
  if request.method == 'POST': 
    lesson_id = request.form['lesson_id'] 
    caption = request.form['caption'] 
    youtube_video = request.form['youtube_video']  

    #-------------------- Upload File-------------------------
    filename=""
    file = request.files['image_file'] 

    if file:
        now = str(datetime.now())
        filename = secure_filename(now+file.filename)
        file.save(os.path.join(UPLOAD_FOLDER, filename)) 
    #-------------------------------------------------
    
    if "edit_id" in request.form: # Edit Record
      edit_id = request.form['edit_id'] 
      cursor.execute('UPDATE lesson_upload_td SET lesson_id="'+lesson_id+'", caption="'+caption+'", youtube_video="'+youtube_video+'", image_file="'+filename+'" WHERE upload_id = "'+edit_id+'"')              
      db.commit()
        
      return redirect('lesson_more?task=edit&value='+edit_id+'&done=1')

    else: #Add  Record 

      cursor.execute(f"INSERT INTO lesson_upload_td (lesson_id, caption, youtube_video, image_file) VALUES ('{lesson_id}', '{caption}', '{youtube_video}', '{filename}')")
      db.commit() 
    
    
      output="Record saved"
      #return render_template('lesson_more.html', msg=output, value=lesson_id) 

      return redirect(url_for('lesson_more_blueprint.lesson_more', msg=output, value=lesson_id))  

  else:

    #loadm form in edit mode
    args = request.args
    msg=''
    if 'task' in args: #check if in edit mode    
      sel_id = args.get('value')  

      cursor.execute('SELECT * FROM lesson_upload_td WHERE upload_id = "'+sel_id+'"')  
      data_preview = cursor.fetchone()            
      msg="Edit"

     
      return render_template('lesson_input.html', preview=data_preview)
      

     
     
    else:
      #load form in add mode
      args = request.args
      sel_id = args.get('value')
      
      cursor.execute('SELECT lesson_title  FROM lesson_td WHERE lesson_id = "'+sel_id+'"')  
      row = cursor.fetchone() 
      lesson_title = row[0]

     
      return render_template('lesson_more_input.html', lesson_title=lesson_title) 




@lesson_more_blueprint.route('/delete_lesson_more', methods =['GET'])
def delete_lesson_more():
  if 'loggedin' in session and session['level']=="admin" or session['level']=="teacher":
    args = request.args
    sel_id = args.get('value')
    lesson_id = args.get('lesson_id')
   
   
    cursor.execute('DELETE FROM lesson_upload_td WHERE upload_id = "'+sel_id+'"')              
    db.commit()
    
    #returning back to seestudents 
    #return redirect(url_for('lesson_more_blueprint.lesson_more')) 
  

    return redirect(url_for('lesson_more_blueprint.lesson_more', value=lesson_id)) 

  else:
    return redirect(url_for('login')) 