import json
from io import BytesIO
from pathlib import Path

import requests
from django.core.files import File
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from django.db import IntegrityError
from django.db import transaction

from gymlog.gym.forms import ExerciseForm
from gymlog.gym.models import Exercise

TIMEOUT = 10
HTTP_OK = 200


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

        total_exercises = len(data)
        self.stdout.write(f"Total exercises to import: {total_exercises}")

        for index, (ex_id, exercise_data) in enumerate(data.items(), start=1):
            self.stdout.write(
                f"Processing exercise {index}/{total_exercises} (ID: {ex_id})...",
            )
            self.process_exercise(ex_id, exercise_data)

        self.stdout.write(self.style.SUCCESS("Successfully imported all exercises"))

    def process_exercise(self, ex_id, exercise_data):
        exercise_data_cleaned = self.clean_exercise_data(exercise_data)
        form = ExerciseForm(data=exercise_data_cleaned)

        if not form.is_valid():
            self.stderr.write(f"Error in data for exercise {ex_id}: {form.errors}")
            return
        try:
            with transaction.atomic():
                exercise, _ = Exercise.objects.update_or_create(
                    name=form.cleaned_data["name"],
                    defaults=form.cleaned_data,
                )
                self.handle_images(exercise, ex_id, exercise_data)
                exercise.save()
                self.stdout.write(
                    self.style.SUCCESS(f"Successfully processed exercise {ex_id}"),
                )
        except IntegrityError as e:
            self.stderr.write(
                f"Database error while processing exercise {ex_id}: {e}",
            )

    @staticmethod
    def clean_exercise_data(exercise_data):
        return {
            "name": exercise_data["title"].strip(),
            "name_en": exercise_data["title"].strip(),
            "name_ru": exercise_data.get("ru_title", "").strip(),
            "name_es": exercise_data.get("es_title", "").strip(),
            "exercise_type": exercise_data["exercise_type"],
            "equipment": exercise_data["equipment_category"],
            "primary_muscle_group": exercise_data["muscle_group"],
            "other_muscles": exercise_data.get("other_muscles", []),
        }

    def handle_images(self, exercise, ex_id, exercise_data):
        if "thumbnail" in exercise_data and not exercise.small_image:
            self.download_and_save_image(
                exercise,
                ex_id,
                exercise_data["thumbnail"],
                "small_image",
            )

        if "web_feature_image" in exercise_data and not exercise.large_image:
            self.download_and_save_image(
                exercise,
                ex_id,
                exercise_data["web_feature_image"],
                "large_image",
            )

    def download_and_save_image(self, exercise, ex_id, url, image_field):
        try:
            response = requests.get(url, timeout=TIMEOUT)
            if response.status_code == HTTP_OK:
                image_name = f"{ex_id}_{image_field}.jpg"
                image_file = File(BytesIO(response.content))
                getattr(exercise, image_field).save(image_name, image_file)
                self.stdout.write(
                    f"Downloaded and saved {image_field} for exercise {ex_id}",
                )
        except requests.RequestException as e:
            self.stderr.write(
                f"Error downloading {image_field} for exercise {ex_id}: {e}",
            )
