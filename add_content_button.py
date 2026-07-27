import re

standard_footer = """<div class="fixed bottom-0 left-0 right-0 bg-[#0b0f17]/95 backdrop-blur-md border-t border-gray-800/80 py-2.5 px-4 flex justify-around items-center text-[11px] text-gray-400 z-40">
        <a href="/dashboard" class="flex flex-col items-center transition hover:text-gray-200">
            <i class="fa-solid fa-chart-pie text-sm mb-0.5"></i> Dashboard
        </a>
        <a href="/compose" class="flex flex-col items-center transition hover:text-gray-200">
            <i class="fa-solid fa-pen-nib text-sm mb-0.5"></i> Compose
        </a>
        <a href="/content" class="flex flex-col items-center transition hover:text-purple-400 font-medium">
            <i class="fa-solid fa-folder-open text-sm mb-0.5"></i> Content
        </a>
        <a href="/analytics" class="flex flex-col items-center transition hover:text-gray-200">
            <i class="fa-solid fa-chart-line text-sm mb-0.5"></i> Analytics
        </a>
        <a href="/settings" class="flex flex-col items-center transition hover:text-gray-200">
            <i class="fa-solid fa-gear text-sm mb-0.5"></i> Settings
        </a>
    </div>"""

for template_file in ['templates/dashboard.html', 'templates/compose.html', 'templates/analytics.html', 'templates/settings.html', 'templates/content.html']:
    try:
        with open(template_file, 'r') as f:
            content = f.read()
        
        # Replace existing bottom navigation bar with the correct 5-item centered footer
        if 'fixed bottom-0' in content:
            content = re.sub(r'<div class="fixed bottom-0.*?(?=<script|</body>|\Z)', standard_footer + '\n\n', content, flags=re.DOTALL)
        else:
            content = content.replace('</body>', standard_footer + '\n</body>')

        with open(template_file, 'w') as f:
            f.write(content)
        print(f"Added Content button to footer in {template_file}")
    except Exception as e:
        print(f"Skipped {template_file}: {e}")
