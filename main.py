# import statements
from flask import Flask, render_template, redirect, url_for, request, flash, abort
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from webform import ContactForm, ContentForm, SignIn, EditForm, Registration
from flask_bootstrap import Bootstrap5
from messages import Messages
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import mapped_column, DeclarativeBase, Mapped
from sqlalchemy import String, Integer, Float
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required
import os


app = Flask(__name__)
app.secret_key = os.environ.get('secret')

bootstrap = Bootstrap5(app)

messages = Messages()

date = datetime.now()

# Configure Flask-Login's Login Manager
login_manager = LoginManager(app)
login_manager.init_app(app)


# Create a user_loader callback
@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


# Database Section:


class Base(DeclarativeBase):
    pass


# Pass a subclass of either DeclarativeBase or DeclarativeBaseNoMeta to the constructor

db = SQLAlchemy(model_class=Base)

# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"

# initialize the app with the extension
db.init_app(app)


# create table model:

class Gallery(UserMixin, db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    header: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    paragraph: Mapped[str] = mapped_column(String(100), nullable=False)
    image: Mapped[str] = mapped_column(String(250), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)


class User(db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(100), nullable=False)
    password: Mapped[str] = mapped_column(String(100), nullable=False)


# create table in database
with app.app_context():
    db.create_all()


@app.route('/')
def home():
    portfolio_items = db.session.execute(db.select(Gallery).order_by(Gallery.id)).scalars()

    return render_template('index.html', year=date.year, columns=portfolio_items, current_user=current_user)


@app.route('/about')
def about():
    return render_template('about.html', current_user=current_user)


@app.route('/services')
def services():
    return render_template('services.html', current_user=current_user)


@app.route("/contact", methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    msg = f'Subject: {form.subject.data} \n\n {form.message.data}'

    if form.validate_on_submit():
        messages.send_mail(address=form.email.data, message=msg)
        return redirect(url_for('contact'))

    return render_template('contact.html', form=form, current_user=current_user)


@app.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    form = ContentForm()

    if form.validate_on_submit():
        thumbnail = Gallery(header=form.header.data, paragraph=form.paragraph.data, image=form.image.data,
                            category=form.category.data)
        db.session.add(thumbnail)
        db.session.commit()

    return render_template('add.html', form=form, current_user=current_user)


@app.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    id_num = request.args.get('id')

    item_obj = db.get_or_404(Gallery, id_num)

    form = EditForm(header=item_obj.header, paragraph=item_obj.paragraph, image=item_obj.image,
                    category=item_obj.category)

    if form.validate_on_submit():
        item_obj.header = form.header.data
        item_obj.paragraph = form.paragraph.data
        item_obj.image = form.image.data
        item_obj.category = form.category.data
        db.session.commit()

        return redirect(url_for('home'))

    return render_template('edit.html', form=form, current_user=current_user)


@app.route('/delete', methods=['GET', 'POST'])
@login_required
def delete():
    id_num = request.args.get('id')

    item_obj = db.get_or_404(Gallery, id_num)

    db.session.delete(item_obj)
    db.session.commit()

    return redirect(url_for('home'))


@app.route('/signin', methods=["GET", "POST"])
def sigin():
    form = SignIn()
    if form.validate_on_submit():
        password = form.password.data
        result = db.session.execute(db.select(User).where(User.email == form.email.data))
        # Note, email in db is unique so will only have one result.
        user = result.scalar()
        # Email doesn't exist
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('signin'))
        # Password incorrect
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for('signin'))
        else:
            login_user(user)
            return redirect(url_for('home'))

    return render_template("signin.html", form=form, current_user=current_user)


@app.route('/register', methods=["GET", "POST"])
def register():
    form = Registration()
    if form.validate_on_submit():

        # Check if user email is already present in the database.
        result = db.session.execute(db.select(User).where(User.email == form.email.data))
        user = result.scalar()
        if user:
            # User already exists
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))

        hash_and_salted_password = generate_password_hash(
            form.password.data,
            method='pbkdf2:sha256',
            salt_length=8
        )
        new_user = User(
            email=form.email.data,
            username=form.username.data,
            password=hash_and_salted_password,
        )
        db.session.add(new_user)
        db.session.commit()
        # This line will authenticate the user with Flask-Login
        login_user(new_user)
        return redirect(url_for("home"))
    return render_template("register.html", form=form, current_user=current_user)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
