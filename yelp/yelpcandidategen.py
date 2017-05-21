class YelpCandidateGen:
    def __init__(self, elasticsearch, biz_acronyms_file, index_name='yelp', biz_doc_type='biz'):
        self.es = elasticsearch
        self.index_name = index_name
        self.biz_doc_type = biz_doc_type
        self.acronym_biz_dict = YelpCandidateGen.__load_biz_acronyms(biz_acronyms_file)

    def gen_candidates(self, mention, rev_biz_city, rev_text):
        candidates = self.gen_candidates_es(mention, rev_biz_city, rev_text)
        abbr = mention.name_str.replace('.', '')
        if ' ' not in abbr and abbr.isupper():
            candidates_acr = self.acronym_biz_dict.get(abbr, None)
            if candidates_acr:
                for biz_id, biz_city in candidates_acr:
                    if len(abbr) > 2 or biz_city == rev_biz_city:
                        candidates.append((biz_id, 1.0))
        return candidates

    def gen_candidates_es(self, mention, rev_biz_city, rev_text):
        query_str1 = None
        if mention.endpos + 1 < len(rev_text) and rev_text[mention.endpos:mention.endpos + 2] == "'s":
            query_str1 = mention.name_str + "'s"
        es_search_result = self.__match_biz_es(rev_biz_city, mention.name_str, query_str1)
        candidates = YelpCandidateGen.__filter_es_candidates(es_search_result, mention)

        return candidates

    def __match_biz_es(self, rev_biz_city, query_str0, query_str1):
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

        res = self.es.search(index=self.index_name, body=qbody, size=30)

        return res['hits']['hits']

    @staticmethod
    def __load_biz_acronyms(biz_acronyms_file):
        acronym_biz_dict = dict()
        f = open(biz_acronyms_file, 'r')
        for line in f:
            vals = line.strip().split('\t')
            if len(vals) < 3:
                continue

            acronym, biz_id, biz_city = vals
            biz_list = acronym_biz_dict.get(acronym, list())
            if not biz_list:
                acronym_biz_dict[acronym] = biz_list
            biz_list.append((biz_id, biz_city.decode('utf-8')))
        f.close()
        return acronym_biz_dict

    @staticmethod
    def __filter_es_candidates(hits, mention):
        candidates = list()
        for hit in hits:
            biz_name = hit['_source']['name']
            if YelpCandidateGen.__all_words_in(mention.name_str, biz_name):
                candidates.append((hit['_source']['business_id'], hit['_score']))
        return candidates

    @staticmethod
    def __all_words_in(s0, s1):
        s1 = s1.lower()
        words = s0.lower().split(' ')
        for w in words:
            if w not in s1:
                return False
        return True
