# Docker example

An image derived from `apache/superset:6.1.0` with these translations added, and the
`superset_config.py` settings that make them work, **including embedded dashboards
(guest token) on 6.1.0**. In a real deployment, add the same `COPY`/`RUN` lines to
your own image and merge `superset_config_i18n.py` into your `superset_config.py`.

## 1. Get the built translations

Either unpack a release zip (it contains `superset/translations/<lang>/LC_MESSAGES/`):

```sh
mkdir -p build-context && unzip superset-translations-6.1.0-all.1.zip -d build-context
```

or build them from this repository (see CONTRIBUTING.md); the result is in `dist/6.1.0/`.

## 2. Build the image

```sh
# Serbian Cyrillic under "sr" (default)
docker build -f docker/Dockerfile -t superset-bcms:6.1.0 dist/6.1.0

# Serbian Latin under "sr" (the only way to get a Latin UI on 6.1.0)
docker build -f docker/Dockerfile --build-arg SERBIAN_SCRIPT=latin -t superset-bcms:6.1.0-latin dist/6.1.0
```

The Dockerfile finds Superset's translations directory from the installed package (in
the official 6.1.0 image: `/app/superset/translations`, which ships only `.po` files)
and only adds files.

## 3. Configure Superset

Merge `docker/superset_config_i18n.py` into your `superset_config.py`. The official
image reads `superset_config.py` from `/app/pythonpath` (on `PYTHONPATH`), or from the
file named by `SUPERSET_CONFIG_PATH`. It sets:

- `LANGUAGES` (6.1.0 ships with `{}`, which turns translations off) and
  `BABEL_DEFAULT_LOCALE = "sr"`: the language for everyone who has not picked one,
  including embedded (guest token) users.
- `FLASK_APP_MUTATOR`: serves `/superset/language_pack/<lang>/` without login.
  On 6.1.0 the embedded page fetches that file without the guest token, the endpoint
  requires login, and the dashboard silently falls back to English
  (apache/superset#42433). Upstream made the endpoint public in Superset 7.0
  (apache/superset#42438); the hook does the same from the config, no Superset patch
  or frontend build needed. It also stops browsers from caching the pack for a year,
  so translation updates show up. If you already have a `FLASK_APP_MUTATOR`, call
  `_public_language_pack(app)` from it.

To choose the language per embedded user instead of using the default, pass it from
your application through the embedded SDK:

```js
embedDashboard({ id, supersetDomain, mountPoint, fetchGuestToken,
  dashboardUiConfig: { urlParams: { _l_: "sr" } } });   // any code in LANGUAGES
```

## 4. Test locally (embedded dashboard with a guest token)

```sh
cp docker/test.env.example docker/test.env    # set a secret key and an admin password
docker run -d --name superset-bcms -p 127.0.0.1:8088:8088 --env-file docker/test.env \
  -v "$PWD/docker/superset_config_i18n.py:/app/pythonpath/superset_config_i18n.py:ro" \
  -v "$PWD/docker/test/superset_config.py:/app/pythonpath/superset_config.py:ro" \
  superset-bcms:6.1.0
docker exec superset-bcms superset db upgrade
docker exec superset-bcms sh -c 'superset fab create-admin --username admin --firstname Admin --lastname User --email admin@example.com --password "$ADMIN_PASSWORD"'
docker exec superset-bcms superset init
docker exec -i superset-bcms python - < docker/test/create_embedded.py   # prints UUID=... and TOKEN=...
```

`docker/test/superset_config.py` enables embedding and turns Talisman and CSRF off:
local testing only. Serve `docker/test/host.html` from another port next to the
embedded SDK bundle (`npm install @superset-ui/embedded-sdk`, copy
`bundle/index.js` to `embedded-sdk/index.js`), then open
`http://localhost:8000/host.html#<UUID>,<TOKEN>`.

**Tested on 6.1.0 (2026-11-27):** with the hook, a dashboard embedded with a guest
token showed the empty-dashboard message and the dashboard menu in Serbian Cyrillic,
and in Latin with `SERBIAN_SCRIPT=latin`; without it, the pack request was redirected
to `/login/`. Not yet tested: dashboards with charts and native filters. Labels that
Superset creates while the page is still loading may stay in English on 6.1.0 (fixed
upstream in apache/superset#40729).

## Limitations on Superset 6.1.0

- **sr_Latn does not work as its own language.** The page bootstrap passes only the
  base language (`sr`) to the frontend, and `/superset/language_pack/` accepts only
  codes like `sr` or `pt_BR`. Use `SERBIAN_SCRIPT=latin` to serve Latin script under
  `sr`. Both scripts at once need Superset 7.0.
