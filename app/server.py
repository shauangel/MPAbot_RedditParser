#!/usr/bin/env python
import os
import time
import logging
import sys
from flask import Flask, jsonify, request
from flasgger import Swagger
import models.outer_search as outer_search
import models.reddit_parser as reddit_parser
from models import db_manager as db

logging.basicConfig(stream=sys.stdout)
app = Flask(__name__)
app.config['SWAGGER'] = {
    "title": "Reddit Parsing Service",
    "description": "API for Reddit data collection & retrieval",
    "version": "1.0",
    "termsOfService": "",
    "hide_top_bar": True
}
swagger = Swagger(app=app, template_file="swagger_doc.yml")


@app.route('/hello', methods=['GET'])
def hello():
    return jsonify({"result": "hello"})


# search only, return urls
@app.route('/search', methods=['GET'])
def search():
    # Step 1: Get parameters
    keywords = request.values.get('keywords')
    page = int(request.values.get('page'))
    result_num = int(request.values.get('num'))

    try:
        # Step 2: Start searching
        result = outer_search.outer_search(keywords=keywords.split(';'),
                                           result_num=int(result_num),
                                           page_num=int(page))
        response = {"result": result}
    except Exception as e:
        response = {"error": e.__class__.__name__ + " : " + e.args[0]}
    return jsonify(response)


# retrieve full information, return posts content
@app.route('/retrieve', methods=['POST'])
def retrieve():
    data = request.get_json()
    try:
        # Step 1: Search webpages by Google
        search_result = data["links"]

        # Step 2: Check if posts is in database
        records = db.query_post_by_link(search_result)

        # Step 3: Check if the parser needs to get more data
        if len(records) == len(search_result):
            # Step 5-1: If all the websites are collected, return records
            response = records
        else:
            # Step 5-2: Modify data, update new ids & links needs to be parse
            for r in records:
                search_result.remove(r['link'])

            # Step 6: Parse data from PRAW
            parser = reddit_parser.RedditData(search_result)
            parser.start_parsing()
            new_parsed = parser.get_results()

            # Step 7: Insert new posts data
            insert_id = db.insert_posts(new_parsed)
            print(insert_id)

            # Step 8: return result
            response = records + new_parsed

        # Step 9: Remove Obj id
        response = db.remove_obj_id(response)

    except Exception as e:
        response = {"error": e.__class__.__name__ + " : " + e.args[0]}
    return jsonify(response)


if __name__ == "__main__":
    print("Welcome to Reddit service system~~")
    app.run(host='0.0.0.0', port=os.environ.get("FLASK_SERVER_PORT", 9090), debug=True)
