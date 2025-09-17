from django.db import models

class TimeEntry(models.Model):
    entry_id = models.CharField(max_length=50)
    name = models.CharField(max_length=100)
    hours = models.DecimalField(max_digits=5, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Time Entries"

    def __str__(self):
        return f"{self.name} - {self.hours} hours"
