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

## Structured outputs

We can use `web-llm`'s in-bult XGrammar support to generated structured outputs by passing a json-schema template via the `output_template=` parameter  (though this seems a bit unreliable to me, and seems to be prompt sensitive?)

```json
output_template="""{
    "title": "A story",
    "type": "object",
    "properties": {
      "tale": {
        "type": "string",
        "description": "The story"
      }}}"""
```

```python
import json
prompt=""""
Using the provided template output format,
write me a story in 50 words that starts:
It was night
""""

raw_response = w.convert(prompt, output_template=output_template, force=True)

json.loads(raw_response)
```

## Setting Model Parameters

We can set model paramters by passing in a parameters dictionary via the `parameters=` parameter:

```python
params={"max_tokens":4096,
        "temperature":0,
        "top_p": 0.1, 
        "frequency_penalty": 0.0,
        "presence_penalty": 0.0}

w.convert("write a poem in 8 lines", params=params)
```

## Installation

```sh
pip install jupyter_anywidget_webllm
```

or with [uv](https://github.com/astral-sh/uv):

```sh
uv add jupyter_anywidget_webllm
```

Open `example.ipynb` in JupyterLab, VS Code, for a demo...
