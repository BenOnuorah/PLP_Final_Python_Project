from flask import Blueprint, render_template, request, url_for, redirect, session
import re 

from conn_database import connect_db
db = connect_db()
cursor = db.cursor() 

subject_blueprint=Blueprint("subject_blueprint", __name__, static_folder="static", template_folder="templates")

#load form


@subject_blueprint.route('/subject', methods =['GET']) 
def subject():
  
    cursor.execute('SELECT * FROM subjects_tb ORDER BY subject_name')
    data_subject = cursor.fetchall()

    cursor.execute('SELECT * FROM class_tb')
    data_class = cursor.fetchall()

    cursor.execute('SELECT * FROM terms_tb')
    data_term = cursor.fetchall()

    return render_template('subject.html', data_subject=data_subject, data_class=data_class, data_term=data_term)     
	  



#process the student add
@subject_blueprint.route('/subject_input', methods=['GET', 'POST']) 
def subject_input(): 

    cursor = db.cursor() 
    
    if request.method == 'POST': 
      subject = request.form['subject'] 
      term = request.form['term'] 
      class_id = request.form['class']  

      if "edit_id" in request.form: # Edit Record
        edit_id = request.form['edit_id'] 
        cursor.execute('UPDATE subjects_tb SET subject_name="'+subject+'", term="'+term+'", class_id="'+class_id+'" WHERE subject_id = "'+edit_id+'"')              
        db.commit()
          
        return redirect('subject?task=edit&value='+edit_id+'&done=1')

      else: #Add  Record 
        #cursor.execute('INSERT INTO subjects_tb (subject_name, term, class_id) VALUES (?,?,?)',(subject, term, class_id)) 
        cursor.execute(f"INSERT INTO subjects_tb (subject_name, term, class_id) VALUES ('{subject}', '{term}', '{class_id}')")
        db.commit() 
      
        output="Record saved"
        return render_template('subject_input.html', msg=output) 
    else:

      #loadm form in edit mode
      args = request.args
      msg=''
      if 'task' in args: #check if in edit mode    
        sel_id = args.get('value')  

        cursor.execute('SELECT * FROM subjects_tb WHERE subject_id = "'+sel_id+'"')  
        data_preview = cursor.fetchone()            
        msg="Edit"


        
        cursor = db.cursor()
        cursor.execute('SELECT * FROM class_tb')
        class_rec = cursor.fetchall()    

        cursor.execute('SELECT * FROM terms_tb')
        terms_rec = cursor.fetchall()  

        return render_template('subject_input.html', preview=data_preview, class_rec=class_rec, terms_rec=terms_rec)

      else:
        #load form in add mode
        cursor = db.cursor()
        cursor.execute('SELECT * FROM class_tb')
        class_rec = cursor.fetchall()    

        cursor.execute('SELECT * FROM terms_tb')
        terms_rec = cursor.fetchall()  

        return render_template('subject_input.html', class_rec=class_rec, terms_rec=terms_rec) 





@subject_blueprint.route('/delete_subject', methods =['GET'])
def delete():
  if 'loggedin' in session and session['level']=="admin":
    args = request.args
    sel_id = args.get('value')
   
   
    cursor.execute('DELETE FROM subjects_tb WHERE subject_id = "'+sel_id+'"')              
    db.commit()
    
    #returning back to seestudents 
    return redirect(url_for('subject_blueprint.subject'))  
  else:
    return redirect(url_for('login')) 