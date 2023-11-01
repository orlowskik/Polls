from django.http import HttpResponseRedirect, Http404, request
from django.shortcuts import render, get_object_or_404
from django import forms
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.contrib.admin.widgets import AdminDateWidget
from .models import Question, Choice


# The ChoiceForm class is a Django form that is used to create
# instances of the Choice model. It includes custom logic to
# handle the form fields and validation based on the current instance.
class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        exclude = ('question',)
        fields = ['choice_text', 'votes']
        initial = {'votes': 0}


class IndexView(generic.ListView):
    template_name = "polls/index.html"
    context_object_name = "latest_questions"

    def get_queryset(self):
        self.request.session.flush()
        return Question.objects.filter(pub_date__lte=timezone.now()).order_by("-pub_date")[:5]


class DetailView(generic.DetailView):
    template_name = "polls/detail.html"
    model = Question

    def get_queryset(self):
        self.request.session.flush()
        return Question.objects.filter(pub_date__lte=timezone.now())


class ResultsView(generic.DetailView):
    template_name = "polls/results.html"
    model = Question

    def get_queryset(self):
        self.request.session.flush()
        return Question.objects.filter(pub_date__lte=timezone.now())


class QuestionCreateView(generic.CreateView):
    template_name = "polls/question_form.html"
    model = Question
    fields = ['question_text', 'pub_date', 'exp_date']

    def get_form(self, form_class=None):
        self.request.session.flush()
        form = super(QuestionCreateView, self).get_form(form_class)
        form.fields['pub_date'].widget = AdminDateWidget(attrs={'type': 'datetime-local'})
        form.fields['exp_date'].widget = AdminDateWidget(attrs={'type': 'datetime-local'})
        return form

    def get_success_url(self):
        return reverse('polls:choice_form', kwargs={'pk': self.object.id})

    def form_valid(self, form):
        self.object = form.save()
        self.request.session['question_id_access'] = self.object.id
        return HttpResponseRedirect(self.get_success_url())


class ChoiceCreateView(generic.CreateView):
    template_name = "polls/choice_form.html"
    model = Choice
    form_class = ChoiceForm

    def check_access(self):
        if 'question_id_access' not in self.request.session:
            raise Http404
        elif self.request.session['question_id_access'] != self.kwargs['pk']:
            raise Http404

    def form_valid(self, form):
        self.check_access()
        self.object = form.save(False)
        self.object.question = Question.objects.get(pk=self.kwargs['pk'])
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('polls:choice_form', kwargs={'pk': self.object.question.id})


#
# def index(request):
#     latest_questions = Question.objects.order_by("-pub_date")[:5]
#     context = {"latest_questions": latest_questions, }
#     return render(request, "polls/index.html", context)

#
# def detail(request, question_id):
#     try:
#         question = Question.objects.get(pk=question_id)
#     except Question.DoesNotExist:
#         raise Http404("Question does not exist")
#
#     return render(request, "polls/detail.html", {"question": question, })

#
# def results(request, question_id):
#     question = get_object_or_404(Question, pk=question_id)
#     return render(request, "polls/results.html", {"question": question})


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        return render(request, "polls/detail.html",
                      {"question": question, "error_message": "You didn't select a choice"}, )
    else:
        selected.votes += 1
        selected.save()
        return HttpResponseRedirect(reverse("polls:results", args=(question_id,)))
