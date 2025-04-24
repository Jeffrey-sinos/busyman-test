document.addEventListener("DOMContentLoaded", function() {
            const passwordField = document.getElementById("password");
            const confirmPasswordField = document.getElementById("confirm_password");
            const passwordError = document.getElementById("password_error");
            const passwordForm = document.getElementById("passwordForm");

            const requirements = {
                length: document.getElementById("length"),
                uppercase: document.getElementById("uppercase"),
                lowercase: document.getElementById("lowercase"),
                number: document.getElementById("number"),
                special: document.getElementById("special"),
            };

            passwordField.addEventListener("input", function() {
                const password = passwordField.value;
                requirements.length.innerHTML = password.length >= 8 ? "✅ At least 8 characters" : "❌ At least 8 characters";
                requirements.uppercase.innerHTML = /[A-Z]/.test(password) ? "✅ 1 uppercase letter" : "❌ 1 uppercase letter";
                requirements.lowercase.innerHTML = /[a-z]/.test(password) ? "✅ 1 lowercase letter" : "❌ 1 lowercase letter";
                requirements.number.innerHTML = /[0-9]/.test(password) ? "✅ 1 number" : "❌ 1 number";
                requirements.special.innerHTML = /[!@#$%^&*]/.test(password) ? "✅ 1 special symbol (!@#$%^&*)" : "❌ 1 special symbol (!@#$%^&*)";
            });

            confirmPasswordField.addEventListener("input", function() {
                if (confirmPasswordField.value !== passwordField.value) {
                    passwordError.textContent = "Passwords do not match!";
                } else {
                    passwordError.textContent = "";
                }
            });

            passwordForm.addEventListener("submit", function(event) {
                const password = passwordField.value;
                const confirmPassword = confirmPasswordField.value;

                if (
                    password.length < 8 ||
                    !/[A-Z]/.test(password) ||
                    !/[a-z]/.test(password) ||
                    !/[0-9]/.test(password) ||
                    !/[!@#$%^&*]/.test(password)
                ) {
                    event.preventDefault();
                    alert("Please ensure your password meets all the requirements.");
                }

                if (password !== confirmPassword) {
                    event.preventDefault();
                    alert("Passwords do not match!");
                }
            });
        });