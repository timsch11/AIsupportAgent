document.addEventListener("DOMContentLoaded", function() {
    const userForm = document.getElementById("userForm");
    const successMessage = document.getElementById("successMessage");

    userForm.addEventListener("submit", function(event) {
        event.preventDefault(); // Prevent actual form submission
        
        // Get form data
        const formData = new FormData(userForm);
        const data = Object.fromEntries(formData);

        // Create AJAX request
        fetch("/addUser", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(jsonresponse => {
            successMessage.classList.remove("hidden");
            if (jsonresponse.success) {
                successMessage.textContent = "User added successfully!";
                successMessage.style.color = "green";
                userForm.reset(); // Reset form fields
            } else {
                successMessage.textContent = "Error adding user. Please try again.";
                successMessage.style.color = "red";
            }
        })
        .catch(error => {
            successMessage.classList.remove("hidden");
            successMessage.textContent = "An error occurred. Please try again.";
            successMessage.style.color = "red";
            console.error("Error:", error);
        });
    });
});