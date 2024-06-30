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

# Configurez votre clé secrète Direct Line ici
DIRECT_LINE_SECRET = "ca2f6332-8734-4099-bb6b-a15e2e92fbfe"
DIRECT_LINE_ENDPOINT = "https://directline.botframework.com/v3/directline/conversations/"

headers = {'Authorization': 'Bearer ' + DIRECT_LINE_SECRET}

def start_conversation():
    response = requests.post(DIRECT_LINE_ENDPOINT, headers=headers)
    if response.status_code == 201:
        conversation_id = response.json()['conversationId']
        return conversation_id
    return None

def send_message(conversation_id, message):
    message_endpoint = f"{DIRECT_LINE_ENDPOINT}{conversation_id}/activities"
    json_data = {
        "type": "message",
        "from": {"id": "user1"},
        "text": message
    }
    response = requests.post(message_endpoint, headers=headers, json=json_data)
    return response

def get_messages(conversation_id):
    message_endpoint = f"{DIRECT_LINE_ENDPOINT}{conversation_id}/activities"
    response = requests.get(message_endpoint, headers=headers)
    if response.status_code == 200:
        messages = response.json()['activities']
        return messages
    return []

def ask_bot_framework(message):
    conversation_id = start_conversation()
    if conversation_id:
        send_message_response = send_message(conversation_id, message)
        if send_message_response.status_code == 200:
            messages = get_messages(conversation_id)
            # Filtre les messages pour obtenir la réponse du bot
            bot_messages = [msg for msg in messages if msg['from']['id'] != 'user1']
            if bot_messages:
                # Retourne le dernier message du bot
                return bot_messages[-1]['text']
    return "Désolé, je ne peux pas répondre à votre question en ce moment."

def chatbot(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        message = data.get('message')
        response = ask_bot_framework(message)
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