import requests
import pandas as pd
import time
import random
from tqdm import tqdm

cookies = {
    'TIKI_GUEST_TOKEN': '8jWSuIDBb2NGVzr6hsUZXpkP1FRin7lY',
    'TOKENS': '{%22access_token%22:%228jWSuIDBb2NGVzr6hsUZXpkP1FRin7lY%22%2C%22expires_in%22:157680000%2C%22expires_at%22:1763654224277%2C%22guest_token%22:%228jWSuIDBb2NGVzr6hsUZXpkP1FRin7lY%22}',
    'amp_99d374': 'eSc-_0HT1um7cb57E7dwA0...1enloc6a2.1enlrj4bc.1k.11.2l',
    'amp_99d374_tiki.vn': 'eSc-_0HT1um7cb57E7dwA0...1enloc6a2.1enlrj2q9.3.1.1',
    '_gcl_au': '1.1.559117409.1605974236',
    '_ants_utm_v2': '',
    '_pk_id.638735871.2fc5': 'b92ae025fbbdb31f.1605974236.1.1605977607.1605974236.',
    '_pk_ses.638735871.2fc5': '*',
    '_trackity': '70e316b0-96f2-dbe1-a2ed-43ff60419991',
    '_ga_NKX31X43RV': 'GS1.1.1605974235.1.1.1605977607.0',
    '_ga': 'GA1.2.657946765.1605974236',
    'ai_client_id': '11935756853.1605974227',
    'an_session': 'zizkzrzjzkzizhzkzlznzdzizizqzgzmzkzmzlzrzmzgzdzizlzjzmzqzkzlzjzgzjzdzizizdzizlzjzmzqzkzlzjzgzjzdzizlzjzmzqzkzlzjzgzjzdzjzdzhzqzdzizd2f27zdzjzdzlzmzmznzq',
    'au_aid': '11935756853',
    'dgs': '1605977598%3A3%3A0',
    'au_gt': '1605974227146',
    '_ants_services': '%5B%22cuid%22%5D',
    '__admUTMtime': '1605974236',
    '__iid': '749',
    '__su': '0',
    '_bs': 'bb9a32f6-ab13-ce80-92d6-57fd3fd6e4c8',
    '_gid': 'GA1.2.867846791.1605974237',
    '_fbp': 'fb.1.1605974237134.1297408816',
    '_hjid': 'f152cf33-7323-4410-b9ae-79f6622ebc48',
    '_hjFirstSeen': '1',
    '_hjAbsoluteSessionInProgress': '0',
    'tiki_client_id': '657946765.1605974236',
    '__gads': 'ID=ae56424189ecccbe-227eb8e1d6c400a8:T=1605974229:RT=1605974229:S=ALNI_MZFWYf2BAjzCSiRNLC3bKI-W_7YHA',
    'proxy_s_sv': '1605978058486',
    'TKSESSID': '8bcd49b02e1e16aa1cdb795c54d7b460',
    'TIKI_RECOMMENDATION': '21dd50e7f7c194df673ea3b717459249',
    'cto_bundle': '7L6ha19NVXNkQmJ6aEVLcXNqbHdjcVZoQ0kzTUZwcEMyNCUyRm5nV3A2SThuOGxTRjI4Wlk1NU9xRnBEOG9tUjd2ekhyZEQxeE9qaVQ4MnFpbiUyRllGd2JiQUpTMW94MlNsTnYxd3dOYWtRcXhGdDNxSjdBVmNxU0FnUSUyQjlWYjhqTUtLdVl2cTBheWFvS0ZnY2pLdlpWRlEyUFF0Y1ElM0QlM0Q',
    'TIKI_RECENTLYVIEWED': '58259141',
    '_ants_event_his': '%7B%22action%22%3A%22view%22%2C%22time%22%3A1605977607258%7D',
    '_hjIncludedInPageviewSample': '1',
    '_hjIncludedInSessionSample': '1',
    '_gat': '1'
}

header = {
    'accept': 'application/json, text/plain, /',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'vi-VN,vi,;q=0.8,en-US,en;q=0.6',
    'referer': 'https://tiki.vn/thoi-trang-nam/c915',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    'x-guest-token': 'kax4WoQfzPUY2mhKri1sFbCJVDe0X8w9',
    'TE': 'Trailers'
}

params = {
    'product_id': '0',
    'sort': 'score|desc,id|desc,stars|all',
    'page': '1',
    'limit': '20',
    'include': 'comments'
}

TIMEOUT_SECONDS = 20
MAX_RETRIES = 3
SAVE_EVERY = 20
PROCESSED_IDS_PATH = 'data/thoitrangnam-tiki/result/processed_ids.txt'


def fetch_reviews(params):
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return requests.get(
                'https://tiki.vn/api/v2/reviews',
                headers=header,
                params=params,
                cookies=cookies,
                timeout=TIMEOUT_SECONDS
            )
        except requests.RequestException as exc:
            if attempt == MAX_RETRIES:
                print(
                    'Request failed for product {} page {}: {}'.format(
                        params.get('product_id'),
                        params.get('page'),
                        exc
                    )
                )
                return None
            time.sleep(2 + attempt)


def comment_parser(json):
    d = dict()
    d['id'] = json.get('id')
    d['title'] = json.get('title')
    d['content'] = json.get('content')
    d['rating'] = json.get('rating')
    return d


def load_processed_ids(path):
    try:
        with open(path, 'r', encoding='utf-8') as handle:
            return set(line.strip() for line in handle if line.strip())
    except FileNotFoundError:
        return set()


def mark_processed_id(path, product_id):
    with open(path, 'a', encoding='utf-8') as handle:
        handle.write(str(product_id) + '\n')


df_id = pd.read_csv('data/thoitrangnam-tiki/result/product_id_ncds.csv')
p_ids = df_id.id.to_list()
processed_ids = load_processed_ids(PROCESSED_IDS_PATH)
result = []
for idx, pid in enumerate(tqdm(p_ids, total=len(p_ids)), start=1):
    if str(pid) in processed_ids:
        continue
    params['product_id'] = pid
    print('Crawl comment for product {}'.format(pid))
    for i in range(10):
        params['page'] = i
        response = fetch_reviews(params)
        if response is None:
            continue
        if response.status_code == 200:
            print('Crawl comment page {} success!!!'.format(i))
            for comment in response.json().get('data'):
                rating = comment.get('rating')
                if rating is not None and int(rating) <= 3:
                    result.append(comment_parser(comment))
        else:
            print('Crawl comment page {} failed: {}'.format(i, response.status_code))
    mark_processed_id(PROCESSED_IDS_PATH, pid)
    if idx % SAVE_EVERY == 0:
        df_comment = pd.DataFrame(result)
        df_comment.to_csv('data/thoitrangnam-tiki/result/comments_data_ncds.csv', index=False)

df_comment = pd.DataFrame(result)
df_comment.to_csv('data/thoitrangnam-tiki/result/comments_data_ncds.csv', index=False)
