from flask import Flask, request, render_template, flash,get_flashed_messages,redirect,url_for,session,abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin,LoginManager,login_user,login_required,logout_user,current_user
from flask_bcrypt import Bcrypt




app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

app.config['SECRET_KEY'] = 'gbjwk34tjkb!@#$%^&*()6328964789tjkvgabsbgwegbkbdk!(%R$)'  
db = SQLAlchemy(app)

bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

#********************************************************
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
#************************************************************
def login_is_required(function):
    def wrapper(*arg,**kwargs):
        if'google_id' not in session:
            return abort(401)
        else:
            return function()
    return wrapper
#****************************************************************   
@app.route('/update',methods =['GET','POST'])
@login_required
def update():
    return render_template('update.html')
#************************************************************
@app.route('/backtoprofile')
def back():
    return redirect('profile')

#***************************************************************

class User(db.Model,UserMixin):
    id = db.Column(db.Integer,primary_key = True)
    first_name=db.Column(db.String,nullable  = False)
    last_name=db.Column(db.String,nullable  = False)
    grade =db.Column(db.Integer,nullable  = False)
    t_no = db.Column(db.Integer,nullable  = False)
    email =db.Column(db.String,nullable = False ,unique =True)
    password=db.Column(db.String,nullable  = False,unique = True)
    NIC = db.Column(db.String,nullable  = False,unique = True)

      
@app.route('/')
def ma():
    return render_template('main.html')


@app.route('/register',methods =['GET','POST'])
def reg():
    
    if request.method == 'POST':
        fm = request.form['f_name']
        lm = request.form['l_name']
        ga = request.form['grade']
        t = request.form['t_no']
        em = request.form['email']
        pa = request.form['password']
        nic = request.form['NIC']
        
        hp2= bcrypt.generate_password_hash(pa)
        if em and pa:
            if int(ga)<=13 and int(ga)>0:
                if int(len(t)) <=10 and int(len(t))>0:
                    user = User.query.filter_by(email =em).first()
                    if  user is None:
                        user = User(first_name=fm,last_name=lm,grade=ga,t_no=t,email=em,password =hp2,NIC=nic)
                        db.session.add(user)
                        db.session.commit()
                        return redirect(url_for('login'))
                    else:
                        flash('email already taken')
                        return render_template('register.html')
                else:
                    flash('invalid phone number')
                    return render_template('register.html')
            else:
                flash ('grade should be within the range of 1 - 13')
                return render_template('register.html')
            
        else:
            flash('somthing wrong maybe password')
            return render_template('register.html')
    else:
        
        return render_template('register.html')

@app.route('/login',methods = ['GET','POST'])
def login():
    if request.method == 'POST':
          ema = request.form['email']
          pas = request.form['password']
        
          if ema and pas:
            user = User.query.filter_by(email=ema).first()
            if user:
                if bcrypt.check_password_hash(user.password,pas):
                    login_user(user)
                    flash('login succesful')
                    
                    return render_template('profile.html')
                else:
                    flash("password doesn't match")
                    return render_template('login.html')
            else:
               flash('user does not exist')
               return render_template('login.html')
          else:
            flash('fill the form')
            return render_template('login.html')   
    else:
        
        return render_template('login.html')
@app.route('/logout',methods = ['GET','POST'])
def logout():
    logout_user()
    return render_template('login.html')

@app.route('/profile')
@login_required
def profile():
    if current_user.is_authenticated:
        return render_template('profile.html')
    else:
        return render_template('login.html')
        
    
@app.route('/courses')
@login_is_required
def course():
    return render_template('courses.html')

        











@app.cli.command('create_db')
def create_db():
    with app.app_context():
        db.create_all()

































































if __name__ == '__main__':
    app.run(debug=True)

