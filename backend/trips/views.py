import logging

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .service import build_trip_plan
from .serializers import TripRequestSerializer

logger = logging.getLogger(__name__)


@api_view(["POST"])
def plan_trip(request):
    serializer = TripRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        return Response(build_trip_plan(serializer.validated_data))
    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.exception("Trip planning failed")
        return Response(
            {"error": f"Trip planning failed: {e}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
def health(request):
    return Response({"status": "ok", "service": "track-log-api"})
