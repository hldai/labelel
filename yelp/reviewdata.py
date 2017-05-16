import json
import gzip

from django.shortcuts import get_object_or_404
from models import LabelResult
from elasticsearch import Elasticsearch

from mention import Mention

index_name = 'yelp'
es_url = 'localhost:9200'
biz_doc_type = 'biz'
rev_doc_type = 'review'
es = Elasticsearch([es_url])
rev_ids = list()
mentions = dict()

rev_id_file = 'e:/data/yelp/valid_reviews_random1m.txt'
mentions_file = 'e:/data/yelp/random_rev_mentions.txt'


def __load_rev_ids():
    if rev_ids:
        return

    print 'loading %s ...' % rev_id_file
    f = open(rev_id_file, 'r')
    for line in f:
        # print line
        rev_ids.append(line.strip())
    f.close()
    print len(rev_ids), 'reviews.'


def __load_mentions():
    print 'loading %s ...' % mentions_file
    f = open(mentions_file, 'r')
    while True:
        m = Mention.fromfile(f)
        if not m:
            break

        rev_mentions = mentions.get(m.docid, list())
        if not rev_mentions:
            mentions[m.docid] = rev_mentions
        rev_mentions.append(m)
    f.close()


__load_rev_ids()
__load_mentions()


def __highlight_mentions(rev_text, mentions):
    new_text = u''
    last_pos = 0
    for i, m in enumerate(mentions):
        new_text += u'%s<span id="mention-span-%d" class="mention" onclick="mentionClicked(%d, \'%s\')">%s</span>' % (
            rev_text[last_pos:m.begpos], i, i, m.mention_id, rev_text[m.begpos:m.endpos])
        last_pos = m.endpos

    if len(mentions) > 0:
        # last_m = mentions[-1]
        new_text += rev_text[last_pos:]
    return new_text.replace('\n', '<br/>')


def get_review(rev_idx):
    if rev_idx >= len(rev_ids) or rev_idx < 0:
        return None

    rev_id = rev_ids[rev_idx]
    res = es.get(index=index_name, doc_type=rev_doc_type, id=rev_id)
    return res['_source']


def get_business(business_id):
    res = es.get(index=index_name, doc_type=biz_doc_type, id=business_id)
    return res['_source']


def get_mentions_of_review(review_id):
    return mentions.get(review_id, None)


# TODO use highlight_mentions directly
def get_review_text_disp_html(rev_info):
    rev_text = rev_info['text']
    rev_id = rev_info['review_id']

    rev_mentions = mentions.get(rev_id, None)

    if not rev_mentions:
        return rev_text

    return __highlight_mentions(rev_text, rev_mentions)


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


def __search_biz_es(es, query_str):
    qbody = {
        "query": {
            "bool": {
                "should": [
                    {"match": {"name": {"query": query_str, "boost": 5}}},
                    {"match": {"city": query_str}},
                    {"match": {"state": query_str}},
                    {"match": {"address": query_str}}
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

    res = es.search(index=index_name, body=qbody, size=30)

    return res['hits']['hits']


def __gen_candidates_es(es, mention, rev_biz_city, rev_text):
    query_str1 = None
    if mention.endpos + 1 < len(rev_text) and rev_text[mention.endpos:mention.endpos + 2] == "'s":
        query_str1 = mention.name_str + "'s"
    es_search_result = __match_biz_es(es, rev_biz_city, mention.name_str, query_str1)
    candidates = __filter_es_candidates(es_search_result, mention)

    return candidates


def search_candidates_es(search_str):
    es_search_result = __search_biz_es(es, search_str)
    candidates = list()
    for hit in es_search_result:
        candidates.append(get_business(hit['_source']['business_id']))
    return candidates


def get_candidates_of_mentions(mentions, review_info, rev_biz_info):
    if not mentions:
        return None

    rev_city = rev_biz_info['city']
    mention_candidates = list()
    for m in mentions:
        es_candidates = __gen_candidates_es(es, m, rev_city, review_info['text'])
        tup = (m, [get_business(c[0]) for c in es_candidates])
        mention_candidates.append(tup)
        # candidates_dict[m.mention_id] = [get_business(c[0]) for c in es_candidates]
    return mention_candidates


def update_label_result(username, post_data):
    main_label_prefix = 'main-label-'
    link_label_prefix = 'link-label-'
    len_main_label = len(main_label_prefix)
    len_link_label = len(link_label_prefix)

    mention_labels_main = dict()
    mention_labels_link = dict()
    for k, v in post_data.iteritems():
        if k.startswith('main-label'):
            mention_labels_main[k[len_main_label:]] = v
        elif k.startswith('link-label'):
            mention_labels_link[k[len_link_label:]] = v

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
                biz_id = mention_labels_link[mention_id]
            lr = LabelResult(mention_id=mention_id, cur_state=curstate, biz_id=biz_id, username=username)
            lr.save()
