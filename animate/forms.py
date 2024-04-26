from flask_wtf import FlaskForm
from wtforms.fields import SubmitField, StringField
from wtforms.validators import InputRequired, email

class CheckoutForm(FlaskForm):
    firstname = StringField("First Name", validators=[InputRequired()])
    surname = StringField("Famlily name", validators=[InputRequired()])
    email = StringField("Email Address", validators=[InputRequired(), email()])
    phone = StringField("Mobile Phone", validators=[InputRequired()])
    submit = SubmitField("Proceed to Checkout")