# SQLi Lab

A small Flask application built to **demonstrate and teach SQL Injection** vulnerabilities in a hands-on way. It contains deliberately vulnerable routes, an automated test script that exploits them, and a set of pages that walk through each attack live in the browser.

> **For educational use only.** The app is intentionally insecure. Do not deploy it on a public server or reuse its database code in a real project.

## What this project does

The app ships with three classic SQL Injection patterns, each with its own vulnerable route and its own front-end walkthrough:

| Type | Route |
|---|---|
| **Authentication-based** | `/login` 
| **UNION-based** | `/search` 
| **Boolean-based (blind)** | `/check` 

Alongside manual testing (typing input directly into the forms), each page has a **"Run test" button** that triggers `test_sqli.py` on the server and narrates, step by step, what the script actually sent and what came back — including the exact payload, the raw server response, and a plain-language explanation of why it worked (or didn't).

## Project structure

```
├── Code/
│   ├── app.py              # Flask app: vulnerable routes + test runner endpoint
│   ├── test_sqli.py        # Standalone script with one function per SQLi type
│   ├── database.db         # SQLite database (created automatically on first run)
│   └── templates/
│       ├── index.html
│       ├── login.html       # also serves /register
│       ├── search.html      # UNION-based walkthrough
│       ├── check.html       # Boolean-based walkthrough
│       └── users.html       # Raw dump of the credentials table, for /data
├── README.md
├── LICENSE
└── .gitignore
```

## How it works

- **`app.py`** contains the vulnerable queries themselves (string-formatted SQL, no parameterization) plus `/run-sqli-test`, which runs `test_sqli.py` as a subprocess and returns its raw `stdout`/`stderr` as JSON.
  
- **`test_sqli.py`** has one function per attack type (`authentication_based`, `union_based`, `boolean_based`). Each one sends a real HTTP request to the app's own routes, checks the response, and returns a JSON-serializable result.

- **Each HTML page** fetches that result and narrates it through an animated, multi-step panel: the payload, the raw database response, and a report such as why it worked or fix it.
## Running it

```bash
cd Code
pip install flask requests
python app.py
```

Then open `http://127.0.0.1:5000/register` to create a test account, and visit `/login`, `/search`, or `/check` to try each vulnerability manually or via the "Run test" button.


## Status

Built as a learning project to understand SQL Injection from the inside: writing the vulnerability, the exploit, and the explanation of both side by side.
