import json
import socket
import gzip
import os
import time
import sqlite3

from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.db import transaction
import django.db
from models import LabelResultV2 as LabelResult
# from models import LabelResult
from elasticsearch import Elasticsearch
from labelel.settings import DATABASES

from mention import Mention
from yelpcandidategen import YelpCandidateGen

# review dispatch
REV_DISPATCH_HOST = 'localhost'
REV_DISPATCH_PORT = 9731
DATA_END_STR = 'DHLDHLDHLEND'

# elasticsearch
index_name = 'yelp'
es_url = 'localhost:9200'
es = Elasticsearch([es_url])
biz_doc_type = 'biz'
rev_doc_type = 'review'

user_num_mentions = dict()
mentions = dict()

data_dir = 'e:/data/yelp'
# data_dir = '/home/hldai/data/yelp'
# rev_id_file = os.path.join(data_dir, 'valid_reviews_random100k.txt')
# mentions_file = os.path.join(data_dir, 'reviews_random400k_mentions_1.txt')
biz_acronyms_file = os.path.join(data_dir, 'biz_acronyms.txt')

ycg = YelpCandidateGen(es, biz_acronyms_file, index_name, biz_doc_type)


def __table_exists(table_name, db_file):
    conn = sqlite3.connect(db_file)
    sql = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"
    # print table_name
    r = conn.execute(sql, (table_name,))

    exist = False
    for _ in r:
        exist = True
        break
    conn.close()
    return exist


def __init():
    # __load_mentions()

    db_file = DATABASES['default']['NAME']
    l = os.path.getsize(db_file) if os.path.isfile(db_file) else 0
    if l == 0:
        return

    if not __table_exists('auth_user', db_file) or not __table_exists(LabelResult.table_name, db_file):
        return

    print 'initing user num mentions ...'
    users = User.objects.all()
    for u in users:
        user_num_mentions[u.username] = LabelResult.objects.filter(username=u.username).count()
    # print user_num_mentions

__init()


def get_user_num_labeled_mentions(username):
    return user_num_mentions.get(username, 0)


def get_user_num_reviews(username):
    received = __query_review_dispatcher(username, -1)
    return received['num_reviews']


def highlight_mentions(rev_text, mentions, label_results):
    new_text = u''
    last_pos = 0
    for i, m in enumerate(mentions):
        span_class = 'span-mention'
        if m.mention_id in label_results:
            span_class += ' span-mention-labeled'
        span_attrs = 'id="mention-span-%d" class="%s" onclick="mentionClicked(%d, \'%s\')' % (
            i, span_class, i, m.mention_id)
        new_text += u'%s<span %s">%s</span>' % (rev_text[last_pos:m.begpos], span_attrs, rev_text[m.begpos:m.endpos])
        last_pos = m.endpos

    new_text += rev_text[last_pos:]
    return new_text.replace('\n', '<br/>')


def __query_review_dispatcher(username, user_rev_idx):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    data = json.dumps({'username': username, 'review_idx': user_rev_idx})

    try:
        # Connect to server and send data
        sock.connect((REV_DISPATCH_HOST, REV_DISPATCH_PORT))
        sock.sendall(data)

        received = ''
        # Receive data from the server and shut down
        while True:
            data = sock.recv(1024)
            received += data
            if received.endswith(DATA_END_STR):
                break
        # print username, received
        received = json.loads(received[:-len(DATA_END_STR)])
    finally:
        sock.close()

    return received


def get_review_for_user(username, user_rev_idx):
    if user_rev_idx < 1:
        user_rev_idx = 1

    received = __query_review_dispatcher(username, user_rev_idx)

    rev_idx = received['review_idx']
    rev_id = received['review_id']
    res = es.get(index=index_name, doc_type=rev_doc_type, id=rev_id)

    mention_dicts = received['mentions']
    mentions = [Mention.from_dict(mdict) for mdict in mention_dicts]

    return rev_idx, res['_source'], mentions


def get_business(business_id):
    res = es.get(index=index_name, doc_type=biz_doc_type, id=business_id)
    return res['_source']


def get_label_results(mentions, username):
    label_result_dict = dict()
    for m in mentions:
        try:
            lr = LabelResult.objects.get(mention_id=m.mention_id, username=username)
            label_result_dict[m.mention_id] = lr
        except LabelResult.DoesNotExist:
            continue
    return label_result_dict


def __all_words_in(s0, s1):
    s1 = s1.lower()
    words = s0.lower().split(' ')
    for w in words:
        if w not in s1:
            return False
    return True


def __filter_es_candidates(hits, mention):
    candidates = list()
    for hit in hits:
        biz_name = hit['_source']['name']
        if __all_words_in(mention.name_str, biz_name):
            candidates.append((hit['_source']['business_id'], hit['_score']))
    return candidates


def __search_biz_es(es, biz_name, biz_city, biz_addr):
    qbody = {
        "query": {
            "bool": {
                "should": [
                    {"match": {"name": {"query": biz_name, "boost": 3}}},
                    {"match": {"city": biz_city}},
                    # {"match": {"state": query_str}},
                    {"match": {"address": biz_addr}}
                ]
            }
        }
    }

    res = es.search(index=index_name, body=qbody, size=30)

    return res['hits']['hits']


def __match_biz_es(es, rev_biz_city, query_str0, query_str1):
    if query_str1:
        qbody_match_name = {
            "bool": {
                "should": [
                    {"match": {"name": {"query": query_str0, "boost": 5}}},
                    {"match": {"name": {"query": query_str1, "boost": 5}}}
                ]
            }
        }
    else:
        qbody_match_name = {"match": {"name": {"query": query_str0, "boost": 5}}}

    qbody_match_city = {"match": {"city": rev_biz_city}}

    qbody = {
        "query": {
            "bool": {
                "must": qbody_match_name,
                "should": qbody_match_city
            }
        }
    }

    res = es.search(index=index_name, body=qbody, size=20)

    return res['hits']['hits']


def __gen_candidates_es(es, mention, rev_biz_city, rev_text):
    query_str1 = None
    if mention.endpos + 1 < len(rev_text) and rev_text[mention.endpos:mention.endpos + 2] == "'s":
        query_str1 = mention.name_str + "'s"
    es_search_result = __match_biz_es(es, rev_biz_city, mention.name_str, query_str1)
    candidates = __filter_es_candidates(es_search_result, mention)

    return candidates


def search_candidates_es(biz_name, biz_city, biz_addr):
    es_search_result = __search_biz_es(es, biz_name, biz_city, biz_addr)
    candidates = list()
    for hit in es_search_result:
        candidates.append(get_business(hit['_source']['business_id']))
    return candidates


def get_candidates_of_mentions(mentions, review_info, rev_biz_info, label_results):
    if not mentions:
        return None

    rev_city = rev_biz_info['city']
    mention_candidates = list()
    for m in mentions:
        lr = label_results.get(m.mention_id, None)
        if lr:
            lr_disp = dict()
            lr_disp['cur_state'] = lr.cur_state
            if lr.cur_state == 3:
                lr_disp['biz'] = get_business(lr.biz_id)
            tup = (m, True, lr_disp)
            mention_candidates.append(tup)
        else:
            # es_candidates = __gen_candidates_es(es, m, rev_city, review_info['text'])
            candidates = ycg.gen_candidates(m, rev_city, review_info['text'])
            tup = (m, False, [get_business(c[0]) for c in candidates])
            mention_candidates.append(tup)
    return mention_candidates


@transaction.atomic
def __save_label_results(username, mention_labels_main, mention_labels_link):
    for mention_id, val in mention_labels_main.iteritems():
        try:
            lr = LabelResult.objects.get(mention_id=mention_id, username=username)
            # TODO server error
        except LabelResult.DoesNotExist:
            curstate = 0
            biz_id = ''
            if val == 'nobiz':
                curstate = 1
            elif val == 'nil':
                curstate = 2
            elif val == 'link':
                curstate = 3
                biz_id = mention_labels_link[mention_id]

            if curstate == 0:
                continue

            lr = LabelResult(mention_id=mention_id, cur_state=curstate, biz_id=biz_id, username=username)
            lr.save()

            cnt = user_num_mentions.get(username, 0)
            user_num_mentions[username] = cnt + 1


def __get_main_labels(post_data):
    main_label_prefix = 'main-label-'
    len_main_label = len(main_label_prefix)
    mention_labels_main = dict()
    for k, v in post_data.iteritems():
        if k.startswith(main_label_prefix):
            mention_labels_main[k[len_main_label:]] = v
    return mention_labels_main


def __get_link_labels(post_data):
    link_label_prefix = 'link-label-'
    len_link_label = len(link_label_prefix)

    mention_labels_link = dict()
    for k, v in post_data.iteritems():
        if k.startswith('link-label'):
            mention_labels_link[k[len_link_label:]] = v
    return mention_labels_link


def __update_label_result_v1(username, post_data):
    mention_labels_main = __get_main_labels(post_data)
    mention_labels_link = __get_link_labels(post_data)
    while True:
        try:
            __save_label_results(username, mention_labels_main, mention_labels_link)
            break
        except django.db.OperationalError:
            print 'Operational Error'
            time.sleep(0.5)


def __update_label_result_v2(username, post_data):
    mention_labels_main = __get_main_labels(post_data)
    mention_labels_link = __get_link_labels(post_data)
    while True:
        try:
            __save_label_results(username, mention_labels_main, mention_labels_link)
            break
        except django.db.OperationalError:
            print 'Operational Error'
            time.sleep(0.5)


def update_label_result(username, post_data):
    # __update_label_result_v1(username, post_data)
    # __update_label_result_v2(username, post_data)
    LabelResult.update_label_result(username, post_data)


def delete_label_result(mention_id, username):
    # lr = LabelResult.objects.get(mention_id=mention_id, username=username)
    lr = get_object_or_404(LabelResult, mention_id=mention_id, username=username)
    lr.delete()

    user_num_mentions[username] -= 1
