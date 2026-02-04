document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    const showRegister = document.getElementById('showRegister');
    const showLogin = document.getElementById('showLogin');
    const loginCard = document.getElementById('loginCard');
    const registerCard = document.getElementById('registerCard');

    // Switch between Login and Register
    showRegister.addEventListener('click', (e) => {
        e.preventDefault();
        loginCard.style.display = 'none';
        registerCard.style.display = 'block';
    });

    showLogin.addEventListener('click', (e) => {
        e.preventDefault();
        registerCard.style.display = 'none';
        loginCard.style.display = 'block';
    });

    // Handle Login
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const btn = document.getElementById('loginBtn');

        try {
            btn.disabled = true;
            btn.innerHTML = '<span>Signing in...</span>';

            await api.login(email, password);
            window.location.href = 'dashboard.html';
        } catch (error) {
            alert(error.message);
            btn.disabled = false;
            btn.innerHTML = '<span>Sign In</span><i class="fas fa-arrow-right"></i>';
        }
    });

    // Handle Registration
    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const full_name = document.getElementById('regFullName').value;
        const email = document.getElementById('regEmail').value;
        const password = document.getElementById('regPassword').value;
        const btn = document.getElementById('registerBtn');

        try {
            btn.disabled = true;
            btn.innerHTML = '<span>Creating account...</span>';

            await api.register({ full_name, email, password, role: 'member' });
            alert('Registration successful! Please login.');
            showLogin.click();
        } catch (error) {
            alert(error.message);
            btn.disabled = false;
            btn.innerHTML = '<span>Register</span>';
        }
    });

    // Check if already logged in
    const token = localStorage.getItem('token');
    if (token) {
        window.location.href = 'dashboard.html';
    }
});
