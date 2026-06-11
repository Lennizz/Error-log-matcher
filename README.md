# My Web App

A minimal full-stack starter: **HTML/CSS/JS** front-end served by a **Flask** (Python) back-end.

## Project Structure

```
webapp/
├── app.py                  # Flask application & API routes
├── requirements.txt        # Python dependencies
├── templates/
│   └── index.html          # Main HTML page (Jinja2 template)
└── static/
    ├── css/
    │   └── style.css       # Styles
    └── js/
        └── main.js         # Front-end JavaScript
```

## Quick Start

### 1 — Install dependencies
```bash
pip install -r requirements.txt
```

### 2 — Run the development server
```bash
python app.py
```

Open **http://localhost:5000** in your browser.

## API Endpoints

| Method | Path         | Description                        |
|--------|--------------|------------------------------------|
| GET    | `/`          | Serves `index.html`                |
| GET    | `/api/hello` | Returns a simple JSON greeting     |
| POST   | `/api/greet` | Accepts `{"name": "…"}`, returns personalised greeting |

## Adding a New Route

1. Add a function in `app.py`:
   ```python
   @app.route("/api/my-endpoint", methods=["GET"])
   def my_endpoint():
       return jsonify({"data": "your data here"})
   ```
2. Call it from `static/js/main.js` with `fetch("/api/my-endpoint")`.
