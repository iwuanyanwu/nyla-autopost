import os
import glob

# 1. Safely add routes to app.py
with open('app.py', 'r') as f:
    app_code = f.read()

routes = """
@app.route('/content')
def content_manager():
    all_posts = list(POSTS_DB)
    all_posts.reverse()
    published = [p for p in all_posts if p.get('status') == 'published']
    scheduled = [p for p in all_posts if p.get('status') == 'pending']
    return render_template('content.html', all_posts=all_posts, published_posts=published, scheduled_posts=scheduled)

@app.route('/api/edit-post/<int:post_id>', methods=['POST'])
def edit_post(post_id):
    data = request.get_json()
    for p in POSTS_DB:
        if p.get('id') == post_id:
            if p.get('status') == 'published': return jsonify({'success': False}), 400
            if data.get('content'):
                p['content'] = data.get('content')
                p['text'] = data.get('content')
            if data.get('scheduled_at'): p['scheduled_at'] = data.get('scheduled_at')
            return jsonify({'success': True})
    return jsonify({'success': False}), 404

@app.route('/api/delete-post/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    global POSTS_DB
    POSTS_DB = [p for p in POSTS_DB if not (p.get('id') == post_id and p.get('status') != 'published')]
    return jsonify({'success': True})
"""
if "@app.route('/content')" not in app_code:
    app_code = app_code.replace("if __name__ == '__main__':", routes + "\nif __name__ == '__main__':")
    with open('app.py', 'w') as f:
        f.write(app_code)
    print("Added Content routes to app.py")

# 2. Inject Content Hub EXACTLY in the middle of the footer
for filepath in glob.glob('templates/*.html'):
    if 'content.html' in filepath: continue
    with open(filepath, 'r') as f:
        html = f.read()
    
    if 'href="/content"' not in html:
        # Target the Analytics button and place Content right before it
        target = '<a href="/analytics"'
        replacement = """<a href="/content" class="flex flex-col items-center transition hover:text-purple-400 font-medium">
            <i class="fa-solid fa-folder-open text-sm mb-0.5"></i> Content
        </a>
        <a href="/analytics\""""
        
        if target in html:
            html = html.replace(target, replacement)
            with open(filepath, 'w') as f:
                f.write(html)
            print(f"Updated footer in {filepath}")

# 3. Generate the Content Hub HTML template
content_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nyla AutoPost - Content Hub</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body class="bg-[#0b0f17] text-gray-100 min-h-screen pb-24 p-4 sm:p-6">
    <div class="max-w-4xl mx-auto">
        <h1 class="text-2xl font-bold tracking-tight text-white flex items-center gap-2 mb-6">
            <i class="fa-solid fa-folder-open text-purple-400"></i> Content Manager
        </h1>
        
        <div class="space-y-4">
            <h2 class="text-sm font-bold text-gray-400 uppercase tracking-wider">Scheduled Queue</h2>
            {% for post in scheduled_posts %}
            <div class="bg-[#10121a] border border-gray-800 rounded-xl p-4 flex justify-between items-center">
                <div>
                    <p class="text-sm text-gray-200">{{ post.get('content', post.get('text', '')) }}</p>
                    <span class="text-xs text-amber-400">Scheduled: {{ post.get('scheduled_at') }}</span>
                </div>
                <div class="flex gap-2">
                    <button onclick="deletePost('{{ post.get('id') }}')" class="px-3 py-1.5 bg-red-500/10 text-red-400 border border-red-500/20 text-xs rounded-lg"><i class="fa-solid fa-trash"></i></button>
                </div>
            </div>
            {% else %}
            <p class="text-xs text-gray-600">No upcoming posts.</p>
            {% endfor %}

            <h2 class="text-sm font-bold text-gray-400 uppercase tracking-wider mt-8">Published History</h2>
            {% for post in published_posts %}
            <div class="bg-[#10121a] border border-gray-800 rounded-xl p-4">
                <p class="text-sm text-gray-200">{{ post.get('content', post.get('text', '')) }}</p>
                <span class="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 mt-2 inline-block">PUBLISHED</span>
            </div>
            {% else %}
            <p class="text-xs text-gray-600">No published posts yet.</p>
            {% endfor %}
        </div>
    </div>

    <!-- Replicated Footer -->
    <div class="fixed bottom-0 left-0 right-0 bg-[#0b0f17]/95 backdrop-blur-md border-t border-gray-800/80 py-2.5 px-4 flex justify-around items-center text-[11px] text-gray-400 z-40">
        <a href="/dashboard" class="flex flex-col items-center hover:text-gray-200"><i class="fa-solid fa-chart-pie text-sm mb-0.5"></i> Dashboard</a>
        <a href="/compose" class="flex flex-col items-center hover:text-gray-200"><i class="fa-solid fa-pen-nib text-sm mb-0.5"></i> Compose</a>
        <a href="/content" class="flex flex-col items-center text-purple-400 font-medium"><i class="fa-solid fa-folder-open text-sm mb-0.5"></i> Content</a>
        <a href="/analytics" class="flex flex-col items-center hover:text-gray-200"><i class="fa-solid fa-chart-line text-sm mb-0.5"></i> Analytics</a>
        <a href="/settings" class="flex flex-col items-center hover:text-gray-200"><i class="fa-solid fa-gear text-sm mb-0.5"></i> Settings</a>
    </div>

    <script>
        async function deletePost(id) {
            if(confirm('Delete this scheduled post?')) {
                await fetch('/api/delete-post/' + id, {method: 'POST'});
                location.reload();
            }
        }
    </script>
</body>
</html>
"""
with open('templates/content.html', 'w') as f:
    f.write(content_html)
print("Created templates/content.html")
