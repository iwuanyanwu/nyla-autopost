with open('app.py', 'r') as f:
    lines = f.readlines()

# Filter out old analytics route if present
new_lines = []
skip = False
for line in lines:
    if "@app.route('/analytics')" in line:
        skip = True
    elif skip and line.startswith("@app.route"):
        skip = False
    
    if not skip:
        new_lines.append(line)

# Append the correct robust analytics route
analytics_block = '''

@app.route('/analytics')
def analytics():
    posts = globals().get('POSTS_DB', [])
    total = len(posts)
    published = sum(1 for p in posts if p.get('status') == 'published')
    scheduled = total - published
    
    ig_count = 0
    x_count = 0
    li_count = 0
    fb_count = 0
    
    for p in posts:
        plat_data = p.get('platform') or p.get('platforms') or p.get('network') or ''
        if isinstance(plat_data, list):
            plat_str = ' '.join(str(x) for x in plat_data).lower()
        else:
            plat_str = str(plat_data).lower()
            
        if 'instagram' in plat_str:
            ig_count += 1
        if any(k in plat_str for k in ['x', 'twitter']):
            x_count += 1
        if 'linkedin' in plat_str:
            li_count += 1
        if 'facebook' in plat_str:
            fb_count += 1
            
    return render_template('analytics.html', 
                           total_posts=total, 
                           published=published, 
                           scheduled=scheduled,
                           ig_count=ig_count,
                           x_count=x_count,
                           li_count=li_count,
                           fb_count=fb_count,
                           posts=posts)
'''

new_lines.append(analytics_block)

with open('app.py', 'w') as f:
    f.writelines(new_lines)

print("Successfully updated app.py!")
