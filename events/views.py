from django.utils import timezone
from django.db.models import Q

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.core.exceptions import PermissionDenied

from rest_framework import generics, permissions, status
from rest_framework.views import APIView

from .models import Event, EventRegistration
from .serializers import EventSerializer, EventRegistrationSerializer


class RegisterUserView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return render(request, 'register.html')

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')

        if not username or not password or not email:
            return render(request, 'register.html', {"error": "Please provide all required fields."})

        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {"error": "Username already exists."})

        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        return redirect('login')


class LoginUserView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return render(request, 'login.html')

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('event_list')
        else:
            return render(request, 'login.html', {"error": "Invalid credentials."})


class LogoutUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('login')

    def post(self, request, *args, **kwargs):
        logout(request)
        return redirect('login')

class EventListView(generics.ListAPIView):
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        Event.objects.filter(date__lt=timezone.now().date()).delete()

        queryset = Event.objects.all()

        if 'apply_filters' in self.request.GET:
            date = self.request.GET.get('date')
            if date:
                date_obj = timezone.datetime.strptime(date, '%Y-%m-%d').date()
                queryset = queryset.filter(date__exact=date_obj)


            time = self.request.GET.get('time')
            if time:
                time_obj = timezone.datetime.strptime(time, '%H:%M').time()
                queryset = queryset.filter(time__exact=time_obj)


            location = self.request.GET.get('location')
            if location:
                queryset = queryset.filter(location__icontains=location)


            search_query = self.request.GET.get('search')
            if search_query:
                queryset = queryset.filter(
                    Q(title__icontains=search_query) |
                    Q(description__icontains=search_query)
                )

        return queryset

    def get(self, request, *args, **kwargs):
        events = self.get_queryset()  # Получаем отфильтрованные события
        return render(request, 'event_list.html', {'events': events})


class EventCreateView(generics.CreateAPIView):
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, *args, **kwargs):
        return render(request, 'event_form.html')

    def post(self, request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied("Only admins can create events.")

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            event = serializer.save()

            user_count = len([key for key in request.POST if key.startswith('first_name_')])
            for i in range(1, user_count + 1):
                first_name = request.POST.get(f'first_name_{i}')
                last_name = request.POST.get(f'last_name_{i}')
                email = request.POST.get(f'email_{i}')
                if first_name and last_name and email:
                    EventRegistration.objects.create(
                        event=event,
                        user=request.user,
                        first_name=first_name,
                        last_name=last_name,
                        email=email
                    )

                    subject = f"Registration Confirmation for {event.title}"

                    message = (f"Hello {first_name},\n\n"
                               f"You have successfully registered for the event {event.title}.\n\n"
                               f"Event Details:\n"
                               f"Title: {event.title}\n"
                               f"Description: {event.description}\n"
                               f"Date and Time: {event.date.strftime('%B %d, %Y')} at {event.time.strftime('%I:%M %p')}\n"
                               f"Location: {event.location}\n"
                               f"Organizer: {event.organizer}\n\n"
                               f"We look forward to seeing you at the event!\n\n"
                               f"Best regards,\n"
                               f"The Event Team")

                    send_mail(
                        subject,
                        message,
                        settings.EMAIL_HOST_USER,
                        [email],
                        fail_silently=False,
                    )

            return redirect('event_list')

        return render(request, 'event_form.html', {'form_errors': serializer.errors})


class EventDetailView(generics.RetrieveAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, pk, *args, **kwargs):
        event = get_object_or_404(Event, pk=pk)
        return render(request, 'event_detail.html', {'event': event})


class EventUpdateView(generics.UpdateAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, pk, *args, **kwargs):
        event = get_object_or_404(Event, pk=pk)
        return render(request, 'event_form.html', {'event': event})

    def post(self, request, pk, *args, **kwargs):
        event = get_object_or_404(Event, pk=pk)
        serializer = self.get_serializer(event, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return redirect('event_detail', pk=pk)
        return render(request, 'event_form.html', {'event': event, 'form_errors': serializer.errors})


class EventDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def post(self, request, pk, *args, **kwargs):
        event = get_object_or_404(Event, pk=pk)
        event.delete()
        return redirect('event_list')

class EventRegistrationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, event_id, *args, **kwargs):
        event = get_object_or_404(Event, id=event_id)
        registrations = event.event_registration.all()
        return render(request, 'event_register.html', {
            'event': event,
            'registrations': registrations
        })

    def post(self, request, event_id, *args, **kwargs):
        event = get_object_or_404(Event, id=event_id)
        data = {
            'event': event.id,
            'user': request.user.id,
            'first_name': request.data.get('first_name'),
            'last_name': request.data.get('last_name'),
            'email': request.data.get('email')
        }

        serializer = EventRegistrationSerializer(data=data)
        if serializer.is_valid():
            serializer.save()

            subject = f"Registration Confirmation for {event.title}"

            message = (
                f"Hello {data['first_name']},\n\n"
                f"You have successfully registered for the event {event.title}.\n\n"
                f"Event Details:\n"
                f"Title: {event.title}\n"
                f"Description: {event.description}\n"
                f"Date and Time: {event.date.strftime('%B %d, %Y')} at {event.time.strftime('%I:%M %p')}\n"
                f"Location: {event.location}\n"
                f"Organizer: {event.organizer}\n\n"
                f"We look forward to seeing you at the event!\n\n"
                f"Best regards,\n"
                f"The Event Team"
            )

            recipient_email = data['email']

            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [recipient_email],
                fail_silently=False,
            )

            return redirect('event_register', event_id=event_id)
        else:
            registrations = event.event_registration.all()
            return render(request, 'event_register.html', {
                'event': event,
                'registrations': registrations,
                'form_errors': serializer.errors
            })
