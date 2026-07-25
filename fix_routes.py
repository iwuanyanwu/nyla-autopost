with open('app.py', 'r') as f:
    text = f.read()

# Add a 404 error handler and a root redirect to prevent Not Found errors
error_handler = '''

@app.errorhandler(404)
def page_not_found(e):
    return redirect(url_for('analytics'))

@app.route('/')
def index():
    return redirect(url_for('analytics'))
'''

if 'page_not_found' not in text:
    text = text.strip() + error_handler
    with open('app.py', 'w') as f:
        f.write(text)
    print("Added fallback routes and 404 handler!")
else:
    print("Fallback routes already present.")
