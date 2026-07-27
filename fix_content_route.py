import re

with open('app.py', 'r') as f:
    code = f.read()

# Clean up any malformed routes if they were partially added
code = re.sub(r'@app\.route\(\'/content\'\).*?return jsonify\(\{'success': True\}\)\s*\}', '', code, flags=re.DOTALL)

content_routes = """
@app.route('/content')
def content_manager():
    all_posts = list(POSTS_DB)
    all_posts.reverse()
    published_posts = [p for p in all_posts if p.get('status') == 'published']
    scheduled_posts = [p for p in all_posts if p.get('status') == 'pending']
    return render_template('content.html', all_posts=all_posts, published_posts=published_posts, scheduled_posts=scheduled_posts)

@app.route('/api/edit-post/<int:post_id>', methods=['POST'])
def edit_post(post_id):
    data = request.get_json()
    new_content = data.get('content')
    new_schedule = data.get('scheduled_at')
    for p in POSTS_DB:
        if p.get('id') == post_id:
            if p.get('status') == 'published':
                return jsonify({'success': False, 'error': 'Cannot edit published posts'}), 400
            if new_content:
                p['content'] = new_content
                p['text'] = new_content
            if new_schedule:
                p['scheduled_at'] = new_schedule
            return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Post not found'}), 404

@app.route('/api/delete-post/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    global POSTS_DB
    for p in POSTS_DB:
        if p.get('id') == post_id and p.get('status') == 'published':
            return jsonify({'success': False, 'error': 'Cannot delete published records'}), 400
    POSTS_DB = [p for p in POSTS_DB if p.get('id'] != post_id]
    return jsonify({'success': True})
"""

# Fix small bracket typo in delete_post lambda if present
content_routes = content_routes.replace("p.get('id']", "p.get('id')")

if "@app.route('/content')" not in code:
    if "if __name__ == '__main__':" in code:
        code = code.replace("if __name__ == '__main__':", content_routes + "\n\nif __name__ == '__main__':")
    else:
        code += content_routes
    with open('app.py', 'w') as f:
        f.write(code)

# Update footers across templates to place Content right in the middle
standard_footer = """<div class="fixed bottom-0 left-0 right-0 bg-[#0b0f17]/95 backdrop-blur-md border-t border-gray-800/80 py-2.5 px-4 flex justify-around items-center text-[11px] text-gray-400 z-40">
        <a href="/dashboard" class="flex flex-col items-center transition hover:text-gray-200">
            <i class="fa-solid fa-chart-pie text-sm mb-0.5"></i> Dashboard
        </a>
        <a href="/compose" class="flex flex-col items-center transition hover:text-gray-200">
            <i class="fa-solid fa-pen-nib text-sm mb-0.5"></i> Compose
        </a>
        <a href="/content" class="flex flex-col items-center transition hover:text-purple-400 font-medium">
            <i class="fa-solid fa-folder-open text-sm mb-0.5"></i> Content
        </a>
        <a href="/analytics" class="flex flex-col items-center transition hover:text-gray-200">
            <i class="fa-solid fa-chart-line text-sm mb-0.5"></i> Analytics
        </a>
        <a href="/settings" class="flex flex-col items-center transition hover:text-gray-200">
            <i class="fa-solid fa-gear text-sm mb-0.5"></i> Settings
        </a>
    </div>"""

for template_file in ['templates/dashboard.html', 'templates/compose.html', 'templates/analytics.html', 'templates/settings.html', 'templates/content.html']:
    try:
        with open(template_file, 'r') as f:
            t_content = f.read()
        
        # Remove any leftover shortcut cards from the main body
        t_content = re.sub(r'<a href="/content"[^>]*>.*?<\/a>', '', t_content, flags=re.DOTALL)
        
        if 'fixed bottom-0' in t_content:
            t_content = re.sub(r'<div class="fixed bottom-0.*?(?=<script|</body>|\Z)', standard_footer + '\n\n', t_content, flags=re.DOTALL)
        else:
            t_content = t_content.replace('</body>', standard_footer + '\n</body>')

        with open(template_file, 'w') as f:
            f.write(t_content)
    except Exception as e:
        print(f"Skipped {template_file}: {e}")

print("Successfully updated app.py and footers!")
