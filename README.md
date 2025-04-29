# URL Expander

A fast Python CLI tool to expand shortened URLs (bit.ly, t.co, etc.) with support for multithreading, proxies, and progress display.

---

## 🚀 Features

- Expand one or many short URLs
- Multithreaded execution for speed
- Proxy support (HTTP & SOCKS5)
- Optional colorized output
- Optional progress bar for multiple URLs
- File input and/or output support

---

## 📦 Installation

Requires **Python 3.7+**

```bash
pip install -r requirements.txt
```

---

## 🛠 Usage

### Expand a single URL:
```bash
python url_expander.py --url https://bit.ly/abc123
```

### Expand multiple URLs:
```bash
python url_expander.py --url https://bit.ly/a https://t.co/b https://cutt.ly/c
```

### Expand URLs from file:
```bash
python url_expander.py --file input.txt
```

### Save output to file:
```bash
python url_expander.py --file input.txt --output result.txt
```

### Use a proxy:
```bash
python url_expander.py --url https://bit.ly/a --proxy http://127.0.0.1:8080
```

---

## ⚙️ Command-Line Options

| Option            | Description                                         |
|-------------------|-----------------------------------------------------|
| `--url`           | One or more short URLs to expand                    |
| `--file`          | Read URLs from file (one per line)                  |
| `--output`        | Write results to file instead of console            |
| `--proxy`         | Optional proxy (HTTP/SOCKS5)                        |
| `--workers`       | Number of threads (default: CPU cores + 4)          |
| `--no-color`      | Disable colorized output                            |
| `--no-progress`   | Disable progress bar (useful for single URL/script) |

---

## 📄 Output Format

Each expanded URL is printed like this:

```
original_url -> final_destination_url
```

Example:

```
https://bit.ly/test -> https://example.com/page
```

---

## 🔐 Proxy Notes

SOCKS proxies require:

```bash
pip install requests[socks]
```
