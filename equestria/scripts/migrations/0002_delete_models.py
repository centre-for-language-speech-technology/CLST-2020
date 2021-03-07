from django.db import migrations, models
import django.db.models.deletion


def remove_all_parameters(apps, schema_editor):
    BaseParameter = apps.get_model("scripts", "BaseParameter")
    BaseParameter.objects.all().delete()
    BooleanParameter = apps.get_model("scripts", "BooleanParameter")
    BooleanParameter.objects.all().delete()
    StaticParameter = apps.get_model("scripts", "StaticParameter")
    StaticParameter.objects.all().delete()
    StringParameter = apps.get_model("scripts", "StringParameter")
    StringParameter.objects.all().delete()
    Choice = apps.get_model("scripts", "Choice")
    Choice.objects.all().delete()
    ChoiceParameter = apps.get_model("scripts", "ChoiceParameter")
    ChoiceParameter.objects.all().delete()
    TextParameter = apps.get_model("scripts", "TextParameter")
    TextParameter.objects.all().delete()
    IntegerParameter = apps.get_model("scripts", "IntegerParameter")
    IntegerParameter.objects.all().delete()
    FloatParameter = apps.get_model("scripts", "FloatParameter")
    FloatParameter.objects.all().delete()
    InputTemplate = apps.get_model("scripts", "InputTemplate")
    InputTemplate.objects.all().delete()
    Profile = apps.get_model("scripts", "Profile")
    Profile.objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ('scripts', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(remove_all_parameters),
    ]
