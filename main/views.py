from django.shortcuts import render

# Assurez-vous d'importer BlogPost au lieu de Article
from .models import BlogPost


# Create your views here.
def article_list(request):
    # Utilisez BlogPost.objects.all() pour récupérer tous les objets BlogPost
    articles = BlogPost.objects.all()
    return render(request, 'article_list.html', {'articles': articles})