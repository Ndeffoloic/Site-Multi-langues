import json
import os

from django.contrib import auth
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from transformers import AutoTokenizer, AutoModelForCausalLM
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv

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


# Initialisation du modèle et du tokenizer avec Falcon
try:
    tokenizer = AutoTokenizer.from_pretrained("tiiuae/falcon-7b")
    model = AutoModelForCausalLM.from_pretrained("tiiuae/falcon-7b")
except Exception as e:
    print(f"Error loading model: {e}")

def generate_text(input_text):
    try:
        inputs = tokenizer(input_text, return_tensors="pt")
        outputs = model.generate(**inputs)
        generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        return generated_text
    except Exception as e:
        return f"Error generating text: {e}"
    
@csrf_exempt
def chatbot(request):
    """
    Gère les interactions avec le chatbot.

    Args:
        request: La requête HTTP.

    Returns:
        Une réponse JSON contenant le message de l'utilisateur et la réponse du chatbot.
        Ou rend le template 'chatbot.html' pour les requêtes GET.
    """
    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        message = body.get('message')
        
        # Utiliser la fonction generate_text pour obtenir la réponse du chatbot
        response_text = generate_text(message)
        
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
