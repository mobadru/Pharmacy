from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import (
    Pharmacy,
    PharmacyStaff,
    Product,
    Stock,
    Reservation,
)

from .serializers import (
    CustomTokenObtainPairSerializer,
    PharmacySerializer,
    PharmacyStaffSerializer,
    ProductSerializer,
    StockSerializer,
    ReservationSerializer,
)


# ==================================================
# JWT LOGIN
# ==================================================

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


# ==================================================
# HELPERS
# ==================================================

def get_role(user):
    profile = getattr(user, "profile", None)
    return profile.role if profile else None


def is_staff(user):
    return get_role(user) == "staff"


def is_patient(user):
    return get_role(user) == "patient"


def get_staff_pharmacy(user):
    staff = PharmacyStaff.objects.filter(user=user).first()
    return staff.pharmacy if staff else None


# ==================================================
# GENERIC CRUD
# ==================================================

def generic_api(model_class, serializer_class):

    @api_view(["GET", "POST", "PUT", "DELETE"])
    @permission_classes([IsAuthenticated])
    def api(request, pk=None):

        user = request.user
        pharmacy = get_staff_pharmacy(user)

        # ==================================================
        # GET
        # ==================================================

        if request.method == "GET":

            if pk:
                try:
                    obj = model_class.objects.get(pk=pk)

                    if model_class == Stock:
                        if is_staff(user) and obj.pharmacy != pharmacy:
                            return Response(
                                {"detail": "Forbidden"},
                                status=status.HTTP_403_FORBIDDEN,
                            )

                    if model_class == Reservation:

                        if is_staff(user):
                            if obj.pharmacy != pharmacy:
                                return Response(
                                    {"detail": "Forbidden"},
                                    status=status.HTTP_403_FORBIDDEN,
                                )

                        elif is_patient(user):
                            if obj.user != user:
                                return Response(
                                    {"detail": "Forbidden"},
                                    status=status.HTTP_403_FORBIDDEN,
                                )

                    return Response(serializer_class(obj).data)

                except model_class.DoesNotExist:
                    return Response(
                        {"detail": "Not found"},
                        status=status.HTTP_404_NOT_FOUND,
                    )

            # LIST

            if model_class == Pharmacy:
                queryset = Pharmacy.objects.all()

            elif model_class == Product:
                queryset = Product.objects.all()

            elif model_class == Stock:

                if not is_staff(user):
                    return Response(
                        {"detail": "Staff only"},
                        status=status.HTTP_403_FORBIDDEN,
                    )

                queryset = Stock.objects.filter(pharmacy=pharmacy)

            elif model_class == Reservation:

                if is_staff(user):
                    queryset = Reservation.objects.filter(pharmacy=pharmacy)
                else:
                    queryset = Reservation.objects.filter(user=user)

            else:
                queryset = model_class.objects.all()

            return Response(serializer_class(queryset, many=True).data)

        # ==================================================
        # POST
        # ==================================================

        elif request.method == "POST":

            serializer = serializer_class(
                data=request.data,
                context={"request": request},
            )

            if not serializer.is_valid():
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:

                # STOCK
                if model_class == Stock:

                    if not is_staff(user):
                        return Response(
                            {"detail": "Staff only"},
                            status=status.HTTP_403_FORBIDDEN,
                        )

                    instance = serializer.save()

                    return Response(
                        serializer_class(instance).data,
                        status=status.HTTP_201_CREATED,
                    )

                # RESERVATION

                if model_class == Reservation:

                    if not is_patient(user):
                        return Response(
                            {"detail": "Patients only"},
                            status=status.HTTP_403_FORBIDDEN,
                        )

                    instance = serializer.save(user=user)

                    return Response(
                        serializer_class(instance).data,
                        status=status.HTTP_201_CREATED,
                    )

                instance = serializer.save()

                return Response(
                    serializer_class(instance).data,
                    status=status.HTTP_201_CREATED,
                )

            except Exception as e:
                return Response(
                    {"error": str(e)},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # ==================================================
        # PUT
        # ==================================================

        elif request.method == "PUT":

            if pk is None:
                return Response(
                    {"detail": "ID required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                obj = model_class.objects.get(pk=pk)

            except model_class.DoesNotExist:
                return Response(
                    {"detail": "Not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            serializer = serializer_class(
                obj,
                data=request.data,
                partial=True,
                context={"request": request},
            )

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)

            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ==================================================
        # DELETE
        # ==================================================

        elif request.method == "DELETE":

            if pk is None:
                return Response(
                    {"detail": "ID required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                obj = model_class.objects.get(pk=pk)

            except model_class.DoesNotExist:
                return Response(
                    {"detail": "Not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            obj.delete()

            return Response(
                {"detail": "Deleted"},
                status=status.HTTP_204_NO_CONTENT,
            )

    return api


# ==================================================
# APPROVE RESERVATION
# ==================================================

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def approve_reservation(request, pk):

    pharmacy = get_staff_pharmacy(request.user)

    try:
        reservation = Reservation.objects.get(pk=pk)
    except Reservation.DoesNotExist:
        return Response(
            {"detail": "Not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    if reservation.pharmacy != pharmacy:
        return Response(
            {"detail": "Forbidden"},
            status=status.HTTP_403_FORBIDDEN,
        )

    try:
        stock = Stock.objects.get(
            pharmacy=pharmacy,
            product=reservation.product,
        )
    except Stock.DoesNotExist:
        return Response(
            {"detail": "Stock not found"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if stock.quantity < reservation.quantity:
        return Response(
            {"detail": "Not enough stock"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    stock.quantity -= reservation.quantity
    stock.save()

    reservation.status = "approved"
    reservation.processed_by = request.user
    reservation.save()

    return Response({"detail": "Reservation approved"})


# ==================================================
# REJECT RESERVATION
# ==================================================

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def reject_reservation(request, pk):

    pharmacy = get_staff_pharmacy(request.user)

    try:
        reservation = Reservation.objects.get(pk=pk)
    except Reservation.DoesNotExist:
        return Response(
            {"detail": "Not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    if reservation.pharmacy != pharmacy:
        return Response(
            {"detail": "Forbidden"},
            status=status.HTTP_403_FORBIDDEN,
        )

    reservation.status = "rejected"
    reservation.processed_by = request.user
    reservation.save()

    return Response({"detail": "Reservation rejected"})


# ==================================================
# ENDPOINTS
# ==================================================

manage_pharmacy = generic_api(Pharmacy, PharmacySerializer)
manage_staff = generic_api(PharmacyStaff, PharmacyStaffSerializer)
manage_product = generic_api(Product, ProductSerializer)
manage_stock = generic_api(Stock, StockSerializer)
manage_reservation = generic_api(Reservation, ReservationSerializer)