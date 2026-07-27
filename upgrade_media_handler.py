import re
import os

print("🔧 Fixing media handler upgrade...")

# ==================== 1. UPDATE BACKEND (app.py) ====================

with open('app.py', 'r', encoding='utf-8') as f:
    app_code = f.read()

new_edit_route = """@app.route('/api/hub/edit-post/<int:post_id>', methods=['POST'])
def hub_edit_post(post_id):
    for p in POSTS_DB:
        if p.get('id') == post_id:
            if p.get('status') == 'published':
                return jsonify({'success': False, 'error': 'Cannot edit published posts'}), 400

            # Support both JSON and Form Data
            if request.is_json:
                data = request.get_json()
                if 'content' in data: p['content'] = data['content']
                if 'scheduled_at' in data: p['scheduled_at'] = data['scheduled_at']
                if 'platforms' in data: p['platforms'] = data['platforms']
                if 'x_premium' in data: p['x_premium'] = data['x_premium']
                if 'has_media' in data: p['has_media'] = data['has_media']
            else:
                if 'content' in request.form: p['content'] = request.form.get('content')
                if 'scheduled_at' in request.form: p['scheduled_at'] = request.form.get('scheduled_at')
                if 'platforms' in request.form:
                    import json
                    try:
                        p['platforms'] = json.loads(request.form.get('platforms', '[]'))
                    except:
                        pass
                if 'x_premium' in request.form:
                    p['x_premium'] = request.form.get('x_premium') == 'true'

                # Handle file upload
                if 'media_file' in request.files:
                    file = request.files['media_file']
                    if file and file.filename:
                        from werkzeug.utils import secure_filename
                        os.makedirs('static/uploads', exist_ok=True)
                        filename = secure_filename(file.filename)
                        filepath = os.path.join('static/uploads', filename)
                        file.save(filepath)
                        p['media_url'] = '/' + filepath.replace('\\\\', '/')
                        p['has_media'] = True

            return jsonify({'success': True})
    return jsonify({'success': False}), 404
"""

# Replace the route
app_code = re.sub(
    r'(@app\.route\(\'/api/hub/edit-post/<int:post_id>\', methods=\[\'POST\'\]\).*?)(?=\\s*def |@app\.route|$)',
    new_edit_route,
    app_code,
    flags=re.DOTALL | re.MULTILINE
)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(app_code)

print("✅ app.py updated successfully")

# ==================== 2. UPDATE FRONTEND ====================
print("✅ templates/content.html was already updated in previous run")

print("\\n🎉 Upgrade finished! Now run:")
print("python3 app.py")
