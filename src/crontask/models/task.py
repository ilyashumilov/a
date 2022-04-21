from django.db import models

from main.models import Blogger


class TaskCron(models.Model):
    blogger = models.ForeignKey(Blogger, on_delete=models.CASCADE, related_name="cron_tasks")
    created_at = models.DateTimeField(auto_now_add=True)
    done = models.BooleanField(default=False)

    class Meta:
        db_table = 'hype_task_cron'
