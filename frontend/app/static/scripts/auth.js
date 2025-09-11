document.addEventListener('DOMContentLoaded', async () => {
    
    const authenticated = await isAuthenticated();
    if (!authenticated) {
        window.location.href = 'http://localhost:8080';
    }
    // loadProtectedData();

    const btnCookie = document.getElementById('btn-cookie');
    // btnCookie.addEventListener('click', (e) => {alert(document.cookie)});
    btnCookie.addEventListener('click', () => {alert(getTokenByCookie('server_api_access_token'))});

    const btnLogout = document.getElementById('btn-logout');
    if (btnLogout) {
        btnLogout.addEventListener('click', () => logout());
    }
    else {
        alert('no button');
    }
})

    async function isAuthenticated() {
        const accessToken = getTokenByCookie('server_api_access_token');
        
        if (!accessToken || isTokenExpired(accessToken)) {
            const refreshSuccess = await refreshToken();
            // alert(refreshSuccess);
            return refreshSuccess;
        }
        return true;
    }

    function loadProtectedData() {

    }

    function isTokenExpired(token) {
        try {  
            // atob() - decode string at base-64; btoa() - encode string
            const payload = JSON.parse(atob(token.split('.')[1]))
            const exp = payload.exp * 1000; // to milliseconds
            return Date.now() >= exp;
        } catch (error) {
            console.log('Error checking token:' + error);
            return true;
        }
    }

    async function refreshToken() {
        try {
            const refreshUrl = 'http://localhost:8000/api/auth/refresh';

            const oldRefreshToken = getTokenByCookie('server_api_refresh_token');
            
            if (!oldRefreshToken) {
                console.error('No refresh token');
                throw new Error('No refresh token');
            }

            response = await fetch(refreshUrl, {
                method: 'POST',
                headers: {
                    'Content-type': 'application/json',
                    'Authentication': `Bearer ${oldRefreshToken}`,
                },
                credentials: 'include',
                mode: 'cors'
            })

            if (!response.ok) {
                logout();
                return false;
            } 
            else {
                const data = await response.json();
                localStorage.setItem('server_api_access_token', data.access_token);
                window.location.reload();
                return true;
            }
        }
        catch (error) {
            console.error('Token refresh failed:' + error);
            logout();
            return false;
        }
    }

    function getTokenByCookie(token) {
        const fullToken = document.cookie.split('; ').find(row => row.startsWith(token + '='));
        return fullToken ? fullToken.split('=')[1] : null;
    }

    async function logout() {
        try {
            const refreshToken = getTokenByCookie('server_api_refresh_token');
            
            await fetch('http://localhost:8000/api/auth/logout', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${refreshToken}`
                },
                mode: 'cors'
            });
        } catch (error) {
            console.error('Logout error:', error);
        } finally {
            localStorage.removeItem('server_api_access_token');
            document.cookie = 'server_api_access_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT;';
            document.cookie = 'server_api_refresh_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT;';
            window.location.href = 'http://localhost:8080';
        }
    }






