import sys
import getopt
import requests
import json

def fetch_art(line_height=0, count=1):
    path = "https://t9twln26m6.execute-api.us-east-1.amazonaws.com/default/ascii-art"
    if line_height != 0:
        path += f"?line_height={line_height}&count={count}"
    response_json = requests.get(path).text
    response_dict = json.loads(response_json)
    return response_dict

if __name__ == "__main__":
    art = {}
    line_height = 0
    count = 0

    options = "l:c:"
    opts = getopt.getopt(sys.argv[1:], options)

    for opt_pair in opts[:-1]:
        for opt, arg in opt_pair:
            if opt == "-l":
                line_height = int(arg)
            elif opt == "-c":
                count = int(arg)
    
    print(f"line_height: {line_height}, count: {count}")

    art = fetch_art(line_height, count)
    for key, val in art.items():
        print(f"{key}: {val}")
