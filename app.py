from flask import Flask, render_template,request, redirect, url_for, session,flash, send_file
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy





app = Flask(__name__)
app.secret_key = "9Tempest"
app.permanent_session_lifetime = timedelta(minutes=5)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class users(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    message = db.Column(db.String(100))

    def __init__(self, name, email, message):
        self.name = name
        self.email = email
        self.message = message



@app.route("/")
def index():
    return redirect(url_for("login"))

@app.route("/login",methods=['GET', 'POST'] )
def login():
    if request.method == "POST":
        session.permanent_session_lifetime = True
        user = request.form["nm"]
        session["user"] = user
        found_user = users.query.filter_by(name = user).first()
        if found_user:
            session["email"] = found_user.email
        else:
            usr = users(user, "", "")
            db.session.add(usr)
            db.session.commit()

        return redirect(url_for("user"))
    else:
        if "user" in session:
            user = session["user"]
            return redirect(url_for("user"))
        return render_template("login.html")

@app.route("/user", methods=['GET', 'POST'])
def user():
    email = None
    message = None
    name = None
    if "user" in session:
        user = session["user"]

        if request.method == "POST" and "name" not in request.form:
            with open("resume.pdf") as f:
                return send_file(f, attachment_filename="resume.pdf", as_attachment=True)
        elif request.method == "POST":
            email = request.form["email"]
            session["email"] = email
            name = request.form["name"]
            session["name"] = name
            message = request.form["message"]
            found_user = users.query.filter_by(name = user).first()
            found_user.email = email
            found_user.message = message
            db.session.commit()
        else:
            if "email" in session:
                email = session["email"]
            if "name" in session:
                name = session["name"]
            if "message" in session:
                message = session["message"]
        return render_template("index.html", user=user, email=email, name=user)
    else:
        return redirect(url_for("login"))

@app.route("/logout")
def logout():
    if "user" in session:
        user = session["user"]
        flash(f"You have been logged out, {user}", "info")
    session.pop("user", None)
    session.pop("name", None)
    session.pop("email", None)
    flash("")
    return redirect(url_for("login"))

@app.route("/view")
def view():
    return render_template("view.html", values=users.query.all())

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)