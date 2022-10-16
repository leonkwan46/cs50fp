from unicodedata import name
from flask import Flask, make_response, jsonify, redirect, request, session
from flask_session import Session
from flask_mysqldb import MySQL
from functools import wraps
from werkzeug.security import check_password_hash, generate_password_hash
from flask import g, request, redirect, url_for
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.config["TEMPLATES_AUTO_RELOAD"] = True

if __name__ == '__main__':
    app.run(debug=True)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# DB & MySQL Connection
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "quiz"
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function



# HomePage
@app.route("/user", methods=["GET", "POST"])
@login_required

def home():
    db = mysql.connection.cursor()
    user_id = session["user_id"]
    if request.method == "GET":
        db.execute("SELECT score_easy, score_medium, score_hard FROM users WHERE userID=(%s)",user_id)
        data = db.fetchall()
        return make_response(jsonify(data))



# LoginPage
@app.route("/login", methods=["GET", "POST"])
def login():

    session.clear()

    if not request.json["username"]:
        return make_response(jsonify({'errorMessage': 'Login failed'}), 401)
    if not request.json["password"]:
        return make_response(jsonify({'errorMessage': 'Login failed'}), 401)

    username = request.json["username"]
    password = request.json["password"]
    
    db = mysql.connection.cursor()
    db.execute("SELECT * FROM users WHERE username LIKE %s", [username])
    rows = db.fetchall()

    if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
        return make_response(jsonify({'errorMessage': 'Incorrect username or password'}), 401)

    session["user_id"] = rows[0]["userID"]
    return make_response(jsonify({'message': 'Login Success'}), 200)



# RegisterPage
@app.route("/register", methods=["GET", "POST"])
def register():

    session.clear()

    con = mysql.connection
    db = con.cursor()

    username = request.json["username"]
    password = request.json["password"]

    if not username:
        return make_response(jsonify({'errorMessage': 'Register failed'}), 401)
    if not password:
        return make_response(jsonify({'errorMessage': 'Register failed'}), 401)

    hash = generate_password_hash(password)
    try:
        db.execute("INSERT INTO users(username, hash, password) VALUES (%s,%s,%s)", (username, hash, password))
        con.commit()
        new_user = db.fetchall()
    except:
        return make_response(jsonify({'errorMessage': 'Account Existed!'}), 401)

    session["user_id"] = new_user
    return make_response(jsonify({'message': 'Register Success'}), 200)

# ForgetPassPage
@app.route("/forget", methods=["GET", "POST"])
@login_required

def forget():
    user_id = session["user_id"]
    con = mysql.connection
    db = con.cursor()

    newpass = request.json["newpass"]

    if not newpass:
        return make_response(jsonify({'errorMessage': 'Changed failed'}), 401)

    hash = generate_password_hash(newpass)
    try:
        db.execute("UPDATE users SET password = %s WHERE id = %s", (hash, user_id))
        con.commit()
    except:
        return make_response(jsonify({'errorMessage': 'Unsuccessful!'}), 401)

    return make_response(jsonify({'message': 'Changed Password Success'}), 200)

# ContactUs
@app.route("/contact", methods=["GET", "POST"])
def contact():
    
    con = mysql.connection
    db = con.cursor()

    name = request.json["name"]
    email = request.json["email"]
    subject = request.json["subject"]
    message = request.json["message"]

    try:
        db.execute("INSERT INTO message(name, email, subject, message) VALUES (%s,%s,%s,%s)", (name, email, subject, message))
        con.commit()
    except:
        return make_response(jsonify({'errorMessage': 'Try Again!'}), 401)
