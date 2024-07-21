from django.db import models


class Report(models.Model):
    STATUS_CHOICES = [
        ("NEW", "New"),
        ("IN_PROGRESS", "In Progress"),
        ("RESOLVED", "Resolved"),
    ]
    VERIFY_CHOICES = [
        ("T", "True"),
        ("F", "False"),
    ]

    post_title = models.CharField(max_length=30)
    building_address = models.CharField(max_length=100)
    landlord_name = models.CharField(max_length=30)
    report = models.TextField(max_length=200)
    time_stamp = models.DateTimeField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="NEW",
    )
    verify = models.TextField(
        choices=VERIFY_CHOICES,
        default="F",
    )
    feedback = models.TextField(
        max_length=200,
        default=" ",
    )
    user = models.CharField(
        max_length=30,
        default="ANONYMOUS",
    )


    def __str__(self):
        return f"{self.post_title}"

