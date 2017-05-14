from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse

import reviewdisp


def index(request):
    return HttpResponse("Hello, world. You're at the yelp index.")


def show_review(request, rev_idx):
    rev_idx = int(rev_idx)
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('login'))

    context = dict()
    context['username'] = request.user.username

    review_info = reviewdisp.get_review(rev_idx)
    rev_biz = reviewdisp.get_business(review_info['business_id'])
    context['reviewed_biz'] = rev_biz
    context['highlighted_review'] = reviewdisp.get_review_text_disp_html(review_info)

    candidates_html = reviewdisp.get_candidates_disp_html(review_info, rev_biz)
    # candidates_html = None
    context['candidates_html'] = candidates_html

    context['next_rev_idx'] = rev_idx + 1
    context['prev_rev_idx'] = 1 if rev_idx == 1 else rev_idx - 1
    return render(request, 'yelp/review.html', context)
