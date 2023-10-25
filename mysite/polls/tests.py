import datetime
import pytest

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from django.db.utils import DataError, IntegrityError
from django.db import models
from .models import Question, Choice


def create_question(question_text, days):
    """
    Function for creating question cases with publish date offset
    :param question_text: text
    :param days: offset from now()
    :return: Question object
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


# Create your tests here.
class QuestionModelTests(TestCase):
    def test_was_published_recently_future_date(self):
        """
        was_published_recently() returns False if question.pub_date is in the future
        :return: True if future date is not recent, else False
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)

        self.assertIs(future_question.was_published_recently(), False, msg="Future date test failed")

    def test_was_published_recently_recent_question(self):
        """
        was_published_recently() returns True if question.pub_date is within the last day
        :return: True if question within day past is recent, else False
        """
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)

        self.assertIs(recent_question.was_published_recently(), True)


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
        response = self.client.get(reverse('polls:results', args=(question.id, )))
        text1 = f"{choice1.choice_text} -- {choice1.votes} votes"
        text2 = f"{choice2.choice_text} -- {choice2.votes} vote"

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, question.question_text)
        self.assertContains(response, text1)
        self.assertContains(response, text2)

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

    def test_create_choice_with_valid_parameters(self):
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
