from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import Pharmacy, PharmacyStaff, Medicine, Stock, Reservation
from .serializers import (
    PharmacySerializer,
    PharmacyStaffSerializer,
    MedicineSerializer,
    StockSerializer,
    ReservationSerializer
)


# =========================
# GENERIC CRUD API (TEST MODE)
# =========================
def generic_api(model_class, serializer_class):

    @api_view(['GET', 'POST', 'PUT', 'DELETE'])
    @permission_classes([AllowAny])   # ✅ TEMP FIX HERE
    def api(request, pk=None):

        # GET ALL OR SINGLE
        if request.method == 'GET':
            if pk:
                try:
                    obj = model_class.objects.get(pk=pk)
                    serializer = serializer_class(obj)
                    return Response(serializer.data)
                except model_class.DoesNotExist:
                    return Response({"message": "Not found"}, status=404)
            else:
                objs = model_class.objects.all()
                serializer = serializer_class(objs, many=True)
                return Response(serializer.data)

        # CREATE
        elif request.method == 'POST':
            serializer = serializer_class(data=request.data)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=201)

            return Response(serializer.errors, status=400)

        # UPDATE
        elif request.method == 'PUT':
            if not pk:
                return Response({"message": "ID required"}, status=400)

            try:
                obj = model_class.objects.get(pk=pk)
                serializer = serializer_class(obj, data=request.data)

                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data)

                return Response(serializer.errors, status=400)

            except model_class.DoesNotExist:
                return Response({"message": "Not found"}, status=404)

        # DELETE
        elif request.method == 'DELETE':
            if not pk:
                return Response({"message": "ID required"}, status=400)

            try:
                obj = model_class.objects.get(pk=pk)
                obj.delete()
                return Response({"message": "Deleted"}, status=204)

            except model_class.DoesNotExist:
                return Response({"message": "Not found"}, status=404)

    return api


# =========================
# RESERVATION APPROVE (TEST MODE)
# =========================
@api_view(['POST'])
@permission_classes([AllowAny])   # ✅ TEMP FIX
def approve_reservation(request, pk):

    try:
        reservation = Reservation.objects.get(pk=pk)
    except Reservation.DoesNotExist:
        return Response({"message": "Not found"}, status=404)

    stock = Stock.objects.filter(
        pharmacy=reservation.pharmacy,
        medicine=reservation.medicine
    ).first()

    if not stock:
        return Response({"message": "Stock not found"}, status=400)

    if stock.quantity < reservation.quantity:
        return Response({"message": "Not enough stock"}, status=400)

    stock.quantity -= reservation.quantity
    stock.save()

    reservation.status = 'approved'
    reservation.save()

    return Response({"message": "Reservation approved successfully"})


# =========================
# RESERVATION REJECT (TEST MODE)
# =========================
@api_view(['POST'])
@permission_classes([AllowAny])   # ✅ TEMP FIX
def reject_reservation(request, pk):

    try:
        reservation = Reservation.objects.get(pk=pk)
    except Reservation.DoesNotExist:
        return Response({"message": "Not found"}, status=404)

    reservation.status = 'rejected'
    reservation.save()

    return Response({"message": "Reservation rejected"})


# =========================
# API ENDPOINTS
# =========================
manage_pharmacy = generic_api(Pharmacy, PharmacySerializer)
manage_staff = generic_api(PharmacyStaff, PharmacyStaffSerializer)
manage_medicine = generic_api(Medicine, MedicineSerializer)
manage_stock = generic_api(Stock, StockSerializer)
manage_reservation = generic_api(Reservation, ReservationSerializer)