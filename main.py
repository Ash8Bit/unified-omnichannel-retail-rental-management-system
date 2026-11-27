#!/bin/python

import os
import psycopg2
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()
app = Flask(__name__)
app.secret_key = os.urandom(24)

# Connect to database
def get_database_connection():
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
                raise RuntimeError("DATABASE_URL is not set!")
        return psycopg2.connect(database_url)


# Initialize dummy user if no record was found in the users table
def init_dummy_user():
	conn = get_database_connection()
	cur = conn.cursor()
	cur.execute("SELECT id FROM users WHERE username = %s;", ("admin",))
	if not cur.fetchone():
		hashed_pw = generate_password_hash("secret123")
		cur.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s);", ("admin", hashed_pw))
		conn.commit()
	cur.close()
	conn.close()

# Authentication
@app.route("/", methods=["GET", "POST"])
def login():
	if request.method == "POST":
		username = request.form.get("username", "").strip()
		password = request.form.get("password", "")

		if not username or not password:
			flash("Username and password are required")
			return render_template("login.html")

		conn = get_database_connection()
		cur = conn.cursor()
		cur.execute("SELECT id, password_hash FROM users WHERE username = %s", (username,))
		user = cur.fetchone()
		cur.close()
		conn.close()

		if user and check_password_hash(user[1], password):
			session["user_id"] = user[0]
			session["user_name"] = username
			return redirect(url_for("dashboard"))
		else:
			flash("Invalid username or password")

	return render_template("login.html")

# Dashboard
@app.route("/dashboard")
def dashboard():
	if "user_id" not in session:
		return redirect(url_for("login"))
	return render_template("dashboard.html", username=session.get("user_name"))

# Inventory Management
@app.route("/inventory")
def inventory():
	if "user_id" not in session:
		return redirect(url_for("login"))
	return render_template("inventory.html", username=session.get("user_name"))

# Rental Management
@app.route("/rental")
def rental():
	if "user_id" not in session:
		return redirect(url_for("login"))
	return render_template("rental.html", username=session.get("user_name"))

# Order Management
@app.route("/orders")
def orders():
	if "user_id" not in session:
		return redirect(url_for("login"))
	return render_template("orders.html", username=session.get("user_name"))

# Customer Management
@app.route("/customers")
def customers():
	if "user_id" not in session:
		return redirect(url_for("login"))
	return render_template("customers.html", username=session.get("user_name"))


# Logout
@app.route("/logout")
def logout():
	session.clear()
	return redirect(url_for("login"))

# Entry point
if __name__ == "__main__":
	init_dummy_user()
	app.run(debug=True)
