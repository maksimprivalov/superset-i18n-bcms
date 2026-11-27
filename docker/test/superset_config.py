# LOCAL TEST ONLY: the i18n snippet plus what an embedded-dashboard test needs.
# Never use these settings in production (Talisman and CSRF are off).
import os

from superset_config_i18n import *  # noqa: F401,F403

FEATURE_FLAGS = {"EMBEDDED_SUPERSET": True}
TALISMAN_ENABLED = False          # allow framing from the local host page
WTF_CSRF_ENABLED = False          # lets the test script call the guest-token API directly
PUBLIC_ROLE_LIKE = "Gamma"        # guest users get the Public role; give it read access
GUEST_ROLE_NAME = "Public"
GUEST_TOKEN_JWT_SECRET = os.environ["SUPERSET_SECRET_KEY"]
GUEST_TOKEN_JWT_EXP_SECONDS = 3600
