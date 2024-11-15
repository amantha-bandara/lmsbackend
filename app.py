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
from datetime import timedelta

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SECRET_KEY'] = 'gbjwk34tjkb!@#$%^&*()6328964789tjkvgabsbgwegbkbdk!(%R$)'  
app.config['UPLOADED_IMAGES_DEST'] = 'static/uploads'
app.config['SERVER_NAME'] = '127.0.0.1:5000' 
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = True

app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)  # Set session lifetime
app.config['SESSION_USE_SIGNER'] = True

Session(app)

Session(app)

images = UploadSet('images', IMAGES)  # Create an UploadSet for images
configure_uploads(app, images)
db = SQLAlchemy(app)

bcrypt = Bcrypt(app)

oauth = OAuth(app)

# Generate state function for CSRF protection
def generate_state():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=16))

# Registering Google OAuth client
google = oauth.register(
    name='google',
    client_id='591740958219-snu37ejp24t4pbfe665tsdg6pqhf86ba.apps.googleusercontent.com',
    client_secret='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',
    server_metadata_uri='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile https://www.googleapis.com/auth/userinfo.email'},
    authorize_url='https://accounts.google.com/o/oauth2/auth'  # Add this line
)

# Registering LinkedIn OAuth client
#linkedin = oauth.register(
    name='linkedin',
  # Replace with your LinkedIn Client ID   client_id='86vaqdmhlqom3o',  # Replace with your LinkedIn Client ID
     # Replace with your LinkedIn Client IDclient_secret='WPL_AP1.o1Fb4IS8rw1aQGOf.aYpVmw==',  # Replace with your LinkedIn Client Secret
    # Replace with your LinkedIn Client ID authorize_url='https://www.linkedin.com/oauth/v2/authorization',
    # Replace with your LinkedIn Client ID authorize_params=None,
    # Replace with your LinkedIn Client ID scope='openid profile email',
     # Replace with your LinkedIn Client IDaccess_token_url='https://www.linkedin.com/oauth/v2/accessToken',
     # Replace with your LinkedIn Client IDrefresh_token_url=None,
     # Replace with your LinkedIn Client IDclient_kwargs={'scope':'openid profile email'}
)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User loader for Flask-Login
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

    def __repr__(self):
        return f"<User {self.first_name} {self.last_name}>"

# Routes
@app.route('/')
def ma():
    return render_template('ban.html')

# Register route
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
            if int(ga) <= 13 and int(ga) > 0:
                if int(len(t)) <= 10 and int(len(t)) > 0:
                    if int(len(pa)) >= 8:
                        user = User.query.filter_by(email=em).first()
                        if user is None:
                            new_user = User(first_name=fm, last_name=lm, grade=ga, t_no=t, email=em, password=hp2, NIC=nic)
                            db.session.add(new_user)
                            db.session.commit()
                            return redirect(url_for('login'))
                        else:
                            flash('Invalid email')
                            return render_template('register.html')
                    else:
                        flash('Password must be greater than 8 characters')
                        return render_template('register.html')
                else:
                    flash('Invalid phone number')
                    return render_template('register.html')
            else:
                flash('Grade should be within the range of 1 - 13')
                return render_template('register.html')
        else:
            flash('Something wrong, maybe password')
            return render_template('register.html')
    else:
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
                if bcrypt.check_password_hash(user.password, pas):
                    login_user(user)
                    flash('Login successful')
                    return render_template('profile.html')
                else:
                    flash("Password doesn't match")
                    return render_template('login.html')
            else:
                flash('User does not exist')
                return render_template('login.html')
        else:
            flash('Fill the form')
            return render_template('login.html')
    else:
        return render_template('login.html')

# Logout route
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for('login'))

# Profile route
@app.route('/profile')
@login_required
def profile():
    if current_user.is_authenticated:
        return render_template('profile.html')
    else:
        return render_template('login.html')

# Update route
@app.route('/update', methods=['GET', 'POST'])
@login_required
def update():
    if current_user.is_authenticated:
        return render_template('update.html')
    else:
        return render_template('login.html')

# Update profile route
@app.route('/updateprofile', methods=['GET', 'POST'])
@login_required
def updateprofile():
    if current_user.is_authenticated:
        pd = User.query.get(current_user.id)

        if request.method == 'POST':
            # Get the form data
            fn = request.form['first_name']
            ln = request.form['last_name']
            ga = request.form['grade']
            nic = request.form['nic']
            tn = request.form['t_no']
            em = request.form['email']
            pa = request.form['password']
            pic = request.files['reciept']
            file = pic.filename

            # Handle password update (if provided)
            if pa:
                hashed_password = bcrypt.generate_password_hash(pa).decode('utf-8')  # Hash password
                pd.password = hashed_password  # Update password if provided

            # Handle profile picture update (if a file is uploaded)
            if pic:
                filename = images.save(pic)  # Save the file using UploadSet
                pd.pic = filename

            # Update other user details
            pd.first_name = fn
            pd.last_name = ln
            pd.grade = ga
            pd.NIC = nic
            pd.t_no = tn
            pd.email = em

            try:
                db.session.commit()  # Commit the changes to the database
                flash('Profile updated successfully!', 'success')  # Flash success message
                return redirect(url_for('profile'))  # Redirect to profile page after update
            except Exception as e:
                flash(f'An error occurred: {e}', 'danger')  # Flash any error
                return render_template('update.html')  # Stay on the update page if there's an error

    # If user is not authenticated, redirect to login page
    return redirect('/login')


@app.route('/login/google')
def login_google():
    try:
        state = generate_state()  # Generate a random state
        session['oauth_state'] = state  # Store state in session
        app.logger.info(f"Generated state: {state}")  # Log the generated state
        redirect_uri = url_for('authorized', _external=True)
        app.logger.info(f"Redirect URI: {redirect_uri}")
        return oauth.google.authorize_redirect(redirect_uri)
    except Exception as e:
        app.logger.error(f"Error during login: {str(e)}")
        flash('Something went wrong. Please try again later.', 'danger')
        return redirect(url_for('login'))


# Inside authorized
@app.route('/authorized/google')
def authorized():
    try:
        received_state = request.args.get('state')  # Get the state from the callback request
        stored_state = session.get('oauth_state')  # Get the state from the session

        app.logger.info(f"Received state: {received_state}")
        app.logger.info(f"Stored state: {stored_state}")

        if received_state != stored_state:
            app.logger.error(f"State mismatch: {received_state} != {stored_state}")
            flash('Invalid state parameter', 'danger')
            session.clear()  # Clear session to reset state and prevent further errors
            return redirect(url_for('login'))

        token = oauth.google.authorize_access_token()
        user = oauth.google.parse_id_token(token)
        session['google_id'] = user['sub']  # Store the Google user ID in session
        flash(f'Welcome, {user["name"]}!', 'success')
        return redirect(url_for('profile'))

    except Exception as e:
        app.logger.error(f"Error during callback: {str(e)}")
        flash('Failed to authenticate with Google. Please try again later.', 'danger')
        return redirect(url_for('login'))
    

if __name__ == '__main__':
    # Enable logging for debugging
    logging.basicConfig(level=logging.INFO)
    app.run(debug=True)
