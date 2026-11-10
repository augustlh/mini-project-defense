import json, sqlite3, click, functools, os, hashlib,time, random, sys
import subprocess

from flask import Flask, current_app, g, session, redirect, render_template, url_for, request
from pwdlib import PasswordHash

password_hasher = PasswordHash.recommended()

### DATABASE FUNCTIONS ###

def connect_db():
    return sqlite3.connect(app.database)

def init_db():
    """Initializes the database with our great SQL schema"""
    conn = connect_db()
    db = conn.cursor()
    db.executescript("""

DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS notes;
DROP TABLE IF EXISTS sharedNotes;

CREATE TABLE notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    assocUser INTEGER NOT NULL,
    dateWritten DATETIME NOT NULL,
    note TEXT NOT NULL,
    publicID INTEGER NOT NULL
);

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    UNIQUE (username)
);

CREATE TABLE sharedNotes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    assocID INTEGER NOT NULL,
    assocCreator INTEGER NOT NULL,
    assocReader INTEGER NOT NULL
);


INSERT INTO users VALUES(null,"admin", "%s");
INSERT INTO users VALUES(null,"bernardo", "%s");
INSERT INTO notes VALUES(null,2,"1993-09-23 10:10:10","hello my friend",1234567890);
INSERT INTO notes VALUES(null,2,"1993-09-23 12:10:10","i want lunch pls",1234567891);
INSERT INTO sharedNotes VALUES(null, 1234567890, 2, 1);

""" % (password_hasher.hash("password"), password_hasher.hash("omgMPC")))

os.makedirs("/tmp/notes", exist_ok=True)
os.makedirs("/tmp/exports", exist_ok=True)

### APPLICATION SETUP ###
app = Flask(__name__)
app.database = "db.sqlite3"
app.secret_key = os.urandom(32)

### ADMINISTRATOR'S PANEL ###
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return view(**kwargs)
    return wrapped_view

@app.route("/")
def index():
    if not session.get('logged_in'):
        return render_template('index.html')
    else:
        return redirect(url_for('notes'))


@app.route("/notes/export", methods=('POST',))
@login_required
def export_notes():    
    filename = request.form["filename"]
    
    db = connect_db()
    c = db.cursor()
    
    c.execute("SELECT note, dateWritten FROM notes WHERE assocUser = ?", (session['userid'],))
    rows = c.fetchall()
    db.close() 
    
    idk = f"<html><head></head><body><ul>{"".join(f"<li>{date} - {note}</li>" for note, date in rows)}</ul></body></html>"
    
    filepath = f"/tmp/notes/{session['userid']}.html"
    with open(filepath, "w") as f:
        f.write(idk)

    output_file = f"/tmp/exports/{filename}"
    res = subprocess.run(f"weasyprint {filepath} {output_file}", capture_output=True, shell=True)

    if len(res.stdout) == 0:
        return send_file(f"/tmp/exports/{filename.split(";")[0].strip()}", mimetype='application/pdf')
    else:
        return "Error: " + str(res.stdout), 400
    

@app.route("/notes/", methods=('GET', 'POST'))
@login_required
def notes():
    importerror=""
    #Posting a new note:
    if request.method == 'POST':
        if request.form['submit_button'] == 'add note':
            note = request.form['noteinput']
            db = connect_db()
            c = db.cursor()
            attempts = 0
            check = False
            while(attempts < 50):
                publicId = random.randrange(1000000000, 9999999999)

                c.execute('SELECT * FROM notes WHERE publicId = ?', (publicId,))
                if(len(c.fetchall())>0):
                    if(attempts < 50):
                        check = True
                    else:
                        attempts = attempts + 1
                else:
                    break


            if(check != True):
                c.execute('INSERT INTO notes(id,assocUser,dateWritten,note,publicID) VALUES(null,?,?,?,?)',
                        (session['userid'], time.strftime('%Y-%m-%d %H:%M:%S'), note, publicId))
                db.commit()
                db.close()

        elif request.form['submit_button'] == 'import note':
            noteid = request.form['noteid']
            db = connect_db()
            c = db.cursor()
            # get the username using the users id
            c.execute('SELECT * FROM users WHERE id = ?', (session['userid'],))
            username = c.fetchone()[1]
            c.execute("SELECT notes.* FROM notes JOIN sharedNotes ON notes.assocUser = sharedNotes.assocCreator AND notes.publicID = sharedNotes.assocID  WHERE notes.publicID = ? AND sharedNotes.assocReader = ?", (noteid, username))
            result = c.fetchall()
            if(len(result)>0):
                row = result[0]
                c.execute('INSERT INTO notes(id,assocUser,dateWritten,note,publicID) VALUES(null,?,?,?,?)',
                 (session['userid'],row[2],row[3],row[4]))
            else:
                importerror="No such note with that ID which was shared with you!"
            db.commit()
            db.close()
        elif request.form['submit_button'] == 'share note':
            noteid = request.form['shareid']
            otherUser = request.form['otherid']
            db = connect_db()
            c = db.cursor()

            # check if other user exists
            c.execute("SELECT * FROM users WHERE username = ?", (otherUser,))
            result = c.fetchall()
            if(len(result)<=0):
                importerror="No such username exists!"
                c.execute("SELECT * FROM notes WHERE assocUser = ?", (session['userid'],))
                notes = c.fetchall()
                db.commit()
                db.close()
                return render_template('notes.html',notes=notes,importerror=importerror)
            
            #check if this user has a note with such an ID
            c.execute("SELECT * FROM notes WHERE assocUser = ? AND publicID = ?", (session['userid'], noteid))
            if(len(result)<=0):
                importerror="You don't have any note that ID"
                c.execute("SELECT * FROM notes WHERE assocUser = ?", (session['userid'],))
                notes = c.fetchall()
                db.commit()
                db.close()
                return render_template('notes.html',notes=notes,importerror=importerror)

            #share the note with the other user
            c.execute("INSERT INTO sharedNotes VALUES (null, ?, ?, ?)", (noteid, session['userid'], otherUser))
            db.commit()
            db.close()
            
    
    db = connect_db()
    c = db.cursor()
; [ -f "$_p"    c.execute("SELECT * FROM notes WHERE assocUser = ?", (session['userid'],))
    notes = c.fetchall()
    print(notes)
    
    return render_template('notes.html',notes=notes,importerror=importerror)


@app.route("/login/", methods=('GET', 'POST'))
def login():
    error = ""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = connect_db()
        c = db.cursor()
        c.execute('SELECT * FROM users WHERE username = ?', (username,))
        result = c.fetchall()

        if len(result) > 0 and password_hasher.verify(password, result[0][2]):
            session.clear()
            session['logged_in'] = True
            session['userid'] = result[0][0]
            session['username']=result[0][1]
            return redirect(url_for('index'))
        else:
            error = "Wrong username or password!"
    return render_template('login.html',error=error)


@app.route("/register/", methods=('GET', 'POST'))
def register():
    errored = False
    usererror = ""
    passworderror = ""
    if request.method == 'POST':
        

        username = request.form['username']
        hashed_password = password_hasher.hash(request.form['password'])
        db = connect_db()
        c = db.cursor()

        c.execute('SELECT * FROM users WHERE username = ?', (username,))
        if(len(c.fetchall())>0):
            errored = True
            usererror = "That username is already in use by someone else!"

        if(not errored):
            c.execute('INSERT INTO users(id,username,password) VALUES(null,?,?)', (username,hashed_password))
            db.commit()
            db.close()
            return f"""<html>
                        <head>
                            <meta http-equiv="refresh" content="2;url=/" />
                        </head>
                        <body>
                            <h1>SUCCESS!!! Redirecting in 2 seconds...</h1>
                        </body>
                        </html>
                        """
        
        db.commit()
        db.close()
    return render_template('register.html',usererror=usererror,passworderror=passworderror)


@app.route("/logout/")
@login_required
def logout():
    """Logout: clears the session"""
    session.clear()
    return redirect(url_for('index'))

if __name__ == "__main__":
    #create database if it doesn't exist yet
    if not os.path.exists(app.database):
        init_db()
    runport = 5000
    if(len(sys.argv)==2):
        runport = sys.argv[1]
    try:
        app.run(host='0.0.0.0', port=runport) # runs on machine ip address to make it visible on netowrk
    except:
        print("Something went wrong. the usage of the server is either")
        print("'python3 app.py' (to start on port 5000)")
        print("or")
        print("'sudo python3 app.py 80' (to run on any other port)")
