import re

with open('apps/dashboard/templates/dashboard/base.html', 'r', encoding='utf-8') as f:
    content = f.read()
    lines = content.split('\n')

# Count all {% if %} tags
if_tags = re.findall(r'\{%\s*if\s', content)
# Count all {% endif %} tags
endif_tags = re.findall(r'\{%\s*endif\s*%\}', content)
# Count all {% elif %} tags (these don't need separate endif)
elif_tags = re.findall(r'\{%\s*elif\s', content)

print("if tags: " + str(len(if_tags)))
print("elif tags: " + str(len(elif_tags)))
print("endif tags: " + str(len(endif_tags)))
print("\nExpected endif tags: " + str(len(if_tags)))
print("Difference: " + str(len(if_tags) - len(endif_tags)))

# Find line numbers of unclosed if tags
stack = []
unclosed = []

for i, line in enumerate(lines, 1):
    # Find if tags (but not elif)
    if_pattern = r'\{%\s*if\s+(?!.*elif)'
    if_matches = list(re.finditer(r'\{%\s*if\s', line))
    # Filter out elif
    if_matches = [m for m in if_matches if 'elif' not in line[m.start():m.end()+10]]
    
    endif_matches = re.findall(r'\{%\s*endif\s*%\}', line)
    
    for match in if_matches:
        stack.append(('if', i, line.strip()))
    
    for _ in endif_matches:
        if stack:
            stack.pop()
        else:
            print("Extra endif at line " + str(i) + ": " + line.strip())

if stack:
    print("\nUnclosed if tags:")
    for tag_type, line_num, line_text in stack:
        text = line_text[:100] if len(line_text) > 100 else line_text
        print("  Line " + str(line_num) + ": " + text)
