from flask import Blueprint, render_template, request, url_for, redirect, session
import re 

from conn_database import connect_db
db = connect_db()

cursor = db.cursor()

student_blueprint=Blueprint("student_blueprint", __name__, static_folder="static", template_folder="templates")

#load form

@student_blueprint.route('/profile')
def profile():
        # Check if user is loggedin
        if 'loggedin' in session:
            
           
            cursor.execute('SELECT * FROM student_tb WHERE student_id = ?', (session['id'],))
            account = cursor.fetchone()
            # Show the profile page with account info
            return render_template('profile.html', account=account)
        # User is not loggedin redirect to login page
        return redirect(url_for('login'))


@student_blueprint.route('/student_record')
def student_record():
        # Check if user is loggedin

        
        
        if 'loggedin' in session and session['level']=="admin":
           
           
            cursor.execute('SELECT * FROM class_tb')
            data_class = cursor.fetchall()

            cursor.execute('SELECT * FROM student_tb ORDER BY surname')          
            student_record = cursor.fetchall() 

            return render_template('student_record.html', student_record=student_record, data_class=data_class) 

        elif 'loggedin' in session and session['level']=="teacher":   
            teacher_class = session['class']
           
            cursor.execute(f'SELECT * FROM class_tb WHERE id={teacher_class} ')
            data_class = cursor.fetchall()

            cursor.execute(f'SELECT * FROM student_tb WHERE class={teacher_class} ORDER BY surname')          
            student_record = cursor.fetchall() 

            return render_template('student_record.html', student_record=student_record, data_class=data_class)
        
        elif 'loggedin' in session and session['level']=="student":   
            class_id = session['class']
            student_id = session['id']
           
            cursor.execute(f'SELECT * FROM class_tb WHERE id={class_id} ')
            data_class = cursor.fetchall()

            cursor.execute(f'SELECT * FROM student_tb WHERE student_id={student_id} ORDER BY surname')          
            student_record = cursor.fetchall() 

            return render_template('student_record.html', student_record=student_record, data_class=data_class)
        

        else:        
            return redirect(url_for('login'))



@student_blueprint.route('/delete_student', methods =['GET'])
def delete_student():
  if 'loggedin' in session and session['level']=="admin":
    args = request.args
    sel_id = args.get('id')
   
    cursor.execute(f'DELETE FROM student_tb WHERE student_id = "{sel_id}"')              
    db.commit()

    return redirect(url_for('student_blueprint.student_record'))  
  else:
    return redirect(url_for('login'))
'''
@student_bp.route('/student', methods =['GET']) 
def student():
  args = request.args
  msg=''
  if 'task' in args: #check if in edit mode    
    sel_id = args.get('value')  

    cursor = conn.cursor() 
    cursor.execute('SELECT * FROM student WHERE id = "'+sel_id+'"')  
    data_preview = cursor.fetchone()            
    msg="Edit"
    return render_template('student.html', preview=data_preview)
  else: # else load add mode      
	  return render_template('student.html')

#display record
@student_bp.route('/seestudents') 
def seestudents():	 

  cursor = conn.cursor()  
  cursor.execute('SELECT * FROM student')
  data = cursor.fetchall()

  return render_template('seestudents.html', students=data)






#process the student add
@student_bp.route('/addstudent', methods=['GET', 'POST']) 
def addstudent(): 
  if request.method == 'POST': 
    surname = request.form['surname'] 
    othernames = request.form['othernames'] 
    address = request.form['address']  

    if "edit_id" in request.form: # Edit Record
      edit_id = request.form['edit_id'] 
      conn.execute('UPDATE student SET surname_name="'+surname+'", other_name="'+othernames+'", address_address="'+address+'" WHERE id = "'+edit_id+'"')              
      conn.commit()
        
      return redirect('student?task=edit&value='+edit_id+'&done=1')

    else: #Add  Record 
      conn.execute('INSERT INTO student (surname_name,other_name,address_address) VALUES (?,?,?)',(surname, othernames, address)) 
      conn.commit() 
    
      output="Student record saved"
      return render_template('student.html', msg=output) 


@student_bp.route('/delete_student', methods =['GET'])
def delete():
  if 'loggedin' in session and session['level']=="admin":
    args = request.args
    sel_id = args.get('value')
   
   
    conn.execute('DELETE FROM student WHERE id = "'+sel_id+'"')              
    conn.commit()
    
    #returning back to seestudents 
    return redirect(url_for('student_blueprint.seestudents'))  
  else:
        return redirect(url_for('login'))
'''        