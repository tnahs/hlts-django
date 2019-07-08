from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView


class ApiRoot(APIView):
    """
    API Documentation...
    """

    def get(self, request):

        # Settings
        user = reverse("user", request=request)
        password = reverse("password", request=request)

        # Nodes
        nodes = reverse("node-list", request=request)

        # Node Data
        sources = reverse("source-list", request=request)
        individuals = reverse("individual-list", request=request)
        tags = reverse("tag-list", request=request)
        collections = reverse("collection-list", request=request)
        origins = reverse("origin-list", request=request)

        # Actions

        merge = reverse("merge", request=request)

        return Response(
            {
                "settings": {"user": user, "password": password},
                "data": {
                    "nodes": nodes,
                    "attributes": {
                        "sources": sources,
                        "individuals": individuals,
                        "tags": tags,
                        "collections": collections,
                        "origins": origins,
                    },
                },
                "actions": {"merge": merge},
            }
        )
