"""LOCAL TEST ONLY: create an empty embeddable dashboard and a guest token.

Run inside the test container (see docker/README.md):
  docker exec -i superset-bcms python - < docker/test/create_embedded.py
Prints UUID=<embed uuid> and TOKEN=<guest token> for docker/test/host.html.
"""

import json
import logging

logging.disable(logging.CRITICAL)

from superset.app import create_app  # noqa: E402

app = create_app()
with app.app_context():
    from superset.extensions import db, security_manager
    from superset.models.dashboard import Dashboard
    from superset.models.embedded_dashboard import EmbeddedDashboard

    admin = security_manager.find_user("admin")
    position = {
        "DASHBOARD_VERSION_KEY": "v2",
        "ROOT_ID": {"type": "ROOT", "id": "ROOT_ID", "children": ["GRID_ID"]},
        "GRID_ID": {"type": "GRID", "id": "GRID_ID", "children": [], "parents": ["ROOT_ID"]},
        "HEADER_ID": {"type": "HEADER", "id": "HEADER_ID", "meta": {"text": "Test embedded"}},
    }
    dashboard = Dashboard(dashboard_title="Test embedded", published=True,
                          position_json=json.dumps(position), owners=[admin])
    db.session.add(dashboard)
    db.session.flush()
    embedded = EmbeddedDashboard(dashboard_id=dashboard.id, allow_domain_list="")
    db.session.add(embedded)
    db.session.commit()
    token = security_manager.create_guest_access_token(
        {"username": "guest", "first_name": "Gost", "last_name": "Korisnik"},
        [{"type": "dashboard", "id": str(embedded.uuid)}],
        [],
    )
    print(f"UUID={embedded.uuid}")
    print(f"TOKEN={token.decode() if isinstance(token, bytes) else token}")
