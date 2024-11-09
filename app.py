from flask import Flask, request, render_template, flash,get_flashed_messages,redirect,url_for,session
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

@login_manager.user_loader
def load_user(user_id):
    
    return User.query.get(int(user_id))

      

class User(db.Model,UserMixin):
    id = db.Column(db.Integer,primary_key = True)
    first_name=db.Column(db.String,nullable  = False,unique = True)
    last_name=db.Column(db.String,nullable  = False,unique = True)
    email =db.Column(db.String,nullable = False ,unique =True)
    password=db.Column(db.String,nullable  = False)
      
@app.route('/')
def ma():
    flash('hello')
    
    return render_template('main.html')


@app.route('/register',methods =['GET','POST'])
def reg():
    
    if request.method == 'POST':
        fm = request.form['f_name']
        lm = request.form['l_name']
        em = request.form['email']
        pa = request.form['password']
        
        hp2= bcrypt.generate_password_hash(pa)
        if em and pa:
            user = User.query.filter_by(email =em).first()
            if  user is None:
                user = User(first_name=fm,last_name=lm,email=em,password =hp2)
                db.session.add(user)
                db.session.commit()
                return redirect(url_for('login'))
            else:
                flash('email already taken')
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
                    #session['email'] = ema
                    #session['password'] = pas
                    return render_template('home.html')
                else:
                    return render_template('login.html')
            else:
               flash('user does not exist')
               return render_template('login.html')
          else:
            flash('fill the form')
            return render_template('login.html')   
    else:
        return render_template('login.html')


















@app.cli.command('create_db')
def create_db():
    with app.app_context():
        db.create_all()



































































if __name__ == '__main__':
    app.run(debug=True)

