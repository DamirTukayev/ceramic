from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, time
# Create your models here.

class Visit(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    date = models.DateField(auto_now_add=True)
    arrival_time = models.TimeField(auto_now_add=True)
    leaving_time = models.TimeField(blank=True, null=True)

    @property
    def working_time(self):
        if self.arrival_time and self.leaving_time:
            # Calculate the time difference
            arrival_datetime = datetime.combine(datetime.today(), self.arrival_time)
            leaving_datetime = datetime.combine(datetime.today(), self.leaving_time)
            duration = leaving_datetime - arrival_datetime

            # Calculate the hours and minutes
            total_minutes = int(duration.total_seconds() / 60)
            hours = total_minutes // 60
            minutes = total_minutes % 60

            # Format the working time as HH:MM
            formatted_time = f'{hours:02}:{minutes:02}'

            return formatted_time

        return 0  # If either arrival_time or leaving_time is missing, return None
    
    @property
    def lateness(self):
        if self.arrival_time and self.arrival_time > time(hour=9):
            # Convert time objects to datetime objects
            arrival_datetime = datetime.combine(datetime.today(), self.arrival_time)
            target_time = datetime.combine(datetime.today(), time(hour=9))

            # Calculate the lateness
            lateness = arrival_datetime - target_time
            total_minutes = int(lateness.total_seconds() / 60)
            hours = total_minutes // 60
            minutes = total_minutes % 60

            # Format the working time as HH:MM
            formatted_time = f'{hours:02}:{minutes:02}'

            return formatted_time

        return 0
    
    @property
    def recycling(self):
        if self.leaving_time and self.leaving_time > time(hour=18):
            # Calculate the working time
            working_time_minutes = int(self.working_time.split(':')[0]) * 60 + int(self.working_time.split(':')[1])

            if working_time_minutes - 60 < 8 * 60:
                return 0

            # Convert time objects to datetime objects
            leaving_datetime = datetime.combine(datetime.today(), self.leaving_time)
            target_time = datetime.combine(datetime.today(), time(hour=18))

            # Calculate the recycling time
            recycling = leaving_datetime - target_time
            total_minutes = int(recycling.total_seconds() / 60)
            hours = total_minutes // 60
            minutes = total_minutes % 60

            # Format the recycling time as HH:MM
            formatted_time = f'{hours:02}:{minutes:02}'

            return formatted_time

        return 0
