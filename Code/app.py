import subprocess
from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import sys

app = Flask(__name__)

connect = sqlite3.connect('database.db')
connect.execute('''
    CREATE TABLE IF NOT EXISTS credentials (
    username TEXT UNIQUE,
    password TEXT
    )
    ''')

connect.close()

@app.route('/')
def index():
    return render_template("index.html")



@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        with sqlite3.connect("database.db") as users:
            cursor = users.cursor()
            try:
                cursor.execute("INSERT INTO credentials \
            (username, password) VALUES (?,?)", (username, password))
                users.commit()
                return render_template("login.html", message="Registration Successfull!")
            except:
               return render_template("login.html", message="That username is already exist.")

    else:
        return render_template("login.html")



#Authentication-Based SQLi
@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        with sqlite3.connect("database.db") as users:
            cur = users.cursor()
            
            try:
                #Vulnerable
                cur.execute(f"SELECT * FROM credentials WHERE username = '{username}' " \
                f"AND password = '{password}'")
                res = cur.fetchone()
            except Exception as e:
                return f'DB_ERROR: {str(e)}'  
            
            #How it should be:
            """
            cur.execute('SELECT * FROM credentials WHERE username = ? AND password = ?',
            (username, password),)
            """
            
        if res:
            return render_template("login.html", message="Login Successfull!")
        else:
            return render_template("login.html", message="Password or Username is incorrect.")
    else:
        return render_template("login.html")



#To test if db works properly.
@app.route('/data', methods=["GET", "POST"])
def data():
    if request.method == "POST":
        username = request.form['username']
        with sqlite3.connect('database.db') as users:
            cur = users.cursor()
            cur.execute("DELETE FROM credentials WHERE username = ?", (username,))
            users.commit()
        return redirect(url_for('data'))
     
    with sqlite3.connect('database.db') as users:
        cur = users.cursor()
        cur.execute('SELECT * FROM credentials')
        data = cur.fetchall()

    return render_template("users.html", data=data)

#Running test_sqli.py
@app.route('/run-sqli-test')
def run_sqli_test():
    test_name = request.args.get('test', 'boolean')
    if test_name not in ('auth', 'union', 'boolean'):
       return {"stdout": "", "stderr": f"Unknown test:{test_name}"}, 400


    try:
        result = subprocess.run(
            [sys.executable, 'test_sqli.py', test_name],
            capture_output=True, text=True, timeout=15
        )
    except subprocess.TimeoutExpired:
       return {"stdout": "", "stderr": "test_sqli.py did not finish within 15 seconds."}, 504

    return {"stdout": result.stdout, "stderr": result.stderr}


#UNION-BASED SQLi
@app.route('/search', methods=['GET', 'POST'])
def search():
  results = []
  if request.method == 'POST':
    keyword = request.form['keyword']
    with sqlite3.connect('database.db') as users:
      cur = users.cursor()
      # VULNERABLE
      query = f"SELECT username FROM credentials WHERE username LIKE '%{keyword}%'"
      cur.execute(query)
      results = cur.fetchall()

  return render_template('search.html', results=results)



#Boolean-Based&Error-Based
#Usage: http://127.0.0.1:5000/check?username=JohnDoe
@app.route('/check')
def check():
  username = request.args.get('username')

  if username is None:
    return render_template('check.html')

  with sqlite3.connect('database.db') as users:
    cur = users.cursor()

    # VULNERABLE
    try:
      cur.execute(f"SELECT * FROM credentials WHERE username = '{username}'")
      res = cur.fetchone()

      if res:
        return 'User Exist.'
      
      else:
        return 'User could not found.'
      
    except Exception as e:
      # Error-based 
      return f'DB_ERROR: {str(e)}'
    
if __name__ == '__main__':
    app.run(threaded=True)
