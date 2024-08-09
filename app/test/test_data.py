import json
import time

import requests

reddit_parser_url = "http://localhost:100"


if __name__ == "__main__":
    with open("samples.json", "r", encoding="utf-8") as file:
        questions = json.load(file)
    file.close()

    for cat in questions:
        print(">> Category: " + cat)
        for q in questions[cat]:
            print(q)

            # Search questions
            search_requests = reddit_parser_url + f"/search?keywords=python;{q}&page=0&num=10"
            links = requests.get(url=search_requests).json()
            print(links)

            # Parse question
            req = {"links": links['result']}
            retrieve_url = reddit_parser_url + "/retrieve"
            resp = requests.post(url=retrieve_url, json=req)
            print(resp.json())

            time.sleep(5)


