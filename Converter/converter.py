import os
import requests
import re
import json
import yaml
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Define paths
source_folder_path = "/Users/liudmilanemkova/Desktop/Migration from readme to docusaurus"
target_folder_path = "/Users/liudmilanemkova/Desktop/Migration result"
issues_folder_path = "/Users/liudmilanemkova/Desktop/Migration result/With_issues"
img_folder_path = os.path.join(target_folder_path, "img")

# Create target and issues folders if they do not exist
os.makedirs(target_folder_path, exist_ok=True)
os.makedirs(issues_folder_path, exist_ok=True)
os.makedirs(img_folder_path, exist_ok=True)

# List of files to be placed in the "With_issues" folder
issues_files = [
    "getting-started-checklist.md",
    "release-checklist-copy.md",
    "analytics-retention.md",
    "analytics-funnels.md",
    "audiences.md",
    "importing-historical-data-to-adapty-copy.md",
    "paywall-builder-fetching.md",
    "server-side-api-specs-old.md",
    "slack.md",
    "switch-from-appsflyer-s2s-api-2-to-3.md",
    "testing-purchases-ios-old.md"
]

# Function to download and save images locally
def save_image_locally(img_url, img_folder_path):
    img_name = os.path.basename(img_url)
    img_path = os.path.join(img_folder_path, img_name)
    if not os.path.exists(img_path):
        try:
            response = requests.get(img_url, stream=True)
            response.raise_for_status()
            with open(img_path, 'wb') as img_file:
                for chunk in response.iter_content(1024):
                    img_file.write(chunk)
            print(f"Saved image: {img_name}")
        except requests.exceptions.RequestException as e:
            print(f"Failed to download {img_url}: {e}")
    return img_name

# Function to transform callouts
def transform_callouts(content):
    transformed_lines = []
    callout_buffer = []
    callout_type = None  # To track the type of callout (note, danger, warning, or info)

    for line in content.splitlines():
        if line.startswith('> 📘'):
            if callout_buffer:
                # Save previous callout buffer as Docusaurus callout
                transformed_lines.append(f":::{callout_type}\n" + "\n".join(callout_buffer) + "\n:::")
                callout_buffer = []
            callout_type = 'note'
            callout_buffer.append(line[4:].strip())  # Remove '> 📘' and trim
        elif line.startswith('> ❗️'):
            if callout_buffer:
                # Save previous callout buffer as Docusaurus callout
                transformed_lines.append(f":::{callout_type}\n" + "\n".join(callout_buffer) + "\n:::")
                callout_buffer = []
            callout_type = 'danger'
            callout_buffer.append(line[4:].strip())  # Remove '> ❗️' and trim
        elif line.startswith('> 🚧'):
            if callout_buffer:
                # Save previous callout buffer as Docusaurus callout
                transformed_lines.append(f":::{callout_type}\n" + "\n".join(callout_buffer) + "\n:::")
                callout_buffer = []
            callout_type = 'warning'
            callout_buffer.append(line[4:].strip())  # Remove '> 🚧' and trim
        elif line.startswith('> 👍'):
            if callout_buffer:
                # Save previous callout buffer as Docusaurus callout
                transformed_lines.append(f":::{callout_type}\n" + "\n".join(callout_buffer) + "\n:::")
                callout_buffer = []
            callout_type = 'info'
            callout_buffer.append(line[4:].strip())  # Remove '> 👍' and trim
        elif line.startswith('>') and callout_buffer:
            callout_buffer.append(line[2:].strip())  # Remove '> ' and trim
        else:
            if callout_buffer:
                # Save the last callout buffer as Docusaurus callout
                transformed_lines.append(f":::{callout_type}\n" + "\n".join(callout_buffer) + "\n:::")
                callout_buffer = []
                callout_type = None
            transformed_lines.append(line)
    
    if callout_buffer:
        # Handle remaining callout buffer
        transformed_lines.append(f":::{callout_type}\n" + "\n".join(callout_buffer) + "\n:::")

    return "\n".join(transformed_lines)

# Function to transform tables
def transform_tables(content):
    table_pattern = re.compile(r'\[block:parameters\]\n?({.*?})\n?\[/block\]', re.DOTALL)
    
    def convert_markdown_table(table_data):
        num_cols = len([key for key in table_data['data'].keys() if key.startswith('h-')])
        
        headers = [table_data['data'][f"h-{i}"] for i in range(num_cols)]
        rows = [
            [table_data['data'].get(f"{r}-{c}", '') for c in range(num_cols)]
            for r in range(table_data['rows'])
        ]

        # Convert paragraphs and lists in cells
        def convert_cell(cell):
            cell = cell.strip()

            # Convert paragraphs
            paragraphs = cell.split('  \n')
            if len(paragraphs) > 1:
                cell = "".join(f"<p>{p.strip()}</p>" for p in paragraphs)

            # Convert ordered lists
            cell = re.sub(r'\n\s*(\d+)\.\s', r'<ol><li>\1. ', cell)
            cell = cell.replace('</li>\n', '</li>')
            cell = cell.replace('</li><ol><li>', '<li>')
            cell = cell.replace(' <ol><li>', '<ol><li>').replace('</li><ol>', '</li><ol>')

            # Wrap the entire list in <ol> if not already wrapped
            if '<li>' in cell and not cell.startswith('<ol>'):
                cell = f'<ol>{cell}</ol>'

            return cell

        # Build markdown table
        markdown_table = []
        markdown_table.append("| " + " | ".join(headers) + " |")
        markdown_table.append("|" + "|".join(["-" * len(header) for header in headers]) + "|")
        for row in rows:
            markdown_table.append("| " + " | ".join(convert_cell(cell) for cell in row) + " |")

        return "\n".join(markdown_table)

    def table_replacer(match):
        table_data = json.loads(match.group(1))
        return convert_markdown_table(table_data)

    return table_pattern.sub(table_replacer, content)

# Function to transform links
def transform_links(content):
    # Internal links to sections
    section_link_pattern = re.compile(r'\[(.*?)\]\(doc:(.*?)\)')
    content = section_link_pattern.sub(r'[\1](\2)', content)

    # Internal links to subsections
    subsection_link_pattern = re.compile(r'\[(.*?)\]\(doc:(.*?)#(.*?)\)')
    content = subsection_link_pattern.sub(r'[\1](\2#\3)', content)

    return content

# Function to transform images
def transform_images(content):
    image_pattern = re.compile(r'\[block:image\]\s*({.*?})\s*\[/block\]', re.DOTALL)

    def image_replacer(match):
        try:
            image_data = json.loads(match.group(1))
        except json.JSONDecodeError:
            return match.group(0)  # Skip this block if JSON is malformed

        images = image_data.get('images', [])
        transformed_images = []
        for img in images:
            src = img['image'][0]
            img_name = save_image_locally(src, img_folder_path)
            relative_path = f"./img/{img_name}"
            alt_text = img.get('caption', 'Example banner').strip()

            # Create the HTML image block with the new format
            transformed_images.append(
                f"""
<img
  src={{require('{relative_path}').default}}
/>
"""
            )
        return "\n".join(transformed_images) + "\n\n"  # Ensure it's on separate lines
    
    return image_pattern.sub(image_replacer, content)

# Function to transform front matter
def transform_front_matter(content):
    front_matter_pattern = re.compile(r'^---\n(.*?)\n---', re.DOTALL)
    match = front_matter_pattern.search(content)
    if match:
        front_matter_yaml = match.group(1)
        front_matter = yaml.safe_load(front_matter_yaml)

        title = front_matter.get('title') or front_matter.get('slug', '')
        description = front_matter.get('metadata', {}).get('description', '')
        metadata_title = front_matter.get('metadata', {}).get('title', '')

        new_front_matter = f'''---
title: "{title}"
description: "{description}"
metadataTitle: "{metadata_title}"
---'''
        # Remove the old front matter and replace with the new one
        content = content[match.end():].strip()
        content = new_front_matter + "\n\n" + content

    return content

# Function to remove <br> tags
def remove_br_tags(content):
    return re.sub(r'<br\s*/?>', '', content)

# Function to transform headings
def transform_headings(content):
    def heading_replacer(match):
        hashes = match.group(1)
        title = match.group(2)
        new_hashes = '#' * (len(hashes) + 1) if len(hashes) < 6 else hashes  # Prevents overflow of heading level
        return f"{new_hashes} {title}"

    # Determine the minimum heading level
    headings = re.findall(r'^(#{1,6}) ', content, re.MULTILINE)
    if not headings:
        return content
    
    min_level = min(len(h) for h in headings)
    if min_level > 2:
        return content  # No adjustment needed if all headings are already level 2 or greater

    # Increase all heading levels by 2 - min_level
    new_content = re.sub(r'^(#{1,6}) (.+)$', heading_replacer, content, flags=re.MULTILINE)
    return new_content

# Function to transform <details> tags
def transform_details_tags(content):
    details_pattern = re.compile(r'<details>\s*<summary>(.*?)<\/summary>(.*?)<\/details>', re.DOTALL)
    
    def format_details(match):
        summary = match.group(1).strip()
        details_content = match.group(2).strip()
        formatted_details = (
            "<details>\n"
            f"   <summary>{summary}</summary>\n\n"
            f"   {details_content.strip()}\n"
            "</details>"
        )
        return formatted_details

    return details_pattern.sub(format_details, content)

# Function to remove comments
def remove_comments(content):
    return re.sub(r'<!---->', '', content)

# Function to remove glossary item links
def remove_glossary_links(content):
    glossary_pattern = re.compile(r'<<glossary:(.*?)>>')
    return glossary_pattern.sub(r'\1', content)

# Function to add titles to code blocks
def add_code_block_titles(content):
    code_block_pattern = re.compile(r'```(\w+)(.*?)\n(.*?)```', re.DOTALL)

    def code_block_replacer(match):
        language = match.group(1)
        title = match.group(2).strip() or language.capitalize()  # Capitalize the title if it starts with a letter
        if title.lower() == "sh":
            title = "Shell"
        elif title.lower() == "csharp":
            title = "C#"
        code = match.group(3)
        return f'```{language} title="{title}"\n{code}```'

    # Avoid double "title=" in the result
    content = code_block_pattern.sub(lambda m: code_block_replacer(m).replace('title="title="', 'title="'), content)
    return content

# Function to transform the entire content
def transform_content(content):
    content = transform_front_matter(content)
    content = transform_callouts(content)
    content = transform_tables(content)
    content = transform_links(content)
    content = transform_images(content)
    content = remove_br_tags(content)
    content = transform_details_tags(content)
    content = transform_headings(content)
    content = remove_comments(content)
    content = remove_glossary_links(content)
    content = add_code_block_titles(content)
    return content

# Walk through all files in the source folder and subfolders
for root, dirs, files in os.walk(source_folder_path):
    for file in files:
        if file.endswith('.md'):
            # Construct full file paths
            source_file_path = os.path.join(root, file)
            # Determine the target file path based on whether it is an issue file or not
            if file in issues_files:
                target_file_path = os.path.join(issues_folder_path, file)
            else:
                target_file_path = os.path.join(target_folder_path, file)
            
            # Read the source file
            with open(source_file_path, 'r') as source_file:
                content = source_file.read()
            
            # Transform content
            transformed_content = transform_content(content)
            
            # Write the transformed content to the target file
            with open(target_file_path, 'w') as target_file:
                target_file.write(transformed_content)

print(f"Transformed markdown files have been saved to {target_folder_path} and {issues_folder_path}")
