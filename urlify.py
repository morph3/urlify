#! /usr/bin/python3
import sys
import argparse
from aiohttp import http
from colorama import *
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import requests
import threading
import re
import urllib3
from bs4 import BeautifulSoup

urllib3.disable_warnings()



def surpress(f):
    async def wrapper(*args, **kwargs):
        try:
            return await f(*args, **kwargs)
        except:
            pass
    return wrapper


subdomains = []
args = None


xlarge_ports   = [ 80, 443, 81, 300, 591, 593, 832, 981, 1010, 1311, 2082, 2087, 2095, 2096, 2480, 3000, 3128, 3333, 4243, 4567, 4711, 4712, 4993, 5000, 5104, 5108, 5800, 6543, 7000, 7396, 7474, 8000, 8001, 8008, 8014, 8042, 8069, 8080, 8081, 8088, 8090, 8091, 8118, 8123, 8172, 8222, 8243, 8280, 8281, 8333, 8443, 8500, 8834, 8880, 8888, 8983, 9000, 9043, 9060, 9080, 9090, 9091, 9200, 9443, 9800, 9981, 12443, 16080, 18091, 18092, 20720, 28017 ]
large_ports    = [ 80, 443, 81, 591, 2082, 2087, 2095, 2096, 3000, 8000, 8001, 8008, 8080, 8083, 8443, 8834, 8888 ]
default_ports  = [ 80, 443]

init()
GREEN   = Fore.GREEN
RED     = Fore.RED
RESET   = Fore.RESET
BLUE    = Fore.BLUE
YELLOW  = Fore.YELLOW
MAGENTA  = Fore.MAGENTA



def forge_response_text(r):
    headers = ""
    for key,val in r.headers.items():
        headers += f"{key}: {val}\r\n"
    headers += "\r\n"
    return headers + r.text


def do_http_request(sub,port):
    retries = Retry(total=args.retries,
                backoff_factor=0.3,
                )

    s = requests.Session()
    s.mount('http://', HTTPAdapter(max_retries=retries))
    try:
        r = s.get(f"http://{sub}:{port}", timeout=args.timeout, allow_redirects=args.redirects) # get should be fine I guess
        return r
    except:
        pass
    return None

def do_https_request(sub,port):
    retries = Retry(total=args.retries,
                backoff_factor=0.3,
                )

    s = requests.Session()
    s.mount('https://', HTTPAdapter(max_retries=retries))
    try:
        r = s.get(f"https://{sub}:{port}",verify=False, timeout=args.timeout, allow_redirects=args.redirects) # get should be fine I guess
        return r
    except:
        pass
    return None

def display_info(r):
    full_response_text = forge_response_text(r)

    if args.string:
        if (args.string in full_response_text):
            sys.stdout.write(r.url)
        else:
            return
        if args.status_codes:
            sys.stdout.write(f" {YELLOW}{r.status_code}{RESET}")
        if args.title:
            #title = r.text[r.text.lower().find('<title>') + 7 : r.text.lower().find('</title>')]
            soup = BeautifulSoup(r.text, 'html.parser')
            title = soup.find('title')
            if title:
                title = title.text
                #print("Title: " + str(title) + "Type of it: "+ str(type(title)))
                title = title.replace("<title>","")
                title = title.replace("</title>","")
                title = title.replace("\n","")
            if title == "":
                title = "<EMPTY>"
            if title == None:
                title = "<NO_TITLE>"
            sys.stdout.write(f" {GREEN}{title}{RESET}")
            pass
        if args.location:
            try:
                sys.stdout.write(f' {MAGENTA}{r.headers["Location"]}{RESET}')
            except:
                pass
    else:
        sys.stdout.write(r.url)
        if args.status_codes:
            sys.stdout.write(f" {YELLOW}{r.status_code}{RESET}")
        if args.title:
            #title = r.text[r.text.lower().find('<title>') + 7 : r.text.lower().find('</title>')]
            soup = BeautifulSoup(r.text, 'html.parser')
            title = soup.find('title')
            if title:
                title = title.text
                #print("Title: " + str(title) + "Type of it: "+ str(type(title)))
                title = title.replace("<title>","")
                title = title.replace("</title>","")
                title = title.replace("\n","")
            if title == "":
                title = "<EMPTY>"
            if title == None:
                title = "<NO_TITLE>"
            sys.stdout.write(f" {GREEN}{title}{RESET}")
            pass
        if args.location:
            try:
                sys.stdout.write(f' {MAGENTA}{r.headers["Location"]}{RESET}')
            except:
                pass
    sys.stdout.write("\n")
    return

def display_requests(http_response,https_response):
    if https_response and args.https_only:
        display_info(https_response)
        return
    if http_response:
        #print(f"Did http_request for {sub}")
        display_info(http_response)
    if https_response:
        #print(f"Did https_request for {sub}")
        display_info(https_response)


def request_handler():
    running = True
    while running:
        try:
            sub = subdomains.pop()

        except IndexError:
            running = False
            break

        ports = None
        if args.ports == "large":
            ports = large_ports
        elif args.ports == "xlarge":
            ports = xlarge_ports
        elif args.ports:
            ports = args.ports.split(",")
        else:
            pass
        #print(f"Doing http_request for {sub}")
        if ports:
            for port in ports:
                http_response  = do_http_request(sub, port) # is an response object
                https_response = do_https_request(sub, port)
                display_requests(http_response,https_response)

        else:
            http_response  = do_http_request(sub, 80) # is an response object
            https_response = do_https_request(sub, 443)
            display_requests(http_response,https_response)

        #print(f"Doing https_request for {sub}")
        return
    return

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    # Mandatory options
    parser.add_argument("-l", "--list",                     dest="list",          help="List of urls")
    parser.add_argument("-p", "--ports",                    dest="ports",         help="List of ports to check, Ex -p 80,81,82 or you can use -p large, -p xlarge")
    parser.add_argument("-to", "--timeout",                 dest="timeout",       help="Timeout in seconds. Default 4",                                 default=4)
    parser.add_argument("-r", "--retries",                  dest="retries",       help="Number of retries. Default 3",                                  default=3)
    parser.add_argument("-status", "--status-code",         dest="status_codes",  help="Display status_codes",                                          action='store_true')
    parser.add_argument("-t", "--threads",                  dest="n_threads",     help="Number of threads. Default 20",                                 default=20)
    parser.add_argument("-title",                           dest="title",         help="Display the title of the page",                                 action='store_true')
    parser.add_argument("-redir","--follow-redirects",      dest="redirects",     help="Follow the redirects",                                          action='store_true', default=False)
    parser.add_argument("-string","--match-string",         dest="string",        help="If the response has this string, print the url",                default=None)
    parser.add_argument("-location","--redirect-location",  dest="location",      help="Display the redirection location",                              action='store_true')
    parser.add_argument("-https", "--https-only",           dest="https_only",    help="Prefer https if the server has both http and https available",  action='store_true')
    

    args = parser.parse_args()
    """
    args.list
    args.ports
    args.timeout
    args.retries
    args.status_codes
    args.n_concurrency
    """
    
    if not sys.stdin.isatty():
        # stdin is not empty
        subdomains = sys.stdin.read().split("\n")[::-1]
        pass
    else:
        # stdin is empty
        subdomains = open(args.list, "r").read().split("\n")[:-1][::-1]
    
    thread_list = []


    for t in range(int(args.n_threads)):
        t = threading.Thread(target=request_handler,)
        thread_list.append(t)
        t.daemon = True
        t.start()

    for t in thread_list:
        try:
            t.join()
        except KeyboardInterrupt:
            sys.stdout.write(f"{RED}[!] Keyboard interrupt recieved, exiting ...{RESET}\n")
            sys.exit(1)
        except:
            pass
