from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse

import reviewdata


def index(request):
    return HttpResponse("Hello. You're at the yelp index.")


def show_review(request, rev_idx):
    rev_idx = int(rev_idx)
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('login'))

    context = dict()
    context['username'] = request.user.username

    review_info = reviewdata.get_review(rev_idx)
    rev_biz = reviewdata.get_business(review_info['business_id'])
    mentions = reviewdata.get_mentions_of_review(review_info['review_id'])

    context['mentions'] = mentions
    context['reviewed_biz'] = rev_biz
    label_results = reviewdata.get_label_results(mentions, request.user.username)
    context['highlighted_review'] = reviewdata.get_review_text_disp_html(review_info)
    context['mention_candidates'] = reviewdata.get_candidates_of_mentions(mentions, review_info, rev_biz,
                                                                          label_results)

    context['rev_idx'] = rev_idx
    context['next_rev_idx'] = rev_idx + 1
    context['prev_rev_idx'] = 1 if rev_idx == 1 else rev_idx - 1
    return render(request, 'yelp/review.html', context)


def label(request, rev_idx):
    reviewdata.update_label_result(request.user.username, request.POST)
    # return HttpResponse('OK' + rev_idx)
    return HttpResponseRedirect(reverse('yelp:review', args=(rev_idx,)))


def delete_label(request, rev_idx, mention_id):
    reviewdata.delete_label_result(mention_id, request.user.username)
    return HttpResponseRedirect(reverse('yelp:review', args=(rev_idx,)))


def search_candidates(request):
    mention_id = request.POST['mention_id']
    search_text = request.POST['search_text']
    # reviewed_city = request.POST['reviewed_biz_city']
    candidates = reviewdata.search_candidates_es(search_text)
    context = {
        'mention_id': mention_id,
        'candidates': candidates,
        "candidate_type": "search"
    }
    return render(request, 'yelp/candidates.html', context)


def test(request):
    return render(request, 'yelp/test.html')


def test_aj(request):
    print request.GET.keys()
    print request.POST.keys()
    curname = request.POST['name']
    res_html = '<input type="radio" name="tradio" value="r%s"> R%s' % (curname, curname)
    return HttpResponse(res_html)


def test_sub(request):
    print request.POST.keys()
    print request.POST['tradio']
    return HttpResponse('SUb')
