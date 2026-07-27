import re

# 1. Update app.py to include content editing and robust management routes
with open('app.py', 'r') as f:
    app_code = f.read()

content_routes = """
@app.route('/content')
def content_manager():
    all_posts = list(POSTS_DB)
    all_posts.reverse()
    
    published_posts = [p for p in all_posts if p.get('status') == 'published']
    scheduled_posts = [p for p in all_posts if p.get('status') == 'pending']
    
    return render_template('content.html', 
                           all_posts=all_posts, 
                           published_posts=published_posts, 
                           scheduled_posts=scheduled_posts)

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
            return jsonify({'success': False, 'error': 'Cannot delete published audit records'}), 400
            
    POSTS_DB = [p for p in POSTS_DB if p.get('id') != post_id]
    return jsonify({'success': True})
"""

if "/api/edit-post" not in app_code:
    app_code += content_routes
    with open('app.py', 'w') as f:
        f.write(app_code)

# 2. Create the complete content management workspace template
content_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nyla AutoPost - Content Hub</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        .tab-btn.active { background-color: #7c3aed !important; color: white !important; border-color: #8b5cf6 !important; }
    </style>
</head>
<body class="bg-[#0b0f17] text-gray-100 min-h-screen pb-24">
    <div class="max-w-4xl mx-auto p-4 sm:p-6">
        <!-- Top Nav -->
        <div class="flex justify-between items-center mb-6">
            <div class="flex items-center space-x-2">
                <span class="bg-purple-600 text-white font-bold px-2.5 py-1 rounded-lg text-sm">N</span>
                <span class="font-bold text-lg tracking-wide">Nyla <span class="text-purple-400 font-normal text-sm">Content Hub</span></span>
            </div>
            <a href="/dashboard" class="bg-gray-800 hover:bg-gray-700 text-xs text-gray-300 px-3 py-1.5 rounded-lg border border-gray-700 transition flex items-center gap-1.5">
                <i class="fa-solid fa-arrow-left"></i> Dashboard
            </a>
        </div>

        <!-- Header -->
        <div class="bg-gradient-to-r from-gray-900 to-[#121824] border border-gray-800 rounded-2xl p-6 mb-6 shadow-xl">
            <h1 class="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
                <i class="fa-solid fa-folder-open text-purple-400"></i> Content Manager
            </h1>
            <p class="text-sm text-gray-400 mt-1">Review historical posts, edit upcoming text, and manage your live scheduled queue.</p>
        </div>

        <!-- Filter Tabs -->
        <div class="flex flex-wrap gap-2 mb-6">
            <button onclick="switchTab('all')" id="tab-all" class="tab-btn active px-4 py-2 rounded-xl text-xs font-semibold bg-gray-900 border border-gray-800 text-gray-400 transition">
                All Posts ({{ all_posts|length }})
            </button>
            <button onclick="switchTab('scheduled')" id="tab-scheduled" class="tab-btn px-4 py-2 rounded-xl text-xs font-semibold bg-gray-900 border border-gray-800 text-gray-400 transition">
                Scheduled Queue ({{ scheduled_posts|length }})
            </button>
            <button onclick="switchTab('published')" id="tab-published" class="tab-btn px-4 py-2 rounded-xl text-xs font-semibold bg-gray-900 border border-gray-800 text-gray-400 transition">
                Published ({{ published_posts|length }})
            </button>
        </div>

        <!-- All Posts Section -->
        <div id="section-all" class="post-section space-y-3">
            {% if all_posts %}
                {% for post in all_posts %}
                <div class="bg-[#10121a] border border-gray-800 rounded-xl p-4 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                    <div class="space-y-1">
                        <p class="text-sm text-gray-200 font-medium">{{ post.get('content', post.get('text', '')) }}</p>
                        <div class="flex items-center gap-2">
                            <span class="text-[10px] px-2 py-0.5 rounded bg-gray-900 border border-gray-800 text-gray-400 uppercase font-mono">{{ post.get('platforms', post.get('platform', 'all')) }}</span>
                            <span class="text-xs text-gray-500">{{ (post.get('scheduled_at')|string)[:16].replace('T', ' ') if post.get('scheduled_at') else 'Just now' }}</span>
                        </div>
                    </div>
                    <div class="flex items-center gap-3">
                        <span class="text-[10px] px-2.5 py-1 rounded-full font-bold {% if post.get('status') == 'published' %}bg-emerald-500/10 text-emerald-400 border border-emerald-500/20{% else %}bg-amber-500/10 text-amber-400 border border-amber-500/20{% endif %}">
                            {{ post.get('status', 'published')|upper }}
                        </span>
                        {% if post.get('status') == 'pending' %}
                        <button onclick="openEditModal('{{ post.get('id') }}', '{{ post.get('content', post.get('text', ''))|replace("'", "\\'") }}', '{{ post.get('scheduled_at', '') }}')" class="px-3 py-1.5 bg-purple-600/20 hover:bg-purple-600/30 text-purple-300 border border-purple-500/30 text-xs rounded-lg transition">
                            <i class="fa-solid fa-pen"></i> Edit
                        </button>
                        <button onclick="deletePost('{{ post.get('id') }}')" class="px-3 py-1.5 bg-red-500/10 hover:bg-red-500/20 text-red-400 border border-red-500/20 text-xs rounded-lg transition">
                            <i class="fa-solid fa-trash"></i>
                        </button>
                        {% endif %}
                    </div>
                </div>
                {% endfor %}
            {% else %}
                <div class="text-center py-16 bg-[#10121a] border border-gray-800 rounded-2xl text-gray-500 text-sm">No posts found.</div>
            {% endif %}
        </div>

        <!-- Scheduled Queue Section -->
        <div id="section-scheduled" class="post-section space-y-3 hidden">
            {% if scheduled_posts %}
                {% for post in scheduled_posts %}
                <div class="bg-[#10121a] border border-gray-800 rounded-xl p-4 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                    <div class="space-y-1">
                        <p class="text-sm text-gray-200 font-medium">{{ post.get('content', post.get('text', '')) }}</p>
                        <div class="flex items-center gap-2">
                            <span class="text-[10px] px-2 py-0.5 rounded bg-gray-900 border border-gray-800 text-gray-400 uppercase font-mono">{{ post.get('platforms', post.get('platform', 'all')) }}</span>
                            <span class="text-xs text-amber-400/80">Scheduled for: {{ (post.get('scheduled_at')|string)[:16].replace('T', ' ') }}</span>
                        </div>
                    </div>
                    <div class="flex items-center gap-3">
                        <span class="text-[10px] px-2.5 py-1 rounded-full font-bold bg-amber-500/10 text-amber-400 border border-amber-500/20">PENDING</span>
                        <button onclick="openEditModal('{{ post.get('id') }}', '{{ post.get('content', post.get('text', ''))|replace("'", "\\'") }}', '{{ post.get('scheduled_at', '') }}')" class="px-3 py-1.5 bg-purple-600/20 hover:bg-purple-600/30 text-purple-300 border border-purple-500/30 text-xs rounded-lg transition">
                            <i class="fa-solid fa-pen"></i> Edit
                        </button>
                        <button onclick="deletePost('{{ post.get('id') }}')" class="px-3 py-1.5 bg-red-500/10 hover:bg-red-500/20 text-red-400 border border-red-500/20 text-xs rounded-lg transition">
                            <i class="fa-solid fa-trash"></i> Cancel
                        </button>
                    </div>
                </div>
                {% endfor %}
            {% else %}
                <div class="text-center py-16 bg-[#10121a] border border-gray-800 rounded-2xl text-gray-500 text-sm">No scheduled posts in queue.</div>
            {% endif %}
        </div>

        <!-- Published Section -->
        <div id="section-published" class="post-section space-y-3 hidden">
            {% if published_posts %}
                {% for post in published_posts %}
                <div class="bg-[#10121a] border border-gray-800 rounded-xl p-4 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                    <div class="space-y-1">
                        <p class="text-sm text-gray-200 font-medium">{{ post.get('content', post.get('text', '')) }}</p>
                        <div class="flex items-center gap-2">
                            <span class="text-[10px] px-2 py-0.5 rounded bg-gray-900 border border-gray-800 text-gray-400 uppercase font-mono">{{ post.get('platforms', post.get('platform', 'all')) }}</span>
                            <span class="text-xs text-gray-500">{{ (post.get('scheduled_at')|string)[:16].replace('T', ' ') if post.get('scheduled_at') else 'Just now' }}</span>
                        </div>
                    </div>
                    <span class="text-[10px] px-2.5 py-1 rounded-full font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">PUBLISHED</span>
                </div>
                {% endfor %}
            {% else %}
                <div class="text-center py-16 bg-[#10121a] border border-gray-800 rounded-2xl text-gray-500 text-sm">No published posts yet.</div>
            {% endif %}
        </div>
    </div>

    <!-- Edit Modal -->
    <div id="editModal" class="hidden fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50">
        <div class="bg-[#10121a] border border-gray-800 rounded-2xl p-6 w-full max-w-lg shadow-2xl">
            <h3 class="text-lg font-bold text-white mb-4 flex items-center gap-2">
                <i class="fa-solid fa-pen-to-square text-purple-400"></i> Edit Scheduled Post
            </h3>
            <input type="hidden" id="editPostId">
            <div class="space-y-4">
                <div>
                    <label class="block text-xs font-semibold uppercase tracking-wider text-gray-400 mb-2">Content</label>
                    <textarea id="editContentInput" rows="4" class="w-full bg-gray-900 border border-gray-800 rounded-xl p-3 text-sm text-gray-200 focus:outline-none focus:border-purple-500"></textarea>
                </div>
                <div>
                    <label class="block text-xs font-semibold uppercase tracking-wider text-gray-400 mb-2">Scheduled Time</label>
                    <input type="datetime-local" id="editScheduleInput" class="w-full bg-gray-900 border border-gray-800 rounded-xl p-3 text-sm text-gray-200 focus:outline-none focus:border-purple-500">
                </div>
                <div class="flex justify-end gap-3 pt-2">
                    <button onclick="closeEditModal()" class="px-4 py-2 bg-gray-800 hover:bg-gray-700 text-gray-300 text-xs font-semibold rounded-xl transition">Cancel</button>
                    <button onclick="submitEdit()" class="px-4 py-2 bg-purple-600 hover:bg-purple-500 text-white text-xs font-semibold rounded-xl transition">Save Changes</button>
                </div>
            </div>
        </div>
    </div>

    <!-- Bottom Nav Bar -->
    <div class="fixed bottom-0 left-0 right-0 bg-[#0b0f17]/90 backdrop-blur-md border-t border-gray-800 py-3 px-6 flex justify-around items-center text-xs text-gray-400">
        <a href="/dashboard" class="flex flex-col items-center hover:text-gray-200 transition">
            <i class="fa-solid fa-chart-pie text-base mb-1"></i> Dashboard
        </a>
        <a href="/content" class="flex flex-col items-center text-purple-400 font-medium">
            <i class="fa-solid fa-folder-open text-base mb-1"></i> Content
        </a>
        <a href="/compose" class="flex flex-col items-center hover:text-gray-200 transition">
            <i class="fa-solid fa-pen-nib text-base mb-1"></i> Compose
        </a>
        <a href="/analytics" class="flex flex-col items-center hover:text-gray-200 transition">
            <i class="fa-solid fa-chart-line text-base mb-1"></i> Analytics
        </a>
    </div>

    <script>
        function switchTab(tabName) {
            document.querySelectorAll('.post-section').forEach(el => el.classList.add('hidden'));
            document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
            
            document.getElementById('section-' + tabName).classList.remove('hidden');
            document.getElementById('tab-' + tabName).classList.add('active');
        }

        function openEditModal(id, content, schedule) {
            document.getElementById('editPostId').value = id;
            document.getElementById('editContentInput').value = content;
            if (schedule) {
                document.getElementById('editScheduleInput').value = schedule.replace(' ', 'T').substring(0, 16);
            }
            document.getElementById('editModal').classList.remove('hidden');
        }

        function closeEditModal() {
            document.getElementById('editModal').classList.add('hidden');
        }

        async function submitEdit() {
            const id = document.getElementById('editPostId').value;
            const content = document.getElementById('editContentInput').value;
            const scheduled_at = document.getElementById('editScheduleInput').value;

            const res = await fetch('/api/edit-post/' + id, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ content, scheduled_at })
            });

            if (res.ok) {
                location.reload();
            } else {
                const err = await res.json();
                alert(err.error || 'Failed to update post');
            }
        }

        async function deletePost(postId) {
            if (!confirm('Are you sure you want to cancel and delete this scheduled post?')) return;
            const res = await fetch('/api/delete-post/' + postId, { method: 'POST' });
            if (res.ok) {
                location.reload();
            } else {
                const err = await res.json();
                alert(err.error || 'Failed to delete post.');
            }
        }
    </script>
</body>
</html>
"""

with open('templates/content.html', 'w') as f:
    f.write(content_html)

# 3. Ensure Content shortcut exists in dashboard
with open('templates/dashboard.html', 'r') as f:
    dash_html = f.read()

if "/content" not in dash_html:
    shortcut_target = '<a href="/ai-writer"'
    content_shortcut = """<a href="/content" class="p-4 rounded-xl bg-[#10121a] border border-gray-800/80 hover:border-purple-500/40 flex items-center gap-4 transition-all group">
                    <div class="w-10 h-10 rounded-xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-purple-400 group-hover:scale-105 transition-transform">
                        <i class="fa-solid fa-folder-open"></i>
                    </div>
                    <div>
                        <h4 class="text-xs font-semibold uppercase tracking-wider text-white">Content Hub</h4>
                        <p class="text-[11px] text-gray-400 mt-0.5">Manage queue & published posts</p>
                    </div>
                </a>
                <a href="/ai-writer\""""
    dash_html = dash_html.replace(shortcut_target, content_shortcut, 1)
    with open('templates/dashboard.html', 'w') as f:
        f.write(dash_html)

print("Content Hub with full Edit/Delete logic successfully deployed!")
