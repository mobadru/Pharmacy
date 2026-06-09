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
def get_staff_pharmacy(user):
    try:
        return user.staff_profile.pharmacy
    except:
        return None

def generic_api(model_class, serializer_class):

    @api_view(['GET', 'POST', 'PUT', 'DELETE'])
    @permission_classes([IsAuthenticated])
    def api(request, pk=None):

        pharmacy = get_staff_pharmacy(request.user)

        if not pharmacy:
          return Response({"detail": "No pharmacy assigned"}, status=403)
        # ================= GET =================
        if request.method == 'GET':

            # SINGLE OBJECT
            if pk:
                try:
                    obj = model_class.objects.get(pk=pk)

                    # 🔐 SECURITY CHECK
                    if hasattr(obj, "pharmacy") and pharmacy:
                        if obj.pharmacy != pharmacy:
                            return Response({"detail": "Forbidden"}, status=403)

                    serializer = serializer_class(obj)
                    return Response(serializer.data)

                except model_class.DoesNotExist:
                    return Response({"detail": "Not found"}, status=404)

            # LIST VIEW (FILTER BY PHARMACY)
            if hasattr(model_class, "pharmacy"):
                objs = model_class.objects.filter(pharmacy=pharmacy)
            else:
                objs = model_class.objects.all()

            serializer = serializer_class(objs, many=True)
            return Response(serializer.data)

        # ================= POST =================
        if request.method == 'POST':

            serializer = serializer_class(
                data=request.data,
                context={'request': request}
            )

            if serializer.is_valid():
                instance = serializer.save()

                # 🔐 FORCE PHARMACY OWNERSHIP
                if hasattr(instance, "pharmacy") and pharmacy:
                    instance.pharmacy = pharmacy
                    instance.save()

                return Response(serializer.data, status=201)

            return Response(serializer.errors, status=400)

        # ================= PUT =================
        if request.method == 'PUT':

            if not pk:
                return Response({"detail": "ID required"}, status=400)

            try:
                obj = model_class.objects.get(pk=pk)

                # 🔐 SECURITY CHECK
                if hasattr(obj, "pharmacy") and pharmacy:
                    if obj.pharmacy != pharmacy:
                        return Response({"detail": "Forbidden"}, status=403)

            except model_class.DoesNotExist:
                return Response({"detail": "Not found"}, status=404)

            serializer = serializer_class(
                obj,
                data=request.data,
                partial=True,
                context={'request': request}
            )

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)

            return Response(serializer.errors, status=400)

        # ================= DELETE =================
        if request.method == 'DELETE':

            if not pk:
                return Response({"detail": "ID required"}, status=400)

            try:
                obj = model_class.objects.get(pk=pk)

                # 🔐 SECURITY CHECK
                if hasattr(obj, "pharmacy") and pharmacy:
                    if obj.pharmacy != pharmacy:
                        return Response({"detail": "Forbidden"}, status=403)

                obj.delete()
                return Response({"detail": "Deleted"}, status=204)

            except model_class.DoesNotExist:
                return Response({"detail": "Not found"}, status=404)

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