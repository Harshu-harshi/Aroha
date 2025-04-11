from django.apps import AppConfig
from django.conf import settings
import openai


class RandomRecipeGeneratorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'random_recipe_generator'
    def ready(self):
        if settings.OPENAI_API_KEY:
            try:
                client = OpenAI(api_key=settings.OPENAI_API_KEY)
                client.models.list()  # Test the API key
            except Exception as e:
                print(f"Warning: OpenAI API key validation failed: {str(e)}")