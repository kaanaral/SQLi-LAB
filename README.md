# SQLi Lab

A small Flask application built to **demonstrate and teach SQL Injection** vulnerabilities in a hands-on way. It contains deliberately vulnerable routes, an automated test script that exploits them, and a set of pages that walk through each attack live in the browser.

> ⚠️ **For educational use only.** The app is intentionally insecure. Do not deploy it on a public server or reuse its database code in a real project.

## What this project does

The app ships with three classic SQL Injection patterns, each with its own vulnerable route and its own front-end walkthrough:

| Type | Route | What it shows |
|---|---|---|
| **Authentication-based** | `/login` | Bypassing a login form with `' OR 1=1 --`, no real credentials needed |
| **UNION-based** | `/search` | Using `UNION SELECT` to pull passwords out through a search box |
| **Boolean-based (blind)** | `/check` | Asking the database true/false questions to infer data one bit at a time |

Alongside manual testing (typing input directly into the forms), each page has a **"Run test" button** that triggers `test_sqli.py` on the server and narrates, step by step, what the script actually sent and what came back — including the exact payload, the raw server response, and a plain-language explanation of why it worked (or didn't).

## Project structure

```
.
├── app.py              # Flask app: vulnerable routes + test runner endpoint
├── test_sqli.py        # Standalone script with one function per SQLi type
├── database.db         # SQLite database (created automatically on first run)
├── templates/
│   ├── index.html
│   ├── login.html       # also serves /register
│   ├── search.html      # UNION-based walkthrough
│   ├── check.html        # Boolean-based walkthrough
│   └── users.html        # Raw dump of the credentials table, for /data
```

## How it works

- **`app.py`** contains the vulnerable queries themselves (string-formatted SQL, no parameterization) plus `/run-sqli-test`, which runs `test_sqli.py` as a subprocess and returns its raw `stdout`/`stderr` as JSON.
- **`test_sqli.py`** has one function per attack type (`authentication_based`, `union_based`, `boolean_based`). Each one sends a real HTTP request to the app's own routes, checks the response, and returns a JSON-serializable result — including an `error` field when the request itself fails (bad status code, connection error) so the front-end can tell "the attack didn't work" apart from "something broke."
- **Each HTML page** fetches that result and narrates it through an animated, multi-step panel: the payload, the raw database response, and a report. The "why this happened" and "the fix" sections only appear when the attack actually succeeded — if the payload has been edited and no longer works, the page shows what the original payload was instead.

## Running it

```bash
pip install flask requests
python app.py
```

Then open `http://127.0.0.1:5000/register` to create a test account, and visit `/login`, `/search`, or `/check` to try each vulnerability — manually or via the "Run test" button.

## The core lesson

Every vulnerable query in this project follows the same unsafe pattern:

```python
cur.execute(f"SELECT * FROM credentials WHERE username = '{username}'")
```

User input is pasted directly into the SQL string, so anything that looks like SQL *becomes* SQL. The fix is the same everywhere: use parameterized queries, which send the value separately from the query itself.

```python
cur.execute("SELECT * FROM credentials WHERE username = ?", (username,))
```

## Status

Built as a learning project to understand SQL Injection from the inside: writing the vulnerability, the exploit, and the explanation of both side by side.
