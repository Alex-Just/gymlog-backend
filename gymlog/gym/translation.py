from modeltranslation.translator import TranslationOptions
from modeltranslation.translator import translator

from .models import Exercise


class ExerciseTranslationOptions(TranslationOptions):
    fields = ("name",)


translator.register(Exercise, ExerciseTranslationOptions)
