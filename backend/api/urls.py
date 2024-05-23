from django.urls import path
from . import views


urlpatterns = [
    path("notes/", views.NoteListCreate.as_view(), name="note-list"),  # URL pattern for listing and creating notes
    path("notes/delete/<int:pk>/", views.NoteDelete.as_view(), name="delete-note"),  # URL pattern for deleting a specific note identified by its primary key
]
