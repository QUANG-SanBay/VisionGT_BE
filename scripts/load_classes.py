import json
from pathlib import Path
import yaml

from django.core.wsgi import get_wsgi_application
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "visionGT_BE.settings")
application = get_wsgi_application()

from traffic_signs.models import TrafficSign

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_YAML = BASE_DIR / "ai_engine" / "data.yaml"


def run():
    with DATA_YAML.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    names = data.get("names", [])
    for idx, name in enumerate(names):
        mcid = str(idx)
        obj, created = TrafficSign.objects.get_or_create(
            model_class_id=mcid,
            defaults={
                "sign_Code": name,
                "name": name,
                "category": "",
            },
        )
        if not created:
            # Ensure sign_Code/name stay in sync with dataset naming
            obj.sign_Code = obj.sign_Code or name
            obj.name = obj.name or name
            obj.save()
    print(f"Synced {len(names)} classes.")


if __name__ == "__main__":
    run()
