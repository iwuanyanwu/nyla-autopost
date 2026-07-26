from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
import uuid
from datetime import datetime, timedelta

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.secret_key = 'supersecretkey'

login_manager = LoginManager()
login_manager.init_app(app)

class SimpleUser(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return SimpleUser(user_id)

POSTS_DB = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
@login_required
def dashboard():
    current_time = datetime.now()
    for p in POSTS_DB:
        if p.get('status') == 'pending' and p.get('scheduled_at'):
            dt = p['scheduled_at']
            if isinstance(dt, str):
                try:
                    dt = datetime.fromisoformat(dt)
                except ValueError:
                    pass
            if isinstance(dt, datetime) and dt <= current_time:
                p['status'] = 'published'

    published_count = sum(1 for p in POSTS_DB if p['status'] == 'published')
    scheduled_count = sum(1 for p in POSTS_DB if p['status'] == 'pending')
    
    display_posts = []
    for p in POSTS_DB:
        p_copy = p.copy()
        dt = p_copy.get('scheduled_at')
        if dt:
            if isinstance(dt, str):
                try:
                    dt = datetime.fromisoformat(dt)
                except ValueError:
                    pass
            if hasattr(dt, '__add__'):
                p_copy['scheduled_at'] = dt + timedelta(minutes=60)
        display_posts.append(p_copy)
    
    return render_template(
        'dashboard.html', 
        total_posts=len(POSTS_DB), 
        published=published_count, 
        scheduled=scheduled_count, 
        recent_posts=display_posts
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
        post_text = request.form.get('content', '')
        selected_platforms = request.form.getlist('platforms')
        platform_string = ', '.join(selected_platforms) if selected_platforms else 'Unspecified Network'
        
        post_type = request.form.get('post_type', 'now')
        scheduled_time_str = request.form.get('scheduled_at_local', '')
        
        post_status = 'published'
        post_time = datetime.now()
        
        if post_type == 'schedule' and scheduled_time_str:
            try:
                post_time = datetime.fromisoformat(scheduled_time_str)
                post_status = 'pending'
            except ValueError:
                pass
        
        if post_text:
            new_post = {
                'id': str(uuid.uuid4()),
                'content': post_text,
                'image_paths': '',
                'scheduled_at': post_time, 
                'platforms': platform_string, 
                'status': post_status
            }
            POSTS_DB.insert(0, new_post)
        return redirect(url_for('dashboard'))
    return render_template('compose.html')

@app.route('/edit_post/<post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post_to_edit = None
    for p in POSTS_DB:
        if p['id'] == post_id:
            post_to_edit = p
            break
            
    if not post_to_edit:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        post_text = request.form.get('content', '')
        selected_platforms = request.form.getlist('platforms')
        platform_string = ', '.join(selected_platforms) if selected_platforms else 'Unspecified Network'
        
        scheduled_time_str = request.form.get('scheduled_at', '')
        
        post_time = post_to_edit['scheduled_at']
        if scheduled_time_str:
            try:
                post_time = datetime.fromisoformat(scheduled_time_str)
            except ValueError:
                pass
                
        if post_text:
            post_to_edit['content'] = post_text
            post_to_edit['platforms'] = platform_string
            post_to_edit['scheduled_at'] = post_time
            post_to_edit['status'] = 'pending'
            
        return redirect(url_for('dashboard'))
        
    return render_template('edit_post.html', post=post_to_edit)

@app.route('/delete_post/<post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    global POSTS_DB
    POSTS_DB = [p for p in POSTS_DB if p['id'] != post_id]
    return redirect(url_for('dashboard'))

@app.route('/analytics')
@login_required
def analytics():
    total_posts = len(POSTS_DB)
    published_count = sum(1 for p in POSTS_DB if p['status'] == 'published')
    scheduled_count = sum(1 for p in POSTS_DB if p['status'] == 'pending')
    
    # Platform counts
    ig_count = sum(1 for p in POSTS_DB if 'instagram' in p.get('platforms', '').lower())
    x_count = sum(1 for p in POSTS_DB if ' x' in p.get('platforms', '').lower() or p.get('platforms', '').lower().startswith('x'))
    li_count = sum(1 for p in POSTS_DB if 'linkedin' in p.get('platforms', '').lower())
    fb_count = sum(1 for p in POSTS_DB if 'facebook' in p.get('platforms', '').lower())

    return render_template(
        'analytics.html',
        total_posts=total_posts,
        published_count=published_count,
        scheduled_count=scheduled_count,
        ig_count=ig_count,
        x_count=x_count,
        li_count=li_count,
        fb_count=fb_count,
        posts=POSTS_DB
    )

@app.route('/settings')
@login_required
def settings():
    return render_template('settings.html')


@app.route('/update-account', methods=['POST'])
def update_account():
    # Handle account update logic here
    return redirect(url_for('settings'))


@app.route('/demo')
def live_demo():
    mock_stats = {
        'total_reach': '128.4K',
        'reach_growth': '+24.2%',
        'scheduled_count': 18,
        'avg_engagement': '4.8%',
        'platforms': [
            {'name': 'X (Twitter)', 'followers': '14.2K', 'posts': 42, 'status': 'Connected'},
            {'name': 'Facebook', 'followers': '38.9K', 'posts': 19, 'status': 'Connected'},
            {'name': 'LinkedIn', 'followers': '8.5K', 'posts': 11, 'status': 'Connected'},
            {'name': 'Instagram', 'followers': '66.8K', 'posts': 55, 'status': 'Connected'}
        ],
        'recent_activity': [
            {'title': 'Q3 Product Teaser Video', 'platform': 'Instagram', 'time': '2 hours ago', 'impressions': '12.4K', 'likes': 840},
            {'title': 'Weekly Industry Digest #42', 'platform': 'LinkedIn', 'time': 'Yesterday', 'impressions': '4.1K', 'likes': 195},
            {'title': 'Feature Release Announcement', 'platform': 'X (Twitter)', 'time': '2 days ago', 'impressions': '18.9K', 'likes': 1210}
        ]
    }
    return render_template('demo.html', stats=mock_stats)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


@app.route('/demo')
def live_demo():
    mock_stats = {
        'total_reach': '128.4K',
        'reach_growth': '+24.2%',
        'scheduled_count': 18,
        'avg_engagement': '4.8%',
        'platforms': [
            {'name': 'X (Twitter)', 'followers': '14.2K', 'posts': 42, 'status': 'Connected'},
            {'name': 'Facebook', 'followers': '38.9K', 'posts': 19, 'status': 'Connected'},
            {'name': 'LinkedIn', 'followers': '8.5K', 'posts': 11, 'status': 'Connected'},
            {'name': 'Instagram', 'followers': '66.8K', 'posts': 55, 'status': 'Connected'}
        ],
        'recent_activity': [
            {'title': 'Q3 Product Teaser Video', 'platform': 'Instagram', 'time': '2 hours ago', 'impressions': '12.4K', 'likes': 840},
            {'title': 'Weekly Industry Digest #42', 'platform': 'LinkedIn', 'time': 'Yesterday', 'impressions': '4.1K', 'likes': 195},
            {'title': 'Feature Release Announcement', 'platform': 'X (Twitter)', 'time': '2 days ago', 'impressions': '18.9K', 'likes': 1210}
        ]
    }
    return render_template('demo.html', stats=mock_stats)

if __name__ == "__main__":
    app.run(debug=True, port=5000)



@app.route('/test-x', methods=['POST'])
def test_x():
    user_email = session.get('user_email', 'demo@nyla.com')
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM credentials WHERE user_email = ?", (user_email,))
    creds = c.fetchone()
    conn.close()
    
    if not creds or not creds['x_api_key']:
        flash('No X API keys found. Save your credentials first.', 'error')
        return redirect(url_for('settings'))
    
    # Test ping to Twitter API v2
    url = "https://api.twitter.com/2/tweets/sample/stream" # Or verify credentials endpoint
    auth = OAuth1(creds['x_api_key'], creds['x_api_secret'], creds['x_access_token'], creds['x_access_secret'])
    try:
        res = requests.get("https://api.twitter.com/2/users/me", auth=auth, timeout=5)
        if res.status_code == 200:
            flash('X (Twitter) API connection verified successfully!', 'success')
        else:
            flash('X API verification failed. Check your keys and access tokens.', 'error')
    except Exception:
        flash('Could not reach X API server. Network timeout.', 'error')
    return redirect(url_for('settings'))

@app.route('/test-fb', methods=['POST'])
def test_fb():
    user_email = session.get('user_email', 'demo@nyla.com')
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM credentials WHERE user_email = ?", (user_email,))
    creds = c.fetchone()
    conn.close()
    
    if not creds or not creds['fb_page_token']:
        flash('No Facebook Page Token found.', 'error')
        return redirect(url_for('settings'))
    
    try:
        res = requests.get(f"https://graph.facebook.com/v19.0/me?access_token={creds['fb_page_token']}", timeout=5)
        if res.status_code == 200:
            flash('Facebook Page Token verified successfully!', 'success')
        else:
            flash('Facebook token invalid or expired.', 'error')
    except Exception:
        flash('Could not reach Facebook Graph API.', 'error')
    return redirect(url_for('settings'))


@app.route('/demo')
def live_demo():
    # Sample analytics data for preview
    mock_stats = {
        'total_reach': '128.4K',
        'reach_growth': '+24.2%',
        'scheduled_count': 18,
        'avg_engagement': '4.8%',
        'platforms': [
            {'name': 'X (Twitter)', 'followers': '14.2K', 'posts': 42, 'status': 'Connected'},
            {'name': 'Facebook', 'followers': '38.9K', 'posts': 19, 'status': 'Connected'},
            {'name': 'LinkedIn', 'followers': '8.5K', 'posts': 11, 'status': 'Connected'},
            {'name': 'Instagram', 'followers': '66.8K', 'posts': 55, 'status': 'Connected'}
        ],
        'recent_activity': [
            {'title': 'Q3 Product Teaser Video', 'platform': 'Instagram', 'time': '2 hours ago', 'impressions': '12.4K', 'likes': 840},
            {'title': 'Weekly Industry Digest #42', 'platform': 'LinkedIn', 'time': 'Yesterday', 'impressions': '4.1K', 'likes': 195},
            {'title': 'Feature Release Announcement', 'platform': 'X (Twitter)', 'time': '2 days ago', 'impressions': '18.9K', 'likes': 1210}
        ]
    }
    return render_template('demo.html', stats=mock_stats)
