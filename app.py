from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Feedback
from forms import RegisterForm, LoginForm, FeedbackForm
#from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///feedback"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False


connect_db(app)

toolbar = DebugToolbarExtension(app)

@app.route("/")
def home():
    """"""
    return redirect("/register")

@app.route("/register", methods=["GET", "POST"])
def show_register():
    """"""
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        new_user = User.register(username,
                        password,
                        email,
                        first_name,
                        last_name)
        db.session.add(new_user)
        db.session.commit()
        flash("You've successfully created an account.")
        session["username"] = new_user.username

        return redirect(f"/users/{new_user.username}")

    return render_template("register.html", form=form)

@app.route("/login", methods=["GET", "POST"])
def show_login():
    """"""
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)
        if user:
            flash(f"Welcome Back, {user.username}!")
            session['username'] = user.username
            return redirect(f"/users/{user.username}")
        else:
            form.username.errors = ["Invalid username/password."]

    return render_template("login.html", form=form)

@app.route("/users/<username>")
def secret(username):
    """"""
    if 'username' not in session:
        flash("Please login first!")
        return redirect("/login")
    elif session["username"] != username:
        flash("That page wasn't for you")
        return redirect(f"/users/{session['username']}")

    user = User.query.get_or_404(username)
    return render_template("secret.html", user=user)

@app.route("/logout")
def logout():
    """"""
    session.pop("username")
    return redirect("/")

@app.route("/users/<username>/delete", methods=["POST"])
def delete_user(username):
    """"""
    if 'username' not in session:
        flash("Please login first!")
        return redirect("/login")
    user = User.query.get_or_404(username)
    if session["username"] != user.username:
        flash("You are not authorized to delete this user!")
        return redirect(f"/users/{username}")

    db.session.delete(user)
    db.session.commit()
    flash("user deleted")
    session.pop("username")
    return redirect("/")


@app.route("/users/<username>/feedback/add", methods=["GET","POST"])
def add_feedback(username):
    """"""
    if 'username' not in session:
        flash("Please login first!")
        return redirect("/login")
    elif session["username"] != username:
        flash("That page wasn't for you")
        return redirect(f"/users/{session['username']}")
    form = FeedbackForm()
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        new_feedback = Feedback(title=title, content=content, user_username=session["username"])
        db.session.add(new_feedback)
        db.session.commit()
        flash("feedback added")
        return redirect(f"/users/{username}")
    return render_template("feedback.html", form=form)


@app.route("/feedback/<feedback_id>/update", methods=["GET","POST"])
def update_feedback(feedback_id):
    """"""

    feedback = Feedback.query.get_or_404(feedback_id)
    username = feedback.user_username
    if 'username' not in session:
        flash("Please login first!")
        return redirect("/login")
    elif session["username"] != username:
        flash("That page wasn't for you")
        return redirect(f"/users/{session['username']}")
    form = FeedbackForm()
    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data
        db.session.add(feedback)
        db.session.commit()
        flash("feedback updated")
        return redirect(f"/users/{username}")
    
    form.title.data = feedback.title
    form.content.data = feedback.content
    return render_template("feedback.html", form=form)

   

@app.route("/feedback/<feedback_id>/delete", methods=["POST"])
def delete_feedback(feedback_id):
    """"""

    feedback = Feedback.query.get_or_404(feedback_id)
    username = feedback.user_username
    if 'username' not in session:
        flash("Please login first!")
        return redirect("/login")
    elif session["username"] != username:
        flash("That page wasn't for you")
        return redirect(f"/users/{session['username']}")
    db.session.delete(feedback)
    db.session.commit()
    return redirect(f"/users/{username}")