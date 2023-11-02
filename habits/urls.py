from django.urls import path
from rest_framework.routers import DefaultRouter

from habits.apps import HabitsConfig
from habits.views import HabitListView, HabitDetailView, HabitCreateView, HabitUpdateView, HabitDeleteView, \
    PublicHabitListView, HabitViewSet

app_name = HabitsConfig.name

router = DefaultRouter()
router.register(r'habits', HabitViewSet, basename='habits')

urlpatterns = [
    path("create/", HabitCreateView.as_view(), name="habit_create"),
    path("public/", PublicHabitListView.as_view(), name="habits_public_list"),
    path("list/", HabitListView.as_view(), name="habits_list"),
    path("<int:pk>/", HabitDetailView.as_view(), name="habit_detail"),
    path("<int:pk>/update/", HabitUpdateView.as_view(), name="habit_update"),
    path("<int:pk>/delete/", HabitDeleteView.as_view(), name="habit_delete"),
] + router.urls
