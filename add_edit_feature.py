import os

# 1. Add the backend Edit Route
with open('app.py', 'r') as f:
    app_code = f.read()

edit_route = """
@app.route('/api/hub/edit-post/<int:post_id>', methods=['POST'])
def hub_edit_post(post_id):
    data = request.get_json()
    for p in POSTS_DB:
        if p.get('id') == post_id:
            if p.get('status') == 'published': 
                return jsonify({'success': False, 'error': 'Cannot edit published posts'}), 400
            
            if data.get('content'):
                p['content'] = data.get('content')
                p['text'] = data.get('content')
            if data.get('scheduled_at'):
                p['scheduled_at'] = data.get('scheduled_at')
            return jsonify({'success': True})
    return jsonify({'success': False}), 404
"""

if "def hub_edit_post" not in app_code:
    app_code = app_code.replace("if __name__ == '__main__':", edit_route + "\nif __name__ == '__main__':")
    with open('app.py', 'w') as f:
        f.write(app_code)
    print("Added Edit backend route successfully!")

# 2. Update Content Hub Template with Edit Modal
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
                <div class="flex-1 pr-4">
                    <p class="text-sm text-gray-200">{{ post.get('content', post.get('text', '')) }}</p>
                    <span class="text-xs text-amber-400">Scheduled: {{ post.get('scheduled_at') }}</span>
                </div>
                <div class="flex gap-2">
                    <button data-id="{{ post.get('id') }}" data-content="{{ post.get('content', post.get('text', '')) }}" data-date="{{ post.get('scheduled_at') }}" onclick="openEditModal(this)" class="px-3 py-1.5 bg-blue-500/10 text-blue-400 border border-blue-500/20 text-xs rounded-lg transition hover:bg-blue-500/20"><i class="fa-solid fa-pen"></i></button>
                    <button onclick="deletePost('{{ post.get('id') }}')" class="px-3 py-1.5 bg-red-500/10 text-red-400 border border-red-500/20 text-xs rounded-lg transition hover:bg-red-500/20"><i class="fa-solid fa-trash"></i></button>
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

    <!-- Edit Modal -->
    <div id="editModal" class="hidden fixed inset-0 bg-black/80 z-50 flex items-center justify-center p-4 backdrop-blur-sm">
        <div class="bg-[#10121a] border border-gray-800 rounded-xl p-6 w-full max-w-md shadow-2xl">
            <h3 class="text-white font-bold mb-4 flex items-center gap-2"><i class="fa-solid fa-pen text-blue-400"></i> Edit Scheduled Post</h3>
            <input type="hidden" id="editPostId">
            
            <label class="block text-xs text-gray-400 mb-1">Post Content</label>
            <textarea id="editContent" class="w-full bg-[#0b0f17] border border-gray-700 text-gray-200 rounded-lg p-3 text-sm mb-4 focus:outline-none focus:border-purple-500" rows="4"></textarea>
            
            <label class="block text-xs text-gray-400 mb-1">Scheduled Time (Optional)</label>
            <input type="datetime-local" id="editDate" class="w-full bg-[#0b0f17] border border-gray-700 text-gray-200 rounded-lg p-3 text-sm mb-6 focus:outline-none focus:border-purple-500">
            
            <div class="flex justify-end gap-3">
                <button onclick="closeEditModal()" class="px-4 py-2 text-sm text-gray-400 hover:text-white transition">Cancel</button>
                <button onclick="saveEdit()" class="px-4 py-2 text-sm bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition font-medium">Save Changes</button>
            </div>
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
        function openEditModal(btn) {
            document.getElementById('editPostId').value = btn.getAttribute('data-id');
            document.getElementById('editContent').value = btn.getAttribute('data-content');
            
            let dateStr = btn.getAttribute('data-date');
            if(dateStr && dateStr.length >= 16) {
                try {
                    let formatted = dateStr.replace(' ', 'T').substring(0,16);
                    document.getElementById('editDate').value = formatted;
                } catch(e) {}
            }
            document.getElementById('editModal').classList.remove('hidden');
        }

        function closeEditModal() {
            document.getElementById('editModal').classList.add('hidden');
        }

        async function saveEdit() {
            const id = document.getElementById('editPostId').value;
            const content = document.getElementById('editContent').value;
            const dateVal = document.getElementById('editDate').value;
            
            const payload = { content: content };
            if(dateVal) {
                payload.scheduled_at = dateVal.replace('T', ' ') + ':00';
            }

            const res = await fetch('/api/hub/edit-post/' + id, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            
            if(res.ok) {
                location.reload();
            } else {
                alert('Failed to save changes.');
            }
        }

        async function deletePost(id) {
            if(confirm('Delete this scheduled post?')) {
                await fetch('/api/hub/delete-post/' + id, {method: 'POST'});
                location.reload();
            }
        }
    </script>
</body>
</html>
"""

with open('templates/content.html', 'w') as f:
    f.write(content_html)
print("Added Edit modal and buttons to content.html!")
