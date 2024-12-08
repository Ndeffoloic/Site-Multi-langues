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
from langchain.chains.question_answering import load_qa_chain
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain_community.llms import OpenAI
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from PyPDF2 import PdfReader

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

# Charger les variables d'environnement
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# Lire et extraire le texte d'un fichier PDF
def lire_pdf(chemin_pdf):
    lecteur = PdfReader(chemin_pdf)
    texte_brut = ''
    for page in lecteur.pages:
        text = page.extract_text()
        if text:
            texte_brut += text
    return texte_brut

# Découper le texte en morceaux
def decouper_texte(texte_brut):
    separateur = "\n"
    decoupeur_texte = CharacterTextSplitter(
        separator=separateur,
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    return decoupeur_texte.split_text(texte_brut)

# Initialiser FAISS
def initialiser_faiss(textes):
    modeles_embedding = OpenAIEmbeddings()
    return FAISS.from_texts(textes, modeles_embedding)

# Charger la chaîne QA
def charger_chaine_qa():
    return load_qa_chain(OpenAI(), chain_type="stuff")

# Filtrer les répétitions dans une réponse
def filter_repetitions(response_text):
    sentences = response_text.split('. ')
    unique_sentences = []
    for sentence in sentences:
        if sentence not in unique_sentences:
            unique_sentences.append(sentence)
    return '. '.join(unique_sentences)

# Vue chatbot
@csrf_exempt
def chatbot(request):
    if request.method == 'POST' and 'file' in request.FILES:
        # Télécharger le fichier
        pdf_file = request.FILES['file']
        chemin_pdf = f"/tmp/{pdf_file.name}"  # Chemin temporaire pour le stockage
        with open(chemin_pdf, 'wb') as destination:
            for chunk in pdf_file.chunks():
                destination.write(chunk)
        
        # Lire et traiter le fichier PDF
        texte_brut = lire_pdf(chemin_pdf)
        textes = decouper_texte(texte_brut)
        docsearch = initialiser_faiss(textes)
        chain = charger_chaine_qa()

        # Traiter la question de l'utilisateur
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        message = body.get('message')
        documents_similaires = docsearch.similarity_search(message)
        response_text = chain.run(input_documents=documents_similaires, question=message)
        response_text = filter_repetitions(response_text)

        return JsonResponse({'response': response_text})

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
