import json
import os

import requests
from django.contrib import auth
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

from .models import BlogPost, Chat

# Charger les variables d'environnement
load_dotenv()

def blog_list(request, *args, **kwargs):
    """
    Affiche la liste des articles de blog.

    Args:
        request: La requête HTTP.

    Returns:
        Une réponse HTTP avec la liste des articles de blog rendue dans le template 'blog_list.html'.
    """
    blogs = BlogPost.objects.all()
    return render(request, 'blog_list.html', {'blogs': blogs})

def blog_detail(request, blog_id):
    """
    Affiche les détails d'un article de blog spécifique.

    Args:
        request: La requête HTTP.
        blog_id: L'identifiant de l'article de blog.

    Returns:
        Une réponse HTTP avec les détails de l'article de blog rendu dans le template 'blog_detail.html'.
    """
    blog = get_object_or_404(BlogPost, pk=blog_id)
    return render(request, 'blog_detail.html', {'blog': blog})

def createBlogPost(request):
    """
    Crée un nouvel article de blog.

    Args:
        request: La requête HTTP.

    Returns:
        Une redirection vers la liste des articles de blog après la création.
        Ou une réponse HTTP avec le formulaire de création d'article rendu dans le template 'createBlogPost.html'.
    """
    if request.method == "POST":
        title = request.POST.get('title')
        content = request.POST.get('content')
        image = request.FILES.get('image')  # Récupération de l'image à partir de request.FILES
        # Création d'une nouvelle instance de BlogPost avec l'image
        new_post = BlogPost(title=title, content=content, publication_date=timezone.now(), image=image)
        new_post.save()  # Enregistrement de l'instance dans la base de données
        return redirect('blog_list')  # Redirection vers la liste des blogs après la création
    return render(request, 'blog/createBlogPost.html')


# Charger la clé API de Hugging Face et l'endpoint personnalisé depuis les variables d'environnement
HF_TOKEN = os.getenv('HF_TOKEN')
HUGGING_FACE_ENDPOINT = os.getenv('HUGGING_FACE_ENDPOINT')

def call_llm(prompt: str):
    """
    Appelle l'API Hugging Face pour générer du texte à partir du prompt.

    Args:
        prompt (str): Le texte d'entrée pour la génération.

    Returns:
        str: Le texte généré par le modèle.
    """
    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 200,
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 50,
            "repetition_penalty": 1.5  # Ajuster la pénalité de répétition pour réduire les répétitions
        }
    }
    try:
        response = requests.post(HUGGING_FACE_ENDPOINT, headers=headers, json=payload)
        response.raise_for_status()
        generated_text = response.json()[0]["generated_text"]
        return generated_text
    except requests.exceptions.RequestException as e:
        return f"Request failed: {e}"

def filter_repetitions(response_text):
    """
    Filtre les répétitions dans le texte généré.

    Args:
        response_text (str): Le texte généré par le modèle.

    Returns:
        str: Le texte filtré sans répétitions.
    """
    sentences = response_text.split('. ')
    unique_sentences = []
    for sentence in sentences:
        if sentence not in unique_sentences:
            unique_sentences.append(sentence)
    return '. '.join(unique_sentences)

@csrf_exempt
def chatbot(request):
    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        message = body.get('message')
        
        response_text = call_llm(message)
        response_text = filter_repetitions(response_text)
        
        return JsonResponse({'message': message, 'response': response_text})
    
    return render(request, 'chatbot.html')


def login(request):
    """
    Gère la connexion des utilisateurs.

    Args:
        request: La requête HTTP.

    Returns:
        Une redirection vers le chatbot après la connexion réussie.
        Ou rend le template 'login.html' avec un message d'erreur en cas d'échec.
    """
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('chatbot')
        else:
            error_message = 'Invalid username or password'
            return render(request, 'login.html', {'error_message': error_message})
    else:
        return render(request, 'login.html')

def register(request):
    """
    Gère l'inscription des utilisateurs.

    Args:
        request: La requête HTTP.

    Returns:
        Une redirection vers le chatbot après l'inscription réussie.
        Ou rend le template 'register.html' avec un message d'erreur en cas d'échec.
    """
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 == password2:
            try:
                user = User.objects.create_user(username, email, password1)
                user.save()
                auth.login(request, user)
                return redirect('chatbot')
            except:
                error_message = 'Error creating account'
                return render(request, 'register.html', {'error_message': error_message})
        else:
            error_message = 'Password dont match'
            return render(request, 'register.html', {'error_message': error_message})
    return render(request, 'register.html')

def logout(request):
    """
    Gère la déconnexion des utilisateurs.

    Args:
        request: La requête HTTP.

    Returns:
        Une redirection vers la page de connexion après la déconnexion.
    """
    auth.logout(request)
    return redirect('login')
