from flask_wtf import FlaskForm
from wtforms import Form, BooleanField, HiddenField, StringField, IntegerField, PasswordField, validators, SubmitField, TextAreaField, SelectField, TelField, DateField, FieldList, FormField
from countries_flags import countries_and_flags, country_choices


class LoginForm(FlaskForm):
    email = StringField(
        'Email', [
            validators.DataRequired(message='this is a required field'),
        ],  render_kw={"placeholder": "name@example.com", "class": "form-control"})
    password = StringField('Password', [validators.DataRequired(message='this is a required field')],
                           render_kw={"placeholder": "password", "class": "form-control", "type": "password"})
    submit = SubmitField('Login', render_kw={"class": "btn large-btn"})


class SignupForm(FlaskForm):
    email = StringField(
        'Email', [
            validators.DataRequired(message='this is a required field'),
        ],  render_kw={"placeholder": "name@example.com", "class": "form-control"})
    password = StringField('Password', [
        validators.DataRequired(message='this is a required field'),
    ],
                           render_kw={"placeholder": "password", "class": "form-control", "type": "password"})

    confirm_password = StringField('Confirm Password', [
        validators.DataRequired(message='this is a required field'),
        validators.EqualTo('password', message='Passwords must match')
    ],
                           render_kw={"placeholder": "re-write the password", "class": "form-control", "type": "password"})
    submit = SubmitField('sign up', render_kw={"class": "btn large-btn"})


class UserForm(FlaskForm):
    name = StringField('Name', validators=[validators.DataRequired(), validators.Length(max=100)], render_kw={"class": "form-control"})
    email = StringField('Email', validators=[validators.DataRequired()], render_kw={"class": "form-control"})
    job_title = StringField('Job Title', validators=[validators.DataRequired(), validators.Length(max=100)], render_kw={"class": "form-control"})
    country = SelectField('Country', choices=country_choices, validators=[validators.DataRequired()], render_kw={"class": "form-control"})
    phone = TelField('Phone Number', validators=[validators.DataRequired(), validators.Length(max=15)], render_kw={"class": "form-control"})
    summary = TextAreaField('Profile Summary', validators=[validators.DataRequired(), validators.Length(max=500)], render_kw={"class": "form-control"})
    submit = SubmitField('Submit',  render_kw={"class": "btn large-btn"})


# Predefined degree options
degree_choices = [
    ('bachelor', 'Bachelor'),
    ('master', 'Master'),
    ('phd', 'PhD'),
    ('associate', 'Associate')
]


class EducationForm(FlaskForm):
    degree = SelectField('Degree', choices=degree_choices, validators=[validators.DataRequired()], render_kw={"class": "form-control"})
    institution = StringField('Institution', validators=[validators.DataRequired(), validators.Length(max=100)], render_kw={"class": "form-control"})
    field_of_study = StringField('Field of Study', validators=[validators.DataRequired(), validators.Length(max=100)], render_kw={"class": "form-control"})
    start_date = DateField('Start Date', validators=[validators.DataRequired()], render_kw={"class": "form-control"})
    end_date = DateField('End Date',  validators=[validators.DataRequired()], render_kw={"class": "form-control"})
    description = TextAreaField('Description', validators=[validators.DataRequired(), validators.Length(max=500)], render_kw={"class": "form-control"})
    honors = TextAreaField('Honors', validators=[validators.DataRequired(), validators.Length(max=500)], render_kw={"class": "form-control"})
    submit = SubmitField('Submit',  render_kw={"class": "btn large-btn"})


class ExperienceForm(FlaskForm):
    job_title = StringField('Job Title', validators=[validators.DataRequired(), validators.Length(max=255)], render_kw={"class": "form-control"})
    company = StringField('Company', validators=[validators.DataRequired(), validators.Length(max=255)], render_kw={"class": "form-control"})
    is_current = BooleanField('Is currently working here?', render_kw={"class": "form-check-input"})
    start_date = DateField('Start Date', validators=[validators.DataRequired()], render_kw={"class": "form-control"})
    end_date = DateField('End Date', validators=[validators.DataRequired()], render_kw={"class": "form-control"})
    responsibilities = TextAreaField('Responsibilities', validators=[validators.DataRequired()], render_kw={"class": "form-control"})
    achievements = TextAreaField('Achievements', validators=[validators.DataRequired()], render_kw={"class": "form-control"})
    description = TextAreaField('Description', validators=[validators.DataRequired()],render_kw={"class": "form-control"})
    submit = SubmitField('Submit', render_kw={"class": "btn large-btn"})


class SkillForm(FlaskForm):
    skill_name = StringField('Skill Name', validators=[validators.DataRequired(), validators.Length(max=255)], render_kw={"class": "form-control"})
    proficiency = SelectField('Proficiency', choices=[(str(i), i) for i in range(1, 6)], validators=[validators.DataRequired()], render_kw={"class": "form-control"})
    years_of_experience = IntegerField('Years of Experience', validators=[validators.DataRequired(), validators.NumberRange(min=0)], render_kw={"class": "form-control"})
    details = TextAreaField('Details', validators=[validators.Length(max=500)], render_kw={"class": "form-control"})
    submit = SubmitField('Submit', render_kw={"class": "btn large-btn"})


class ToolForm(FlaskForm):
    ID = HiddenField('ID')
    tool_name = StringField('Tool Name', validators=[validators.DataRequired()], render_kw={"class": "form-control"})


class AchievementForm(FlaskForm):
    ID = HiddenField('ID')
    achievement_description = TextAreaField('Achievement Description', validators=[validators.DataRequired()])
    date_achieved = DateField('Date Achieved', validators=[validators.DataRequired()])
    impact = TextAreaField('Impact', validators=[validators.DataRequired()])
    tools = FieldList(FormField(ToolForm), min_entries=1, max_entries=40)


class ProjectsForm(FlaskForm):
    project_title = StringField('Project Title', validators=[validators.DataRequired(), validators.Length(max=255)], render_kw={"class": "form-control"})
    project_type = SelectField('Project Type', choices=[('Professional', 'Professional'), ('School', 'School')], validators=[validators.DataRequired()], render_kw={"class": "form-control"})
    company = StringField('Company', validators=[validators.DataRequired(), validators.Length(max=255)], render_kw={"class": "form-control"})
    start_date = DateField('Start Date', validators=[validators.DataRequired()], render_kw={"class": "form-control"})
    end_date = DateField('End Date', validators=[validators.DataRequired()], render_kw={"class": "form-control"})
    project_url = StringField('Project URL', validators=[validators.DataRequired(), validators.URL(), validators.Length(max=255)], render_kw={"class": "form-control"})
    objectives = TextAreaField('Objectives', validators=[validators.DataRequired()], render_kw={"class": "form-control"})
    collaborators = TextAreaField('Collaborators', validators=[validators.DataRequired()], render_kw={"class": "form-control"})
    description = TextAreaField('Description', validators=[validators.DataRequired()], render_kw={"class": "form-control"})
    outcomes = TextAreaField('Outcomes', validators=[validators.DataRequired()], render_kw={"class": "form-control"})
    achievements = FieldList(FormField(AchievementForm), min_entries=1, max_entries=40)
    submit = SubmitField('Submit', render_kw={"class": "btn large-btn"})
