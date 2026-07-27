// Map elements to consts
document.addEventListener("DOMContentLoaded", () => {
    const sendButton = document.getElementById("sendBtn");
    const userInput = document.getElementById("userInput");
    const chatWindow = document.getElementById("chatWindow");

    const thinkingSymbols = ['/', '-', '\\', '|'];
    let pendingCity = null;
    let pendingQuery = null;
    // Send user message to Flask
    async function sendMessage() {
        const message = userInput.value.trim();

        // No empty messages please
        if (!message) return;

        // Display user input in the HTML page box      
        chatWindow.innerHTML += `
            <div class="user-message">
                <strong>You:</strong> ${message}
            </div>
        `;
        chatWindow.scrollTop=chatWindow.scrollHeight;

        // Thinking animation
        const thinkingDiv = document.createElement("div");
        thinkingDiv.className = "bot-message";
        
        let symbolIndex = 0;
        thinkingDiv.innerHTML = `<strong>Meteor:</strong> Meteor is thinking... <span class="spinner">${thinkingSymbols[0]}</span>`;
        
        chatWindow.appendChild(thinkingDiv);

        // Cycle a symbol every 200ms
        const spinnerInterval = setInterval(() => {
            symbolIndex = (symbolIndex + 1) % thinkingSymbols.length;
            const spinnerSpan = thinkingDiv.querySelector(".spinner");
            if (spinnerSpan) {
                spinnerSpan.textContent = thinkingSymbols[symbolIndex];
            }
        }, 200);
        // Reset input box
        userInput.value = "";

        // Attach the remembered city if resolving duplicate
        const payload = pendingCity ? {message: message, target_city: pendingCity, original_query: pendingQuery} : {message: message};
        
        try {
            // Send POST request to the /chat route
            const response = await fetch("/chat", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                throw new Error(`Server error: ${response.status}`);
            }

            // Parse JSON response from Flask
            const data = await response.json();

            // Check if a duplicate city prompt was sent
            if (data.is_duplicate) {
                pendingCity = data.city_name;
                pendingQuery = pendingQuery || message;
            } else if (data.response.includes("couldn't find")) {
                // Keep pending info intact for another attempt
            } else {
                pendingCity = null;
                pendingQuery = null;
            }

            // Display response output in the HTML page box
            const formattedData = data.response.replace(/\n/g, "<br>");
            clearInterval(spinnerInterval);
            thinkingDiv.innerHTML = `<strong>Meteor:</strong> ${formattedData}`;

            chatWindow.scrollTop=chatWindow.scrollHeight;
        } catch (error) {
            console.error("Error with server:", error);
            clearInterval(spinnerInterval);
            pendingCity = null;
            thinkingDiv.innerHTML = `<strong>Meteor:</strong> Sorry, something went wrong`;

            chatWindow.scrollTop=chatWindow.scrollHeight;
        }
    }

    // Trigger on button click
    sendButton.addEventListener("click", sendMessage);

    // Trigger on 'Enter' key press inside the input box
    userInput.addEventListener("keypress", (event) => {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            sendMessage();
        }
    });
});
