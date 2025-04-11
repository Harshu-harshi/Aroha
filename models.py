from django.db import models

class GeneratedRecipe(models.Model):
    ingredients = models.TextField()
    recipe = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Recipe generated from {self.ingredients[:50]}..."