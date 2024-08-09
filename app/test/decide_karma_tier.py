from pymongo import MongoClient
from collections import Counter
import csv

client = MongoClient("mongodb://localhost:50003/")
DB = client['RedditService']
POSTS_COLLECTION = DB['Posts']


if __name__ == "__main__":
    data = [p for p in POSTS_COLLECTION.find()]
    test = Counter(A=0, B=0, C=0, D=0, N=0)
    real_num = Counter()
    for p in data:
        for ans in p['answers']:
            karma = ans['author_comment_karma']
            real_num[karma]+=1
            if karma >= 50000:
                test['A'] += 1
            elif 50000 > karma >= 30000:
                test['B'] += 1
            elif 30000 > karma >= 10000:
                test['C'] += 1
            elif 10000 > karma >= 1000:
                test['D'] += 1
            else:
                test['N'] += 1

    print(sorted(test.items()))

    # Calculate percentiles for each element
    percentiles = []
    count = 0
    total_count = sum(real_num.values())
    print(total_count)
    keys = []
    values = []
    for item, item_count in sorted(real_num.items(), reverse=False):
        # Calculate the current percentile based on the cumulative count
        count += item_count
        percentile = (count / total_count) * 100
        percentiles.append(percentile)
        keys.append(item)
        values.append(item_count)

    with open('karma_range.csv', 'w') as csvfile:
        fieldnames = ['Score', 'count', 'percentile']
        writer = csv.writer(csvfile)
        writer.writerow(fieldnames)
        for item, item_count, percentile in zip(keys, values, percentiles):
            #print(f"Item: {item}, Count: {item_count}, Percentile: {percentile:.2f}%")
            writer.writerow([item, item_count, percentile])






