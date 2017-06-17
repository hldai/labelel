from __future__ import unicode_literals

from django.db import models, OperationalError, transaction
import time


def get_main_labels(post_data):
    main_label_prefix = 'main-label-'
    len_main_label = len(main_label_prefix)
    mention_labels_main = dict()
    for k, v in post_data.iteritems():
        if k.startswith(main_label_prefix):
            mention_labels_main[k[len_main_label:]] = v
    return mention_labels_main


def get_link_labels(post_data):
    link_label_prefix = 'link-label-'
    len_link_label = len(link_label_prefix)

    mention_labels_link = dict()
    for k, v in post_data.iteritems():
        if k.startswith('link-label'):
            mention_labels_link[k[len_link_label:]] = v
    return mention_labels_link


class LabelResult(models.Model):
    table_name = 'yelp_labelresult'

    mention_id = models.CharField(max_length=64)
    cur_state = models.IntegerField(default=0)
    biz_id = models.CharField(max_length=64)
    username = models.CharField(max_length=64)

    def __str__(self):
        return '%s\t%s\t%s\t%s' % (self.mention_id, self.cur_state,
                                   self.biz_id, self.username)

    @staticmethod
    @transaction.atomic
    def __save_label_results(username, mention_labels_main, mention_labels_link):
        success_cnt = 0
        for mention_id, val in mention_labels_main.iteritems():
            try:
                lr = LabelResult.objects.get(mention_id=mention_id, username=username)
                # TODO server error
            except LabelResult.DoesNotExist:
                curstate = 0
                biz_id = ''
                if val == 'nil':
                    curstate = 1
                elif val == 'wm':
                    curstate = 2
                elif val == 'link':
                    curstate = 3
                    biz_id = mention_labels_link[mention_id]

                if curstate == 0:
                    continue

                lr = LabelResult(mention_id=mention_id, cur_state=curstate, biz_id=biz_id, username=username)
                lr.save()

                success_cnt += 1
        return success_cnt

    @staticmethod
    def update_label_result(username, post_data):
        mention_labels_main = get_main_labels(post_data)
        mention_labels_link = get_link_labels(post_data)
        while True:
            try:
                return LabelResult.__save_label_results(username, mention_labels_main, mention_labels_link)
            except OperationalError:
                print 'Operational Error'
                time.sleep(0.5)


class LabelResultV2(models.Model):
    table_name = 'yelp_labelresultv2'

    mention_id = models.CharField(max_length=64)
    cur_state = models.IntegerField(default=0)
    # is_franchise = models.SmallIntegerField(default=0)
    is_wrong_span = models.SmallIntegerField(default=0)
    biz_id = models.CharField(max_length=64)
    username = models.CharField(max_length=64)

    def __str__(self):
        return '%s\t%s\t%s\t%s\t%s' % (
            self.mention_id, self.cur_state, self.is_wrong_span,
            self.biz_id, self.username)

    @staticmethod
    @transaction.atomic
    def __save_label_results(username, mention_labels_main, post_data):
        success_cnt = 0
        for mention_id, val in mention_labels_main.iteritems():
            # is_franchise = 0
            is_wrong_span = 0
            try:
                lr = LabelResultV2.objects.get(mention_id=mention_id, username=username)
                # TODO server error
            except LabelResultV2.DoesNotExist:
                curstate = 0
                biz_id = ''
                if val == 'nil':
                    curstate = 1
                elif val == 'wm':
                    curstate = 2
                elif val == 'fran':
                    curstate = 4
                elif val == 'unlinkable':
                    curstate = 5
                elif val == 'link':
                    curstate = 3
                    link_key = 'link-label-' + mention_id
                    biz_id = post_data.get(link_key, None)
                    if not biz_id:
                        continue

                    # val_franchise = post_data.get('franchise-' + mention_id, None)
                    # is_franchise = 1 if val_franchise else 0
                    val_wrongspan = post_data.get('wrongspan-' + mention_id, None)
                    is_wrong_span = 1 if val_wrongspan else 0

                if curstate == 0:
                    continue

                # lr = LabelResultV2(mention_id=mention_id, cur_state=curstate, biz_id=biz_id, username=username,
                #                    is_franchise=is_franchise, is_wrong_span=is_wrong_span)
                lr = LabelResultV2(mention_id=mention_id, cur_state=curstate, biz_id=biz_id, username=username,
                                   is_wrong_span=is_wrong_span)
                lr.save()

                success_cnt += 1
        return success_cnt

    @staticmethod
    def update_label_result(username, post_data):
        # print post_data
        mention_labels_main = get_main_labels(post_data)
        # mention_labels_link = get_link_labels(post_data)
        while True:
            try:
                return LabelResultV2.__save_label_results(username, mention_labels_main, post_data)
            except OperationalError:
                print 'Operational Error'
                time.sleep(0.5)
