import os
import glob
import re

pages_dir = r"c:\Users\mathe\OneDrive\Desktop\fabricflow\frontend\pages"
html_files = glob.glob(os.path.join(pages_dir, "*.html"))

print(f"=== FABRICFLOW FRONTEND RESPONSIVE AUDIT ===")
print(f"Found {len(html_files)} HTML pages:\n")

all_passed = True

for f in sorted(html_files):
    name = os.path.basename(f)
    with open(f, "r", encoding="utf-8") as fh:
        content = fh.read()
    
    has_viewport = "name=\"viewport\"" in content or "name='viewport'" in content
    has_mobile_btn = "mobileMenuBtn" in content or name == "login.html"
    tables_count = len(re.findall(r"<table", content))
    resp_tables_count = len(re.findall(r"table-responsive", content))
    
    pass_viewport = "PASS" if has_viewport else "FAIL"
    pass_mobile_btn = "PASS" if has_mobile_btn else "FAIL"
    pass_tables = "PASS" if (tables_count == resp_tables_count) else "FAIL"
    
    print(f"Page: {name}")
    print(f"  [x] Viewport Meta Tag: {pass_viewport}")
    print(f"  [x] Mobile Hamburger Button: {pass_mobile_btn}")
    print(f"  [x] Table Responsiveness: {pass_tables} (Tables: {tables_count}, Responsive Containers: {resp_tables_count})")
    print("-" * 50)

print("\nAudit Complete.")
