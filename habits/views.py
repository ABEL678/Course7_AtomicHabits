from rest_framework import status, viewsets
from rest_framework.generics import RetrieveAPIView, CreateAPIView, ListAPIView, DestroyAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from habits.models import Habit
from habits.serializers import HabitSerializer
from habits.paginators import HabitPaginator
from habits.services import create_periodic_task
from habits.permissions import IsOwner


class HabitViewSet(viewsets.ModelViewSet):
    serializer_class = HabitSerializer
    queryset = Habit.objects.all()


class HabitCreateView(CreateAPIView):
    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated & IsOwner]

    def perform_create(self, serializer):
        new_habit = serializer.save()
        new_habit.owner = self.request.user
        new_habit.task = create_periodic_task(new_habit.frequency, new_habit.pk, new_habit.time)
        new_habit.save()


class HabitListView(ListAPIView):
    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated & IsOwner]
    pagination_class = HabitPaginator

    def get_queryset(self):
        if self.request.user.is_staff:
            return Habit.objects.all().order_by("pk")
        else:
            return Habit.objects.filter(owner=self.request.user).order_by("pk")


class HabitDetailView(RetrieveAPIView):
    queryset = Habit.objects.all()
    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated & IsOwner]


class HabitUpdateView(UpdateAPIView):
    queryset = Habit.objects.all()
    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated & IsOwner]

    def perform_update(self, serializer):
        update_habit = serializer.save()
        update_habit.task.delete()
        update_habit.task = create_periodic_task(update_habit.frequency, update_habit.pk, update_habit.time)
        update_habit.save()


class HabitDeleteView(DestroyAPIView):
    queryset = Habit.objects.all()
    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated & IsOwner]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if len(Habit.objects.filter(link_pleasant=instance)) > 0:
            return Response({'error_message': 'не могу удалить, связанная привычка'},
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.task.delete()
        instance.delete()


class PublicHabitListView(ListAPIView):
    queryset = Habit.objects.filter(is_public=True).order_by('pk')
    serializer_class = HabitSerializer
    pagination_class = HabitPaginator
