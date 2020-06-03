from django.test import TestCase
from django import forms
from scripts.forms import (
    ProfileSelectForm,
    AlterDictionaryForm,
    ProjectCreateForm,
    ParameterForm,
    ChoiceParameterAdminForm,
)
from scripts.models import (
    Script,
    Profile,
    Pipeline,
    BaseParameter,
    BooleanParameter,
    StaticParameter,
    StringParameter,
    Choice,
    ChoiceParameter,
    TextParameter,
    IntegerParameter,
    FloatParameter,
)
from unittest.mock import patch
from django.contrib.auth.models import User


class ParameterMock:
    def __init__(self, name, typ):
        self.name = name
        self.type = typ

    def get_default_value(self):
        return None


class TestForms(TestCase):
    """Class to test forms."""

    fixtures = ["uploadDB3"]

    def setUp(self):
        """Set up data for form tests."""
        self.profiles = [Profile.objects.create(), Profile.objects.create()]
        self.bool_base = BaseParameter.objects.create(
            name="bool", type=BaseParameter.BOOLEAN_TYPE
        )
        self.bool_param = BooleanParameter.objects.create(base=self.bool_base)

        self.static_base = BaseParameter.objects.create(
            name="static", type=BaseParameter.STATIC_TYPE
        )
        self.static_param = StaticParameter.objects.create(
            base=self.static_base
        )

        self.string_base = BaseParameter.objects.create(
            name="string", type=BaseParameter.STRING_TYPE
        )
        self.string_param = StringParameter.objects.create(
            base=self.string_base
        )

        self.choice_base = BaseParameter.objects.create(
            name="choice", type=BaseParameter.CHOICE_TYPE
        )
        self.choice_param = ChoiceParameter.objects.create(
            base=self.choice_base
        )
        self.choice = Choice.objects.create(
            corresponding_choice_parameter=self.choice_param, value="Hi"
        )

        self.text_base = BaseParameter.objects.create(
            name="text", type=BaseParameter.TEXT_TYPE
        )
        self.text_param = TextParameter.objects.create(base=self.text_base)

        self.int_base = BaseParameter.objects.create(
            name="int", type=BaseParameter.INTEGER_TYPE
        )
        self.int_param = IntegerParameter.objects.create(base=self.int_base)

        self.float_base = BaseParameter.objects.create(
            name="float", type=BaseParameter.FLOAT_TYPE
        )
        self.float_param = FloatParameter.objects.create(base=self.float_base)

        self.user = User.objects.create_user(
            "john", "lennon@thebeatles.com", "johnpassword"
        )

        self.pipelines = Pipeline.objects.all()

    def test_ProfileSelectForm_creation(self):
        """Test ProfileSelectForm creation."""
        form = ProfileSelectForm(
            profiles=self.profiles, data={"profile": self.profiles[0]}
        )
        self.assertEquals(
            len(form.fields["profile"].choices), len(self.profiles)
        )
        self.assertTrue(form.is_valid())

    def test_ProfileSelectForm_no_profiles(self):
        """Test ProfileSelectForm with no profiles."""
        form = ProfileSelectForm(
            profiles=[], data={"profile": self.profiles[0]}
        )
        self.assertEquals(len(form.fields["profile"].choices), 0)

        self.assertFalse(form.is_valid())
        self.assertEquals(len(form.errors), 1)

    def test_ProfileSelectForm_no_data(self):
        """Test ProfileSelectForm with no data."""
        form = ProfileSelectForm(profiles=[], data={})

        self.assertFalse(form.is_valid())
        self.assertEquals(len(form.errors), 1)

    def test_AlterDictionaryForm_some_dictionary(self):
        """Test AlterDictionaryForm with some words."""
        form = AlterDictionaryForm(
            data={"dictionary": "This is a simple test string."}
        )

        self.assertTrue(form.is_valid())

    def test_AlterDictionaryForm_no_dictionary(self):
        """Test AlterDictionaryForm with no words."""
        form = AlterDictionaryForm(data={"dictionary": ""})

        self.assertTrue(form.is_valid())

    def test_AlterDictionaryForm_no_data(self):
        """Test AlterDictionaryForm with no data."""
        form = AlterDictionaryForm(data={})
        # self.assertEquals(len(form.errors), 1)
        self.assertTrue(form.is_valid())

    def test_ProjectCreateForm_valid_data(self):
        """Test ProjectCreateForm with valid data."""
        form = ProjectCreateForm(
            user=self.user,
            pipelines=self.pipelines,
            data={
                "project_name": "pName",
                "pipeline": Pipeline.objects.all()[0].id,
            },
        )

        print(form.errors)

        self.assertTrue(form.is_valid())

    def test_ProjectCreateForm_no_data(self):
        """Test ProjectCreateForm with no data."""
        form = ProjectCreateForm(user=self.user, data={})

        self.assertFalse(form.is_valid())
        self.assertEquals(len(form.errors), 2)

    def test_ParameterForm_bool_data(self):
        """Test ParameterForm with bool parameter."""
        form = ParameterForm([self.bool_base])
        self.assertTrue(
            isinstance(form.fields[self.bool_base.name], forms.BooleanField)
        )

    def test_ParameterForm_static_data(self):
        """Test ParameterForm with static parameter."""
        form = ParameterForm([self.static_base])
        self.assertTrue(
            isinstance(form.fields[self.static_base.name], forms.CharField)
        )

    def test_ParameterForm_string_data(self):
        """Test ParameterForm with string parameter."""
        form = ParameterForm([self.string_base])
        self.assertTrue(
            isinstance(form.fields[self.string_base.name], forms.CharField)
        )

    def test_ParameterForm_choice_data(self):
        """Test ParameterForm with choice parameter."""
        form = ParameterForm([self.choice_base])
        self.assertTrue(
            isinstance(form.fields[self.choice_base.name], forms.ChoiceField)
        )
        self.assertEquals(
            form.fields[self.choice_base.name].choices,
            [(self.choice.id, self.choice.value)],
        )

    def test_ParameterForm_text_data(self):
        """Test ParameterForm with text parameter."""
        form = ParameterForm([self.text_base])
        self.assertTrue(
            isinstance(form.fields[self.text_base.name], forms.CharField)
        )

    def test_ParameterForm_int_data(self):
        """Test ParameterForm with integer parameter."""
        form = ParameterForm([self.int_base])
        self.assertTrue(
            isinstance(form.fields[self.int_base.name], forms.IntegerField)
        )

    def test_ParameterForm_float_data(self):
        """Test ParameterForm with float parameter."""
        form = ParameterForm([self.float_base])
        self.assertTrue(
            isinstance(form.fields[self.float_base.name], forms.FloatField)
        )

    def test_ParameterForm_invalid_data(self):
        """Test ParameterForm with invalid parameter."""
        parameter = ParameterMock("invalid_field", 7)
        form = ParameterForm([parameter])
        self.assertFalse(form.is_valid())

    def test_ChoiceParameterAdminForm(self):
        """Test ChoiceParameterAdminForm."""
        pass
