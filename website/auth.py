from flask import Blueprint, render_template, redirect, url_for, flash
from .forms import LoginForm, RegisterForm
#new imports:
from flask_login import login_user, login_required, logout_user
from flask_bcrypt import generate_password_hash, check_password_hash
from .models import User
from . import db

#create a blueprint
authbp = Blueprint('auth', __name__ )

@authbp.route('/register', methods=['GET', 'POST'])
def register():
    register = RegisterForm()
    #the validation of form is fine, HTTP request is POST
    if register.validate_on_submit():
            #get username, password and email from the form
            uname = register.user_name.data
            fname = register.first_name.data
            lname = register.surname.data
            pwd = register.password.data
            email = register.email_id.data
            number = register.contact_number.data
            address = register.street_address.data
            #check if a similar user or phone number exists
            user = db.session.scalar(db.select(User).where(User.name==uname))
            phone = db.session.scalar(db.select(User).where(User.number==number))

            if user:#this returns true when user is not None
                flash('Username already exists, please try another', 'danger')
                return redirect(url_for('auth.register'))
            if phone:#this returns true when phone is not None
                flash('phone number already exists, please double check your number', 'danger')
                return redirect(url_for('auth.register'))
            
            # don't store the password in plaintext!
            pwd_hash = generate_password_hash(pwd)
            #create a new User model object
            new_user = User(name=uname, fname=fname, lname=lname, password_hash=pwd_hash, 
            emailid=email, number=number, address=address)
            db.session.add(new_user)
            db.session.commit()
            #commit to the database and redirect to HTML page
            return redirect(url_for('main.index'))
    #the else is called when the HTTP request calling this page is a GET
    else:
        print(register.errors)
        return render_template('user.html', form=register, heading='Register')

@authbp.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    error = None
    if(login_form.validate_on_submit()==True):
        #get the username and password from the database
        user_name = login_form.user_name.data
        password = login_form.password.data
        user = db.session.scalar(db.select(User).where(User.name==user_name))
        #if there is no user with that name
        if user is None:
            error = 'Incorrect username'#could be a security risk to give this much info away
        #check the password - notice password hash function
        elif not check_password_hash(user.password_hash, password): # takes the hash and password
            error = 'Incorrect password'
        if error is None:
            #all good, set the login_user of flask_login to manage the user
            login_user(user)
            return redirect(url_for('main.index'))
        else:
            flash(error)
    return render_template('user.html', form=login_form, heading='Login')

@authbp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))