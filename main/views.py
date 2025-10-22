from django.shortcuts import render
import csv
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.db import transaction
from django.http import JsonResponse, HttpResponseNotAllowed

from .models import Venue

# Create your views here.
def show_main(request):
    context = {
    }

    return render(request, "main.html", context)


CSV_RELATIVE_PATH = Path("data") / "venues - courts_enriched_data.csv"  # sesuaikan nama file

def _parse_hhmm(s: str):
    if not s:
        return None
    s = s.strip()
    # CSV kamu konsisten "H:MM" atau "HH:MM"
    return datetime.strptime(s, "%H:%M").time()

# @staff_member_required TODO aktifkan kalau udah siap
def import_venues_from_csv(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    csv_path = Path(settings.BASE_DIR) / CSV_RELATIVE_PATH
    if not csv_path.exists():
        return JsonResponse({"ok": False, "error": f"CSV not found at {csv_path}"}, status=400)

    created = updated = skipped = errors = 0

    with transaction.atomic():
        try:
            with open(csv_path, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                expected = ["name","category","address","price","capacity","opening_time","closing_time","time","thumbnail"]
                # cek header minimal
                missing = [h for h in expected if h not in reader.fieldnames]
                if missing:
                    return JsonResponse({"ok": False, "error": f"Missing columns: {missing}"}, status=400)

                for i, row in enumerate(reader, start=2):
                    try:
                        name = row["name"].strip()
                        if not name:
                            skipped += 1
                            continue

                        # lookup kunci duplikasi sederhana
                        address = (row.get("address") or "").strip()
                        lookup = {"name": name}
                        if address:
                            lookup["address"] = address

                        defaults = {
                            "category": (row.get("category") or "").strip(),
                            "price": int(row["price"]) if row.get("price") not in (None, "",) else None,
                            "capacity": int(row["capacity"]) if row.get("capacity") not in (None, "",) else None,
                            "opening_time": _parse_hhmm(row.get("opening_time")),
                            "closing_time": _parse_hhmm(row.get("closing_time")),
                            "time_display": (row.get("time") or "").strip(),
                            "thumbnail": (row.get("thumbnail") or "").strip(),
                        }
                        if address:
                            defaults["address"] = address

                        obj, is_created = Venue.objects.update_or_create(**lookup, defaults=defaults)
                        if is_created:
                            created += 1
                        else:
                            updated += 1

                    except Exception:
                        errors += 1
                        # lanjut baris berikutnya, kita tidak rollback seluruhnya
                        continue

        except Exception as e:
            transaction.set_rollback(True)
            return JsonResponse({"ok": False, "error": str(e)}, status=500)

    return JsonResponse({"ok": True, "stats": {"created": created, "updated": updated, "skipped": skipped, "errors": errors}}, status=200)
