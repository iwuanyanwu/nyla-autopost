from flask import Flask, render_template, request, redirect, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_apscheduler import APScheduler
from datetime import datetime, timezone, timedelta

app = Flask(__name__)
app.secret_key = 'super-secret-key-change-this'

scheduler = APScheduler()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

POSTS_DB = []

class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

def check_and_publish_scheduled_posts():
    now_utc = datetime.now(timezone.utc)
    for post in POSTS_DB:
        if post['status'] == 'scheduled':
            post_time = post['scheduled_at']
            if post_time.tzinfo is None:
                post_time = post_time.replace(tzinfo=timezone.utc)
            
            if post_time <= now_utc:
                post['status'] = 'published'
                post['impressions'] = 180

def create_post_from_form(req):
    try:
        content = req.form.get('content', '')
        scheduled_time_raw = req.form.get('scheduled_at_local') or req.form.get('scheduled_at')
        tz_offset_minutes = req.form.get('tz_offset', 0)
        post_type = req.form.get('post_type', 'now')
        
        selected_platforms = req.form.getlist('platforms') or ['Facebook', 'X']
        platforms_str = ", ".join([p.capitalize() for p in selected_platforms])

        now_utc = datetime.now(timezone.utc)
        scheduled_at = now_utc
        status = 'published'

        if post_type == 'schedule' and scheduled_time_raw:
            try:
                # Handle standard datetime-local format
                clean_time = scheduled_time_raw.replace('Z', '').split('.')[0]
                naive_dt = datetime.strptime(clean_time, "%Y-%m-%dT%H:%M")
                
                try:
                    offset_val = int(tz_offset_minutes)
                except ValueError:
                    offset_val = 0

                utc_dt = naive_dt + timedelta(minutes=offset_val)
                scheduled_at = utc_dt.replace(tzinfo=timezone.utc)
                
                if scheduled_at > now_utc:
                    status = 'scheduled'
            except Exception as err:
                print(f"[TIME PARSE ERROR] {err}")

        new_post = {
            'id': len(POSTS_DB) + 1,
            'content': content,
            'status': status,
            'scheduled_at': scheduled_at,
            'platforms': platforms_str,
            'image_paths': None,
            'impressions': 180 if status == 'published' else 0
        }
        
        POSTS_DB.insert(0, new_post)
        if status == 'scheduled':
            flash("Post scheduled successfully!", "info")
        else:
            flash("Post published successfully!", "success")
    except Exception as e:
        print(f"[FORM SUBMIT ERROR] {e}")
        flash("Post submitted, but encountered a formatting issue.", "warning")

@app.route('/', methods=['GET', 'POST'])
def landing():
    if request.method == 'POST':
        create_post_from_form(request)
        return redirect('/dashboard', code=303)
    return render_template('landing.html')

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if request.method == 'POST':
        create_post_from_form(request)
        return redirect('/dashboard', code=303)

    total_posts = len(POSTS_DB)
    published = sum(1 for p in POSTS_DB if p['status'] == 'published')
    scheduled = sum(1 for p in POSTS_DB if p['status'] == 'scheduled')

    return render_template(
        'dashboard.html',
        total_posts=total_posts,
        published=published,
        scheduled=scheduled,
        recent_posts=POSTS_DB
    )

@app.route('/compose', methods=['GET', 'POST'])
@login_required
def compose():
    if request.method == 'POST':
        create_post_from_form(request)
        return redirect('/dashboard', code=303)
    return render_template('compose.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect('/dashboard', code=303)
    if request.method == 'POST':
        user = User(id="1")
        login_user(user)
        return redirect('/dashboard', code=303)
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect('/', code=303)

if __name__ == '__main__':
    scheduler.add_job(id='scheduled_publisher', func=check_and_publish_scheduled_posts, trigger='interval', seconds=30)
    scheduler.start()
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
