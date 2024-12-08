import json
import os

import requests
from django.conf import settings
from django.contrib import auth
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from langchain.chains.question_answering import load_qa_chain
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAI
from PyPDF2 import PdfReader

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
        image = request.FILES.get('image')
        new_post = BlogPost(title=title, content=content, publication_date=timezone.now(), image=image)
        new_post.save()
        return redirect('blog_list')
    return render(request, 'blog/createBlogPost.html')

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

def decouper_texte(texte_brut):
    separateur = "\n"
    decoupeur_texte = CharacterTextSplitter(
        separator=separateur,
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    return decoupeur_texte.split_text(texte_brut)

def initialiser_faiss(textes):
    modeles_embedding = OpenAIEmbeddings()
    return FAISS.from_texts(textes, modeles_embedding)

def charger_chaine_qa():
    return load_qa_chain(OpenAI(), chain_type="stuff")

def filter_repetitions(response_text):
    sentences = response_text.split('. ')
    unique_sentences = []
    for sentence in sentences:
        if sentence not in unique_sentences:
            unique_sentences.append(sentence)
    return '. '.join(unique_sentences)

@csrf_exempt
def chatbot(request):
    if request.method == 'POST':
        try:
            print("a0")
            print(request.body)
            # Récupération du message de l'utilisateur
            body_unicode = request.body.decode('utf-8')
            
            body = json.loads(body_unicode)
            message = body.get('message', '').strip()
            print("a1")
            if not message:
                return JsonResponse({'error': 'Le message est vide.'}, status=400)
            print("a2")

            # Vérification et traitement du fichier téléversé
            if 'file' not in request.FILES:
                return JsonResponse({'error': 'Aucun fichier téléversé.'}, status=400)
            print("a3")

            fichier_pdf = request.FILES['file']
            chemin_pdf = os.path.join(settings.MEDIA_ROOT, fichier_pdf.name)

            with open(chemin_pdf, 'wb+') as destination:
                for chunk in fichier_pdf.chunks():
                    destination.write(chunk)

            print("a4")
            # Lecture et traitement du fichier PDF
            with open(chemin_pdf, 'rb') as f:
                reader = PdfReader(f)
                texte_brut = ""
                for page in reader.pages:
                    texte_brut += page.extract_text()
            print(texte_brut)
            textes = decouper_texte(texte_brut)
            docsearch = initialiser_faiss(textes)
            chain = charger_chaine_qa()

            # Recherche et génération de réponse
            documents_similaires = docsearch.similarity_search(message)
            response_text = chain.run(input_documents=documents_similaires, question=message)
            response_text = filter_repetitions(response_text)

            return JsonResponse({'response': response_text})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Erreur lors du décodage du JSON.'}, status=400)
        except UnicodeDecodeError:
            return JsonResponse({'error': 'Erreur lors du décodage de la requête.'}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'Erreur lors de la génération de la réponse: {str(e)}'}, status=500)

    # Pour les autres méthodes (GET, etc.)
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