from functools import wraps
from IPython.display import display
import warnings

# Create a decorator to simplify panel autolaunch
# First parameter on decorated function is optional title
# Second parameter on decorated function is optional anchor location
# Via Claude.ai
def create_panel(func):
    try:
        from sidecar import Sidecar
    except:
        warnings.warn(
            "Missing package (sidecar): run `pip install sidecar` before trying to access the panel.",
            UserWarning,
        )

    @wraps(func)
    def wrapper(title=None, anchor="split-right", *args, **kwargs):
        if title is None:
            title = f"{func.__name__[:-6]} Output"  # Assuming function names end with '_panel'

        widget_ = func(*args, **kwargs)
        widget_.sc = Sidecar(title=title, anchor=anchor)

        with widget_.sc:
            display(widget_)

        # Add a close method to the widget
        def close():
            widget_.sc.close()

        widget_.close = close

        return widget_

    return wrapper
