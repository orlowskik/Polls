import datetime
from unittest.mock import MagicMock

import pytest
from django.http import Http404

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from django.db.utils import DataError, IntegrityError
from django.core.exceptions import ValidationError
from .models import Question, Choice
from .views import ChoiceForm
from psycopg.errors import UniqueViolation


def create_question(question_text, days):
    """
    Function for creating question cases with publish date offset
    :param question_text: text
    :param days: offset from now()
    :return: Question object
    """
    time = timezone.now() + datetime.timedelta(days=days)
    exp = time + datetime.timedelta(days=7)
    return Question.objects.create(question_text=question_text, pub_date=time, exp_date=exp)


# Create your tests here.
class QuestionModelTests(TestCase):
    def test_was_published_recently_future_date(self):
        """
        was_published_recently() returns False if question.pub_date is in the future
        :return: True if future date is not recent, else False
        """

        future_question = create_question("Test", 30)

        self.assertIs(future_question.was_published_recently(), False, msg="Future date test failed")

    def test_was_published_recently_recent_question(self):
        """
        was_published_recently() returns True if question.pub_date is within the last day
        :return: True if question within day past is recent, else False
        """
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        exp = time + datetime.timedelta(7)
        recent_question = Question(question_text="Test", pub_date=time, exp_date=exp)

        self.assertIs(recent_question.was_published_recently(), True)


# Generated by CodiumAI
class TestQuestion(TestCase):

    #  Creating a new question with valid question_text and pub_date should successfully create a Question object
    def test_create_question_successfully(self):
        question_text = "What is your favorite color?"
        pub_date = timezone.now()
        question = Question(question_text=question_text, pub_date=pub_date)
        self.assertIsInstance(question, Question)

    def test_question_has_pub_date_attribute_of_type_datetime(self):
        question = Question.objects.create(question_text="Test Question", pub_date=timezone.now())
        self.assertIsInstance(question.pub_date, datetime.datetime)

    #  The __str__ method should return the question_text attribute of the Question object
    def test_str_method_returns_question_text(self):
        question_text = "What is your favorite color?"
        pub_date = timezone.now()
        question = Question(question_text=question_text, pub_date=pub_date)
        self.assertEqual(str(question), question_text)

    #  The was_published_recently method should return True if the pub_date attribute is within the
    #  last day, and False otherwise
    def test_was_published_recently_within_last_day(self):
        pub_date = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        question = Question(pub_date=pub_date)
        self.assertTrue(question.was_published_recently())

    def test_exactly_one_day_ago(self):
        pub_date = timezone.now() - datetime.timedelta(days=1)
        question = Question(pub_date=pub_date)
        self.assertFalse(question.was_published_recently())

    def test_exactly_now(self):
        pub_date = timezone.now()
        question = Question(pub_date=pub_date)
        self.assertTrue(question.was_published_recently())

    def test_returns_false_if_question_published_in_future(self):
        future_date = timezone.now() + datetime.timedelta(days=1)
        question = Question(pub_date=future_date)
        assert question.was_published_recently() == False

    def test_was_published_recently_within_specified_number_of_days(self):
        pub_date = timezone.now() - datetime.timedelta(days=2)
        question = Question(pub_date=pub_date)
        self.assertTrue(question.was_published_recently(days=3))

    def test_returns_false_if_published_exactly_specified_days_ago(self):
        pub_date = timezone.now() - datetime.timedelta(days=1)
        question = Question(pub_date=pub_date)
        self.assertFalse(question.was_published_recently(days=1))

    def test_returns_false_if_question_published_more_than_specified_days_ago(self):
        pub_date = timezone.now() - datetime.timedelta(days=2)
        question = Question(pub_date=pub_date)
        self.assertFalse(question.was_published_recently(days=1))

    #  Creating a new question with a pub_date in the future should still create a Question object
    def test_create_question_with_future_pub_date(self):
        question_text = "What is your favorite color?"
        pub_date = timezone.now() + datetime.timedelta(days=1)
        question = Question(question_text=question_text, pub_date=pub_date)
        self.assertIsInstance(question, Question)

    #  The was_published_recently method should return False if the pub_date attribute
    #  is more than one day in the past
    def test_was_published_recently_more_than_one_day_in_past(self):
        pub_date = timezone.now() - datetime.timedelta(days=2)
        question = Question(pub_date=pub_date)
        self.assertFalse(question.was_published_recently())

    def test_create_choice_with_long_choice_text_raises_validation_error(self):
        question = Question.objects.create(question_text="Test Question", pub_date=timezone.now())
        long_choice_text = "a" * 201
        with self.assertRaises(DataError):
            Choice.objects.create(question=question, choice_text=long_choice_text, votes=0)

    def test_create_question_with_empty_question_text_raises_validation_error(self):
        with self.assertRaises(IntegrityError):
            Question.objects.create(question_text="", pub_date=timezone.now())


# Generated by CodiumAI
class TestChoice(TestCase):

    #  Creating a Choice object with valid parameters should successfully create a new Choice instance.
    def test_create_choice_with_valid_parameters(self):
        question = Question.objects.create(question_text="Test Question", pub_date=timezone.now())
        choice = Choice.objects.create(question=question, choice_text="Test Choice", votes=0)
        assert isinstance(choice, Choice)

    #  Calling str() on a Choice object should return the choice_text attribute.
    def test_str_method_returns_choice_text_attribute(self):
        question = Question.objects.create(question_text="Test Question", pub_date=timezone.now())
        choice = Choice.objects.create(question=question, choice_text="Test Choice", votes=0)
        assert str(choice) == "Test Choice"

    #  Calling votes() on a Choice object should return the votes attribute.
    def test_votes_method_returns_votes_attribute(self):
        question = Question.objects.create(question_text="Test Question", pub_date=timezone.now())
        choice = Choice.objects.create(question=question, choice_text="Test Choice", votes=5)
        assert choice.votes == 5

    #  Creating a Choice object with a choice_text parameter that exceeds 200 characters should raise a ValidationError.
    def test_create_choice_with_long_choice_text_raises_validation_error(self):
        question = Question.objects.create(question_text="Test Question", pub_date=timezone.now())
        long_choice_text = "a" * 201
        with pytest.raises(DataError):
            Choice.objects.create(question=question, choice_text=long_choice_text, votes=0)

    def test_create_choice_with_valid_parameter(self):
        question = Question.objects.create(question_text="Test Question", pub_date=timezone.now())
        choice = Choice.objects.create(question=question, choice_text="Test Choice", votes=0)
        assert isinstance(choice, Choice)

    def test_create_choice_with_negative_votes_raises_check_constraint_error(self):
        question = Question.objects.create(question_text="Test Question", pub_date=timezone.now())
        with pytest.raises(IntegrityError):
            Choice.objects.create(question=question, choice_text="Test Choice", votes=-1)

    def test_create_choice_with_empty_choice_text_raises_check_constraint_error(self):
        question = Question.objects.create(question_text="Test Question", pub_date=timezone.now())
        with pytest.raises(IntegrityError):
            Choice.objects.create(question=question, choice_text="", votes=0)


# Generated by CodiumAI
class QuestionIndexViewTests(TestCase):
    def test_no_question(self):
        """
        :return: True if no questions msg is displayed, else False
        """
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available")
        self.assertQuerySetEqual(response.context["latest_questions"], [])

    def test_past_questions(self):
        """
        :return: True if past published questions are displayed, else False
        """

        question = create_question("test", days=-30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(response.context["latest_questions"], [question])

    def test_future_questions(self):
        """
        :return: True if future published questions are not displayed, else False
        """
        create_question("test", days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(response.context["latest_questions"], [])
        self.assertContains(response, "No polls are available")

    def test_future_and_past_questions(self):
        """
        :return: True if both future published questions are not displayed and past ones are , else False
        """
        question = create_question("test1", days=-30)
        create_question("test2", days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(response.context["latest_questions"], [question])

    def test_multiple_past_questions(self):
        """
        :return: True if multiple questions are displayed from most recent ones, else False
        """
        question1 = create_question("test1", -30)
        question2 = create_question("test2", -10)
        response = self.client.get(reverse("polls:index"))

        self.assertQuerySetEqual(response.context["latest_questions"], [question2, question1])


# Generated by CodiumAI
class DetailViewTest(TestCase):
    # Context of DetailView is equal to the Question object which corresponds to it
    def test_past_question_context(self):
        question = create_question("test1", days=-30)
        response = self.client.get(reverse("polls:detail", args=(question.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["object"], question)

    # Future question is not visualized and raises error 404
    def test_future_question_status_code(self):
        question = create_question(question_text="Test", days=5)
        response = self.client.get(reverse("polls:detail", args=(question.id,)))
        self.assertEqual(response.status_code, 404)

    # Invalid question raises error 404
    def test_no_question_status_code(self):
        response = self.client.get(reverse("polls:detail", args=(1,)))
        self.assertEqual(response.status_code, 404)

    # View displays all valid information
    def test_displays_all_information(self):
        question = create_question("test", -5)
        choice1 = Choice.objects.create(question=question, choice_text="Test1", votes=0)
        choice2 = Choice.objects.create(question=question, choice_text="Test2", votes=5)
        response = self.client.get(reverse("polls:detail", args=(question.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, question.question_text)
        self.assertContains(response, choice1.choice_text)
        self.assertContains(response, choice2.choice_text)


# Generated by CodiumAI
class TestResultsView(TestCase):
    #  Renders the 'polls/results.html' template with the context containing the question object.
    def test_renders_template_with_question_object(self):
        question = Question.objects.create(question_text="Test Question", pub_date=timezone.now())
        response = self.client.get(reverse('polls:results', args=(question.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'polls/results.html')
        self.assertEqual(response.context['question'], question)

    #  Returns an HTTP 404 response if the question with the given ID does not exist.
    def test_returns_404_if_question_does_not_exist(self):
        response = self.client.get(reverse('polls:results', args=(1,)))
        self.assertEqual(response.status_code, 404)

    #  Returns an HTTP 404 response if the question has a pub_date in the future.
    def test_returns_404_if_question_has_future_pub_date(self):
        question = Question.objects.create(question_text="Test Question",
                                           pub_date=timezone.now() + datetime.timedelta(days=1))
        response = self.client.get(reverse('polls:results', args=(question.id,)))
        self.assertEqual(response.status_code, 404)

    # Returns view with suitable message if the question has no choices.
    def test_message_if_question_has_no_choices(self):
        question = Question.objects.create(question_text="Test Question", pub_date=timezone.now())
        response = self.client.get(reverse('polls:results', args=(question.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No choices available")

    def test_display_question_choices_and_votes(self):
        # Create a question
        question = Question.objects.create(question_text="Test Question", pub_date=timezone.now())
        choice1 = question.choice_set.create(question=question, choice_text="Choice 1", votes=5)
        choice2 = question.choice_set.create(question=question, choice_text="Choice 2", votes=1)
        response = self.client.get(reverse('polls:results', args=(question.id,)))
        text1 = f"{choice1.choice_text} -- {choice1.votes} votes"
        text2 = f"{choice2.choice_text} -- {choice2.votes} vote"

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, question.question_text)
        self.assertContains(response, text1)
        self.assertContains(response, text2)


# Generated by CodiumAI
class TestChoiceForm(TestCase):
    def test_choice_form_valid_input(self):
        form_data = {
            'choice_text': 'Valid choice',
            'votes': 10
        }
        form = ChoiceForm(data=form_data)
        assert form.is_valid()

    def test_choice_form_initial_votes(self):
        form_data = {
            'choice_text': 'Valid choice',
        }
        form = ChoiceForm(data=form_data)
        assert not form.is_valid()

    def test_choice_form_empty_choice_text(self):
        form_data = {
            'choice_text': '',
            'votes': 10
        }
        form = ChoiceForm(data=form_data)
        assert not form.is_valid()

    def test_choice_form_negative_votes(self):
        form_data = {
            'choice_text': 'Valid choice',
            'votes': -10
        }
        form = ChoiceForm(data=form_data)
        assert not form.is_valid()

    def test_choice_form_saves_new_choice_object_with_valid_input(self):
        # Create a question object
        question = Question.objects.create(question_text="Test Question")

        # Create a form instance with valid input
        form_data = {
            'choice_text': 'Test Choice',
            'votes': 0
        }
        form = ChoiceForm(data=form_data)

        # Set the question field to the created question object
        form.instance.question = question

        # Check if the form is valid
        assert form.is_valid() == True

        # Save the form
        choice = form.save()

        # Check if the choice object is saved with the correct values
        assert choice.choice_text == 'Test Choice'
        assert choice.votes == 0
        assert choice.question == question

    def test_choice_form_does_not_save_with_empty_choice_text(self):
        form_data = {'choice_text': ''}
        form = ChoiceForm(data=form_data)
        assert not form.is_valid()
        assert 'choice_text' in form.errors

    def test_choice_form_does_not_save_with_negative_votes(self):
        form_data = {
            'choice_text': 'Option 1',
            'votes': -1
        }
        form = ChoiceForm(data=form_data)
        assert not form.is_valid()
        assert 'votes' in form.errors

    def test_choice_form_not_valid_with_long_choice_text(self):
        form_data = {
            'choice_text': 'a' * 201,
            'votes': 0
        }
        form = ChoiceForm(data=form_data)
        assert not form.is_valid()

    def test_choice_form_valid_choice_text_length(self):
        form_data = {
            'choice_text': 'a' * 200,
            'votes': 0
        }
        form = ChoiceForm(data=form_data)
        assert form.is_valid()


# Generated by CodiumAI
class TestQuestionCreateView(TestCase):

    #  User can access the question creation form
    def test_user_can_access_question_creation_form(self):
        response = self.client.get(reverse('polls:question_form'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'polls/question_form.html')

    #  User can submit a valid question form
    def test_user_can_submit_valid_question_form(self):
        response = self.client.post(reverse('polls:question_form'),
                                    data={'question_text': 'Test question', 'pub_date': '2022-01-01T00:00',
                                          'exp_date': '2022-01-07T00:00'})
        self.assertEqual(response.status_code, 302)

    # Question form creates object with given data
    def test_question_create_view_valid_data(self):
        response = self.client.post(reverse('polls:question_form'),
                                    data={'question_text': 'Test question', 'pub_date': '2022-01-01T00:00',
                                          'exp_date': '2022-01-07T00:00'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual('Test question', Question.objects.last().question_text)
        self.assertEqual(timezone.datetime(2022, 1, 1, 0, 0), Question.objects.last().pub_date)
        self.assertEqual(timezone.datetime(2022, 1, 7, 0, 0), Question.objects.last().exp_date)

    #  User is redirected to the choice creation form after submitting a valid question form
    def test_user_redirected_to_choice_creation_form_after_submitting_valid_question_form(self):
        response = self.client.post(reverse('polls:question_form'),
                                    data={'question_text': 'Test question', 'pub_date': '2022-01-01T00:00',
                                          'exp_date': '2022-01-07T00:00'})
        self.assertRedirects(response, reverse('polls:choice_form', kwargs={'pk': Question.objects.last().id}))

    #  User cannot submit an invalid question form
    def test_user_cannot_submit_invalid_question_form(self):
        response = self.client.post(reverse('polls:question_form'),
                                    data={'question_text': '', 'pub_date': '2022-01-01T00:00',
                                          'exp_date': '2022-01-07T00:00'})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'question_text', 'This field is required.')


# Generated by CodiumAI
class TestChoiceCreateView(TestCase):
    #  User cannot access the choice creation form without submitting a valid question form
    def test_user_cannot_access_choice_creation_form_without_submitting_valid_question_form(self):
        response = self.client.get(reverse('polls:choice_form', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 404)

    #  User can successfully create a new choice for a question
    def test_user_can_create_choice(self):
        # Arrange
        question = Question.objects.create(question_text="Test Question")
        # Set the session variable
        session = self.client.session
        session['question_id_access'] = question.id
        session.save()

        form_data = {
            'choice_text': 'New Choice',
            'votes': 0
        }
        response = self.client.post(reverse(viewname='polls:choice_form', args=[question.id,]), data=form_data)

        # Assert
        assert response.status_code == 302
        assert Choice.objects.filter(choice_text='New Choice', question=question, votes=0).exists()

    #  User is redirected to new choice form page after successfully creating a new choice
    def test_user_redirected_to_detail_page(self):
        # Arrange
        question = Question.objects.create(question_text="Test Question")
        # Set the session variable
        session = self.client.session
        session['question_id_access'] = question.id
        session.save()

        form_data = {
            'choice_text': 'New Choice',
            'votes': 0
        }
        # Act
        response = self.client.post(reverse(viewname='polls:choice_form', args=[question.id,]), data=form_data)

        # Assert
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('polls:choice_form', args=[question.id,]))

    #  User cannot access the form to create a new choice if session does not contain question_id_access
    def test_user_cannot_access_form_if_session_does_not_contain_question_id_access(self):
        # Arrange
        question = Question.objects.create(question_text="Test Question")

        # Set the session variable
        self.client.session['question_id_access'] = None

        # Send a POST request to create a choice with an empty choice_text field
        response = self.client.post(reverse('polls:choice_form', kwargs={'pk': question.id}),
                                    {'choice_text': '', 'votes': 0})

        self.assertEqual(response.status_code, 404)

    #  User cannot access the form to create a new choice if session
    #  contains question_id_access different from the one in the URL
    def test_user_cannot_access_form_if_session_contains_different_question_id_access(self):
        # Arrange
        question = Question.objects.create(question_text="Test Question")

        # Set the session variable
        self.client.session['question_id_access'] = question.id

        # Send a POST request to create a choice with an empty choice_text field
        response = self.client.post(reverse('polls:choice_form', kwargs={'pk': question.id - 1}),
                                    {'choice_text': '', 'votes': 0})

        self.assertEqual(response.status_code, 404)

    def test_empty_choice_text_field(self):
        # Create a question
        question = Question.objects.create(question_text="Test Question")

        # Set the session variable
        self.client.session['question_id_access'] = question.id

        # Send a POST request to create a choice with an empty choice_text field
        response = self.client.post(reverse('polls:choice_form', kwargs={'pk': question.id}),
                                    {'choice_text': '', 'votes': 0})

        # Assert that the response status code is 400 (failure)
        self.assertEqual(response.status_code, 404)

        # Assert that the choice was not created
        assert Choice.objects.filter(question=question).count() == 0

    def test_negative_votes(self):
        # Create a question
        question = Question.objects.create(question_text="Test Question", pub_date=timezone.now(), exp_date=timezone.now() + timezone.timedelta(7))

        # Set the session variable for question access
        self.client.session['question_id_access'] = question.id

        # Send a POST request to create a choice with negative votes
        response = self.client.post(reverse('polls:choice_form', kwargs={'pk': question.id}), {'choice_text': 'Test Choice', 'votes': -1})

        # Assert that the response is a 404 error
        self.assertEqual(response.status_code, 404)

        # Assert that no choices were created
        self.assertEqual(Choice.objects.count(), 0)

    def test_duplicate_choice_text(self):
        question = Question.objects.create(question_text="Test Question")
        # Create a choice with the same choice_text as an existing choice for the same question
        existing_choice = Choice.objects.create(question=question, choice_text="Test Choice")
        # Set the session variable
        session = self.client.session
        session['question_id_access'] = question.id
        session.save()

        # Create a choice with a different choice_text for the same question
        form_data = {'choice_text': "Another Choice", 'votes': 0}
        response = self.client.post(reverse(viewname='polls:choice_form', args=[question.id, ]), data=form_data)
        self.assertEqual(response.status_code, 302)

        # Create a choice with the same choice_text for the same question
        form_data = {'choice_text': "Test Choice", 'votes': 0}
        with pytest.raises(IntegrityError):
            self.client.post(reverse(viewname='polls:choice_form', args=[question.id, ]), data=form_data)
