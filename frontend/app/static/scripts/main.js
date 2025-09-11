document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById("login-form");
    const registerForm = document.getElementById("register-form")

    if (loginForm) {
        loginForm.onsubmit = handleLogin
    }
    if (registerForm) {
        registerForm.onsubmit = handleRegister
    }
})

const apiUrl = 'http://localhost:8000/api'
const clientUrl = window.location.origin;

async function handleLogin(event) {
    event.preventDefault();

    const username = document.getElementById("login_username").value;
    const password = document.getElementById("login_password").value;
    
    try {
        const response = await fetch(`${clientUrl}/login`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({username, password})
        });

        alert(response.url);

        if (response.ok) {
            // a SweetAlert 'fire' window about sign in
            Swal.fire({
                icon: 'success',
                title: 'Successful enter!',
                text: 'Welcome',
                timer: 2000,
                showConfirmButton: false

            });

            // Closing a modal window
            setTimeout(() => {
                // get bootstrap login modal window
                const loginModal = bootstrap.Modal.getInstance(document.getElementById('loginModal'));

                if (loginModal) {
                    loginModal.hide();
                }

                window.location.href = `${clientUrl}/accounting`;
            }, 2000);
            
            if (response.redirected) {
                window.location.href = response.url
            }
        
        } else {
            const errorData = await response.json().catch(() => ({}));
            Swal.fire({
                icon: 'error',
                title: 'Error!',
                text: errorData.detail || 'Invalid username or password',
                confirmButtonText: 'Try again'
            });
        }
        
    } catch (error) {
        Swal.fire({
                icon: 'error',
                title: 'Network Error!',
                text: 'Please check your connection',
                confirmButtonText: 'Try again'
            });
    }
}



    

async function handleRegister(event) {
    event.preventDefault();
    

    
    
}










