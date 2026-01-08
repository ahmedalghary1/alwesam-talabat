
import re

def parse_tags(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')
    stack = []
    
    # Simple regex for block tags
    # This is a naive parser but might catch the issue
    tag_re = re.compile(r'{%\s*(\w+)\b')
    
    for i, line in enumerate(lines):
        line_num = i + 1
        pos = 0
        while True:
            match = tag_re.search(line, pos)
            if not match:
                break
            
            tag_name = match.group(1)
            pos = match.end()
            print(f"DEBUG: Found tag {tag_name}")
            
            # Logic for block tags
            if tag_name in ['if', 'for', 'block', 'with', 'while', 'ifequal', 'ifnotequal']:
                stack.append((tag_name, line_num))
                # print(f"Line {line_num}: Open {tag_name}")
            elif tag_name in ['endif', 'endfor', 'endblock', 'endwith', 'endwhile', 'endifequal', 'endifnotequal']:
                if not stack:
                    print(f"Error at line {line_num}: Unexpected {tag_name}")
                    return
                
                last_tag, last_line = stack[-1] # Peek
                
                expected_end = 'end' + last_tag
                if tag_name == expected_end:
                     stack.pop()
                     # print(f"Line {line_num}: Close {tag_name}")
                else:
                    # Mismatch
                    # In Django, if we are closing a block but 'if' is open, it's an error.
                    # Or if we close 'if' but 'for' is open...
                    # But also 'elif' and 'else' are allowed inside 'if'.
                    pass 
                    
                # Strict check:
                if tag_name != expected_end:
                     print(f"Error at line {line_num}: Found {tag_name}, expected {expected_end} for {last_tag} opened at {last_line}")
                     return

    if stack:
        print("Unclosed tags remaining:")
        for tag, line in stack:
            print(f"  {tag} at line {line}")
    else:
        print("All tags balanced.")

if __name__ == '__main__':
    parse_tags('templates/products/product_detail.html')
