from django import forms

from .models import Exercise


class ExerciseForm(forms.ModelForm):
    class Meta:
        model = Exercise
        fields = [
            "name",
            "exercise_type",
            "equipment",
            "primary_muscle_group",
            "other_muscles",
            "small_image",
            "large_image",
            "name_en",
            "name_ru",
            "name_es",
        ]
