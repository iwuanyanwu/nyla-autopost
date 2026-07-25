with open('templates/base.html', 'r') as f:
    text = f.read()

# Replace all corrupted url_for blocks with clean valid ones
text = text.replace('url_for(\'dashboard\')', 'url_for(\'dashboard\')')
text.replace('url_for(\'analytics\')', 'url_for(\'analytics\')')

# Let's cleanly reset the navigation hrefs for dashboard, analytics, and settings
import re
text = re.sub(r'href="[^"]*"\s*>\s*<i class="fa-solid fa-chart-pie', 'href="{{ url_for(\'dashboard\') }}">\n    <i class="fa-solid fa-chart-pie', text)
text = re.sub(r'href="[^"]*"\s*>\s*<i class="fa-solid fa-chart-line', 'href="{{ url_for(\'analytics\') }}">\n    <i class="fa-solid fa-chart-line', text)
text = re.sub(r'href="[^"]*"\s*>\s*<i class="fa-solid fa-gear', 'href="{{ url_for(\'settings\') }}">\n    <i class="fa-solid fa-gear', text)

with open('templates/base.html', 'w') as f:
    f.write(text)

print("Base template successfully repaired!")
