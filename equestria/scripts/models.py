from django.db import models

# Create your models here.


class Process(models.Model):

    process_id = models.IntegerField()
    input_file = models.FilePathField()
    output_file = models.FilePathField()
    executing = models.BooleanField()
