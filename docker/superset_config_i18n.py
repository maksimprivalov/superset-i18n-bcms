# Language settings for the superset-i18n-bcms translations (Superset 6.1.0).
# Merge these lines into your own superset_config.py (they are not a full config).
#
# Superset 6.1.0 ships with LANGUAGES = {}, which turns translations off. Users pick
# a language from the language menu (kept per session); before that, everyone sees
# BABEL_DEFAULT_LOCALE. The browser's Accept-Language header is not used. A page can
# also force a language with the URL argument ?_l_=<code> (any code in LANGUAGES);
# for embedded dashboards pass it through the embedded SDK:
#   embedDashboard({ ..., dashboardUiConfig: { urlParams: { _l_: "sr" } } })

import os
import re

LANGUAGES = {
    "en": {"flag": "us", "name": "English"},
    # Serbian. On 6.1.0 use the "sr" code for both scripts: build the image with
    # SERBIAN_SCRIPT=latin for Latin script, and rename this entry to "Srpski".
    "sr": {"flag": "rs", "name": "Српски"},
    # Superset 7.0+ only (6.1.0 cannot load the sr_Latn frontend pack):
    # "sr_Latn": {"flag": "rs", "name": "Srpski (latinica)"},
    # Not translated yet:
    # "hr": {"flag": "hr", "name": "Hrvatski"},
    # "bs": {"flag": "ba", "name": "Bosanski"},
}

# Language shown before a user picks one, and for embedded (guest token) users.
BABEL_DEFAULT_LOCALE = "sr"


# Embedded dashboards on 6.1.0: the embedded page fetches /superset/language_pack/<lang>/
# without the guest token, and 6.1.0 protects that endpoint with @has_access, so guests
# are redirected to /login/ and the dashboard falls back to English
# (apache/superset#42433). Upstream made the endpoint public in apache/superset#42438
# (Superset 7.0). This hook does the same on 6.1.0 without patching Superset: it serves
# the (non-sensitive) language pack JSON for any GET request, using the same language
# code check and file location as the original view, and lets browsers revalidate it
# instead of caching it for a year. Remove it after upgrading to 7.0.
# If you already define FLASK_APP_MUTATOR, call _public_language_pack(app) from yours.
_LANGUAGE_PACK_PATH = re.compile(r"(?:^|/)superset/language_pack/([a-z]{2,3}(?:_[A-Z]{2})?)/$")


def _public_language_pack(app):
    from flask import request, send_file

    import superset

    translations_dir = os.path.join(os.path.dirname(superset.__file__), "translations")

    @app.before_request
    def serve_language_pack_without_login():
        if request.method != "GET":
            return None
        match = _LANGUAGE_PACK_PATH.search(request.path)
        if not match:
            return None
        path = os.path.join(translations_dir, match.group(1), "LC_MESSAGES", "messages.json")
        if not os.path.isfile(path):
            return None  # let Superset answer (404 / login) as usual
        # max_age=0: browsers revalidate (ETag/Last-Modified, usually a 304) instead of
        # keeping the pack for a year (SEND_FILE_MAX_AGE_DEFAULT), so updated
        # translations reach users without a cache flush.
        return send_file(path, mimetype="application/json", max_age=0)


def FLASK_APP_MUTATOR(app):
    _public_language_pack(app)
