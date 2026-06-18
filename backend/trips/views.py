from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .hos_engine import HOSEngine
from .routing import build_full_route, geocode
from .serializers import TripRequestSerializer


@api_view(["POST"])
def plan_trip(request):
    serializer = TripRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data
    try:
        current = geocode(data["current_location"])
        pickup = geocode(data["pickup_location"])
        dropoff = geocode(data["dropoff_location"])
        legs, total_miles, _ = build_full_route(current, pickup, dropoff)

        engine = HOSEngine(cycle_used=data["cycle_used_hours"])
        plan = engine.plan_trip(current, pickup, dropoff, legs, total_miles)

        result = plan.to_dict()
        result["locations"] = {
            "current": current,
            "pickup": pickup,
            "dropoff": dropoff,
        }
        result["legs"] = [
            {"from": l["from"], "to": l["to"], "miles": round(l["miles"], 1)} for l in legs
        ]
        return Response(result)
    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": f"Trip planning failed: {e}"}, status=status.HTTP_502_BAD_GATEWAY)


@api_view(["GET"])
def health(request):
    return Response({"status": "ok", "service": "track-log-api"})
