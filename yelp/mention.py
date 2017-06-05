class Mention:
    def __init__(self, mention_id='', docid='', begpos=-1,
                 endpos=-1, mtype='', name_str=''):
        self.mention_id = mention_id
        self.docid = docid
        self.begpos = begpos
        self.endpos = endpos  # exclude
        self.mtype = mtype
        self.name_str = name_str

    def __str__(self):
        return u'%s\t%s\t%d\t%d\t%s\t%s' % (self.mention_id, self.docid, self.begpos, self.endpos,
                                            self.mtype, self.name_str)

    def tofile(self, f):
        f.write((u'%s\t%s\t%d\t%d\t%s\t%s\n' % (self.mention_id, self.docid,
                                                self.begpos, self.endpos, self.mtype,
                                                self.name_str)).encode('utf-8'))

    @staticmethod
    def from_dict(mention_dict):
        return Mention(mention_id=mention_dict['mention_id'], docid=mention_dict['docid'],
                       begpos=mention_dict['begpos'], endpos=mention_dict['endpos'],
                       mtype=mention_dict['mtype'], name_str=mention_dict['name_str'])

    @staticmethod
    def fromfile(f):
        try:
            line = f.next()
            vals = line.strip().split('\t')
            m = Mention(mention_id=vals[0], docid=vals[1], begpos=int(vals[2]),
                        endpos=int(vals[3]), mtype=vals[4], name_str=vals[5].decode('utf-8'))
            return m
        except StopIteration:
            return None

    @staticmethod
    def next_doc_mentions_ob(fin):
        try:
            line = fin.next()
        except StopIteration:
            return None

        vals = line.split('\t')
        docid = vals[0]
        num_mentions = int(vals[1])
        mentions = list()
        for i in xrange(num_mentions):
            line = fin.next()
            vals = line.strip().split('\t')
            m = Mention(mention_id=vals[0], docid=docid, begpos=int(vals[1]),
                        endpos=int(vals[2]), mtype=vals[3], name_str=vals[4].decode('utf-8'))
            mentions.append(m)
        return docid, mentions
