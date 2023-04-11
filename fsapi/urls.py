from django.urls import include, path
from .views import FSFileViewUuidSet, FileUploadView

urlpatterns = [
    path('info/<str:uuid>', FSFileViewUuidSet.as_view({'get': 'info'})),
    path('delete/<str:uuid>', FSFileViewUuidSet.as_view({'get': 'delete'})),
    path('download/<str:uuid>', FSFileViewUuidSet.as_view({'get': 'download'})),
    path('upload', FileUploadView.as_view()),
    path('clean', FSFileViewUuidSet.as_view({'get': 'clean'})),
]
