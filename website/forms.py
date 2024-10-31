from flask_wtf import FlaskForm
from wtforms.fields import TextAreaField, SubmitField, StringField, PasswordField, IntegerField, SelectField, SelectMultipleField, FormField, DateField, TimeField
from wtforms.validators import InputRequired, Email, EqualTo
from flask_wtf.file import FileRequired, FileField, FileAllowed
from wtforms.widgets import CheckboxInput

ALLOWED_FILE = {'PNG', 'JPG', 'JPEG', 'png', 'jpg', 'jpeg'}

class ExperienceForm(FlaskForm):
    experience_levels = [
        ('Beginner', 'Beginner'),
        ('Intermediate', 'Intermediate'),
        ('Advanced', 'Advanced'),
        ('Expert', 'Expert')
    ]
    
    # Dynamically creates a checkbox for each experience level
    checkboxes = SelectMultipleField('Experience', choices=experience_levels, option_widget=CheckboxInput())

# Buy a Ticket
class TicketForm(FlaskForm):
  num_tickets = IntegerField("Number of Tickets", validators=[InputRequired()])
  card = IntegerField('Card Details', validators=[InputRequired()])
  submit = SubmitField("Create")
    
class EventForm(FlaskForm):
  name = StringField('Event Name:', validators=[InputRequired()])
  description = TextAreaField('Description:', render_kw={"style": "resize: none; height: 200px;"}, 
            validators=[InputRequired()])
  image = FileField('Event Image:', validators=[
    FileRequired(message='Image cannot be empty'),
    FileAllowed(ALLOWED_FILE, message='Only supports PNG, JPG, png, jpg')])
  location = StringField('Location:', validators=[InputRequired()])
  activity = SelectField('Activity:', choices=[
            ('Arts', 'Arts & Craft'),
            ('Sports', 'Sports & Fitness'),
            ('Music', 'Music'),
            ('bGames', 'Board Games'),
            ('eGames', 'Electronic Games'),
            ('Education', 'Education')], validators=[InputRequired()])
  status = SelectField('Activity:', choices=[
            ('Open'),
            ('Inactive'),
            ('Sold Out'),
            ('Cancelled')], validators=[InputRequired()])
  host_name = StringField('Host Name:', validators=[InputRequired()])
  host_experience = TextAreaField('Host Experience:', render_kw={"style": "resize: none; height: 200px;"}, 
            validators=[InputRequired()])
  host_contact = IntegerField('Host Contact:', validators=[InputRequired()])
  host_phone = StringField('Host Phone:', validators=[InputRequired()])
  experience_required = FormField(ExperienceForm)  # Embed the experience form
  tickets_avaliable = IntegerField('Tickets Avaliable:', validators=[InputRequired()])
  tickets_price = IntegerField('Tickets Price:', validators=[InputRequired()])
  start_date = DateField('Start Date', format='%Y-%m-%d')
  end_date = DateField('End Date', format='%Y-%m-%d')
  start_time = TimeField('Start Time', format='%H:%M')
  end_time = TimeField('End Time', format='%H:%M')
  submit = SubmitField("Create")

# User login
class LoginForm(FlaskForm):
    user_name = StringField("User Name", validators=[InputRequired('Enter user name')])
    password = PasswordField("Password", validators=[InputRequired('Enter user password')])
    submit = SubmitField("Login")

# User register
class RegisterForm(FlaskForm):
    user_name = StringField("User Name", validators=[InputRequired()])
    first_name = StringField("First Name", validators=[InputRequired()])
    surname = StringField("Surname", validators=[InputRequired()])
    email_id = StringField("Email Address", validators=[Email("Please enter a valid email")])  
    # linking two fields - password should be equal to data entered in confirm
# linking two fields - password should be equal to data entered in confirm
    password = PasswordField("Password", validators=[InputRequired(),
                  EqualTo('confirm', message="Passwords should match")])
    confirm = PasswordField("Confirm Password")
    # submit button
# other details
    contact_number = IntegerField("Contact Number", validators=[InputRequired()])
    street_address = TextAreaField("Street Address", validators=[InputRequired()])
# submit button
    submit = SubmitField("Register")

# User comment
class CommentForm(FlaskForm):
  text = TextAreaField('Comment', [InputRequired()])
  submit = SubmitField('Create')