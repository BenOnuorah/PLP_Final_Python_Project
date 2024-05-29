from flask import Blueprint, render_template, request, url_for, redirect, session
import re 

from conn_database import connect_db
db = connect_db()
cursor = db.cursor() 

class_blueprint=Blueprint("class_blueprint", __name__, static_folder="static", template_folder="templates")

#load form


@class_blueprint.route('/class_record', methods =['GET']) 
def class_record():
  
    cursor.execute('SELECT * FROM class_tb')
    class_list = cursor.fetchall()

    return render_template('class_list.html', class_list=class_list)     
	  



#process the student add
@class_blueprint.route('/class_input', methods=['GET', 'POST']) 
def class_input(): 

  
  if request.method == 'POST': 
    class_name = request.form['class_name'] 
   
    if "edit_id" in request.form: # Edit Record
      edit_id = request.form['edit_id'] 
      cursor.execute('UPDATE class_tb SET class_name="'+class_name+'" WHERE id = "'+edit_id+'"')              
      db.commit()
        
      return redirect('class_input?task=edit&value='+edit_id+'&done=1')

    else: #Add  Record 
      
      cursor.execute(f"INSERT INTO class_tb (class_name) VALUES ('{class_name}')")
      db.commit() 
    
      output="Record saved"
      return render_template('class_input.html', msg=output) 
  else:

    #load form in edit mode
    args = request.args
    msg=''
    if 'task' in args: #check if in edit mode    
      sel_id = args.get('value')  

      cursor.execute('SELECT * FROM class_tb WHERE id = "'+sel_id+'"')  
      data_preview = cursor.fetchone()            
      msg="Edit"


      return render_template('class_input.html', preview=data_preview)

    else:
     
      return render_template('class_input.html') 





@class_blueprint.route('/delete_class', methods =['GET'])
def delete():
  if 'loggedin' in session and session['level']=="admin":
    args = request.args
    sel_id = args.get('value')
   
   
    cursor.execute('DELETE FROM class_tb WHERE id = "'+sel_id+'"')              
    db.commit()
    
    #returning back to seestudents 
    return redirect(url_for('class_blueprint.class_record'))  
  else:
    return redirect(url_for('login')) 