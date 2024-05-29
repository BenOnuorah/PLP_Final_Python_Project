import sqlite3 
import os
dir_path = os.path.dirname(os.path.realpath(__file__))

def connect_db():
		#create and connect to the database
		db = sqlite3.connect(dir_path+'/school_app.db', check_same_thread=False) 
		return db