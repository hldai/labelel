import json
import gzip

from mention import Mention
from elasticsearch import Elasticsearch

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
    for m in mentions:
        new_text += u'%s<span class="mention" onclick="mentionClicked(\'%s\')">%s</span>' % (
            rev_text[last_pos:m.begpos], m.mention_id, rev_text[m.begpos:m.endpos])
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


def __gen_candidates_es(es, mention, rev_biz_city):
    qbody = {
        "query": {
            "bool": {
                "must": {
                    "match": {
                        "name": {
                            "query": "Choderwood",
                            "boost": 5
                        }
                    }
                },
                "should": {
                    "match": {
                        "city": "Phoenix"
                    }
                }
            }
        }
    }

    qbody['query']['bool']['must']['match']['name']['query'] = mention.name_str
    qbody['query']['bool']['should']['match']['city'] = rev_biz_city
    res = es.search(index=index_name, body=qbody, size=30)

    candidates = __filter_es_candidates(res['hits']['hits'], mention)

    return candidates


def __get_candidates_disp(mention, rev_city):
    es_candidates = __gen_candidates_es(es, mention, rev_city)
    disp_html = '<div class="div-candidates" id="m%s">' % mention.mention_id
    for biz_id, score in es_candidates:
        biz_info = get_business(biz_id)
        disp_html += '%s %f<br>' % (biz_info['name'], score)
    disp_html += '</div>\n'
    return disp_html


def get_candidates_disp_html(rev_info, rev_biz_info):
    rev_id = rev_info['review_id']
    rev_mentions = mentions.get(rev_id, None)
    if not rev_mentions:
        return ''

    all_candidates_disp = ''
    for m in rev_mentions:
        all_candidates_disp += __get_candidates_disp(m, rev_biz_info['city'])
    return all_candidates_disp


def get_candidates_of_mentions(mentions, rev_biz_info):
    if not mentions:
        return None

    rev_city = rev_biz_info['city']
    mention_candidates = list()
    for m in mentions:
        es_candidates = __gen_candidates_es(es, m, rev_city)
        tup = (m, [get_business(c[0]) for c in es_candidates])
        mention_candidates.append(tup)
        # candidates_dict[m.mention_id] = [get_business(c[0]) for c in es_candidates]
    return mention_candidates
