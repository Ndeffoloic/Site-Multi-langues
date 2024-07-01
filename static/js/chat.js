document.getElementById("send-btn").addEventListener("click", function() {
    var message = document.getElementById("chat-input").value;
    var chatList = document.getElementById("chat-list");
    var userLang = navigator.language || navigator.userLanguage; // Récupérer la langue de l'utilisateur

    // Afficher le message de l'utilisateur dans la liste
    var userMessageElement = document.createElement("li");
    console.log(userMessageElement);
    userMessageElement.classList.add("list-group-item");
    userMessageElement.textContent = "Vous: " + message;
    chatList.appendChild(userMessageElement);

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
        botMessageElement.classList.add("list-group-item");
        botMessageElement.textContent = "Chatbot: " + data.response;
        chatList.appendChild(botMessageElement);

        // Vider la case de saisie
        document.getElementById("chat-input").value = '';
    })
    .catch(error => console.error('Error:', error));
});