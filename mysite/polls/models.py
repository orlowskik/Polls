import datetime

from django.db import models
from django.db.models.functions import Length
from django.utils import timezone
from django.urls import reverse
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from .validators import validate_votes, validate_text, validate_userid

models.CharField.register_lookup(Length)


# The `Question` class represents a model for a question with text, publication date, and expiration date, and includes
# methods for checking if the question was published recently.
class Question(models.Model):
    question_text = models.CharField(max_length=200, unique=True, validators=[validate_text])
    pub_date = models.DateTimeField('date published', default=timezone.now)
    exp_date = models.DateTimeField('expiration date', default=timezone.now() + timezone.timedelta(7))

    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(question_text__length__gte=1), name="question_text_length"),
            models.CheckConstraint(check=models.Q(exp_date__gte=models.F("pub_date")), name="Expiration date")
        ]

    def __str__(self):
        return self.question_text

    def was_published_recently(self, days=1):
        """
        The function checks if an object was published within a certain number of days.

        :param days: The "days" parameter is an optional parameter that specifies the number of days to consider when
        determining if an object was published recently. By default, it is set to 1 day, defaults to 1 (optional)
        """
        """
        Returns True if the question was published within the specified number of days, False otherwise.
        """
        if self.pub_date is None:
            return False

        if not isinstance(days, int) or days <= 0:
            raise ValueError("Days must be a positive integer")

        now = timezone.now()
        if isinstance(days, float):
            days = int(days)

        if days < 0:
            return False

        return now - datetime.timedelta(days=days) < self.pub_date <= now


# The Choice class represents a choice for a question in a poll, with attributes for the choice text, number of votes,
# and a foreign key to the associated question.
class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200, validators=[validate_text])
    votes = models.IntegerField(default=0, validators=[validate_votes])

    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(choice_text__length__gte=1), name="choice_text_length"),
            models.CheckConstraint(check=models.Q(votes__gte=0), name="negative votes number"),
            models.UniqueConstraint(fields=['question', 'choice_text'], name='Unique answers to question'),
        ]

    def __str__(self):
        return self.choice_text

    def clean(self):
        """
        The function checks if a choice already exists in a question and raises a validation error if it does.
        """
        try:
            if self.question.choice_set.filter(choice_text=self.choice_text).count():
                raise ValidationError('Choice already exists')
        except ObjectDoesNotExist:
            pass

    def get_absolute_url(self):
        return reverse('polls:detail', args=[self.question.id])


# The User class is a model that represents a user with a username and a unique userid.
class User(models.Model):
    username = models.CharField(max_length=20, default='Guest', validators=[validate_text])
    userid = models.CharField(unique=True, max_length=20, validators=[validate_userid])

    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(username__length__gte=1), name="username_length"),
            models.CheckConstraint(check=models.Q(userid__length=20), name="userid_length"),
        ]


# The Vote class represents a vote made by a user on a specific question and choice, with a unique constraint on the
# combination of question and user.
class Vote(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now())

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['question', 'user'], name='Unique user votes'),
        ]

    def clean(self):
        if self.date >= timezone.now():
            raise ValidationError('Future date not permitted')
        try:
            if self.choice not in self.question.choice_set.all():
                raise ValidationError('Choice does not exist for this question')
        except ObjectDoesNotExist:
            pass

