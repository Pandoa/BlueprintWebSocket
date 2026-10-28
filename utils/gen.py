import json
import os
from xml.etree import ElementTree as ET
from xml.dom import minidom

def main():
    with open("./defaults.json", "r", encoding="utf-8") as f:
        defaults = json.load(f)
    
    with open("./pseo.template", "r", encoding="utf-8") as f:
        content = f.read()
        
    with open("./kw.json", "r", encoding="utf-8") as f:
        db = json.load(f)
        
    output_dir = "../docs"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    base_url = "https://pandoa.github.io/BlueprintWebSocket"
    
    backlinks = []
    urlset = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    
    url_el = ET.SubElement(urlset, "url")
    loc_el = ET.SubElement(url_el, "loc")
    loc_el.text = f"{base_url}/index.html"
    
    changefreq_el = ET.SubElement(url_el, "changefreq")
    changefreq_el.text = "daily"
    
    priority_el = ET.SubElement(url_el, "priority")
    priority_el.text = "1.0"
    
    for e in db:
        e = {**defaults, **e}
        
        c = content
        for k, v in e.items():
            c = c.replace(f"{{{{{k}}}}}", v)
            
        file_slug = e.get("plugin_slug", "unreal-engine-websocket-plugin")
        filename = f"{file_slug}.html"
        output_path = os.path.join(output_dir, filename)
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(c)
            
        backlinks.append({
            "url": f"{base_url}/{filename}".replace("index.html", "").split(".html")[0],
            "anchor": e.get("target_keyword_h1", "WebSocket Documentation")
        })
        
        print(backlinks[-1])
        
        url_el = ET.SubElement(urlset, "url")
        loc_el = ET.SubElement(url_el, "loc")
        loc_el.text = f"{base_url}/{filename}".replace('index.html', '').split('.html')[0]
        
        changefreq_el = ET.SubElement(url_el, "changefreq")
        changefreq_el.text = "monthly"
        
        priority_el = ET.SubElement(url_el, "priority")
        priority_el.text = "0.8"

    html_links = "".join([f'        <li><a href="{link["url"]}">{link["anchor"]}</a></li>\n' for link in backlinks])
    backlink_page_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BlueprintWebSocket Documentation Hub</title>
    <style>
        body {{ font-family: -apple-system, sans-serif; background: #000; color: #fff; padding: 3rem; }}
        h1 {{ font-size: 1.75rem; margin-bottom: 2rem; }}
        ul {{ list-style: none; padding: 0; }}
        li {{ margin-bottom: 0.75rem; }}
        a {{ color: #2997ff; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <h1>BlueprintWebSocket Module Index</h1>
    <ul>
{html_links}    </ul>
</body>
</html>"""

    with open(os.path.join(output_dir, "links.html"), "w", encoding="utf-8") as f:
        f.write(backlink_page_content)

    raw_xml = ET.tostring(urlset, encoding="utf-8")
    parsed_xml = minidom.parseString(raw_xml)
    pretty_xml = parsed_xml.toprettyxml(indent="  ", encoding="utf-8")
    
    with open(os.path.join(output_dir, "sitemap.xml"), "wb") as f:
        f.write(pretty_xml)

if __name__ == '__main__':
    main()