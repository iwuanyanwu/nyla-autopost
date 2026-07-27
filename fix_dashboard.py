import re

with open('templates/dashboard.html', 'r') as f:
    content = f.read()

# 1. Update the Analytics Counters (Targeting only the 0s, keeping your design)
content = re.sub(r'(<div[^>]*class="[^"]*text-3xl[^"]*text-white[^"]*"[^>]*>)\s*0\s*(<\/div>)', r'\1{{ total_posts }}\2', content)
content = re.sub(r'(<div[^>]*class="[^"]*text-3xl[^"]*text-emerald-400[^"]*"[^>]*>)\s*0\s*(<\/div>)', r'\1{{ published }}\2', content)
content = re.sub(r'(<div[^>]*class="[^"]*text-3xl[^"]*text-amber-400[^"]*"[^>]*>)\s*0\s*(<\/div>)', r'\1{{ scheduled }}\2', content)

# 2. Update the Recent Content Stream (Wrapping your exact design with Jinja logic)
if "{% if recent_posts %}" not in content:
    # Locate your exact "No active queue items" block so we can preserve it
    empty_state_pattern = r'(<div[^>]*class="[^"]*text-center[^"]*border-dashed[^"]*"[^>]*>.*?COMPOSE FIRST POST.*?<\/a>\s*<\/div>)'
    
    dynamic_stream_html = r"""{% if recent_posts %}
                <div class="space-y-3">
                    {% for post in recent_posts %}
                    <div class="bg-gray-900/60 border border-gray-800 rounded-xl p-4 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
                        <div>
                            <p class="text-sm text-gray-200 font-medium line-clamp-1">{{ post.content }}</p>
                            <div class="flex items-center gap-2 mt-1">
                                <span class="text-xs px-2 py-0.5 rounded bg-gray-800 text-gray-400 uppercase font-mono">{{ post.platform }}</span>
                                <span class="text-xs text-gray-500">
                                    {% if post.status == 'published' %}Published at:{% else %}Scheduled for:{% endif %} 
                                    <span class="text-gray-400">{{ post.scheduled_at[:16].replace('T', ' ') if post.scheduled_at else 'Just now' }}</span>
                                </span>
                            </div>
                        </div>
                        <span class="text-xs px-2.5 py-1 rounded-full font-semibold {% if post.status == 'published' %}bg-emerald-500/10 text-emerald-400 border border-emerald-500/20{% else %}bg-amber-500/10 text-amber-400 border border-amber-500/20{% endif %}">
                            {{ post.status|upper }}
                        </span>
                    </div>
                    {% endfor %}
                </div>
            {% else %}
\1
            {% endif %}"""
    
    # Replace the static stream with the dynamic one (dropping your original empty state into the {% else %} block)
    content = re.sub(empty_state_pattern, dynamic_stream_html, content, flags=re.DOTALL)

with open('templates/dashboard.html', 'w') as f:
    f.write(content)
    
print("Dashboard data connections fixed without altering design!")
