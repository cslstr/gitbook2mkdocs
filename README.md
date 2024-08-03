# gitbook2mkdocs

Mkdocs plugin that converts gitbook markdown syntax to mkdocs support markdown



## Setup

1. ```
   pip3 install git+https://github.com/cslstr/gitbook2mkdocs
   ```

2. Setup gitbook's `Synchronize with Git` option to store the markdown files in your git repository 

3. Make sure you set the `Project directory` under `Monorepo` to "docs"

4. Create a mkdocs.yml file next to the docs directory in the repo where gitbook saves the source files

5. Add the gitbook2mkdocs to your plugins list (more info on plugins 

   [Mkdocs Plugins]: https://www.mkdocs.org/dev-guide/plugins/

   )

```
plugins:
  - gitbook2mkdocs
```

You'll also probably want to load admonitions:

```
markdown_extensions:
  - admonition
  - pymdownx.details
  - pymdownx.superfences
```
