import os

from flask import Flask, render_template, session, request, redirect
from flask_session import Session
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required
import sqlite3

app = Flask(__name__)
conn = sqlite3.connect('bergonline.db', check_same_thread=False)

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route("/")
def index():

    with conn: 
        cursor = conn.cursor()
        data = cursor.execute("SELECT * FROM menu_data")
    
    return render_template("index.html", data=data)

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Ensure confirmation was submitted
        elif not request.form.get("confirmation"):
            return apology("must provide confirmation", 400)

        # Ensure password and confirmation are the same
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("password does not match", 400)

        with conn:
            
            cursor = conn.cursor()

            # Ensure username does not already exist
            cursor.execute("SELECT * FROM users WHERE username = ?", (request.form.get("username"),))
            row = cursor.fetchone()
            if row is not None:
                return apology("username already exists", 400)


            # Insert username and password into database
            userpass = cursor.execute("INSERT or IGNORE INTO users (username, hash) VALUES (?, ?)", (request.form.get("username"), generate_password_hash(request.form.get("password"))))

            # Query database for username
            cursor.execute("SELECT * FROM users WHERE username = ?", (request.form.get("username"),))

            # Remember which user has logged in
            session["user_id"] = cursor.fetchall()[0][0]

            conn.commit()

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

@app.route("/nutrition", methods=["GET", "POST"])
@login_required
def nutrition():

    if request.method == "POST":

        name = request.form.get("name")

        # Find the cash the user has at the moment
        with conn: 
            cursor = conn.cursor()
            search = cursor.execute("SELECT * FROM menu_data WHERE name = ?", (name,))

        # Redirect user to home page
        return render_template("index.html", data=search)

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("nutrition.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        with conn:
            
            cursor = conn.cursor()
        
            # Query database for username
            cursor.execute("SELECT * FROM users WHERE username = ?", (request.form.get("username"),))
            row = cursor.fetchone()
            # Ensure username exists and password is correct
            
            if row is None:
                return apology("invalid username", 400)
            if not (check_password_hash(row[2],request.form.get("password"))):
                return apology("invalid password", 400)

            cursor.execute("SELECT * FROM users WHERE username = ?", (request.form.get("username"),))
            session["user_id"] = cursor.fetchall()[0][0]

            conn.commit()

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")