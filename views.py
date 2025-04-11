from openai import OpenAI, AuthenticationError
from django.conf import settings
from django.shortcuts import render, redirect
from .models import GeneratedRecipe
from django.contrib import messages
import logging

logger = logging.getLogger(__name__)

def get_openai_client():
    """Helper function to create and verify OpenAI client"""
    if not settings.OPENAI_API_KEY:
        raise ValueError("OpenAI API key is not configured")
    
    try:
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        # Test the client with a simple request
        client.models.list()  # This verifies the API key is valid
        return client
    except AuthenticationError as e:
        logger.error(f"OpenAI authentication failed: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error initializing OpenAI client: {str(e)}")
        raise

def generate_recipe_prompt(ingredients, dietary_preferences=None, cuisine_type=None, meal_type=None):
    prompt = f"Create a detailed recipe using primarily these ingredients: {ingredients}.\n"
    
    if dietary_preferences:
        prompt += f"The recipe should be {dietary_preferences}.\n"
    if cuisine_type:
        prompt += f"The recipe should be {cuisine_type} style.\n"
    if meal_type:
        prompt += f"This is for a {meal_type} meal.\n"
    
    prompt += """
    Provide the recipe in this format:
    Recipe Name: [Creative recipe name]
    Description: [Brief description of the dish]
    Ingredients: [List all ingredients with quantities]
    Instructions: [Numbered steps for preparation]
    Cooking Time: [Estimated time]
    Difficulty Level: [Easy/Medium/Hard]
    Serving Size: [Number of servings]
    """
    
    return prompt

def index(request):
    if request.method == 'POST':
        ingredients = request.POST.get('ingredients', '')
        dietary_preferences = request.POST.get('dietary_preferences', '')
        cuisine_type = request.POST.get('cuisine_type', '')
        meal_type = request.POST.get('meal_type', '')
        
        if not ingredients:
            messages.error(request, "Please enter at least one ingredient")
            return redirect('index')
        
        try:
            client = get_openai_client()
            prompt = generate_recipe_prompt(ingredients, dietary_preferences, cuisine_type, meal_type)
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional chef and recipe creator."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            recipe = response.choices[0].message.content
            
            GeneratedRecipe.objects.create(
                ingredients=ingredients,
                recipe=recipe
            )
            
            return render(request, 'recipe_result.html', {
                'recipe': recipe,
                'ingredients': ingredients
            })
            
        except AuthenticationError:
            messages.error(request, "Authentication failed with OpenAI. Please check the API key configuration.")
            logger.error("OpenAI authentication failed")
        except Exception as e:
            messages.error(request, f"An error occurred while generating the recipe: {str(e)}")
            logger.error(f"Recipe generation error: {str(e)}")
        return redirect('index')
    
    return render(request, 'index.html')

def recipe_history(request):
    recipes = GeneratedRecipe.objects.all().order_by('-created_at')
    return render(request, 'recipe_history.html', {'recipes': recipes})

def documentation(request):
    return render(request, 'documentation.html')