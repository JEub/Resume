from bs4 import BeautifulSoup
import os

def convert_html_to_markdown(html_file, md_file):
    """
    Converts the JE-Resume.html file to a structured Markdown file.
    """
    with open(html_file, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    # Remove non-content elements
    for s in soup(['svg', 'script', 'style', 'meta', 'link']):
        s.decompose()

    output = []

    # Header Info (Name, Title, Contact)
    hd = soup.find(id='hd')
    if hd:
        name_node = hd.find('h1')
        if name_node:
            output.append(f"# {name_node.get_text().strip()}\n")
        
        main_title_node = hd.find('h2')
        if main_title_node:
            output.append(f"## {main_title_node.get_text().strip()}\n")

        contact = hd.find(class_='contact-info')
        if contact:
            contacts = []
            for h3 in contact.find_all('h3'):
                text = h3.get_text().strip()
                if text and text not in contacts:
                    contacts.append(text)
            for c in contacts:
                output.append(f"- {c}")
            output.append("\n")

    # Content Sections (Experience, Education, Skills)
    for gf in soup.find_all(class_='yui-gf'):
        section_title_node = gf.find(class_='first')
        if not section_title_node:
            continue
        
        section_title = section_title_node.get_text().strip()
        output.append(f"### {section_title}\n")

        # Find the main content node
        content_nodes = gf.find_all(class_='yui-u')
        if len(content_nodes) < 2:
            content_node = gf.find(class_='yui-u', recursive=False)
            if not content_node: continue
        else:
            content_node = content_nodes[1]

        # Handle different section structures
        if section_title == "Technologies Used":
            talents = content_node.find_all(class_='talent')
            for t in talents:
                items = [li.get_text().strip() for li in t.find_all('li')]
                output.append(", ".join(items))
            output.append("\n")
        elif section_title == "Education":
            edu_items = gf.find_all(class_='education')
            for edu in edu_items:
                h2 = edu.find('h2')
                h3s = edu.find_all('h3')
                if h2:
                    output.append(f"**{h2.get_text().strip()}**")
                for h3 in h3s:
                    output.append(f"- {h3.get_text().strip()}")
                output.append("")
        else:
            # Experience / Jobs
            jobs = content_node.find_all(class_='job')
            for job in jobs:
                h2 = job.find('h2')
                h3 = job.find('h3')
                h4 = job.find('h4')
                if h2:
                    output.append(f"#### {h2.get_text().strip()}")
                if h3:
                    output.append(f"*{h3.get_text().strip()}*")
                if h4:
                    output.append(f"**{h4.get_text().strip()}**")
                
                bullets = job.find('ul', class_='bulleted-job')
                if bullets:
                    for li in bullets.find_all('li', recursive=False):
                        nested = li.find('ul')
                        if nested:
                            # Extract main text without nested list
                            clean_li = BeautifulSoup(str(li), 'html.parser')
                            if clean_li.ul: clean_li.ul.decompose()
                            main_text = clean_li.get_text().replace('\n', ' ').strip()
                            output.append(f"- {main_text}")
                            for nli in nested.find_all('li'):
                                output.append(f"  - {nli.get_text().strip()}")
                        else:
                            text = li.get_text().replace('\n', ' ').strip()
                            output.append(f"- {text}")
                output.append("")

    with open(md_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(output))

if __name__ == "__main__":
    convert_html_to_markdown('JE-Resume.html', 'JE-Resume.md')
    print("Successfully converted JE-Resume.html to JE-Resume.md")
