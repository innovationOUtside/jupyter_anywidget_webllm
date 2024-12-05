# jupyter_anywidget_webllm

Example Jupyter/VS Code [`anywidget`](https://anywidget.dev/) that will sideload a `web-llm` model into the browser and run prompts against it.

Install as: `pip install jupyter_anywidget_webllm`

For example:

```python
from jupyter_anywidget_webllm import webllm_headless

# Load the headless widget
w = webllm_headless()

# Wait for webllm wasm to load (blocking;; does not work in JupyterLite)
w.ready()

# Try a conversion
# This is blocking - does not work in JupyterLite
output = w.convert("Write me a poem")
output


#Non-blocking
w.base_convert("Write me a story")
# When it's ready, collect from:
w.response
> {'status': 'processing'}
> {'status': 'completed', 'output_raw': 'OUTPUT'}
```

TO DO: ALLOW a json outpur template from a string or file: Use `w.convert_from_file(path, output_template="", timeout=3)` etc. to load from a local file path or a URL.

## Installation

```sh
pip install jupyter_anywidget_webllm
```

or with [uv](https://github.com/astral-sh/uv):

```sh
uv add jupyter_anywidget_webllm
```

Open `example.ipynb` in JupyterLab, VS Code, for a demo...
