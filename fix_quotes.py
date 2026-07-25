with open('templates/base.html', 'r') as f:
    text = f.read()

# Put proper single quotes inside url_for calls
text = text.replace('url_for(dashboard)', 'url_for(\'dashboard\')')
text = text.replace('url_for(analytics)', 'url_for(\'analytics\')')
text = text.replace('url_for(settings)', 'url_for(\'settings\')')

with open('templates/base.html', 'w') as f:
    f.write(text)

print("Quotes fixed successfully!")
