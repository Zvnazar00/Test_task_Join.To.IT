from django.urls import path
from django.contrib.auth.decorators import login_required

from .views import (RegisterUserView, LoginUserView, LogoutUserView,
                    EventListView, EventCreateView, EventDetailView,
                    EventUpdateView, EventDeleteView, EventRegistrationView)

urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register'),
    path('', LoginUserView.as_view(), name='login'),
    path('logout/', login_required(LogoutUserView.as_view()), name='logout'),
    path('events/', login_required(EventListView.as_view()), name='event_list'),
    path('events/create/', login_required(EventCreateView.as_view()), name='event_create'),
    path('events/<int:pk>/', login_required(EventDetailView.as_view()), name='event_detail'),
    path('events/<int:pk>/edit/', login_required(EventUpdateView.as_view()), name='event_update'),
    path('events/<int:pk>/delete/', login_required(EventDeleteView.as_view()), name='event_delete'),
    path('events/<int:event_id>/register/', login_required(EventRegistrationView.as_view()), name='event_register'),
]
