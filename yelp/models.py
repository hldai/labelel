from __future__ import unicode_literals

from django.db import models


class LabelResult(models.Model):
    mention_id = models.CharField(max_length=64)
    cur_state = models.IntegerField(default=0)
    biz_id = models.CharField(max_length=64)
    username = models.CharField(max_length=64)

    def __str__(self):
        return '%s\t%s\t%s\t%s' % (self.mention_id, self.cur_state,
                                   self.biz_id, self.username)


class UserReview(models.Model):
    username = models.CharField(max_length=64)
    review_id = models.CharField(max_length=64)

    def __str__(self):
        return '%s\t%s' % (self.username, self.review_id)


# class UserLabelStat(models.Model):
#     username = models.CharField(max_length=64)
#     num_mentions_labeled = models.IntegerField(default=0)
#
#     def __str__(self):
#         return '%s\t%s' % (self.username, self.num_mentions_labeled)
