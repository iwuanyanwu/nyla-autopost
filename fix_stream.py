import re

with open('templates/dashboard.html', 'r') as f:
    content = f.read()

if "{% if recent_posts %}" not in content:
    # Safely target the exact empty state block using re.DOTALL
    pattern = r'(<div class="p-12 rounded-xl border border-dashed border-gray-800 text-center.*?COMPOSE FIRST POST\s*</a>\s*</div>)'
    
    dynamic_html = r"""{% if recent_posts %}
            <div class="space-y-3">
                {% for post in recent_posts %}
                <div class="bg-gray-900/40 border border-gray-800 hover:border-gray-700 transition rounded-xl p-4 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
                    <div>
                        <p class="text-sm text-gray-200 font-medium line-clamp-1">{{ post.get('content', post.get('text', 'No preview available')) }}</p>
                        <div class="flex items-center gap-2 mt-2">
                            <span class="text-[10px] px-2 py-0.5 rounded bg-[#10121a] border border-gray-700 text-gray-400 uppercase font-mono tracking-wider">{{ post.get('platforms', post.get('platform', 'API')) }}</span>
                            <span class="text-xs text-gray-500 flex items-center gap-1">
                                <i class="fa-regular fa-clock text-gray-600"></i>
                                {{ post.get('scheduled_at', 'Just now')[:16].replace('T', ' ') if post.get('scheduled_at') else 'Just now' }}
                            </span>
                        </div>
                    </div>
                    <span class="text-[10px] px-2.5 py-1 rounded-full font-bold tracking-wider {% if post.get('status', '')|lower == 'published' %}bg-emerald-500/10 text-emerald-400 border border-emerald-500/20{% else %}bg-amber-500/10 text-amber-400 border border-amber-500/20{% endif %}">
                        {{ post.get('status', 'PUBLISHED')|upper }}
                    </span>
                </div>
                {% endfor %}
            </div>
        {% else %}
\1
        {% endif %}"""
        
    content = re.sub(pattern, dynamic_html, content, flags=re.DOTALL)
    
    with open('templates/dashboard.html', 'w') as f:
        f.write(content)
    print("Dashboard stream successfully connected to database!")
else:
    print("Stream was already updated.")
