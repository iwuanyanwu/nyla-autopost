from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

app = Flask(__name__)
app.secret_key = 'supersecretkey'

login_manager = LoginManager()
login_manager.init_app(app)

class SimpleUser(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return SimpleUser(user_id)

# Global in-memory storage for posts
POSTS_DB = []

@app.route('/')
def index():
    return render_template('landing.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template(
        'dashboard.html', 
        total_posts=len(POSTS_DB), 
        published=len(POSTS_DB), 
        scheduled=0, 
        ig_count=0, 
        x_count=0, 
        li_count=0, 
        fb_count=0, 
        posts=POSTS_DB
    )

@app.route('/analytics')
@login_required
def analytics():
    return render_template(
        'analytics.html', 
        total_posts=len(POSTS_DB), 
        published=len(POSTS_DB), 
        scheduled=0, 
        ig_count=0, 
        x_count=0, 
        li_count=0, 
        fb_count=0, 
        posts=POSTS_DB
    )

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = SimpleUser(1)
        login_user(user)
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user = SimpleUser(1)
        login_user(user)
        return redirect(url_for('dashboard'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/compose', methods=['GET', 'POST'])
@login_required
def compose():
    if request.method == 'POST':
        message = request.form.get('message', '')
        if message:
            POSTS_DB.append({'message': message})
        return redirect(url_for('dashboard'))
    return render_template('compose.html')

@app.route('/settings')
@login_required
def settings():
    return render_template('settings.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
