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

The `.convert()` and `.base_convert()` calls also accept a `timeout=SECONDS` parameter (seconds); to disable the timeout, use `timeout=None`.

The `force=True` parameter can be used to force the model to rerun if the prompt has not been changed (otherwise the model only runs if the prompt has changed).

## Why is this interesting?

More and more tools are being published as wasm wrappers, and the anywidget model provides a simple way of bundling those in a python api wrapper we can call from notebooks. The main advantages are:

1) runs in browser, so no installation required;

2) runs in browser, so all you need to serve the application is a simple static file serving webserver;

3) also runs (in non-blocking) way in JupyterLite, which can be saved as a progressive web app and then used offline, and provides a way of publishing a Jupyter environment without the need for anything other than a simple static file serving webserver.

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
    }
  }
}
"""
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

We can set model parameters by passing in a parameters dictionary via the `parameters=` parameter:

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
