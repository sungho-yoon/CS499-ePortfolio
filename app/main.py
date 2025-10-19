from dotenv import load_dotenv
load_dotenv()
from . import create_app
from .layout import build_layout
from .callbacks import table, exports  # noqa: F401 (import to register callbacks)

app = create_app()
app.layout = build_layout()

server = app.server  # for gunicorn

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050)
