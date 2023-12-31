from django.urls import path

from . import views

app_name = "polls"
urlpatterns = [
    path("", views.IndexView.as_view(), name='index'),
    path("<int:pk>/", views.DetailView.as_view(), name="detail"),
    path("question_form/", views.QuestionCreateView.as_view(), name='question_form'),
    path("<int:pk>/choice_form", views.ChoiceCreateView.as_view(), name='choice_form'),
    path("<int:pk>/results/", views.ResultsView.as_view(), name="results"),
    path("<int:question_id>/vote/", views.vote, name="vote"),
]
