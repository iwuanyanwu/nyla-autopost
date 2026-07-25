with open('app.py', 'r') as f:
    text = f.read()

# Clean up anything after the main execution block or remove duplicate routes
if "if __name__ == '__main__':" in text:
    parts = text.split("if __name__ == '__main__':")
    core_code = parts[0]
else:
    core_code = text

# Remove any broken text lines at the end of core_code
clean_code = core_code.split("@app.route('/analytics')")[0].strip()

# Append a clean, working analytics route and main block
final_code = clean_code + '''

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
'''

with open('app.py', 'w') as f:
    f.write(final_code)

print("app.py successfully cleaned and fixed!")
