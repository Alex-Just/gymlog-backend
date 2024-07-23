import json
from pathlib import Path

from django.core.management.base import BaseCommand
from django.core.management.base import CommandError

from gymlog.gym.forms import ExerciseForm
from gymlog.gym.models import Exercise


class Command(BaseCommand):
    help = "Import exercises from a JSON file."

    def add_arguments(self, parser):
        parser.add_argument(
            "filepath",
            type=str,
            help="The path to the JSON file containing exercises.",
        )

    def handle(self, *args, **options):
        filepath = Path(options["filepath"])

        if not filepath.exists():
            error_message = f'File "{filepath}" does not exist.'
            raise CommandError(error_message)

        with filepath.open() as file:
            data = json.load(file)

        for exercise_id, exercise_data in data.items():
            exercise_data_cleaned = {
                "name": exercise_data["title"].strip(),
                "name_en": exercise_data["title"].strip(),
                "name_ru": exercise_data.get("ru_title", "").strip(),
                "name_es": exercise_data.get("es_title", "").strip(),
                "exercise_type": exercise_data["exercise_type"],
                "equipment": exercise_data["equipment_category"],
                "primary_muscle_group": exercise_data["muscle_group"],
                "other_muscles": exercise_data.get("other_muscles", []),
                "small_image": exercise_data.get("thumbnail"),
                "large_image": exercise_data.get("web_feature_image"),
            }

            form = ExerciseForm(data=exercise_data_cleaned)
            if form.is_valid():
                Exercise.objects.update_or_create(
                    name=form.cleaned_data["name"],
                    defaults=form.cleaned_data,
                )
            else:
                self.stderr.write(
                    f"Error in data for exercise {exercise_id}: {form.errors}",
                )

        self.stdout.write(self.style.SUCCESS("Successfully imported exercises"))
