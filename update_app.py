with open('app.py', 'r') as f:
    code = f.read()

# Add content manager route if not already present
if "'/content'" not in code:
    routes = """

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
    POSTS_DB = [p for p in POSTS_DB if p.get('id') != post_id]
    return jsonify({'success': True})
"""
    if "if __name__ == '__main__':" in code:
        code = code.replace("if __name__ == '__main__':", routes + "\n\nif __name__ == '__main__':")
    else:
        code += routes
    
    with open('app.py', 'w') as f:
        f.write(code)
    print("app.py updated successfully!")
else:
    print("Content route already exists in app.py")
