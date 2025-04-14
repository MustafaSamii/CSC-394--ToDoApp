from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError

class ToDo(models.Model):
    STATUS_CHOICES = [
        ('Not Started', 'Not Started'),
        ('In Progress', 'In Progress'),
        ('Paused', 'Paused'),
        ('Completed', 'Completed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(blank=True)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Not Started')
    category = models.CharField(max_length=100, blank=True, null=True)
    # New fields:
    due_date = models.DateField(blank=True, null=True)
    team = models.ForeignKey('Team', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    start_time = models.DateTimeField(blank=True, null=True)
    elapsed_time = models.DurationField(blank=True, null=True)

    def __str__(self):
        return self.name
    
    def clean(self):
        if not self.name or not self.due_date:
            raise ValidationError('To-Do Name and Due-Date are required.')

    def save(self, *args, **kwargs):
        self.clean() 
        super().save(*args, **kwargs) 

    def get_total_elapsed(self):
        """Return a timedelta of total elapsed time."""
        total = self.elapsed_time or timezone.timedelta(0)
        if self.status == 'In Progress' and self.start_time:
            total += timezone.now() - self.start_time
        return total

    @property
    def total_seconds_elapsed(self):
        """Return total elapsed time in seconds as a float."""
        return self.get_total_elapsed().total_seconds()

    @property
    def formatted_elapsed(self):
        """Return the total elapsed time as a formatted string H:MM:SS."""
        total_seconds = int(self.get_total_elapsed().total_seconds())
        hrs = total_seconds // 3600
        mins = (total_seconds % 3600) // 60
        secs = total_seconds % 60
        return f"{hrs}:{mins:02d}:{secs:02d}"

class Team(models.Model):
    name = models.CharField()
    description = models.TextField()
    members = models.ManyToManyField(User, blank=True)

    def __str__(self):
        return self.name

    def clean(self):
        if not self.name or not self.description:
            raise ValidationError('Both Team Name and Description are required.')

    def save(self, *args, **kwargs):
        self.clean() 
        super().save(*args, **kwargs) 
