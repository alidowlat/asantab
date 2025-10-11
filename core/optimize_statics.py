import os, re
from bs4 import BeautifulSoup
from tinycss2 import parse_stylesheet

TEMPLATES_DIR = "templates"
STATIC_CSS_PATH = "static/css"
OUTPUT_PATH = "static/optimized_css"

os.makedirs(OUTPUT_PATH, exist_ok=True)

used_selectors = set()

for root, _, files in os.walk(TEMPLATES_DIR):
    for f in files:
        if f.endswith(".html"):
            with open(os.path.join(root, f), "r", encoding="utf-8") as file:
                soup = BeautifulSoup(file.read(), "html.parser")
                for tag in soup.find_all(True):
                    classes = tag.get("class", [])
                    ids = tag.get("id")
                    used_selectors.update([f".{cls}" for cls in classes])
                    if ids:
                        used_selectors.add(f"#{ids}")

for root, _, files in os.walk(STATIC_CSS_PATH):
    for f in files:
        if f.endswith(".css"):
            css_path = os.path.join(root, f)
            output_path = os.path.join(OUTPUT_PATH, f)

            with open(css_path, "r", encoding="utf-8") as file:
                css_content = file.read()

            rules = parse_stylesheet(css_content)
            cleaned_rules = []
            removed_count = 0

            for rule in rules:
                if not hasattr(rule, "prelude"):
                    cleaned_rules.append(rule)
                    continue

                selectors = re.split(r",\s*", rule.prelude.as_css())
                keep = any(sel.strip() in used_selectors for sel in selectors)
                if keep:
                    cleaned_rules.append(rule)
                else:
                    removed_count += 1

            with open(output_path, "w", encoding="utf-8") as out:
                out.write("".join([r.serialize() for r in cleaned_rules]))

            print(f"✅ Cleaned {f}: removed {removed_count} unused selectors")

print("\n🎯 Optimization done! Clean CSS saved in 'static/optimized_css/' folder.")
