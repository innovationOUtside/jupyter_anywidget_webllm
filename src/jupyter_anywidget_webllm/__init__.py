import importlib.metadata
from pathlib import Path
try:
    import requests
except:
    pass
import anywidget
import traitlets
import time
import warnings

from IPython.display import display

try:
    __version__ = importlib.metadata.version("jupyter_anywidget_webllm")
except importlib.metadata.PackageNotFoundError:
    __version__ = "unknown"

try:
    from jupyter_ui_poll import ui_events
except:
    warnings.warn(
        "You must install jupyter_ui_poll if you want to return cell responses / blocking waits (not JupyterLite); install necessary packages then restart the notebook kernel:%pip install jupyter_ui_poll",
        UserWarning,
    )


class Widget(anywidget.AnyWidget):
    _esm = Path(__file__).parent / "static" / "widget.js"
    _css = Path(__file__).parent / "static" / "widget.css"
    value = traitlets.Int(0).tag(sync=True)


class webllmWidget(anywidget.AnyWidget):
    _esm = Path(__file__).parent / "static" / "webllm.js"
    _css = Path(__file__).parent / "static" / "webllm.css"

    headless = traitlets.Bool(False).tag(sync=True)
    doc_content = traitlets.Unicode("").tag(sync=True)
    output_raw = traitlets.Unicode("").tag(sync=True)
    input_format = traitlets.Unicode("").tag(sync=True)
    output_template= traitlets.Unicode("").tag(sync=True)
    about = traitlets.Dict().tag(sync=True)
    response = traitlets.Dict().tag(sync=True)

    def __init__(self, headless=False, **kwargs):
        super().__init__(**kwargs)
        self.headless = headless
        self.response = {"status": "initialising"}

    def _wait(self, timeout, conditions=("status", "completed")):
        start_time = time.time()
        try:
            with ui_events() as ui_poll:
                while self.response[conditions[0]] != conditions[1]:
                    ui_poll(10)
                    if timeout and ((time.time() - start_time) > timeout):
                        raise TimeoutError(
                            "Action not completed within the specified timeout."
                        )
                    time.sleep(0.1)
        except:
            warnings.warn(
                "jupyter_ui_poll not available (if you are in JupyterLite, this is to be expected...)",
                UserWarning,
            )
        self.response["time"] = time.time() - start_time
        return

    def ready(self, timeout=5):
        self._wait(timeout, ("status", "ready"))

    # Need to guard this out in JupyterLite (definitely in pyodide)
    def blocking_reply(self, timeout=None):
        self._wait(timeout)
        return self.response

    def set_doc_content(self, value, force=False):
        # We really need to handle the case where the input hasn't changed
        if not value:
            print("You must provide a prompt.")
            return
        elif self.doc_content != value or force:
            if force:
                self.doc_content = ""
            self.response = {"status": "processing"}
            self.doc_content = value

    def set_input_format(self, value):
        self.input_format = value

    def set_output_template(self, value):
        self.output_template = value

    def base_convert(self, input_text, input_format="markdown", output_template="", force=False):
        self.set_input_format(input_format)
        self.set_output_template(output_template)
        self.set_doc_content(input_text, force=force)

    def convert(
        self, input_text, input_format="markdown", output_template="", timeout=None, force=False
    ):
        self.base_convert(input_text, input_format, output_template, force=force)
        self.blocking_reply(timeout)
        return self.output_raw

    def convert_from_file(
        self, path, input_format=None, output_template="", timeout=None
    ):
        if path.startswith("http"):
            # Download the content from the URL
            response = requests.get(path)
            if response.status_code == 200:
                input_text = response.text
                # Attempt to extract file type from URL, if possible
                filetype = path.split(".")[-1] if "." in path else "unknown"
            else:
                raise Exception(
                    f"Failed to fetch the URL. Status code: {response.status_code}"
                )
        else:
            # Check if the file exists
            file_path = Path(path)
            if file_path.exists() and file_path.is_file():
                # Read the content of the file
                input_text = file_path.read_text()
                # Get the file type (suffix)
                filetype = file_path.suffix
            else:
                raise FileNotFoundError(f"The file '{path}' does not exist.")

        if not input_format:
            # Clean the filetype
            filetype = filetype.lstrip(".")
            # Repair
            repair_map = {"html=": "html", "md": "markdown"}
            input_format = repair_map.get(filetype, filetype)

        return self.convert(input_text, input_format, output_template, timeout)


def webllm_headless():
    widget_ = webllmWidget(headless=True)
    display(widget_)
    return widget_


def webllm_inline():
    widget_ = webllmWidget()
    display(widget_)
    return widget_


from .magics import WebllmAnywidgetMagic


def load_ipython_extension(ipython):
    ipython.register_magics(WebllmAnywidgetMagic)


from .panel import create_panel


# Launch with custom title as: webllm_panel("WebLLM")
# Use second parameter for anchor
@create_panel
def webllm_panel(title=None, anchor=None):
    return webllmWidget()
