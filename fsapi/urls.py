from django.urls import include, path
from .views import FSFileViewUuidSet, FileUploadView

urlpatterns = [
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('<str:uuid>/info', FSFileViewUuidSet.as_view({'get': 'info'})),
    path('<str:uuid>/delete', FSFileViewUuidSet.as_view({'get': 'delete'})),
    path('<str:uuid>/download', FSFileViewUuidSet.as_view({'get': 'download'})),
    path('upload', FileUploadView.as_view()),
]
