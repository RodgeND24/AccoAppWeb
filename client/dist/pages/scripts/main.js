document.addEventListener('DOMContentLoaded', () => {

    const authForm = document.getElementById('login-form')

    if (authForm) {
        
        authForm.addEventListener('submit', function(event) {
            event.preventDefault();
            const formData = new FormData(authForm);

            const authData = {
                username: formData.get('username'),
                password: formData.get('password')
            };

            sendLoginRequest(authData);
        })

    }

    async function sendLoginRequest(authData) {
        const loginUrl = 'http://localhost:8000/auth/login';

        const requestData = new URLSearchParams();
        requestData.append('username', authData.username);
        requestData.append('password', authData.password);

        response = await fetch(loginUrl, {
            method: 'POST',
            credentials: 'include',
            headers: {
                'Content-type': 'application/x-www-form-urlencoded'
            },
            body: requestData.toString(),
            mode: 'cors'
        })

        if (!response.ok) {
            // alert("HTTP-error: " + response.status)

            // a SweetAlert 'fire' window about error
            Swal.fire({
                icon: 'error',
                title: 'Error!',
                text: 'Invalid username or password',
                confirmButtonText: 'Try again'
            });
        } 
        else {
        
            const data = await response.json();
            handledLoginSuccess(data);
        }
    }

    function handledLoginSuccess(data) {
        
        // alert(data.access_token)

        if (data.access_token) {
            localStorage.setItem('server_api_access_token', data.access_token);
            localStorage.setItem('server_api_refresh_token', data.refresh_token);
        

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

                window.location.href = 'http://localhost:3000/accounting.html';
            }, 2000);
        }

    }
})