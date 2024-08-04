from flask import render_template, url_for, flash, redirect, request
from app import app, db, bcrypt
from models import User, Ad, Category
from forms import RegistrationForm, LoginForm, AdForm
from flask_login import login_user, current_user, logout_user, login_required

@app.route("/")
@app.route("/home")
def home():
    ads = Ad.query.all()
    return render_template('home.html', ads=ads)

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=True)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/profile")
@login_required
def profile():
    return render_template('profile.html', title='Profile')

@app.route("/ad/new", methods=['GET', 'POST'])
@login_required
def new_ad():
    form = AdForm()
    form.category.choices = [(category.id, category.name) for category in Category.query.all()]
    if form.validate_on_submit():
        ad = Ad(title=form.title.data, description=form.description.data, price=form.price.data, author=current_user, category_id=form.category.data)
        db.session.add(ad)
        db.session.commit()
        flash('Your ad has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('create_ad.html', title='New Ad', form=form)

@app.route("/ad/<int:ad_id>")
def ad(ad_id):
    ad = Ad.query.get_or_404(ad_id)
    return render_template('ad_detail.html', title=ad.title, ad=ad)

@app.route("/ad/<int:ad_id>/favorite", methods=['POST'])
@login_required
def favorite_ad(ad_id):
    ad = Ad.query.get_or_404(ad_id)

    flash('Ad added to favorites!', 'success')
    return redirect(url_for('ad', ad_id=ad.id))

@app.route("/ad/<int:ad_id>/question", methods=['POST'])
@login_required
def ask_question(ad_id):
    ad = Ad.query.get_or_404(ad_id)
    question_content = request.form.get('question')

    flash('Question submitted!', 'success')
    return redirect(url_for('ad', ad_id=ad.id))
