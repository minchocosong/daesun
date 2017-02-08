from apis.models import Scraps, Keywords, Pledge
from django.http import HttpResponse
from django.db.models import Count
from django.db.models import Q, Case, When, Sum, F
from urllib import parse, request
from django.core.serializers.json import DjangoJSONEncoder
from django.views.decorators.csrf import csrf_exempt
import json
import os
import pylibmc
from .util import hangle
from datetime import datetime, timedelta


def get_memcache_client():
    # Environment variables are defined in app.yaml.
    # Note: USE_GAE_MEMCACHE is in whitelist-only alpha. See README.md
    if os.environ.get('USE_GAE_MEMCACHE'):
        memcache_server = ':'.join([
            os.environ.get('GAE_MEMCACHE_HOST', 'localhost'),
            os.environ.get('GAE_MEMCACHE_PORT', '11211')])
    else:
        memcache_server = os.environ.get('MEMCACHE_SERVER', 'localhost:11211')

    memcache_client = pylibmc.Client([memcache_server], binary=True)

    return memcache_client


def index(req):
    scraps = Scraps.objects.all().values('title', 'cp', 'created_at').order_by('-created_at')[0:100]
    return HttpResponse(json.dumps(list(scraps), cls=DjangoJSONEncoder), content_type='application/json; charset=utf-8')


candidate_q_list = (Q(title__contains='문재인') | Q(title__contains='안철수') | Q(title__contains='이재명') |
            Q(title__contains='유승민') | Q(title__contains='안희정') | Q(title__contains='황교안') |
            Q(title__contains='남경필'))


def cp_group(req):
    cache_key = 'cp_group_result'
    client = get_memcache_client()
    result = client.get(cache_key)

    if result is None:
        group_list = Scraps.objects.filter(candidate_q_list).values('cp').annotate(
            moon=Count(Case(When(title__contains='문재인', then=1))),
            ahn=Count(Case(When(title__contains='안철수', then=1))),
            lee=Count(Case(When(title__contains='이재명', then=1))),
            you=Count(Case(When(title__contains='유승민', then=1))),
            hee=Count(Case(When(title__contains='안희정', then=1))),
            hwang=Count(Case(When(title__contains='황교안', then=1))),
            nam=Count(Case(When(title__contains='남경필', then=1)))
        )

        print(group_list.query)
        result = json.dumps(list(group_list))
        client.add(key=cache_key, val=result, time=600)
        print('memcache not hit')

    return HttpResponse(result, content_type='application/json; charset=utf-8')


def cp_daily(req):
    cache_key = 'cp_daily_result'
    client = get_memcache_client()
    result = client.get(cache_key)

    if result is None:
        daily_list = Scraps.objects.filter(candidate_q_list).extra({'date': 'date(created_at)'}).values('date').annotate(
            moon=Count(Case(When(title__contains='문재인', then=1))),
            ahn=Count(Case(When(title__contains='안철수', then=1))),
            lee=Count(Case(When(title__contains='이재명', then=1))),
            you=Count(Case(When(title__contains='유승민', then=1))),
            hee=Count(Case(When(title__contains='안희정', then=1))),
            hwang=Count(Case(When(title__contains='황교안', then=1)),
            nam=Count(Case(When(title__contains='남경필', then=1))))
        )

        result = json.dumps(list(daily_list), cls=DjangoJSONEncoder)
        client.add(key=cache_key, val=result, time=600)

    return HttpResponse(result, content_type='application/json; charset=utf-8')


def shop(req):
    client_id = "cC0cf4zyUuLFmj_kKUum"
    client_secret = "EYop6SBs44"
    # 추후 parameter 로 변경
    enc_text = parse.quote("문재인")
    # json 결과
    url = "https://openapi.naver.com/v1/search/book.json?query=" + enc_text

    send_request = request.Request(url)
    send_request.add_header("X-Naver-Client-Id", client_id)
    send_request.add_header("X-Naver-Client-Secret", client_secret)
    response = request.urlopen(send_request)
    code = response.getcode()

    if code == 200:
        response_body = response.read()
        print(response_body.decode('utf-8'))
        return HttpResponse(response_body, content_type='application/json; charset=utf-8')

    else:
        print("Error Code:" + code)
        return HttpResponse(status=code)


def pledge_rank(req):
    cache_key = 'pledge_rank'
    client = get_memcache_client()
    result = client.get(cache_key)

    if result is None:
        pledges = Pledge.objects.annotate(score=Sum(F('like')-F('unlike'))).order_by('-score')[0:10]
        result = json.dumps(list(pledges.values()), cls=DjangoJSONEncoder)
        client.add(key=cache_key, val=result, time=60)

    return HttpResponse(result, content_type='application/json; charset=utf-8')


def pledge(req):
    pledge_obj = Pledge.objects.annotate(score=Sum(F('like')+F('unlike'))).order_by('score')[0:1]
    pledges = list(pledge_obj.values())
    print(pledges)
    return HttpResponse(json.dumps(pledges[0], cls=DjangoJSONEncoder), content_type='application/json; charset=utf-8')


@csrf_exempt
def pledge_evaluation(req, id):
    if req.method == 'POST':
        body = json.loads(req.body)
        type = body.get('type', None)
        if type:
            if type == 'like':
                Pledge.objects.filter(id=id).update(like=F('like') + 1)
            elif type == 'unlike':
                Pledge.objects.filter(id=id).update(unlike=F('unlike') + 1)
            else:
                return HttpResponse(status=400, content_type='application/json; charset=utf-8')
    else:
        return HttpResponse(status=400, content_type='application/json; charset=utf-8')

    return HttpResponse(status=200, content_type='application/json; charset=utf-8')


@csrf_exempt
def name_chemistry(req):
    if req.method == 'GET':
        name1 = req.GET.get('name1', None)
        name2 = req.GET.get('name2', None)

    elif req.method == 'POST':
        body = json.loads(req.body)
        name1 = body.get('name1', None)
        name2 = body.get('name2', None)
    else:
        return HttpResponse(status=400)

    if name1 is None or name2 is None:
        return HttpResponse(status=400)

    if len(name1) == 3 and len(name2) == 3:
        result = hangle.name_chemistry(name1, name2)
    else:
        result = 0

    return HttpResponse(json.dumps({'score': result}), content_type='application/json; charset=utf-8')


def timeline(req):
    cache_key = 'timeline_result'
    client = get_memcache_client()
    result = client.get(cache_key)

    if result is None:
        item_list = Keywords.objects.values('candidate', 'created_at').annotate(Count('candidate'), Count('created_at')).filter(created_at__gte=datetime.now() - timedelta(hours=3)).order_by('-created_at')

        for item in item_list:
            keywords = Keywords.objects.values('keyword').filter(candidate__contains=item['candidate']).filter(created_at__contains=item['created_at'])
            keyword_list = []
            for k in keywords:
                inner_item = {}
                inner_item['keyword'] = k['keyword']
                scraps = [scraps for scraps in Scraps.objects.values('title', 'link', 'cp', 'created_at').filter(title__contains=item['candidate']).filter(title__contains=k['keyword'])[:5]]
                inner_item['news'] = scraps
                keyword_list.append(inner_item)
            item['keywords'] = keyword_list

            result = json.dumps(list(item_list), cls=DjangoJSONEncoder)
            client.add(key=cache_key, val=result, time=600)
            print('memcache not hit')

    return HttpResponse(result, content_type='application/json; charset=utf-8')
