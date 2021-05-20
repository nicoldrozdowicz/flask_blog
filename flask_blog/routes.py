from flask import flash, redirect, render_template, request, url_for
from flask_blog import app, bcrypt, db
from flask_blog.forms import LoginForm, PostForm, RegistrationForm, UpdateAccountForm
from flask_blog.models import Post, User
from flask_login import current_user, login_required, login_user, logout_user
from PIL import Image

import secrets
import os

@app.route("/")
@app.route("/home")
def home():
  posts = Post.query.all()
  return render_template('home.html', title='Home', posts=posts)

@app.route("/register", methods=['GET', 'POST'])
def register():
  form = RegistrationForm()

  if form.validate_on_submit():
    hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
    user = User(username=form.username.data, email=form.email.data, password=hashed_password)

    db.session.add(user)
    db.session.commit()

    flash(f'Your account has been created. You are now able to login.', 'success')
    return redirect(url_for('login'))

  return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
  form = LoginForm()

  if form.validate_on_submit( ):
    user = User.query.filter_by(email=form.email.data).first()
    if user and bcrypt.check_password_hash(user.password, form.password.data):
      login_user(user, remember=form.remember.data)
      return redirect(url_for('home'))
    else:
      flash('Login Unsuccessful. Please check email and password', 'danger')

  return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
  logout_user()
  return redirect(url_for('home'))

def save_image_file(image_file):
  random_hex = secrets.token_hex(8)
  _, image_file_extension = os.path.splitext(image_file.filename)

  new_image_file_name = random_hex + image_file_extension
  new_image_file_path = os.path.join(app.root_path, 'static/profile_pictures', new_image_file_name)

  new_image = Image.open(image_file)
  new_image.thumbnail((125, 125))
  new_image.save(new_image_file_path)

  return new_image_file_name

@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
  form = UpdateAccountForm()

  if form.validate_on_submit():
    current_user.username = form.username.data
    current_user.email = form.email.data
    if form.image_file.data:
      image_file = save_image_file(form.image_file.data)
      current_user.image_file = image_file
  
    db.session.commit()

    flash('Your account has been updated.', 'success')
    return redirect(url_for('account'))

  form.username.data = current_user.username
  form.email.data = current_user.email
  image_file = url_for('static', filename = 'profile_pictures/' + current_user.image_file)

  return render_template('account.html', title = 'Account', image_file = image_file, form = form)

@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def create_post():
  form = PostForm()

  if form.validate_on_submit():
    post = Post(title=form.title.data, content=form.content.data, user=current_user)

    db.session.add(post)
    db.session.commit()

    flash('Your post has been created!', 'success')
    return redirect(url_for('home'))
  
  return render_template('create_post.html', title = "New Post", form = form)
