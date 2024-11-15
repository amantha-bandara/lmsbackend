from flask import Flask, request, render_template, flash, redirect, url_for, session, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from flask_uploads import UploadSet, configure_uploads, IMAGES
import random
import string
from authlib.integrations.flask_client import OAuth
import logging
from flask_session import Session
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

# Flask configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_BINDS'] = {'admins': 'sqlite:///admins.db'}
app.config['SECRET_KEY'] = 'gbjwk34tjkb!@#$%^&*()6328964789tjkvgabsbgwegbkbdk!(%R$)'
app.config['UPLOADED_IMAGES_DEST'] = 'static/uploads'
app.config['SERVER_NAME'] = '127.0.0.1:5000'

# File upload setup
images = UploadSet('images', IMAGES)
configure_uploads(app, images)

# Initialize extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
oauth = OAuth(app)

# OAuth state generator
def generate_state():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=16))

# Google OAuth client setup
google = oauth.register(
    name='google',
    client_id='591740958219-snu37ejp24t4pbfe665tsdg6pqhf86ba.apps.googleusercontent.com',
    client_secret='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',
    server_metadata_uri='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile https://www.googleapis.com/auth/userinfo.email'},
    authorize_url='https://accounts.google.com/o/oauth2/auth'
)

# LinkedIn OAuth client setup
linkedin = oauth.register(
    name='linkedin',
    client_id='86vaqdmhlqom3o',
    client_secret='WPL_AP1.o1Fb4IS8rw1aQGOf.aYpVmw==',
    authorize_url='https://www.linkedin.com/oauth/v2/authorization',
    access_token_url='https://www.linkedin.com/oauth/v2/accessToken',
    client_kwargs={'scope': 'openid profile email'}
)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# User model
class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    grade = db.Column(db.Integer, nullable=False)
    t_no = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=True, unique=True)
    NIC = db.Column(db.String, nullable=True)
    pic = db.Column(db.String, nullable=True)
    status = db.Column(db.Integer, default=0, nullable=False)

    def __repr__(self):
        return f"<User {self.first_name} {self.last_name}>"

# Admin model
class Admin(db.Model, UserMixin):
    __bind_key__ = 'admins'
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f'Admin("{self.username}", "{self.id}")'

# Routes
@app.route('/')
def main():
    return render_template('main.html')

# Registration route
@app.route('/register', methods=['GET', 'POST'])
def reg():
    if request.method == 'POST':
        fm = request.form['f_name']
        lm = request.form['l_name']
        ga = request.form['grade']
        t = request.form['t_no']
        em = request.form['email']
        pa = request.form['password']
        nic = request.form['NIC']
        
        hp2 = bcrypt.generate_password_hash(pa)
        if em and pa:
            if 1 <= int(ga) <= 13:
                if 1 <= len(t) <= 10:
                    if len(pa) >= 8:
                        if not User.query.filter_by(email=em).first():
                            new_user = User(first_name=fm, last_name=lm, grade=ga, t_no=t, email=em, password=hp2, NIC=nic)
                            db.session.add(new_user)
                            db.session.commit()
                            flash('Registration successful! Please login.')
                            return redirect(url_for('login'))
                        else:
                            flash('Email already registered')
                    else:
                        flash('Password must be at least 8 characters')
                else:
                    flash('Invalid phone number')
            else:
                flash('Grade must be between 1 and 13')
        else:
            flash('Please fill out all fields')
    return render_template('register.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        ema = request.form['email']
        pas = request.form['password']

        if ema and pas:
            user = User.query.filter_by(email=ema).first()
            if user:
                if user.status == 1:  # Approved users only
                    if bcrypt.check_password_hash(user.password, pas):
                        login_user(user)
                        flash('Login successful')
                        return redirect(url_for('profile'))
                    else:
                        flash("Incorrect password")
                else:
                    flash("Account pending approval")
            else:
                flash("User does not exist")
        else:
            flash('Please fill in both fields')
    return render_template('login.html')

# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully')
    return redirect(url_for('login'))

# Profile route
@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

# Update route
@app.route('/update', methods=['GET', 'POST'])
@login_required
def update():
    return render_template('update.html')
@app.route('/backtoprofile', methods=['GET', 'POST'])

def backtoprofile():
    return redirect(url_for('profile'))

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}



@app.route('/updateprofile', methods=['POST', 'GET'])
@login_required
def updateprofile():
    if request.method == 'POST':
        # Get the current user record
        pd = User.query.get(current_user.id)

        # Get form data
        fn = request.form['first_name']
        ln = request.form['last_name']
        ga = request.form['grade']
        nic = request.form['nic']
        tn = request.form['t_no']
        em = request.form['email']
        pa = request.form['password']
        pic = request.files.get('reciept')

        # Handle password update
        if pa:
            hashed_password = bcrypt.generate_password_hash(pa).decode('utf-8')
            pd.password = hashed_password

        # Handle picture upload
        if pic and '.' in pic.filename:
            ext = pic.filename.rsplit('.', 1)[1].lower()
            if ext in ALLOWED_EXTENSIONS:
                filename = secure_filename(pic.filename)
                pic.save(os.path.join(app.config['UPLOADED_IMAGES_DEST'], filename))
                pd.pic = filename
            else:
                flash('Only JPG, JPEG, and PNG files are allowed.')
                return redirect(url_for('update'))  # Return to update page if file is invalid

        # Update user information
        pd.first_name = fn
        pd.last_name = ln
        pd.grade = ga
        pd.NIC = nic
        pd.t_no = tn
        pd.email = em

        try:
            db.session.commit()  # Commit the changes to the database
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('profile'))  # Redirect to profile page after update
        except Exception as e:
            flash(f'An error occurred: {e}', 'danger')
            return render_template('update.html')  # Stay on the update page if there's an error

    # If GET request, just show the update form
    return render_template('update.html')  # Render update form for the user


# Google login route
@app.route('/login/google')
def login_google():
    try:
        state = generate_state()  # Generate a random state
        session['oauth_state'] = state  # Store state in session
        redirect_uri = url_for('authorized', _external=True)
        return oauth.google.authorize_redirect(redirect_uri)
    except Exception as e:
        flash('Something went wrong. Please try again later.', 'danger')
        return redirect(url_for('login'))

# Google OAuth callback
@app.route('/authorized/google')
def authorized():
    try:
        received_state = request.args.get('state')
        stored_state = session.get('oauth_state')

        if received_state != stored_state:
            flash('State mismatch error', 'danger')
            session.clear()
            return redirect(url_for('login'))

        token = oauth.google.authorize_access_token()
        user = oauth.google.parse_id_token(token)
        session['google_id'] = user['sub']  # Store the Google user ID in session
        flash(f'Welcome, {user["name"]}!', 'success')
        return redirect(url_for('profile'))
    except Exception as e:
        flash('Failed to authenticate with Google. Please try again later.', 'danger')
        return redirect(url_for('login'))

# Admin section
@app.route('/admin')
def admin():
    return render_template('admin/welcome.html')

@app.route('/logoutadmin')
def logoutadmin():
    logout_user()
    return redirect(url_for('login'))

# Admin Dashboard route
@app.route('/admin/dashboard')
def admin_dashboard():
    total_user = User.query.count()
    total_approved = User.query.filter_by(status=1).count()
    total_pending = User.query.filter_by(status=0).count()
    return render_template('admin/admindashboard.html', title="Admin Dashboard", 
                           total_user=total_user, total_approved=total_approved, total_pending=total_pending)

@app.route('/admin/get-all-user', methods=["POST", "GET"])
def admin_get_all_user():
    search = request.form.get('search') if request.method == "POST" else None
    users = User.query.filter(User.first_name.like(f'%{search}%')).all() if search else User.query.all()
    return render_template('admin/all.html', title='Approve User', users=users)

@app.route('/admin/approve-user/<int:id>')
def admin_approve(id):
    user = User.query.get(id)
    if user:
        user.status = 1
        db.session.commit()
        flash('User approved successfully', 'success')
    else:
        flash('User not found', 'danger')
    return redirect(url_for('admin_get_all_user'))

def create_db():
    with app.app_context():
        db.create_all()

create_db()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    app.run(debug=True)
