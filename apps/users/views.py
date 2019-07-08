from django.contrib.auth import get_user_model
from rest_framework import permissions, status, views
from rest_framework.response import Response

from ..users.serializers import UserPasswordChangeSerializer, UserSerializer


class UserView(views.APIView):
    """
    UserView Documentation...
    """

    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer

    def get(self, request):

        serializer = self.serializer_class(request.user)

        return Response(serializer.data)

    def patch(self, request):

        serializer = self.serializer_class(
            request.user, data=request.data, partial=True
        )

        if serializer.is_valid(raise_exception=True):
            serializer.save()

        return Response(serializer.data)


class UserPasswordChangeView(views.APIView):
    """
    UserPasswordChangeView Documentation...
    """

    permission_classes = (permissions.AllowAny,)
    queryset = get_user_model().objects.all()
    serializer_class = UserPasswordChangeSerializer

    def post(self, request):
        """
        {
            "email": "",
            "password": "",
            "password_new": "",
            "password_confirm": ""
        }
        """
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid(raise_exception=True):
            serializer.save()

        return Response(status=status.HTTP_200_OK)
