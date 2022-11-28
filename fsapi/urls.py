from django.urls import include, path
from rest_framework import routers
from django.conf.urls import url
from rest_framework.decorators import action
from .views import FSFileViewUuidSet, FSFileViewSet, FSPathViewSet, FileUploadView

#default api listings, for debugging
router = routers.SimpleRouter()
router.register(r'file', FSFileViewSet)
router.register(r'path', FSPathViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('<str:uuid>/info', FSFileViewUuidSet.as_view({'get': 'info'})),
    path('<str:uuid>/delete', FSFileViewUuidSet.as_view({'get': 'delete'})),
    path('upload', FileUploadView.as_view()),
]
