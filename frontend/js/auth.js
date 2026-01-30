const loginForm = document.querySelector("#loginForm");
const registerForm = document.querySelector("#registerForm");

async function login(email, password) {
  const res = await fetch("http://127.0.0.1:8000/auth/login", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    email: email,
    password: password
  })
});

  if (!res.ok) throw new Error("Ошибка входа");
  const data = await res.json();
  localStorage.setItem("token", data.access_token);
  alert("Вход успешен");
  window.location.href = "index.html";
}

async function register(email, password) {
  const res = await fetch("http://127.0.0.1:8000/auth/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) throw new Error("Ошибка регистрации");
  alert("Регистрация успешна!");
  window.location.href = "login.html";
}

if (loginForm) {
  loginForm.addEventListener("submit", e => {
    e.preventDefault();
    login(loginForm.email.value, loginForm.password.value).catch(alert);
  });
}

if (registerForm) {
  registerForm.addEventListener("submit", e => {
    e.preventDefault();
    register(registerForm.email.value, registerForm.password.value).catch(alert);
  });
}
