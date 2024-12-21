from datetime import date
from flask import Flask, abort, render_template, redirect, url_for, flash
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from forms import RegisterForm, LoginForm, AddProductForm, ContactForm
from dotenv import load_dotenv
import datetime
import os

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("FLASK_KEY")
ckeditor = CKEditor(app)
Bootstrap5(app)

# Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


# CREATE DATABASE
class Base(DeclarativeBase):
    pass


app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///website.db"
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# CONFIGURE TABLES
# Create a User table for all your registered users
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(100))


class Product(db.Model):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    price: Mapped[float] = mapped_column(db.Float, nullable=False)
    image_url: Mapped[str] = mapped_column(String(300), nullable=True)  # Optional field for image links
    date_added: Mapped[datetime.date] = mapped_column(db.Date, default=date.today)


# with app.app_context():
#     db.create_all()


# Create an admin-only decorator
def admin_only(func):
    @wraps(func)
    def wrapper_function(*args, **kwargs):
        # If id is not 1 then return abort with 403 error
        if current_user.id != 1:
            return abort(403)
        # Otherwise continue with the route function
        return func(*args, **kwargs)

    return wrapper_function


@app.route('/')
def homepage():
    current_year = datetime.datetime.now().year

    return render_template('index.html', current_year=current_year)


# Register new users into the User database
@app.route('/register', methods=["GET", "POST"])
def register():
    current_year = datetime.datetime.now().year

    register_form = RegisterForm()
    if register_form.validate_on_submit():

        result = db.session.execute(db.select(User).where(User.email == register_form.email.data))
        user = result.scalar()
        if user:

            flash("Email already assigned to a user. Please login.")
            return redirect(url_for('login'))

        hash_and_salted_password = generate_password_hash(
            register_form.password.data,
            method='pbkdf2:sha256',
            salt_length=9
        )
        new_user = User(
            email=register_form.email.data,
            name=register_form.name.data,
            password=hash_and_salted_password,
        )
        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        return redirect(url_for("get_all_products"))
    return render_template("register.html", form=register_form, current_user=current_user, current_year=current_year)


@app.route('/login', methods=["GET", "POST"])
def login():
    current_year = datetime.datetime.now().year

    login_form = LoginForm()
    if login_form.validate_on_submit():
        password = login_form.password.data
        result = db.session.execute(db.select(User).where(User.email == login_form.email.data))

        user = result.scalar()

        if not user:
            flash("Email not recognised. Try again.")
            return redirect(url_for('login'))

        elif not check_password_hash(user.password, password):
            flash('Password invalid. Try again.')
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('get_all_products'))

    return render_template("login.html", form=login_form, current_user=current_user, current_year=current_year)


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    current_year = datetime.datetime.now().year
    contact_form = ContactForm()

    if contact_form.validate_on_submit():

        name = contact_form.name.data
        email = contact_form.email.data
        number = contact_form.number.data
        message = contact_form.message.data

        # try: with smtplib.SMTP("smtp.gmail.com", 587) as connection: connection.starttls() connection.login(
        # user=my_email, password=email_password) email_message = f"Subject:New Contact Form Submission\n\nName: {
        # name}\nEmail: {email}\nPhone Number: " \ f"{number}\nMessage:\n{message}" connection.sendmail(
        # from_addr=email, to_addrs=my_email, msg=email_message ) flash("Your message has been sent successfully!",
        # "success") except Exception as e: flash(f"An error occurred while sending your message: {e}", "danger")
        return redirect(url_for('contact'))

    return render_template("contact.html", form=contact_form, current_user=current_user, current_year=current_year)


@app.route('/about')
def about():
    current_year = datetime.datetime.now().year

    return render_template('about.html', current_year=current_year)


@app.route('/all-products')
def get_all_products():
    current_year = datetime.datetime.now().year

    return render_template('all_products.html', current_year=current_year)


@app.route('/product', methods=["GET", "POST"])
def product():
    current_year = datetime.datetime.now().year

    return render_template('product.html', current_year=current_year)


@app.route("/new-post", methods=["GET", "POST"])
@admin_only
def add_new_post():
    current_year = datetime.datetime.now().year
    form = AddProductForm()
    if form.validate_on_submit():
        new_product = Product(
            name=form.name.data,
            description=form.description.data,
            price=form.price.data,
            image_url=form.image_url.data,
            user=current_user,
            date_added=date.today().strftime("%B %d, %Y")
        )

        db.session.add(new_product)
        db.session.commit()
        return redirect(url_for("get_all_products"))
    return render_template("add_product.html", form=form, current_user=current_user, current_year=current_year)


@app.route('/checkout')
def checkout():
    current_year = datetime.datetime.now().year

    return render_template('checkout.html', current_year=current_year)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('get_all_products'))


if __name__ == '__main__':
    app.run(debug=True)

