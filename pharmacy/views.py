from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from .models import UserProfile


from .models import (
    Pharmacy,
    PharmacyStaff,
    Product,
    Stock,
    Reservation,
)

from .serializers import (
    CustomTokenObtainPairSerializer,
    UserProfileSerializer,
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

        if request.method == "GET":

            # --------------------------
            # GET SINGLE RECORD
            # --------------------------
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

            # --------------------------
            # LIST RECORDS
            # --------------------------

            if model_class == Pharmacy:

                queryset = Pharmacy.objects.all()

            elif model_class == Product:

                queryset = Product.objects.all()

            elif model_class == Stock:

                # Staff sees only their pharmacy stock
                if is_staff(user):

                    queryset = Stock.objects.filter(
                        pharmacy=pharmacy
                    )

                # Patients see all available medicines
                elif is_patient(user):

                    queryset = Stock.objects.filter(
                        quantity__gt=0
                    )

                else:

                    return Response(
                        {"detail": "Unauthorized"},
                        status=status.HTTP_403_FORBIDDEN,
                    )

            elif model_class == Reservation:

                if is_staff(user):

                    queryset = Reservation.objects.filter(
                        pharmacy=pharmacy
                    )

                else:

                    queryset = Reservation.objects.filter(
                        user=user
                    )

            else:

                queryset = model_class.objects.all()

            return Response(
                serializer_class(queryset, many=True).data
            )

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

            # ------------------------------------------
            # STOCK AUTHORIZATION
            # Staff can only update stock belonging
            # to their assigned pharmacy
            # ------------------------------------------
            if model_class == Stock:

                if not is_staff(user):
                    return Response(
                        {"detail": "Staff only"},
                        status=status.HTTP_403_FORBIDDEN,
                    )

                if obj.pharmacy != pharmacy:
                    return Response(
                        {
                            "detail": "You do not have permission to manage this pharmacy's stock."
                        },
                        status=status.HTTP_403_FORBIDDEN,
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

            # ------------------------------------------
            # STOCK AUTHORIZATION
            # Staff can only delete stock belonging
            # to their assigned pharmacy
            # ------------------------------------------
            if model_class == Stock:

                if not is_staff(user):
                    return Response(
                        {"detail": "Staff only"},
                        status=status.HTTP_403_FORBIDDEN,
                    )

                if obj.pharmacy != pharmacy:
                    return Response(
                        {
                            "detail": "You do not have permission to delete this pharmacy's stock."
                        },
                        status=status.HTTP_403_FORBIDDEN,
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

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

@api_view(["GET", "PUT", "PATCH"])
@permission_classes([IsAuthenticated])
def profile(request):
    user = request.user

    profile = getattr(user, "profile", None)

    if profile is None:
        return Response(
            {"detail": "Profile not found."},
            status=status.HTTP_404_NOT_FOUND,
        )

    if request.method == "GET":
        data = UserProfileSerializer(profile).data
    else:
        serializer = UserProfileSerializer(
            profile,
            data=request.data,
            partial=True,
        )

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = UserProfileSerializer(serializer.save()).data

    pharmacy = get_staff_pharmacy(user)

    data["pharmacy"] = pharmacy.name if pharmacy else None
    data["pharmacy_id"] = pharmacy.id if pharmacy else None

    return Response(data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def change_password(request):
    current_password = request.data.get("current_password")
    new_password = request.data.get("new_password")
    confirm_password = request.data.get("confirm_password")

    if not current_password or not new_password or not confirm_password:
        return Response(
            {"detail": "All password fields are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = request.user

    if not user.check_password(current_password):
        return Response(
            {"detail": "Current password is incorrect."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if new_password != confirm_password:
        return Response(
            {"detail": "New passwords do not match."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        validate_password(new_password, user)
    except ValidationError as error:
        return Response(
            {"detail": error.messages},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user.set_password(new_password)
    user.save(update_fields=["password"])

    return Response(
        {"detail": "Password changed successfully."},
        status=status.HTTP_200_OK,
    )


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

from django.contrib.auth.models import User
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import UserProfile


@api_view(["POST"])
@permission_classes([AllowAny])
def register_patient(request):

    username = request.data.get("username")
    email = request.data.get("email")
    password = request.data.get("password")


    if not username or not password:

        return Response(
            {
                "error":"Username and password required"
            },
            status=status.HTTP_400_BAD_REQUEST
        )


    if User.objects.filter(username=username).exists():

        return Response(
            {
                "error":"Username already exists"
            },
            status=status.HTTP_400_BAD_REQUEST
        )


    user = User.objects.create_user(

        username=username,

        email=email,

        password=password

    )


    UserProfile.objects.create(

        user=user,

        role="patient"

    )


    return Response(

        {
            "message":"Patient account created successfully"
        },

        status=status.HTTP_201_CREATED

    )
@api_view(["POST"])
@permission_classes([AllowAny])
def forgot_password(request):

    email = request.data.get("email")


    if not email:

        return Response(
            {
                "error":"Email required"
            },
            status=400
        )


    user = User.objects.filter(
        email=email
    ).first()


    if not user:

        return Response(

            {
                "error":"Email not found"
            },

            status=404

        )


    return Response(

        {
            "message":"Password reset request accepted"
        }

    )
# ==================================================
# ENDPOINTS
# ==================================================

manage_pharmacy = generic_api(Pharmacy, PharmacySerializer)
manage_staff = generic_api(PharmacyStaff, PharmacyStaffSerializer)
manage_product = generic_api(Product, ProductSerializer)
manage_stock = generic_api(Stock, StockSerializer)
manage_reservation = generic_api(Reservation, ReservationSerializer)


