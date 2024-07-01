document.querySelector("#send-btn").addEventListener("click", function(event) {
    event.preventDefault(); // Empêcher le rechargement de la page
    var message = document.getElementById("chat-input").value;
    var chatList = document.getElementById("chat-list");
    var userLang = navigator.language || navigator.userLanguage; // Récupérer la langue de l'utilisateur

    if (message.trim() !== "") { // Assurez-vous que le message n'est pas vide
        // Afficher le message de l'utilisateur dans la liste
        var userMessageElement = document.createElement("li");
        userMessageElement.classList.add("list-group-item", "text-right"); // Classe Bootstrap pour aligner à droite
        userMessageElement.textContent = "Vous: " + message;
        chatList.appendChild(userMessageElement);

        // Nettoyer le champ de saisie
        document.getElementById("chat-input").value = '';

        // Envoyer le message au serveur
        fetch("/chatbot/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value,
            },
            body: JSON.stringify({ message: message, lang: userLang })
        })
        .then(response => response.json())
        .then(data => {
            // Afficher la réponse du chatbot
            var botMessageElement = document.createElement("li");
            botMessageElement.classList.add("list-group-item"); // Utiliser Bootstrap pour le style
            botMessageElement.textContent = "Chatbot: " + data.response;
            chatList.appendChild(botMessageElement);
            // Faire défiler automatiquement vers le bas pour voir le dernier message
            chatList.scrollTop = chatList.scrollHeight;
        })
        .catch(error => console.error('Error:', error));
    }
});
