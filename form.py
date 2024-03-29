from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    SubmitField,
    FloatField,
    IntegerField,
    MultipleFileField,
    TextAreaField,
)
from flask_wtf.file import FileAllowed, FileRequired
from wtforms.validators import DataRequired, Email, Length, InputRequired, NumberRange


class UserLoginForm(FlaskForm):
    email = StringField(
        "Email", validators=[DataRequired(), Email()], render_kw={"type": "email"}
    )
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8)])
    submit = SubmitField("Login")


class UserRegisterForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField(
        "Email", validators=[DataRequired(), Email()], render_kw={"type": "email"}
    )
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8)])
    submit = SubmitField("Sign Up")


class SellerLoginForm(FlaskForm):
    email = StringField(
        "Email", validators=[DataRequired(), Email()], render_kw={"type": "email"}
    )
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8)])
    submit = SubmitField("Login")


class SellerRegisterForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField(
        "Email", validators=[DataRequired(), Email()], render_kw={"type": "email"}
    )
    phone_num = StringField("Phone Number", validators=[DataRequired()])
    address = StringField("Address", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8)])
    submit = SubmitField("Sign Up")


class AddItemForm(FlaskForm):
    name = StringField("Name of the item", validators=[DataRequired()])
    description = StringField("Brief Description of item", validators=[DataRequired()])
    price = FloatField("Price in Rs", validators=[DataRequired()])
    available_quantity = IntegerField("Quantity", validators=[DataRequired()])
    images = MultipleFileField(
        "Images of Item",
        validators=[
            FileRequired("Please choose at least one file."),
            FileAllowed(["jpg", "png", "jpeg"], "Only images are allowed!"),
        ],
        render_kw={"accept": "image/*"},
    )
    submit = SubmitField("Add Item")


class RatingReviewForm(FlaskForm):
    title = StringField(
        "Title", validators=[DataRequired()], render_kw={"placeholder": "Required..."}
    )
    review = TextAreaField("Review", render_kw={"placeholder": "Optional..."})
    submit = SubmitField("Submit", render_kw={"class": "btn-success"})


class AddressForm(FlaskForm):
    address = TextAreaField("Address", validators=[DataRequired()])
    city = StringField("City", validators=[DataRequired()])
    state = StringField("State", validators=[DataRequired()])
    pincode = StringField("Pincode", validators=[DataRequired()])
    phn_no = StringField(
        "Phone Number", validators=[DataRequired(), Length(min=10, max=10)]
    )
    submit = SubmitField("Add Address")
