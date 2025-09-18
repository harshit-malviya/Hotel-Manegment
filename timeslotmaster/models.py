
from django.db import models

class TimeslotMaster(models.Model):
	id = models.AutoField(primary_key=True, unique=True)
	name = models.CharField(max_length=100)
	time = models.PositiveIntegerField(help_text="Enter hours")

	def __str__(self):
		return f"{self.name} ({self.time} hrs)"
