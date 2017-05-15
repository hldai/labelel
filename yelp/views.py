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
    mentions = reviewdisp.get_mentions_of_review(review_info['review_id'])

    context['mentions'] = mentions
    context['reviewed_biz'] = rev_biz
    context['highlighted_review'] = reviewdisp.get_review_text_disp_html(review_info)

    # candidates_html = reviewdisp.get_candidates_disp_html(review_info, rev_biz)
    # candidates_html = None
    # context['candidates_html'] = candidates_html
    context['mention_candidates'] = reviewdisp.get_candidates_of_mentions(mentions, rev_biz)

    context['next_rev_idx'] = rev_idx + 1
    context['prev_rev_idx'] = 1 if rev_idx == 1 else rev_idx - 1
    return render(request, 'yelp/review.html', context)


def label(request, rev_idx):
    print request.POST.keys()
    return HttpResponse('OK' + rev_idx)
    # return HttpResponseRedirect(reverse('yelp:results', args=(question.id,)))


def search_candidates(request):
    mention_id = request.POST['mention_id']
    search_text = request.POST['search_text']
    reviewed_city = request.POST['reviewed_biz_city']
    candidates = reviewdisp.search_candidates_es(search_text, reviewed_city)
    context = {
        'mention_id': mention_id,
        'candidates': candidates
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
