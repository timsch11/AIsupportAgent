document.addEventListener("DOMContentLoaded", function() {
    const bookingForm = document.getElementById("bookingForm");
    const successMessage = document.getElementById("successMessage");

    bookingForm.addEventListener("submit", function(event) {//userForm
        event.preventDefault(); // Prevent actual form submission
        
        // Get form data
        const data = {
            court: document.getElementById('court').value,
            startDate: document.getElementById('startDate').value,
            duration: document.getElementById('duration').value,
            category: document.getElementById('category').value
        };

        // Create AJAX request
        fetch("/recurrentBook", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(jsonResponse => {
            successMessage.classList.remove("hidden");
            console.log(jsonResponse);
            if (jsonResponse.success) {
                successMessage.textContent = "Booking added successfully!";
                successMessage.style.color = "green";
                bookingForm.reset(); // Reset form fields
            } else {
                successMessage.textContent = "Error adding booking. Please try again.";
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