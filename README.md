# superset-i18n-bcms

Unofficial Serbian, Croatian and Bosnian UI translations for
[Apache Superset](https://github.com/apache/superset).

> **Status: in progress.** Serbian (Cyrillic and Latin) for Superset 6.1.0 can be
> installed (see [Install](#install)); 271 of its strings are machine drafts awaiting
> native review. Croatian and Bosnian are not translated yet. No release has been
> published yet.

## What this is

Drop-in `.po` catalogs, laid out exactly like upstream
`superset/translations/<lang>/LC_MESSAGES/`, so they can be installed into a
Superset image and later submitted upstream unchanged.

| Language              | Locale code     | Script   | Variant    | Notes |
|-----------------------|-----------------|----------|------------|-------|
| Serbian (Latin)       | `sr_Latn`       | Latin    | ekavian    | Source catalog for Serbian; same code as upstream |
| Serbian (Cyrillic)    | `sr`            | Cyrillic | ekavian    | Generated from `sr_Latn`, never edited by hand |
| Croatian              | `hr`            | Latin    | ijekavian  | |
| Bosnian               | `bs`            | Latin    | ijekavian  | |
| Montenegrin           | deferred        | Latin    | ijekavian  | `cnr` does not work with Babel (it maps to `sr_Latn_ME`) |

## Supported Superset versions

| Superset | Catalog path                                  |
|----------|-----------------------------------------------|
| 6.1.0    | `versions/6.1.0/superset/translations/<lang>/` |

## Install

Installing a language takes three things: the built files in Superset's translations
directory, a few lines in `superset_config.py`, and a restart. Nothing in Superset is
patched and the frontend is not rebuilt. The steps below are for **Superset 6.1.0**
(check with `superset version`).

### 1. Get the built files

Each language needs three files in `<lang>/LC_MESSAGES/`: `messages.mo` (server-side
strings), `messages.json` (browser strings) and `messages.po` (source). Superset's
Docker image ships only `.po` files, so the other two must come from here.

- **Release zip** (once releases exist): attached to each
  [GitHub release](https://github.com/maksimprivalov/superset-i18n-bcms/releases), with
  tags like `6.1.0-sr_Latn.1` (one language) or `6.1.0-all.2` (all languages).
- **Latest CI build** (needs a GitHub login, kept for 7 days):
  ```sh
  gh run download --repo maksimprivalov/superset-i18n-bcms -n translations-6.1.0 -D build-context
  ```
- **Build from source**: see [CONTRIBUTING.md](CONTRIBUTING.md); the result is in
  `dist/6.1.0/`.

All three contain the same tree: `superset/translations/<lang>/LC_MESSAGES/`.

### 2. Choose the folder to install

| You want                 | Install this folder | Under the name |
|--------------------------|---------------------|----------------|
| Serbian, Cyrillic script | `sr`                | `sr`           |
| Serbian, Latin script    | `sr_Latn`           | `sr`           |

On 6.1.0 the frontend always asks for the base language code, so Latin script must be
installed under `sr`, and you cannot offer both scripts at once (Superset 7.0 can).
Croatian (`hr`) and Bosnian (`bs`) are not available yet.

### 3. Put the files in Superset's translations directory

The target is `<superset package>/translations/sr/LC_MESSAGES/`. In the official Docker
image that is **`/app/superset/translations/sr/`**. For any other install, find it with:

```sh
python -c "import os, superset; print(os.path.join(os.path.dirname(superset.__file__), 'translations'))"
```

- **Docker / docker compose, no rebuild:** mount the folder read-only into **every**
  service that runs the Superset image (web app, Celery worker and beat, init). Make the
  files world-readable (`chmod -R a+rX`): the image runs as user `superset`.
  ```yaml
  volumes:
    - ./build-context/superset/translations/sr:/app/superset/translations/sr:ro
  ```
  Copying into a running container (`docker cp`) is lost when the container is recreated.
- **Docker, your own image:** add the `COPY`/`RUN` lines from
  [docker/Dockerfile](docker/Dockerfile), which also handles the Latin variant
  (`--build-arg SERBIAN_SCRIPT=latin`). Kubernetes/Helm: use that image.
- **pip / virtualenv:** copy the folder into the directory printed above. Reinstalling or
  upgrading Superset removes it, so copy it again afterwards.

### 4. Configure Superset

Copy [docker/superset_config_i18n.py](docker/superset_config_i18n.py) next to your
`superset_config.py` (any folder on Superset's `PYTHONPATH`; `/app/pythonpath` in the
official image) and add this line at the **end** of `superset_config.py`:

```python
from superset_config_i18n import *  # noqa: F401,F403
```

It sets:

- `LANGUAGES` with English and Serbian. Superset 6.1.0 ships with `LANGUAGES = {}`,
  which turns translations off. For the Latin variant, change the name to `"Srpski"`.
- `BABEL_DEFAULT_LOCALE = "sr"`: the language for everyone who has not picked one,
  including embedded dashboards. Keep `"en"` if only some users should get Serbian;
  they can switch in the language menu.
- `FLASK_APP_MUTATOR`: makes embedded dashboards (guest token) translate on 6.1.0, see
  [Known limitations](#known-limitations).

If your config already defines `LANGUAGES` or `FLASK_APP_MUTATOR`, the import
replaces them. Add the `"sr"` entry to your own `LANGUAGES` instead, and call the hook
from your own mutator:

```python
from superset_config_i18n import _public_language_pack

def FLASK_APP_MUTATOR(app):
    ...  # your existing code
    _public_language_pack(app)
```

### 5. Restart and check

Restart all Superset processes. Then, **without** logging in:

```sh
curl -s -o /dev/null -w '%{http_code}\n' https://<superset-host>/superset/language_pack/sr/
```

`200` means it works. `302` (redirect to `/login/`) means the hook is not loaded (the
import line is missing, or a later `FLASK_APP_MUTATOR` replaced it) or the files are not
in `translations/sr/LC_MESSAGES/`.

### Embedded dashboards

With `BABEL_DEFAULT_LOCALE = "sr"`, embedded dashboards are in Serbian; nothing changes in
the host application or in how it creates guest tokens. To choose the language per embed
instead, pass it through the embedded SDK (not tested yet):

```js
embedDashboard({ id, supersetDomain, mountPoint, fetchGuestToken,
  dashboardUiConfig: { urlParams: { _l_: "sr" } } });
```

### Updating and removing

- **Update:** replace the files and restart. Browsers pick up the new strings on the
  next page load, because the hook stops them from caching the pack.
- **Remove:** delete the import line and the files (or the volume), restart.
- **After upgrading to Superset 7.0:** remove the `FLASK_APP_MUTATOR` hook; 7.0 serves the
  language pack to embedded dashboards by itself.

To try everything locally first, see [docker/README.md](docker/README.md).

## Review status

See [REVIEW_STATUS.md](REVIEW_STATUS.md). Machine-drafted strings are marked
`#, fuzzy` until a native speaker reviews them. Superset serves fuzzy strings,
so drafts are visible in the UI.

## Known limitations

- **Embedded dashboards on Superset 6.1.0 need a config hook.** Out of the box they
  stay in English whatever locale is set
  ([apache/superset#42433](https://github.com/apache/superset/issues/42433)): the
  embedded page fetches the language pack without the guest token, and 6.1.0 requires
  login for it. The fix ([apache/superset#42438](https://github.com/apache/superset/pull/42438))
  is in the 7.0.0 release candidates. On 6.1.0, the `FLASK_APP_MUTATOR` in
  [docker/superset_config_i18n.py](docker/superset_config_i18n.py) does the same from
  `superset_config.py`; tested with a guest-token embedded dashboard, see
  [docker/README.md](docker/README.md).
- **Serbian Latin (`sr_Latn`) cannot be its own language on 6.1.0**: the frontend
  always asks for the base language (`sr`). Serve the Latin files under `sr` instead
  (see docker/README.md); 7.0 supports `sr_Latn` directly.

## License

Apache License 2.0. See [LICENSE](LICENSE) and [NOTICE](NOTICE). This project is
not affiliated with or endorsed by the Apache Software Foundation.

---

## Srpski (ukratko)

Nezvanični prevodi korisničkog interfejsa Apache Superseta na srpski (latinica i
ćirilica), hrvatski i bosanski. Projekat je u pripremi: srpski za Superset 6.1.0
može da se instalira, hrvatski i bosanski još nisu prevedeni. Mašinski prevedeni
nizovi su označeni kao `fuzzy` dok ih ne pregleda izvorni govornik.

Instalacija ukratko (detalji u odeljku [Install](#install)): folder `sr` (ćirilica) ili
`sr_Latn` (latinica, instalira se pod imenom `sr`) ide u
`/app/superset/translations/sr/` u svim Superset kontejnerima; fajl
`docker/superset_config_i18n.py` ide pored `superset_config.py`, a na kraj
`superset_config.py` se dodaje `from superset_config_i18n import *`; zatim restart.
Tako su na srpskom i ugrađene (embedded) kontrolne table u verziji 6.1.0
(apache/superset#42433).
