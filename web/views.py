from django.shortcuts import render, render_to_response
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import cache_page
from apis import views
from django.http import HttpResponse
from datetime import datetime


def labs(request):
    book_list = views.get_shop()
    # book_list = []
    return render(request, 'labs.html', {'book_list': book_list})


def terms(request):
    return render(request, 'terms.html')


@cache_page(60 * 1)
def main(request):
    ratings = views.approval_rating_list(None, True)
    cheerings = views.get_cheering_message_list(0)
    return render(request, 'main.html', {'ratings': ratings, 'cheering_list': cheerings, 'today': datetime.today()})


def lets_encrypt(request, authorization_code):
    return render(request, 'lets_encrypt.html',
                  {'lets_encrypt_authorization_code': 'RFUcoJwfCni-GMuQEDFpKaXIrd3gwS9ZJ45FcF8dGvQ._wy1NPw2PM2-Tj2pxrj4JuyU2iCElWaebHkUZVAerkY'})


def google_app_engine_health_check(req):
    return HttpResponse(status=200)


@csrf_exempt
def cheering(request):
    if request.method == 'POST':
        views.create_cheering_message(request)

    page = request.GET.get('page', None)
    if page is None:
        page = 0
    else:
        page = int(page)

    lists = views.get_cheering_message_list(page)
    return render_to_response('cheering_table.html', {'cheering_list': lists, 'today': datetime.today()})


@cache_page(60 * 10)
@csrf_exempt
def rating(request):
    if request.method == 'POST':
        ratings = views.lucky_rating_list()
        return render_to_response('rating.html', {'ratings': ratings})
    else:
        return HttpResponse(status=404)


@csrf_exempt
def pledge(request):
    if request.method == 'GET':
        type = request.GET.get('type', None)
        if type == 'rank':
            results = views.pledge_rank_list()
            return render_to_response('pledge_rank_modal.html', {'pledge_rank_list': results})
    else:
        results = views.pledge_post(request)
        return render_to_response('pledge_result.html', {'results': results})


@csrf_exempt
def constellation_chemistry(request):
    if request.method == 'POST':
        results = views.constellation_post(request)
        return render_to_response('constellation_modal.html', {'constellation_result': results})


@csrf_exempt
def slot(request):
    if request.method == 'POST':
        result = views.save_lucky_result(request)
        return render_to_response('slot_modal.html', {'lucky': result})


@csrf_exempt
def luckyname(request):
    result = views.lucky_name(request)
    print(result)
    return render_to_response('lucky_name_modal.html', result)


@cache_page(60 * 10)
@csrf_exempt
def keyword(request):
    result = views.get_issue_keyword_list(request.GET.get('date', None))
    print(result)
    if len(result) > 0:
        return render_to_response('keyword.html', {'results': result[0]['items']})
    else:
        return render_to_response('keyword.html', {'results': []})


@cache_page(60 * 10)
@csrf_exempt
def news(request):
    if request.method == 'POST':
        news_list = views.get_news_list(request)
        return render_to_response('keyword_modal.html', {'results': news_list})
