with open('templates/dashboard.html', 'r') as f:
    content = f.read()

# Replace the specific line causing the crash with a version that converts the datetime to a string first
bad_code = "{{ post.get('scheduled_at', 'Just now')[:16].replace('T', ' ') if post.get('scheduled_at') else 'Just now' }}"
good_code = "{{ (post.get('scheduled_at')|string)[:16].replace('T', ' ') if post.get('scheduled_at') else 'Just now' }}"

content = content.replace(bad_code, good_code)

with open('templates/dashboard.html', 'w') as f:
    f.write(content)

print("Datetime rendering bug fixed!")
