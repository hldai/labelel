from time import time

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import views as auth_views

import reviewdata

FIX_MODE = True


def index(request):
    if not request.user.is_authenticated():
        return auth_views.login(request, template_name="login.html")

    context = dict()
    context['username'] = username = request.user.username

    if FIX_MODE:
        num_mentions = reviewdata.get_user_num_mentions(username)
        context['num_mentions'] = num_mentions
        context['label_review_idx'] = 1
        return render(request, 'yelp/userlabelstatfix.html', context)
    else:
        num_reviews = reviewdata.get_user_num_reviews(username)
        context['num_reviews'] = num_reviews
        context['num_mentions'] = reviewdata.get_user_num_labeled_mentions(username)
        context['label_review_idx'] = 1 if num_reviews == 0 else num_reviews
        return render(request, 'yelp/userlabelstat.html', context)


def show_review(request, username, user_rev_idx):
    beg_time = time()

    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('yelp:login'))
    if username != request.user.username:
        return HttpResponse('404')

    context = dict()
    context['username'] = request.user.username

    user_rev_idx = int(user_rev_idx)
    r = reviewdata.get_review_for_user(username, user_rev_idx)
    if not r:
        user_num_mentions = reviewdata.get_user_num_mentions(username)
        context['user_num_mentions'] = user_num_mentions
        return render(request, 'yelp/nomorereviews.html', context)

    user_rev_idx, review_info, mentions = r
    print len(mentions)
    rev_biz = reviewdata.get_business(review_info['business_id'])

    context['mentions'] = mentions
    context['num_mentions'] = len(mentions)
    context['reviewed_biz'] = rev_biz
    label_results = reviewdata.get_label_results(mentions, request.user.username)
    context['highlighted_review'] = reviewdata.highlight_mentions(review_info['text'], mentions, label_results)
    context['mention_candidates'] = reviewdata.get_candidates_of_mentions(mentions, review_info, rev_biz,
                                                                          label_results)

    context['user_rev_idx'] = user_rev_idx
    context['next_rev_idx'] = user_rev_idx + 1
    context['prev_rev_idx'] = 1 if user_rev_idx == 1 else user_rev_idx - 1

    elp = time() - beg_time
    # if elp > 1:
    print elp, username, user_rev_idx

    return render(request, 'yelp/review.html', context)


def label(request, user_rev_idx):
    tbeg = time()
    reviewdata.update_label_result(request.user.username, request.POST)
    # return HttpResponse('OK' + rev_idx)
    print time() - tbeg
    return HttpResponseRedirect(reverse('yelp:review', args=(request.user.username, user_rev_idx,)))


def delete_label(request, user_rev_idx, mention_id):
    reviewdata.delete_label_result(mention_id, request.user.username)
    return HttpResponseRedirect(reverse('yelp:review', args=(request.user.username, user_rev_idx,)))


def search_candidates(request):
    mention_id = request.POST['mention_id']
    biz_name = request.POST['query_name']
    biz_city = request.POST['query_city']
    biz_addr = request.POST['query_addr']
    # reviewed_city = request.POST['reviewed_biz_city']
    candidates = reviewdata.search_candidates_es(biz_name, biz_city, biz_addr)
    context = {
        'mention_id': mention_id,
        'candidates': candidates,
        "candidate_type": "search"
    }
    return render(request, 'yelp/candidates.html', context)


def logout(request):
    return auth_views.logout(request, next_page=reverse('yelp:login'))
