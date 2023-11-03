from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404
from django import forms
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.contrib.admin.widgets import AdminDateWidget
from .models import Question, Choice


# The ChoiceForm class is a ModelForm that is used to create and update Choice objects,
# excluding the question field and including the choice_text and votes fields with
# an initial value of 0.
class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        exclude = ('question',)
        fields = ['choice_text', 'votes']
        initial = {'votes': 0}


# The IndexView class is a generic ListView that renders a template called "polls/index.html" and provides a context
# variable called "latest_questions".
class IndexView(generic.ListView):
    template_name = "polls/index.html"
    context_object_name = "latest_questions"

    def get_queryset(self):
        """
        The function returns the latest 5 questions that have a publication date before or equal to the current time.
        :return: The code is returning a queryset of Question objects that meet the following criteria:
        - The pub_date of the Question is less than or equal to the current time.
        - The queryset is ordered by the pub_date in descending order.
        - Only the first 5 Question objects are included in the queryset.
        """
        self.request.session.flush()
        return Question.objects.filter(pub_date__lte=timezone.now()).order_by("-pub_date")[:5]

# The DetailView class returns a queryset of Question objects that have a pub_date
# earlier than or equal to the current
# time.
class DetailView(generic.DetailView):
    template_name = "polls/detail.html"
    model = Question

    def get_queryset(self):
        """
        The function returns a queryset of Question objects that have a pub_date earlier than or equal to the current
        time. :return: The code is returning a queryset of Question objects that have a pub_date less than or equal
        to the current time.
        """
        self.request.session.flush()
        return Question.objects.filter(pub_date__lte=timezone.now())


# The ResultsView class is a generic detail view that displays the results of a specific question in a template, and it
# filters the queryset to only include questions that have a publication date before or equal to the current time.
class ResultsView(generic.DetailView):
    template_name = "polls/results.html"
    model = Question

    def get_queryset(self):
        """
        The function returns a queryset of Question objects that have a pub_date earlier than or equal to the current
        time. :return: The code is returning a queryset of Question objects that have a pub_date less than or equal
        to the current time.
        """
        self.request.session.flush()
        return Question.objects.filter(pub_date__lte=timezone.now())


# The `QuestionCreateView` class is a generic view for creating a new question object with a form, and it sets the
# success URL and saves the question ID to the session.
class QuestionCreateView(generic.CreateView):
    template_name = "polls/question_form.html"
    model = Question
    fields = ['question_text', 'pub_date', 'exp_date']

    def get_form(self, form_class=None):
        """
        The function `get_form` clears the session, modifies the widgets of two fields in a form, and returns the
        modified form.

        :param form_class: The `form_class` parameter is used to specify the form class that should be used for the
        view. If `form_class` is not provided, the default form class for the view will be used :return: the form
        object.
        """
        self.request.session.flush()
        form = super(QuestionCreateView, self).get_form(form_class)
        form.fields['pub_date'].widget = AdminDateWidget(attrs={'type': 'datetime-local'})
        form.fields['exp_date'].widget = AdminDateWidget(attrs={'type': 'datetime-local'})
        return form

    def get_success_url(self):
        return reverse('polls:choice_form', kwargs={'pk': self.object.id})

    def form_valid(self, form):
        """
        The function saves a form, sets a session variable, and redirects to a success URL.

        :param form: The `form` parameter is an instance of a Django form that has been submitted by the user. It
        contains the data entered by the user :return: The method `form_valid` is returning an `HttpResponseRedirect`
        object.
        """
        self.object = form.save()
        self.request.session['question_id_access'] = self.object.id
        return HttpResponseRedirect(self.get_success_url())


# The `ChoiceCreateView` class is a generic CreateView that handles the creation of Choice objects, with additional
# access checks.
class ChoiceCreateView(generic.CreateView):
    template_name = "polls/choice_form.html"
    model = Choice
    form_class = ChoiceForm

    def get_form(self, form_class=None):
        """
        The function `get_form` returns a form object after checking access permissions.

        :param form_class: The `form_class` parameter is used to specify the form class that should be used for the
        view. If `form_class` is not provided, the default form class for the view will be used :return: The "form"
        variable is being returned.
        """
        form = super(ChoiceCreateView, self).get_form(form_class)
        self.check_access()
        return form

    def form_valid(self, form):
        """
        The function saves a form object, associates it with a question object, and redirects to a success URL.

        :param form: The `form` parameter is an instance of a Django form that has been submitted by the user. It
        contains the data entered by the user and can be used to validate and save the data :return: an
        HttpResponseRedirect object.
        """
        self.check_access()
        self.object = form.save(False)
        self.object.question = Question.objects.get(pk=self.kwargs['pk'])
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('polls:choice_form', kwargs={'pk': self.object.question.id})

    def check_access(self):
        """
        The function checks if the 'question_id_access' key is present in the session and if its value matches the 'pk'
        value from the kwargs, otherwise it raises a Http404 exception.
        """
        if 'question_id_access' not in self.request.session:
            raise Http404
        elif self.request.session['question_id_access'] != self.kwargs['pk']:
            raise Http404


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
    """
    The function handles the voting process for a specific question by incrementing the vote count for the selected
    choice and redirecting to the results page.

    :param request: The request object represents the HTTP request made by the user. It contains information such as
    the user's browser details, the requested URL, and any data sent with the request
    :param question_id: The question_id parameter is the unique identifier of the question for which the user is voting.
     It is used to retrieve the corresponding Question object from the database
    :return: an HTTP redirect response to the "polls:results" view with the question_id as an argument.
    """
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
