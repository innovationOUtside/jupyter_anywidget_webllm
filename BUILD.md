# BUILD

Minimal instructions...

## Setup

`npm create anywidget@latest` (e.g. use js + esbuild tools)

`npm install`

Uses: [`@mlc-ai/web-llm`](https://github.com/mlc-ai/web-llm): `npm install --save @mlc-ai/web-llm`

## Build

Install node packages: `npm install`

Build / package Typescript/JS: `npm run build`

Build Python package (into `dist/`): `hatch build`

Install package: `pip install --upgrade --force-reinstall --no-deps dist/jupyter_anywidget_webllm-0.0.0-py2.py3-none-any.whl`

Push to PyPi: `twine upload  dist/*0.0.0*` etc.