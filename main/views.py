import json
import os

import requests  # Assurez-vous d'importer requests
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv

from .models import BlogPost

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



@csrf_exempt
def chatbot_api(request):
    if request.method == "GET":
        return render(request, 'chatbot.html')
    elif request.method == "POST":
        data = json.loads(request.body)
        message = data.get("message")
        
        # URL de l'API de ChatGPT
        chatgpt_url = "https://api.openai.com/v1/chat/completions"
        
        # Préparation de la requête à l'API de ChatGPT
        payload = json.dumps({
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": message}]
        })
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {os.getenv("OPEN_API_KEY")}'
        }
        
        try:
            # Envoi de la requête à l'API de ChatGPT
            response = requests.post(chatgpt_url, data=payload, headers=headers)
            
            # Vérification que la requête a réussi
            if response.status_code == 200:
                # Extraction de la réponse de ChatGPT
                chatgpt_response = response.json()
                return JsonResponse({"response": chatgpt_response})
            else:
                return JsonResponse({"error": "Erreur lors de la communication avec ChatGPT"}, status=500)
        except requests.exceptions.RequestException as e:
            # Gestion des erreurs de requête
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse({"error": "Méthode non autorisée"}, status=405)