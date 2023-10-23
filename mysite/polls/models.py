import datetime

from django.db import models
from django.db.models.functions import Length
from django.utils import timezone
from django.core import validators

models.CharField.register_lookup(Length)


# The Question class is a Django model that represents a question
# with a text and a publication date.
class Question(models.Model):

    question_text = models.CharField(max_length=200, unique=True)
    pub_date = models.DateTimeField('date published')

    def __str__(self):
        return self.question_text

    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(question_text__length__gte=1), name="question_text_length")
        ]

    def was_published_recently(self, days=1):
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


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200, unique=True)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text

    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(choice_text__length__gte=1), name="choice_text_length"),
            models.CheckConstraint(check=models.Q(votes__gte=0), name="negative votes number")
        ]
