import os
import re
import json
import yaml

# Define paths
source_folder_path = "/Users/liudmilanemkova/Desktop/Migration from readme to docusaurus"
target_folder_path = "/Users/liudmilanemkova/Desktop/Migration result"

# Function to transform callouts
def transform_callouts(content):
    transformed_lines = []
    callout_buffer = []
    callout_type = None  # To track the type of callout (info or warning)

    for line in content.splitlines():
        if line.startswith('> 📘'):
            if callout_buffer:
                # Save previous callout buffer as Docusaurus callout
                transformed_lines.append(f":::{callout_type}\n" + "\n".join(callout_buffer) + "\n:::")
                callout_buffer = []
            callout_type = 'info'
            callout_buffer.append(line[4:].strip())  # Remove '> 📘' and trim
        elif line.startswith('> ❗️') or line.startswith('> 🚧'):
            if callout_buffer:
                # Save previous callout buffer as Docusaurus callout
                transformed_lines.append(f":::{callout_type}\n" + "\n".join(callout_buffer) + "\n:::")
                callout_buffer = []
            callout_type = 'warning'
            callout_buffer.append(line[4:].strip())  # Remove '> ❗️' or '> 🚧' and trim
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
    table_pattern = re.compile(r'\[block:parameters\]\n({.*?})\n\[/block\]', re.DOTALL)

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
        image_data = json.loads(match.group(1))
        images = image_data['images']
        transformed_images = []
        for img in images:
            src = img['image'][0]
            alt = img['image'][2] or 'Image'
            width = img.get('sizing', 'auto').strip()
            if width[-1].isdigit():  # Append 'px' if the width value is a plain number
                width += 'px'
            border = '1px solid grey' if img.get('border') else 'none'
            align = img.get('align', 'left')
            textAlign = 'center' if align == 'center' else 'left'

            # Create the HTML image block with double curly braces for style
            transformed_images.append(
                f"""
<div style={{{{ textAlign: '{textAlign}' }}}}>
  <img 
    src="{src}" 
    alt="{alt}" 
    style={{{{ width: '{width}', border: '{border}' }}}}
  />
</div>
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
        heading = f"# {title}"
        # Remove the old front matter and replace with the new one plus heading
        content = content[match.end():].strip()
        content = new_front_matter + "\n\n" + heading + "\n\n" + content

    return content

# Function to remove <br> tags
def remove_br_tags(content):
    return re.sub(r'<br\s*/?>', '', content)

# Function to transform the entire content
def transform_content(content):
    content = transform_front_matter(content)
    content = transform_callouts(content)
    content = transform_tables(content)
    content = transform_links(content)
    content = transform_images(content)
    content = remove_br_tags(content)
    return content

# Create target folder if it does not exist
if not os.path.exists(target_folder_path):
    os.makedirs(target_folder_path)

# Walk through all files in the source folder and subfolders
for root, dirs, files in os.walk(source_folder_path):
    for file in files:
        if file.endswith('.md'):
            # Construct full file paths
            source_file_path = os.path.join(root, file)
            # Create a relative path to reproduce the folder structure in the target folder
            relative_path = os.path.relpath(source_file_path, source_folder_path)
            target_file_path = os.path.join(target_folder_path, relative_path)
            
            # Ensure target directory exists
            target_file_dir = os.path.dirname(target_file_path)
            if not os.path.exists(target_file_dir):
                os.makedirs(target_file_dir)
            
            # Read the source file
            with open(source_file_path, 'r') as source_file:
                content = source_file.read()
            
            # Transform content
            transformed_content = transform_content(content)
            
            # Write the transformed content to the target file
            with open(target_file_path, 'w') as target_file:
                target_file.write(transformed_content)

print(f"Transformed markdown files have been saved to {target_folder_path}")
