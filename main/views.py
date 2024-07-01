import json
import os

import openai
import requests  # Assurez-vous d'importer requests
from django.contrib import auth
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv

from .models import BlogPost, Chat

# Charger les variables d'environnement
load_dotenv()

def blog_list(request, *args, **kwargs):
    blogs = BlogPost.objects.all()
    return render(request, 'blog_list.html', {'blogs': blogs})

def blog_detail(request, blog_id):
    blog = get_object_or_404(BlogPost, pk=blog_id)
    return render(request, 'blog_detail.html', {'blog': blog})

def createBlogPost(request):
    if request.method == "POST":
        title = request.POST.get('title')
        content = request.POST.get('content')
        image = request.FILES.get('image')  # Récupération de l'image à partir de request.FILES
        # Création d'une nouvelle instance de BlogPost avec l'image
        new_post = BlogPost(title=title, content=content, publication_date=timezone.now(), image=image)
        new_post.save()  # Enregistrement de l'instance dans la base de données
        return redirect('blog_list')  # Redirection vers la liste des blogs après la création
    return render(request, 'blog/createBlogPost.html')

#https://poe.com/BotPoeGratuitEssai1
openai_api_key = os.getenv('OPEN_API_KEY')
openai.api_key = openai_api_key

import requests
from requests.exceptions import HTTPError, RequestException


def ask_openai(message):
    session = requests.Session()  # Utilisation d'une session pour les requêtes
    headers = {
        "Authorization": f"Bearer {openai_api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": message},
        ],
        "max_tokens": 150,
        "n": 1,
        "stop": None,
        "temperature": 0.7,
    }
    try:
        response = session.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers)
        response.raise_for_status()  # Cela va lever une exception pour les réponses 4xx/5xx
        data = response.json()
        answer = data['choices'][0]['message']['content'].strip()
        return answer
    except HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        try:
            error_response = response.json()
            print(error_response)
        except ValueError:  # inclut simplejson.decoder.JSONDecodeError
            print("Le corps de la réponse n'est pas un JSON valide.")
        return "Une erreur HTTP s'est produite. Veuillez réessayer plus tard."
    except RequestException as req_err:
        print(f"Request error occurred: {req_err}")
        return "Une erreur de requête s'est produite. Veuillez vérifier votre connexion Internet."
    except openai.error.RateLimitError:
        return "Désolé, vous avez dépassé votre quota d'utilisation de l'API OpenAI. Veuillez vérifier votre plan et vos détails de facturation."

    finally:
        session.close()  # Fermeture de la session après l'opération
        
        
@csrf_exempt
def chatbot(request):
    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        message = body.get('message')
        response = ask_openai(message)
        return JsonResponse({'message': message, 'response': response})
    return render(request, 'chatbot.html')
  
def login(request):
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
    auth.logout(request)
    return redirect('login')