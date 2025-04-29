#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests, argparse, sys, os, concurrent.futures
from functools import partial

try:
    from tqdm import tqdm;

    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False
try:
    import colorama
    from colorama import Fore, Style

    colorama.init(autoreset=True);
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False


    class Dummy:
        def __getattr__(self, name): return ""


    Fore = Style = Dummy()

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124 Safari/537.36'}
REQUEST_TIMEOUT = 10
DEFAULT_WORKERS = min(32, os.cpu_count() + 4)


def expand_url(url, proxy=None):
    try:
        r = requests.head(url, allow_redirects=True, timeout=REQUEST_TIMEOUT, headers=HEADERS, proxies=proxy)
        return r.url, r.status_code, None
    except requests.exceptions.Timeout:
        return None, None, "Timeout"
    except requests.exceptions.TooManyRedirects:
        return None, None, "Too many redirects"
    except requests.exceptions.RequestException as e:
        return None, None, f"Request error: {e}"
    except Exception as e:
        return None, None, f"Unexpected error: {e}"


def process_urls(urls, output=None, workers=DEFAULT_WORKERS, proxy_url=None):
    proxies = {'http': proxy_url, 'https': proxy_url} if proxy_url else None
    writer = (open(output, 'w', encoding='utf-8').write if output else lambda l: print(l, flush=True))
    expand_func = partial(expand_url, proxy=proxies)
    results, ok = {}, True

    show_progress = TQDM_AVAILABLE and not output and len(urls) > 1

    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex:
        futures = {ex.submit(expand_func, url): url for url in urls if url.strip()}
        iterable = tqdm(concurrent.futures.as_completed(futures), total=len(futures), desc="Expanding",
                        unit="url") if show_progress else concurrent.futures.as_completed(futures)

        for f in iterable:
            url = futures[f]
            try:
                final, _, err = f.result()
                results[url] = (final, err)
                if err: ok = False
            except Exception as e:
                results[url] = (None, f"Exec error: {e}")
                ok = False

    for url in urls:
        if not url.strip(): continue
        final, err = results.get(url, (None, "Unknown"))
        if err:
            writer(f"{url} -> {Fore.RED}ERROR ({err}){Style.RESET_ALL}")
        else:
            writer(f"{url} -> {final}")

    if output: writer('\n'); writer.close()
    return ok


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Expand short URLs concurrently.")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--url", metavar="URL", nargs='+', help="Short URL(s)")
    g.add_argument("--file", metavar="INPUT_FILE", dest="input_file", help="File with short URLs")
    p.add_argument("--output", metavar="OUTPUT_FILE", help="Save output to file")
    p.add_argument("-w", "--workers", type=int, default=DEFAULT_WORKERS, help="Parallel workers")
    p.add_argument("-p", "--proxy", metavar="PROXY_URL", help="Proxy (http/socks5)")
    p.add_argument("--no-color", action="store_true", help="Disable colors")
    p.add_argument("--no-progress", action="store_true", help="Disable progress bar")
    args = p.parse_args()

    if args.no_color: COLORAMA_AVAILABLE = False
    if args.no_progress: TQDM_AVAILABLE = False

    urls, ok = [], True
    if args.url:
        urls = [u.strip() for u in args.url if u.strip()]
    elif args.input_file:
        if not os.path.exists(args.input_file):
            print(f"{Fore.RED}Error: File not found: {args.input_file}{Style.RESET_ALL}", file=sys.stderr)
            ok = False
        else:
            try:
                with open(args.input_file, 'r', encoding='utf-8') as f:
                    urls = [line.strip() for line in f if line.strip()]
                if not urls:
                    print(f"{Fore.YELLOW}Warning: File is empty.{Style.RESET_ALL}", file=sys.stderr)
            except Exception as e:
                print(f"{Fore.RED}Error reading file: {e}{Style.RESET_ALL}", file=sys.stderr)
                ok = False

    if args.proxy and args.proxy.startswith('socks'):
        try:
            import requests_socks
        except ImportError:
            print(f"{Fore.RED}Error: SOCKS proxy requires 'requests[socks]'.{Style.RESET_ALL}", file=sys.stderr)
            ok = False

    if ok and urls:
        sys.exit(0 if process_urls(urls, args.output, args.workers, args.proxy) else 1)
    sys.exit(1 if not ok else 0)