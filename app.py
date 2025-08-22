from datetime import datetime
from flask import (
    Flask, render_template, request, redirect,
    url_for, flash
)
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager, UserMixin, login_user,
    login_required, logout_user, current_user
)
from werkzeug.security import generate_password_hash, check_password_hash
import os

# ---- App setup ----
app = Flask(__name__)
app.secret_key = "pi_hackathon_super_secret_key_v1"

# SQLite DB location (file will be created inside instance folder)
instance_dir = os.path.join(os.path.dirname(__file__), "instance")
os.makedirs(instance_dir, exist_ok=True)
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(instance_dir, 'site.db')}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# ---- Login manager ----
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message_category = "warning"

# ---- Models ----
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    skills = db.relationship("Skill", backref="user", lazy=True, cascade="all, delete-orphan")

    def set_password(self, raw):
        self.password_hash = generate_password_hash(raw)

    def check_password(self, raw):
        return check_password_hash(self.password_hash, raw)

class Skill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)         # used in templates as s.name
    description = db.Column(db.String(600), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    # alias for templates that use s.title
    @property
    def title(self):
        return self.name

# ---- User loader ----
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ---- Create DB + seed demo data (if empty) ----
with app.app_context():
    db.create_all()

    # Seed demo users & skills once (only if empty)
    if User.query.count() == 0:
        demo = User(username="demo_user")
        demo.set_password("demo123")
        db.session.add(demo)

        mentor = User(username="mentor")
        mentor.set_password("mentor123")
        db.session.add(mentor)
        db.session.commit()

        demos = [
            ("Python Basics", "I can teach Python fundamentals and help with projects."),
            ("Web Development", "I build responsive websites with HTML/CSS/JS."),
            ("Data Science", "I analyze data using pandas and visualize results."),
            ("C++ Competitive", "I help with DS & Algo and contest prep."),
            ("Flask Apps", "I can build backend APIs & small webapps."),
            ("React Basics", "Intro to components, hooks and state."),
            ("SQL", "Database design and advanced SQL queries."),
            ("Machine Learning", "Supervised models & basic pipelines."),
            ("Git & GitHub", "Version control, PR workflow, branching."),
            ("UI/UX Tips", "Design basics for better user experience."),
        ]
        for i, (t, d) in enumerate(demos):
            owner = demo if i < 7 else mentor
            db.session.add(Skill(name=t, description=d, user=owner))
        db.session.commit()

# ---- Helpers ----
def redirect_home_if_logged():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

# ---- Routes ----
@app.route("/")
def home():
    # If logged -> dashboard, else browse public marketplace
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    return redirect(url_for("browse_skills"))

# Register
@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = (request.form.get("password") or "").strip()

        if not username or not password:
            flash("Both username and password are required.", "danger")
            return redirect(url_for("register"))

        if User.query.filter_by(username=username).first():
            flash("Username already taken. Choose another.", "danger")
            return redirect(url_for("register"))

        u = User(username=username)
        u.set_password(password)
        db.session.add(u)
        db.session.commit()
        flash("Account created — you can now login.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

# Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = (request.form.get("password") or "").strip()

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash(f"Welcome back, {user.username}!", "success")
            return redirect(url_for("dashboard"))
        flash("Invalid username or password.", "danger")
        return redirect(url_for("login"))

    return render_template("login.html")

# Logout
@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))

# Dashboard — shows and adds skills
# Template you have posts form to url_for('dashboard')
@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        desc = (request.form.get("description") or "").strip()
        if not name or not desc:
            flash("Please provide both name and description.", "danger")
            return redirect(url_for("dashboard"))
        s = Skill(name=name, description=desc, user=current_user)
        db.session.add(s)
        db.session.commit()
        flash("Skill added successfully!", "success")
        return redirect(url_for("dashboard"))

    skills = Skill.query.filter_by(user_id=current_user.id).order_by(Skill.id.desc()).all()
    return render_template("dashboard.html", skills=skills)

# Edit skill
@app.route("/edit_skill/<int:skill_id>", methods=["GET", "POST"])
@login_required
def edit_skill(skill_id):
    skill = Skill.query.get_or_404(skill_id)
    if skill.user_id != current_user.id:
        flash("Unauthorized action.", "danger")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        desc = (request.form.get("description") or "").strip()
        if not name or not desc:
            flash("Both fields required.", "danger")
            return redirect(url_for("edit_skill", skill_id=skill.id))
        skill.name = name
        skill.description = desc
        db.session.commit()
        flash("Skill updated.", "success")
        return redirect(url_for("dashboard"))

    return render_template("edit_skill.html", skill=skill)

# Delete skill (simple GET link in templates)
@app.route("/delete_skill/<int:skill_id>")
@login_required
def delete_skill(skill_id):
    skill = Skill.query.get_or_404(skill_id)
    if skill.user_id != current_user.id:
        flash("Unauthorized.", "danger")
        return redirect(url_for("dashboard"))
    db.session.delete(skill)
    db.session.commit()
    flash("Skill deleted.", "info")
    return redirect(url_for("dashboard"))

# Browse marketplace (search q param)
@app.route("/browse")
def browse_skills():
    q = (request.args.get("q") or "").strip()
    query = Skill.query.order_by(Skill.id.desc()).join(User)
    if q:
        like = f"%{q}%"
        query = query.filter(db.or_(Skill.name.ilike(like), Skill.description.ilike(like)))
    skills = query.all()
    return render_template("browse_skills.html", skills=skills, q=q)

# Profile page for a user
@app.route("/profile/<int:user_id>")
def profile(user_id):
    user = User.query.get_or_404(user_id)
    skills = Skill.query.filter_by(user_id=user.id).order_by(Skill.id.desc()).all()
    return render_template("profile.html", profile_user=user, skills=skills)

# ---- Run ----
if __name__ == "__main__":         
    app.run(debug=True)
