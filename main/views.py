import json

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from .models import BlogPost


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

@csrf_exempt
def chatbot_api(request):
    if request.method == "GET":
        # Rendre l'interface utilisateur du chatbot pour les requêtes GET
        return render(request, 'chatbot.html')
    elif request.method == "POST":
        data = json.loads(request.body)
        message = data.get("message")
        # Logique existante pour traiter le message
        response_message = "Echo: " + message
        return JsonResponse({"response": response_message})
    else:
        # Réponse pour les méthodes non autorisées
        return JsonResponse({"error": "Méthode non autorisée"}, status=405)