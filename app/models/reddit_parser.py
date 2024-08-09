import json
import time
import praw
from multiprocessing.pool import ThreadPool

# refresh token: https://praw.readthedocs.io/en/stable/tutorials/refresh_token.html

# permalink (We can get the permalink for each comment if needed.)


class RedditData:
    def __init__(self, urls):
        self.__links = urls
        # store parsed data
        self.__results = []
        self.__reddit = ""
        self.init_parser()

    def init_parser(self):
        # 可能需要改成refresh
        reddit = praw.Reddit(
            client_id="iFPQiyRmCeog2sJ3al2xFg",
            client_secret="SZKO-W9HcQrcbHtrSfBzvBsW3vzrqg",
            user_agent="python:com.psabot.redditparser:v1"
        )
        self.__reddit = reddit

    def start_parsing(self):

        pool = ThreadPool(processes=len(self.__links))
        results = pool.map(self.get_posts, self.__links)
        pool.close()
        pool.join()
        print(results)
        self.__results = results
        """
        for u in self.__links:
            temp = self.get_posts(u)
            self.__results.append(temp)
        """

    def get_posts(self, url):
        print(url)
        temp = {"link": url, "question": {}, "answers": []}
        # Step 1: Submit request for a webpage, get Submission Obj
        start = time.time()
        sub = self.__reddit.submission(url=url)
        sub.comment_sort = "top"
        subreddit = sub.subreddit

        # Step 2: Get question information
        temp["question"]["id"] = sub.id
        temp["question"]["title"] = sub.title
        temp["question"]["content"] = sub.selftext
        temp["question"]["subreddit"] = {
            "created_utc": subreddit.created_utc,
            "subscribers": subreddit.subscribers
        }

        # Step 3: Get all comments
        sub.comments.replace_more(limit=0)  # Only retrieve the first page of comments
        comments = sub.comments.list()
        for c in comments[:20 if len(comments) > 20 else len(comments)]:
            if f"t3_{temp['question']['id']}" == c.parent_id:
                author = c.author
                c.replies.replace_more(limit=None)
                reply_list = c.replies.list()
                try:
                    temp["answers"].append({
                        "id": c.id,
                        "total_vote": sum([c.score]+[reply.score for reply in reply_list[:10]]),
                        "dialogue": "\n\n".join([c.body]+[reply.body for reply in reply_list[:10]]),
                        "author_comment_karma": author.comment_karma
                    })
                except AttributeError:
                    continue
            else:
                break

        end = time.time()
        print(end-start)
        return temp

    def set_links(self, new_link_list):
        self.__links = new_link_list

    def get_results(self):
        return self.__results


if __name__ == "__main__":
    print("Reddit Parser v.1")
    test = ['https://www.reddit.com/r/adventofcode/comments/k7ndux/2020_day_06_solutions/']
    r = RedditData(test[:2])
    r.start_parsing()

    with open("test_reddit.json", 'w', encoding='utf-8') as file:
        json.dump(fp=file, obj=r.get_results())
    file.close()



