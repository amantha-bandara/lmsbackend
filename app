from flask import Flask, request, render_template, flash,redirect,url_for,session
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin,LoginManager,login_user,login_required,logout_user,current_user
from flask_bcrypt import Bcrypt



app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

app.config['SECRET_KEY'] = 'gbjwk34tjkb!@#$%^&*()6328964789tjkvgabsbgwegbkbdk!(%R$)'  
db = SQLAlchemy(app)

bcrypt = Bcrypt(app)
      

class User(db.Model,UserMixin):
    id = db.Column(db.Integer,primary_key = True)
    first_name=db.Column(db.String,nullable  = False,unique = True)
    last_name=db.Column(db.String,nullable  = False,unique = True)
    email =db.Column(db.String,nullable = False ,unique =True)
    password=db.Column(db.String,nullable  = False)
      
@app.route('/')
def ma():
    return render_template('main.html')
@app.route('/login')
def login():
    return render_template('login.html')

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
                return redirect(url_for('ma'))
            else:
                flash('email already taken')
                return render_template('register.html')
        else:
            flash('somthing wrong ')
            return render_template('register.html')
    else:
        return render_template('register.html')






















































































if __name__ == '__main__':
    app.run(debug=True)

