from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class BlogPost(models.Model):
    """
    Modèle représentant un article de blog.

    Attributes:
        title (str): Le titre de l'article.
        content (str): Le contenu de l'article.
        publication_date (datetime): La date de publication de l'article.
        image (ImageField): L'image associée à l'article (optionnelle).

    Methods:
        __str__(): Retourne le titre de l'article pour qu'il représente l'article dans la base de données
    """
    title = models.CharField(max_length=100)
    content = models.TextField()
    publication_date = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='blog_images/', blank=True, null=True)
    
    def __str__(self):
        return self.title
    
    
class Chat(models.Model):
    """
    Représente une conversation dans le système. Au début, je voulais associer les conversations aux utilisateurs, mais 
    comme ça n'a pas marché, je n'ai pas sauvegardé les conversations des utilisateurs.  

    Attributes:
        user (User): L'utilisateur associé à la conversation.
        message (str): Le message envoyé dans la conversation.
        response (str): La réponse reçue dans la conversation.
        created_at (datetime): La date et l'heure de création de la conversation.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username}: {self.message}'