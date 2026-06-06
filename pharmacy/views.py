from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Pharmacy, PharmacyStaff, Medicine, Stock, Reservation
from .serializers import (
    PharmacySerializer,
    PharmacyStaffSerializer,
    MedicineSerializer,
    StockSerializer,
    ReservationSerializer
)

# =========================
# GENERIC CRUD API
# =========================
def generic_api(model_class, serializer_class):

    @api_view(['GET', 'POST', 'PUT', 'DELETE'])
    @permission_classes([IsAuthenticated])
    def api(request, pk=None):

        # ================= GET =================
        if request.method == 'GET':

            if pk:
                try:
                    obj = model_class.objects.get(pk=pk)
                except model_class.DoesNotExist:
                    return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)

                serializer = serializer_class(obj)
                return Response(serializer.data)

            # OPTIONAL SECURITY FILTER (staff only see own pharmacy data)
            if model_class == Stock or model_class == Reservation:
                try:
                    staff = request.user.staff_profile
                    objs = model_class.objects.filter(pharmacy=staff.pharmacy)
                except:
                    objs = model_class.objects.none()
            else:
                objs = model_class.objects.all()

            serializer = serializer_class(objs, many=True)
            return Response(serializer.data)

        # ================= POST =================
        if request.method == 'POST':

            serializer = serializer_class(
                data=request.data,
                context={'request': request}   # IMPORTANT FIX
            )

            if serializer.is_valid():
                instance = serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # ================= PUT =================
        if request.method == 'PUT':

            if not pk:
                return Response({"detail": "ID required"}, status=status.HTTP_400_BAD_REQUEST)

            try:
                obj = model_class.objects.get(pk=pk)
            except model_class.DoesNotExist:
                return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)

            serializer = serializer_class(
                obj,
                data=request.data,
                partial=True,
                context={'request': request}
            )

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # ================= DELETE =================
        if request.method == 'DELETE':

            if not pk:
                return Response({"detail": "ID required"}, status=status.HTTP_400_BAD_REQUEST)

            try:
                obj = model_class.objects.get(pk=pk)
                obj.delete()
                return Response({"detail": "Deleted"}, status=status.HTTP_204_NO_CONTENT)

            except model_class.DoesNotExist:
                return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    return api


# =========================
# APPROVE RESERVATION
# =========================
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def approve_reservation(request, pk):

    try:
        reservation = Reservation.objects.get(pk=pk)
    except Reservation.DoesNotExist:
        return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    if reservation.status != 'pending':
        return Response(
            {"detail": "Only pending reservations can be approved"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        stock = Stock.objects.get(
            pharmacy=reservation.pharmacy,
            medicine=reservation.medicine
        )
    except Stock.DoesNotExist:
        return Response({"detail": "Stock not found"}, status=status.HTTP_400_BAD_REQUEST)

    if stock.quantity < reservation.quantity:
        return Response({"detail": "Not enough stock"}, status=status.HTTP_400_BAD_REQUEST)

    # reduce stock
    stock.quantity -= reservation.quantity
    stock.save()

    reservation.status = 'approved'
    reservation.processed_by = request.user   # IMPORTANT FIX
    reservation.save()

    return Response({"detail": "Reservation approved"})


# =========================
# REJECT RESERVATION
# =========================
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reject_reservation(request, pk):

    try:
        reservation = Reservation.objects.get(pk=pk)
    except Reservation.DoesNotExist:
        return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    if reservation.status == 'approved':
        return Response(
            {"detail": "Cannot reject approved reservation"},
            status=status.HTTP_400_BAD_REQUEST
        )

    reservation.status = 'rejected'
    reservation.processed_by = request.user   # IMPORTANT FIX
    reservation.save()

    return Response({"detail": "Reservation rejected"})


# =========================
# ENDPOINTS
# =========================
manage_pharmacy = generic_api(Pharmacy, PharmacySerializer)
manage_staff = generic_api(PharmacyStaff, PharmacyStaffSerializer)
manage_medicine = generic_api(Medicine, MedicineSerializer)
manage_stock = generic_api(Stock, StockSerializer)
manage_reservation = generic_api(Reservation, ReservationSerializer)