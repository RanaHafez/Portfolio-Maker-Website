from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from forms import *
from flask import Flask, render_template, request, redirect, url_for, flash
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, joinedload, relationship
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Text, ForeignKey, Date, Enum, Boolean
from typing import List
from flask_bootstrap import Bootstrap5


app = Flask(__name__, static_url_path='')
app.secret_key = 'mysupersecretkey'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///portfolios.db"
Bootstrap5(app)
login_manager = LoginManager(app)
login_manager.init_app(app)


class Base(DeclarativeBase):
    pass


# initialize the app with the extension
db = SQLAlchemy(model_class=Base)
db.init_app(app)


class Auth(UserMixin, db.Model):
    __tablename__ = "auth"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(30), nullable=False)


class Users(db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    phone: Mapped[str] = mapped_column(String(20))
    job_title: Mapped[str] = mapped_column(String(255))
    country: Mapped[str] = mapped_column(String(255))
    summary: Mapped[str] = mapped_column(Text)
    educations: Mapped[List["Education"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    experiences: Mapped[List["Experience"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    skills: Mapped[List["Skills"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    projects: Mapped[List["Projects"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class Education(db.Model):
    __tablename__ = "education"
    education_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    degree: Mapped[str] = mapped_column(String(255))
    institution: Mapped[str] = mapped_column(String(255))
    field_of_study: Mapped[str] = mapped_column(String(255))
    start_date: Mapped[Date] = mapped_column(Date)
    end_date: Mapped[Date] = mapped_column(Date)
    description: Mapped[str] = mapped_column(Text)
    honors: Mapped[str] = mapped_column(Text)
    user: Mapped["Users"] = relationship(back_populates="educations")


class Experience(db.Model):
    __tablename__ = "experiences"
    experience_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    job_title: Mapped[str] = mapped_column(String(255))
    company: Mapped[str] = mapped_column(String(255))
    start_date: Mapped[Date] = mapped_column(Date)
    end_date: Mapped[Date] = mapped_column(Date)
    description: Mapped[str] = mapped_column(Text)
    is_current: Mapped[bool] = mapped_column(Boolean)
    responsibilities: Mapped[str] = mapped_column(Text)
    achievements: Mapped[str] = mapped_column(Text)
    user: Mapped["Users"] = relationship(back_populates="experiences")


class Skills(db.Model):
    __tablename__ = "skills"
    skill_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    skill_name: Mapped[str] = mapped_column(String(255))
    proficiency: Mapped[int] = mapped_column(Integer)
    years_of_experience: Mapped[int] = mapped_column(Integer)
    details: Mapped[str] = mapped_column(Text)
    user: Mapped["Users"] = relationship(back_populates="skills")


class Projects(db.Model):
    __tablename__ = "projects"
    project_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    project_title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    project_type: Mapped[str] = mapped_column(Enum('Professional', 'School'))
    company: Mapped[str] = mapped_column(String(255))
    start_date: Mapped[Date] = mapped_column(Date)
    end_date: Mapped[Date] = mapped_column(Date)
    objectives: Mapped[str] = mapped_column(Text)
    collaborators: Mapped[str] = mapped_column(Text)
    project_url: Mapped[str] = mapped_column(String(255))
    outcomes: Mapped[str] = mapped_column(Text)
    user: Mapped["Users"] = relationship(back_populates="projects")
    project_achievements: Mapped[List["Achievements"]] = relationship(back_populates="project", cascade="all, delete-orphan")


class Achievements(db.Model):
    __tablename__ = "achievements"
    achievement_id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey('projects.project_id'), nullable=False)
    achievement_description: Mapped[str] = mapped_column(Text)
    date_achieved: Mapped[Date] = mapped_column(Date)
    impact: Mapped[str] = mapped_column(Text)
    project: Mapped["Projects"] = relationship(back_populates="project_achievements")
    achievement_tools: Mapped[List["Tools"]] = relationship(back_populates="achievement", cascade="all, delete-orphan")


class Tools(db.Model):
    __tablename__ = "tools"
    tool_id: Mapped[int] = mapped_column(primary_key=True)
    tool_name: Mapped[String] = mapped_column(String)
    achievement_id: Mapped[int] = mapped_column(Integer, ForeignKey('achievements.achievement_id'), nullable=False)
    achievement: Mapped["Achievements"] = relationship(back_populates="achievement_tools")


# Create a user_loader callback
@login_manager.user_loader
def load_user(admin_id):
    return Auth.query.get(int(admin_id))


# Define a custom filter to make the int function accessible in the template
@app.template_filter('to_int')
def to_int(value):
    return int(value)


@app.route("/all", methods=["GET"])
def get_all_portfolio():
    """
    this function get all the portfolio from the database, returns a list of all users in db
    """
    with app.app_context():
        result = db.session.query(Users).options(
            joinedload(Users.educations),
            joinedload(Users.experiences),
            joinedload(Users.skills),
            joinedload(Users.projects).joinedload(Projects.project_achievements).joinedload(
                Achievements.achievement_tools)
        ).order_by(Users.name).all()
    return result


@app.route("/")
def index():
    users = get_all_portfolio()
    print(users)
    return render_template("portfolioes_cards.html", all_portfolios=users)


@app.route("/details/<int:user_id>")
def user_details(user_id):
    """
    get specific user details
    """
    user = db.session.execute(db.select(Users).where(Users.id == user_id)).scalar()
    return render_template("user_details.html", user=user)


# ------------------------- ADMIN login and signup --------------------------
@app.route("/admin/login", methods=["POST", "GET"])
def admin_login():
    print(current_user)
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    login_form = LoginForm()
    if request.method == 'POST':
        email = login_form.email.data
        password = login_form.password.data
        if login_form.validate_on_submit():
            with app.app_context():
                result = db.session.execute(db.select(Auth).where(Auth.email == email))
                admin = result.scalar()
            if admin:
                if check_password_hash(admin.password, password):
                    print("Done")
                    login_user(user=admin)
                    return redirect(url_for("dashboard"))
                else:
                    flash("wrong password")
                    return redirect(url_for("admin_login"))
            flash(message="No Such Admin, Login Instead")
            return redirect(url_for("admin_signup"))
    return render_template("admin/signup.html", form=login_form, msg="Login", action="/admin/login")


@app.route("/admin/signup", methods=["POST", "GET"])
def admin_signup():
    """"""
    # if there is already an admin logged in, redirect to the main page
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    signup_form = SignupForm()
    if request.method == 'POST':
        if signup_form.validate_on_submit():
            password = signup_form.password.data
            email = signup_form.email.data
            # checking if the user has an account
            if Auth.query.filter_by(email=email).first():
                flash(message="You have an account. Login Instead!")
                return redirect(url_for("admin_login"))

            hash_and_salted_password = generate_password_hash(
                password,
                method='pbkdf2:sha256',
                salt_length=8
            )
            with app.app_context():
                new_user = Auth(
                    password=hash_and_salted_password,
                    email=email
                )
                db.session.add(new_user)
                db.session.commit()

            flash("Admin created. Try Login Now!")
            return redirect(url_for("admin_login"))

    return render_template("admin/signup.html", form=signup_form, msg="Signup", action="/admin/signup")


# ------------------ Admin logout ------------------------------------------------------------------
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/admin/dashboard", methods=["POST", "GET"])
@login_required
def dashboard():
    users = get_all_portfolio()
    return render_template("admin/dashboard.html", users=users)


# ---------------------- CRUD USER -------------------
@app.route("/add-user", methods=["GET", "POST"])
@login_required
def add_user():
    """
    this adds a user to the db and if successful, redirect to the dashboard
    """
    user_form = UserForm()
    if request.method == "POST":
        if user_form.validate_on_submit():
            # we want to check if the user has been already added before of not
            existing_user = Users.query.filter_by(email=user_form.email.data).first()
            if existing_user:
                flash("this email has been already used, try another mail", "error")
                return redirect(url_for("add_user"))

            # create a user
            new_user = Users(
                email=user_form.email.data,
                name=user_form.name.data,
                job_title=user_form.job_title.data,
                country=user_form.country.data,
                summary=user_form.summary.data,
                phone=user_form.phone.data,
            )
            # add user to the db
            with app.app_context():
                db.session.add(new_user)
                db.session.commit()
            return redirect(url_for("dashboard"))
    return render_template("forms/add_form.html", form=user_form, msg="User", action=url_for("add_user"))


@app.route("/update-user/<int:user_id>", methods=["POST", "GET"])
@login_required
def update_user(user_id):
    """
    a method that updates the user to new info entered, if successful, update the user
    :param user_id: the user id to update
    :return: redirect to the dashboard page
    """
    with app.app_context():
        user = db.session.execute(db.select(Users).where(Users.id == user_id)).scalar()
        form = UserForm(obj=user)

        if request.method == "POST":
            if form.validate_on_submit():
                # check if the updated email has been used before or not
                if form.email.data != user.email:
                    existing_user = Users.query.filter_by(email=form.email.data).first()
                    if existing_user:
                        flash("Email already exists", "error")
                        return redirect(url_for("update_user", user_id=user_id))

                # update the user with entered values
                user.name = form.name.data
                user.email = form.email.data
                user.phone = form.phone.data
                user.country = form.country.data
                user.summary = form.summary.data
                user.job_title = form.job_title.data

                db.session.commit()

                return redirect(url_for("dashboard"))

    return render_template("forms/update_form.html", form=form, msg="User", action=url_for("update_user", user_id=user_id))


@app.route("/delete-user/<int:user_id>", methods=["POST", "GET"])
@login_required
def delete_user(user_id):
    """
    deletes all user info from the db
    :param user_id:
    :return: redirect to the dashboard
    """
    user = Users.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
    return redirect(url_for("dashboard"))


# ------------------------ CRUD EDUCATION ----------------
@app.route("/add-education/<int:user_id>", methods=["GET", "POST"])
@login_required
def add_education(user_id):
    """
    Add education information for a user.
    Args:
        user_id (int): The ID of the user for whom education information is being added.
    Returns:
        redirect: Redirects to the dashboard page after successfully adding education information.
    Methods:
        GET: Renders the education form.
        POST: Validates and adds the education information to the database.

    """
    form = EducationForm()
    if request.method == "POST":
        print(form.validate_on_submit())
        if form.validate_on_submit():
            education = Education(
                degree=form.degree.data,
                institution=form.institution.data,
                field_of_study=form.field_of_study.data,
                start_date=form.start_date.data,
                end_date=form.end_date.data,
                description=form.description.data,
                honors=form.honors.data,
                user_id=user_id
            )
            with app.app_context():
                db.session.add(education)
                db.session.commit()
            return redirect(url_for("dashboard"))
    return render_template("forms/add_form.html", form=form, msg="Education", action=url_for("add_education", user_id=user_id))


@app.route("/update-education/<int:edu_id>", methods=["POST", "GET"])
@login_required
def update_education(edu_id):
    with app.app_context():
        education = db.session.execute(db.select(Education).where(Education.education_id == edu_id)).scalar()
        form = EducationForm(obj=education)
        if request.method == "POST":
            if form.validate_on_submit():
                education.degree = form.degree.data
                education.institution = form.institution.data
                education.field_of_study = form.field_of_study.data
                education.start_date = form.start_date.data
                education.end_date = form.end_date.data
                education.description = form.description.data
                education.honors = form.honors.data

                db.session.commit()
                return redirect(url_for("dashboard"))

    return render_template("forms/update_form.html", form=form, msg="Education", action=url_for("update_education", edu_id=edu_id))


@app.route("/delete-education/<int:edu_id>", methods=["GET"])
@login_required
def delete_education(edu_id):
    """
    Delete an education record for a user.

    Args:
        edu_id (int): The ID of the education record to delete.

    Returns:
        redirect: Redirects to the dashboard page after successfully deleting the education record.

    Methods:
        GET: Deletes the specified education record from the database.
    """
    education_to_delete = Education.query.get(edu_id)
    if education_to_delete:
        db.session.delete(education_to_delete)
        db.session.commit()
    return redirect(url_for("dashboard"))


# ------------------CRUD Experience--------------------------
@app.route("/add-experience/<int:user_id>", methods=["GET", "POST"])
@login_required
def add_experience(user_id):
    """
    Add a new work experience record for a user.

    Args:
        user_id (int): The ID of the user to whom the experience will be added.

    Returns:
        redirect: Redirects to the dashboard page after successfully adding the experience record.
        render_template: Renders the add experience form if the request method is GET or if the form validation fails.

    Methods:
        GET: Renders the form to add a new experience.
        POST: Validates the form and adds a new experience record to the database if the form is valid.
    """
    form = ExperienceForm()
    with app.app_context():
        if request.method == "POST":
            new_experience = Experience(
                job_title=form.job_title.data,
                company=form.company.data,
                start_date=form.start_date.data,
                end_date=form.end_date.data,
                description=form.description.data,
                is_current=form.is_current.data,
                responsibilities=form.responsibilities.data,
                achievements=form.achievements.data,
                user_id=user_id
            )
            db.session.add(new_experience)
            db.session.commit()
            return redirect(url_for("dashboard"))

    return render_template("forms/add_form.html", form=form, msg="Experience", action=url_for("add_experience", user_id=user_id))


@app.route("/update-experience/<int:exp_id>", methods=["GET", "POST"])
@login_required
def update_experience(exp_id):
    """
    Update an existing work experience record.

    Args:
        exp_id (int): The ID of the experience record to update.

    Returns:
        redirect: Redirects to the dashboard page after successfully updating the experience record.
        render_template: Renders the update experience form if the request method is GET or if the form validation fails.

    Methods:
        GET: Renders the form to update an existing experience.
        POST: Validates the form and updates the experience record in the database if the form is valid.
    """
    with app.app_context():
        experience_to_update = Experience.query.get(exp_id)
        form = ExperienceForm(obj=experience_to_update)
        if request.method == "POST":
            if form.validate_on_submit():
                experience_to_update.job_title = form.job_title.data
                experience_to_update.company = form.company.data
                experience_to_update.start_date = form.start_date.data
                experience_to_update.end_date = form.end_date.data
                experience_to_update.description = form.description.data
                experience_to_update.is_current = form.is_current.data
                experience_to_update.responsibilities = form.responsibilities.data
                experience_to_update.achievements = form.achievements.data

                db.session.commit()
                return redirect(url_for("dashboard"))

    return render_template("forms/update_form.html", form=form, msg="Experience", action=url_for('update_experience', exp_id=exp_id))


@app.route("/delete-experience/<int:exp_id>", methods=["GET", "POST"])
@login_required
def delete_experience(exp_id):
    """
    Delete an existing work experience record.

    Args:
        exp_id (int): The ID of the experience record to delete.

    Returns:
        redirect: Redirects to the dashboard page after successfully deleting the experience record.

    Methods:
        GET: Deletes the specified experience record and redirects to the dashboard.
        POST: Not typically used for deletions in this method, but included for completeness.
    """
    with app.app_context():
        experience_to_delete = Experience.query.get(exp_id)
        db.session.delete(experience_to_delete)
        db.session.commit()
    return redirect(url_for("dashboard"))


# -------------------CRUD skills---------------------------
@app.route("/add-skill/<int:user_id>", methods=["GET", "POST"])
@login_required
def add_skill(user_id):
    """
    Add a new skill for a specific user.

    Args:
        user_id (int): The ID of the user to whom the skill will be added.

    Returns:
        render_template: Renders the form for adding a new skill.
        redirect: Redirects to the dashboard page after successfully adding the skill.

    Methods:
        GET: Displays the form for adding a new skill.
        POST: Processes the form submission, adds the skill to the database, and redirects to the dashboard.
    """
    form = SkillForm()
    if request.method == "POST":
        if form.validate_on_submit():
            new_skill = Skills(
                user_id=user_id,
                skill_name=form.skill_name.data,
                proficiency=form.proficiency.data,
                years_of_experience=form.years_of_experience.data,
                details=form.details.data
            )
            db.session.add(new_skill)
            db.session.commit()
            return redirect(url_for("dashboard"))
    return render_template("forms/add_form.html", form=form, msg="Skill", action=url_for("add_skill", user_id=user_id))


@app.route("/update-skill/<int:skill_id>", methods=["GET", "POST"])
@login_required
def update_skill(skill_id):
    """
        Update an existing skill.

        Args:
            skill_id (int): The ID of the skill to be updated.

        Returns:
            render_template: Renders the form for updating the skill.
            redirect: Redirects to the dashboard page after successfully updating the skill.

        Methods:
            GET: Displays the form for updating the skill.
            POST: Processes the form submission, updates the skill in the database, and redirects to the dashboard.
        """
    with app.app_context():
        skill_to_update = Skills.query.get(skill_id)
        form = SkillForm(obj=skill_to_update)
        if request.method == "POST":
            if form.validate_on_submit():
                skill_to_update.skill_name = form.skill_name.data
                skill_to_update.proficiency = form.proficiency.data
                skill_to_update.years_of_experience = form.years_of_experience.data
                skill_to_update.details = form.details.data
                db.session.commit()
                return redirect(url_for("dashboard"))

    return render_template("forms/update_form.html", form=form, msg="Skill", action=url_for('update_skill', skill_id=skill_id))


@app.route("/delete-skill/<int:skill_id>", methods=["GET"])
@login_required
def delete_skill(skill_id):
    """
    Delete an existing skill.

    Args:
        skill_id (int): The ID of the skill to be deleted.

    Returns:
        redirect: Redirects to the dashboard page after successfully deleting the skill.

    Methods:
        GET: Processes the deletion of the skill from the database and redirects to the dashboard.
    """
    with app.app_context():
        skill_to_delete = Skills.query.get(skill_id)
        db.session.delete(skill_to_delete)
        db.session.commit()
    return redirect(url_for("dashboard"))


# ---------------------- CRUD Projects ---------------------
@app.route("/add-project/<int:user_id>", methods=["GET", "POST"])
@login_required
def add_project(user_id):
    """
    Add a new project for a specific user.

    Args:
        user_id (int): The ID of the user for whom the project is being added.

    Returns:
        redirect: Redirects to the dashboard after successfully adding the project and its related achievements and tools.

    Methods:
        GET: Renders the add project form.
        POST: Validates the form data and creates a new project along with its achievements and tools in the database.
    """
    form = ProjectsForm()
    with app.app_context():
        if request.method == "POST":
            if form.validate_on_submit():
                print("in post")
                print("invalidate")
                new_project = Projects(
                    user_id=user_id,
                    project_title=form.project_title.data,
                    description=form.description.data,
                    project_type=form.project_type.data,
                    company=form.company.data,
                    start_date=form.start_date.data,
                    end_date=form.end_date.data,
                    objectives=form.objectives.data,
                    collaborators=form.collaborators.data,
                    project_url=form.project_url.data,
                    outcomes=form.outcomes.data)
                db.session.add(new_project)
                db.session.flush()
                for achievement_form in form.achievements:
                    achievement = Achievements(
                        project_id=new_project.project_id,
                        achievement_description=achievement_form.achievement_description.data,
                        date_achieved=achievement_form.date_achieved.data,
                        impact=achievement_form.impact.data
                    )
                    db.session.add(achievement)
                    db.session.flush()
                    for tool_form in achievement_form.tools:
                        print(tool_form.tool_name)
                        tool = Tools(
                            achievement_id=achievement.achievement_id,
                            tool_name=tool_form.tool_name.data
                        )
                        db.session.add(tool)

                db.session.commit()
                return redirect(url_for("dashboard"))
    return render_template("forms/add_project.html", form=form, msg="Project", action=url_for("add_project", user_id=user_id))


@app.route("/update-project/<int:project_id>", methods=["GET", "POST"])
@login_required
def update_project(project_id):
    """
    Update an existing project and its related achievements and tools.

    Args:
        project_id (int): The ID of the project to be updated.

    Returns:
        redirect: Redirects to the dashboard after successfully updating the project and its related achievements and tools.
        str: Returns an error message if the project is not found.

    Methods:
        GET: Renders the update project form with existing data.
        POST: Validates the form data and updates the project along with its achievements and tools in the database.
    """
    with app.app_context():
        project_to_update = db.session.query(Projects).filter_by(project_id=project_id).first()
        if not project_to_update:
            return "ERROR"
        print(project_to_update)
        # Query the related achievements and tools
        achievements_with_tools = db.session.query(Achievements).join(Tools).filter(Achievements.project_id == project_id).all()
        achievements_data = []
        for achievement in achievements_with_tools:
            tools_data = [{'tool_name': tool.tool_name, 'ID': tool.tool_id} for tool in achievement.achievement_tools]
            print(achievement.achievement_id)
            achievements_data.append({
                'achievement_description': achievement.achievement_description,
                'date_achieved': achievement.date_achieved,
                'impact': achievement.impact,
                'tools': tools_data,
                'ID': achievement.achievement_id
            })
        form = ProjectsForm(
            project_title=project_to_update.project_title,
            description=project_to_update.description,
            project_type=project_to_update.project_type,
            company=project_to_update.company,
            start_date=project_to_update.start_date,
            end_date=project_to_update.end_date,
            objectives=project_to_update.objectives,
            collaborators=project_to_update.collaborators,
            project_url=project_to_update.project_url,
            outcomes=project_to_update.outcomes,
            achievements=achievements_data
        )
        if request.method == "POST" and form.validate_on_submit():
            project_to_update.project_title = form.project_title.data
            project_to_update.description = form.description.data
            project_to_update.project_type = form.project_type.data
            project_to_update.company = form.company.data
            project_to_update.start_date = form.start_date.data
            project_to_update.end_date = form.end_date.data
            project_to_update.objectives = form.objectives.data
            project_to_update.collaborators = form.collaborators.data
            project_to_update.project_url = form.project_url.data
            project_to_update.outcomes = form.outcomes.data
            for i, achievement_form in enumerate(form.achievements):
                achievement_data = achievement_form.data
                if 'ID' in achievement_data and achievement_data['ID']:
                    achievement = Achievements.query.get(achievement_data['ID'])
                    achievement.achievement_description = achievement_data['achievement_description']
                    achievement.date_achieved = achievement_data['date_achieved']
                    achievement.impact = achievement_data['impact']
                else:
                    achievement = Achievements(
                        project_id=project_id,
                        achievement_description=achievement_data['achievement_description'],
                        date_achieved=achievement_data['date_achieved'],
                        impact=achievement_data['impact']
                    )
                    db.session.add(achievement)
                    db.session.flush()  # To get the ID of the new achievement
                for j, tool_form in enumerate(achievement_form.tools):
                    tool_data = tool_form.data
                    if 'ID' in tool_data and tool_data['ID']:
                        tool = Tools.query.get(tool_data['ID'])
                        tool.tool_name = tool_data['tool_name']
                    else:
                        tool = Tools(
                            achievement_id=achievement.achievement_id,
                            tool_name=tool_data['tool_name']
                        )
                        db.session.add(tool)
            db.session.commit()
            return redirect(url_for("dashboard"))
    return render_template("forms/update_project.html", form=form, msg="Project", action=url_for('update_project', project_id=project_id), project_id=project_id)


@app.route("/delete-project/<int:project_id>", methods=["GET", "POST"])
@login_required
def delete_project(project_id):
    """
    Delete an existing project and its related achievements and tools.

    Args:
        project_id (int): The ID of the project to be deleted.

    Returns:
        redirect: Redirects to the dashboard after successfully deleting the project and its related achievements and tools.

    Methods:
        GET: Processes the deletion of the project and its related achievements and tools from the database.
    """
    with app.app_context():
        project = Projects.query.get(project_id)
        if project:
            db.session.delete(project)
            db.session.commit()

    return redirect(url_for("dashboard"))


# -------------------------- Delete Achievement --------------------
@app.route("/delete-achievement/<int:achievement_id>/<int:project_id>", methods=["GET"])
def delete_achievement(achievement_id, project_id):
    """
    Delete an existing achievement.

    Args:
        achievement_id (int): The ID of the achievement to be deleted.
        project_id (int): The ID of the project to redirect to after deletion.

    Returns:
        redirect: Redirects to the update project page after successfully deleting the achievement.

    Methods:
        GET: Processes the deletion of the achievement from the database and redirects to the update project page.
    """
    achievement = Achievements.query.get(achievement_id)
    if achievement:
        db.session.delete(achievement)
        db.session.commit()

    return redirect(url_for("update_project", project_id=project_id))


# ------------------------- deletes a tool ------------------------------
@app.route("/delete-tool/<int:tool_id>/<int:project_id>", methods=["GET"])
def delete_tool(tool_id, project_id):
    """
    Delete an existing tool.

    Args:
        tool_id (int): The ID of the tool to be deleted.
        project_id (int): The ID of the project to redirect to after deletion.

    Returns:
        redirect: Redirects to the update project page after successfully deleting the tool.

    Methods:
        GET: Processes the deletion of the tool from the database and redirects to the update project page.
    """
    with app.app_context():
        tool_to_delete = Tools.query.get(tool_id)
        if tool_to_delete:
            db.session.delete(tool_to_delete)
            db.session.commit()
            return redirect(url_for("update_project", project_id=project_id))
        return redirect(url_for("update_project", project_id=project_id))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)