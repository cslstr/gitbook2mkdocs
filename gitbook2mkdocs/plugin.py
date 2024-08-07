import os
import re
import shutil

from mkdocs.plugins import BasePlugin


class Gitbook2Mkdocs(BasePlugin):
    def on_page_markdown(self, markdown, page, config, files, **kwargs):
        # Replace GitBook syntax with MkDocs syntax
        markdown = self.replace_gitbook_syntax(markdown)

        # Replace HTML figures with Markdown images
        markdown = self.replace_figures_with_images(markdown)

        # Replace all references to .gitbook directory with assets
        markdown = markdown.replace(".gitbook/assets/", "gbassets/")

        return markdown

    def on_pre_build(self, config, **kwargs):
        # Define the source directory (.gitbook/assets)
        source_dir = os.path.join(config["docs_dir"], ".gitbook", "assets")

        # Define the destination directory (assets/images)
        dest_dir = os.path.join(config["docs_dir"], "gbassets")

        # Create a symbolic link to avoid warnings in the build process
        if os.path.exists(source_dir) and not os.path.exists(dest_dir):
            os.symlink(source_dir, dest_dir)

    def on_post_build(self, config, **kwargs):
        # Define the source directory (.gitbook/assets)
        source_dir = os.path.join(config["docs_dir"], ".gitbook", "assets")

        # Define the destination directory (site/assets/images)
        dest_dir = os.path.join(config["site_dir"], "gbassets")

        # Define the destination directory (assets/gbtomk)
        symlink = os.path.join(config["docs_dir"], "gbassets")

        # If the source directory exists, copy it to the destination
        if os.path.exists(source_dir):
            shutil.copytree(source_dir, dest_dir, dirs_exist_ok=True)

        # If the destination directory exists, remove it
        if os.path.exists(symlink):
            os.remove(symlink)

        # No need to replace .gitbook/assets/ with assets/ in HTML files
        # because that's handled in on_page_markdown

    # Function to replace GitBook syntax with MkDocs Admonition syntax
    def replace_gitbook_syntax(self, content):
        # Remove all gitbook specific [^1] values
        content = re.sub(r"\[\^1\]:?", "", content)

        # Remove content-ref tags and keep only the text between the tags
        content = re.sub(r"{% content-ref %}(.*?){% endcontent-ref %}", r"\1", content)

        # Remove content-ref tags
        content = re.sub(
            r"{%[\w\s]+?content-ref\s*.*?%}(.*?)\{%[\w\s]+?endcontent-ref\s*.*?%}",
            r"\1",
            content,
            flags=re.DOTALL,
        )

        content = self.convert_code(content)
        content = self.convert_hints(content)
        content = self.convert_tabs(content)
        return content

    
    # Replace gitbook code blocks with titles
    # {% code title="attacker@local" %}
    # ```py
    # ...
    # ```
    # {% endcode %}
    def convert_code(self, content):
        def indent_text(match):
            titletext = match.group(1)
            blockstartlang = match.group(2).strip()
            inner_text = match.group(3).rstrip()
            return f'{blockstartlang} {titletext}\n{inner_text}\n'

        pattern = r'{% code (title="[^"]+") %}\n(```.*?)\n(.*?)\s*{% endcode %}'
        return re.sub(pattern, indent_text, content, flags=re.DOTALL)

        
    # Replace gitbook hint blocks with admonition
    def convert_hints(self, content):
        def indent_text(match):
            hint_style = match.group(1)
            title = match.group(2).strip()
            inner_text = match.group(3).rstrip()
            indented_text = inner_text.replace("\n", "\n    ")
            return f'!!! {hint_style} "{title}"\n    {indented_text}\n'

        pattern = r'{% hint style="([a-zA-Z]+)" %}\s*(.*?)\s*\n(.*?)\s*{% endhint %}'
        return re.sub(pattern, indent_text, content, flags=re.DOTALL)

    
    # Function to change gitbooks tab format into mkdocs tab format
    def convert_tabs(self, content):
        # Replace {% tabs %} with an empty string (not needed in the target format)
        content = re.sub(r"{% tabs %}", "", content)

        # Replace {% endtabs %} with an empty string (not needed in the target format)
        content = re.sub(r"{% endtabs %}", "", content)

        # Replace {% tab title="Title" %} with the respective tab title
        content = re.sub(r'{% tab title="([^"]+)" %}', r'=== "\1"', content)

        # Replace {% endtab %} with an empty string (not needed in the target format)
        content = re.sub(r"{% endtab %}", "", content)

        # Indent content within tabs
        tab_content_pattern = r'(=== ".*?")((?:\r?\n)(?:(?!\r?\n===).)*)(\r?\n)'

        def indent_content(match):
            title = match.group(1)
            content = "    " + match.group(2).strip().replace("\n", "\n    ")
            return "{}\n{}\n".format(title, content)

        content = re.sub(tab_content_pattern, indent_content, content)

        return content

    def replace_figures_with_images(self, markdown):
        # Find all occurrences of <figure><img src="..."><figcaption>...</figcaption></figure>
        # and replace them with ![...](...)
        markdown = re.sub(
            r'<figure><img src="(.*?)" alt="(.*?)"><figcaption>.*?</figcaption></figure>',
            r"![\2](\1)",
            markdown,
        )

        return markdown

    # Function to remove escaping characters between colons
    def remove_escaping_chars(self, content):
        def process_match(match):
            return match.group(1) + match.group(2).replace("\\", "") + match.group(3)

        content = re.sub(r"(:)(.*?)(:)", process_match, content)
        return content
