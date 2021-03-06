import logging
from datetime import datetime

from dateutil import parser
from django.conf import settings
from django.core.cache import caches
from django.http import HttpResponseRedirect

from affiliate.helpers import is_new_ip
from relish.helpers.request import get_client_ip

import metrics
from .tools import get_affiliate_param_name, remove_affiliate_code, \
    get_seconds_day_left, get_affiliate_model, get_affiliatestats_model

logger = logging.getLogger(__name__)

AFFILIATE_NAME = get_affiliate_param_name()
AFFILIATE_SESSION = getattr(settings, 'AFFILIATE_SESSION', True)
AFFILIATE_SESSION_AGE = getattr(settings, 'AFFILIATE_SESSION_AGE', 5 * 24 * 60 * 60)
AFFILIATE_SKIP_PATH = getattr(settings, 'AFFILIATE_SKIP_PATH_STARTS', [])

C_PFX = 'a_'

AffiliateModel = get_affiliate_model()
AffiliateModelStats = get_affiliatestats_model()


class AffiliateMiddleware(object):
    def process_request(self, request):
        aid = None
        session = request.session
        now = datetime.now()
        str_now = str(now)
        if request.method == 'GET':
            aid = request.GET.get(AFFILIATE_NAME, None)
            if aid:
                request.aid = aid
                if AFFILIATE_SESSION:
                    session['aid'] = aid
                    session['aid_dt'] = str_now
                    url = remove_affiliate_code(request.get_full_path())
                    metrics.bs_affiliate_new_counter.inc()
                    return HttpResponseRedirect(url)

            current_domain = request.get_host().split(':')[0]
            try:
                if current_domain in settings.PARTNERS_SETTINGS:
                    aid = settings.PARTNERS_SETTINGS[current_domain]['aid']
                    session['aid'] = aid
                    session['aid_dt'] = str_now
                    metrics.bs_affiliate_new_counter.inc()
            except BaseException as e:
                logger.warning(
                    "[affiliate][partner_domain] aid not found in partner settings, partner_domain: {}, "
                    "error: '{}'".format(current_domain, e)
                )
        if not aid and AFFILIATE_SESSION:
            aid = session.get('aid', None)
            if aid:
                aid_dt = parser.parse(session.get('aid_dt', None))
                if (now - aid_dt).total_seconds() > AFFILIATE_SESSION_AGE:
                    # aid expired
                    aid = None
                    session.pop('aid')
                    session.pop('aid_dt')
                    metrics.bs_affiliate_wrong_counter.inc()
        request.aid = aid

    def process_response(self, request, response):
        aid = getattr(request, "aid", None)
        if not aid:
            logger.error("[affiliate] error: aid not set")
        elif response.status_code == 200 and self.is_track_path(request.path):
            now = datetime.now()
            ip = get_client_ip(request)
            cache = caches['default']
            c_key = "".join((C_PFX, aid))
            ip_new, aid_ip_pool = is_new_ip(c_key, cache, ip)
            if ip_new:
                aid_ip_pool.add(ip)
                timeout = get_seconds_day_left(now)
                cache.set(c_key, aid_ip_pool, timeout)
            nb = AffiliateModelStats.objects.incr_count_views(aid, now,
                                                              ip_new=ip_new)
            if not nb:
                try:
                    aff = AffiliateModel.objects.get(aid=aid)
                    AffiliateModelStats.objects.create(affiliate=aff,
                                                       total_views=1, unique_visitors=1)
                except AffiliateModel.DoesNotExist:
                    logger.warning("[affiliate] error: Access with unknown affiliate code: {0}"
                                   .format(aid))
        return response

    def is_track_path(self, path):
        return len(filter(path.startswith, AFFILIATE_SKIP_PATH)) == 0

# TODO: attach lazy method to request: affiliate, that return Affiliate instance
