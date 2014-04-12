Affiliate system for django
===========================

Allows to track affiliate code. So it is possible to log this code at needed moment, for example when payments are made.

Example
-------

Visitor goes to site with affiliate code:

        http://site.com/?aid=12345

Now all urls, rendered using {% url_aff %} template tag will keep this code.

        {% url_aff 'news' %}

Will render automatically

        /news/?aid=12345


Requirements
-----------

- python (2.7)
- django (1.5, 1.6)


Quick start
-----------

1. Install this package to your python distribution

2. Add 'affiliate' to INSTALLED_APP in your settings.py:

        INSTALLED_APPS = [
            # ...
            'affiliate',
        ]

3. Add 'affiliate.context_processors.common' to TEMPLATE_CONTEXT_PROCESSORS in your settings.py:

        TEMPLATE_CONTEXT_PROCESSORS = (
            # ...
            'affiliate.context_processors.common',
        )

4. In your template load 'affiliate_urls' tags:

        {% load affiliate_urls %}

5. In your template use 'url_aff' instead of 'url' template tag:

        <a href="{% url_aff 'home' %}">Home</a>

6. Optional. Specify affiliate parameter name in settings.py:

    # Optional. Default is 'aid'
    AFFILIATE_PARAM_NAME = 'aid'

