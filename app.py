from flask import Flask, render_template, request, session, url_for, redirect
import re 


from conn_database import connect_db
conn = connect_db()

	

from student_blueprint import student_blueprint
from authentication_blueprint import auth_bp
from subject_blueprint import subject_blueprint
from class_blueprint import class_blueprint
from lesson_blueprint import lesson_blueprint
from lesson_more_blueprint import lesson_more_blueprint
from lesson_assignment_blueprint import lesson_assignment_blueprint
from teacher_blueprint import teacher_blueprint
from scheme_of_work_blueprint import scheme_of_work_blueprint
from assessment_blueprint import assessment_blueprint
from performance_blueprint import performance_blueprint


app = Flask(__name__) 
app.secret_key = 'your secret key'

#register blueprints
app.register_blueprint(student_blueprint)
app.register_blueprint(auth_bp)
app.register_blueprint(subject_blueprint)
app.register_blueprint(class_blueprint)
app.register_blueprint(lesson_blueprint)
app.register_blueprint(lesson_more_blueprint)
app.register_blueprint(lesson_assignment_blueprint)
app.register_blueprint(teacher_blueprint)
app.register_blueprint(scheme_of_work_blueprint)
app.register_blueprint(assessment_blueprint)
app.register_blueprint(performance_blueprint)

#load the home or index page
@app.route('/home') 
@app.route('/') 
def home(): 
  return render_template('index.html')

#user loggedin URL
@app.route('/auth') 
def auth(): 
  if 'loggedin' in session:     
      return render_template('auth.html')
  else:
      return redirect(url_for('home'))
        
if __name__ == '__main__': 
       app.run(debug=True)