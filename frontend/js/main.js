document.addEventListener("DOMContentLoaded", () => {
  const API_URL = "http://127.0.0.1:8000";


  function showToast(message, color="#10b981") {
    const toast = document.getElementById("toast");
    toast.textContent = message;
    toast.style.background = color;
    toast.style.display = "block";
    setTimeout(() => toast.style.display = "none", 3000);
  }
  // === DOM ELEMENTS ===
  const productsContainer = document.getElementById("products");
  const searchInput = document.getElementById("searchInput");

  // Auth buttons
  const loginBtn = document.getElementById("login-btn");
  const registerBtn = document.getElementById("register-btn");
  const logoutBtn = document.getElementById("logout-btn");
  const ordersBtn = document.getElementById("orders-btn");

  // Modals
  const loginModal = document.getElementById("login-modal");
  const registerModal = document.getElementById("register-modal");
  const ordersModal = document.getElementById("orders-modal");
  const ordersList = document.getElementById("orders-list");
  const closeLogin = document.getElementById("close-login");
  const closeRegister = document.getElementById("close-register");
  const closeOrdersBtn = document.getElementById("close-orders-btn");

  // === UTILS ===
  function handleUnauthorized(err) {
    if (err.status === 401 || (err.message && err.message.includes("Token"))) {
      localStorage.removeItem("token");
      showToast("Сессия истекла. Войдите снова.");
      updateAuthUI();
      closeAllModals();
      return true;
    }
    return false;
  }

  function updateAuthUI() {
    const token = localStorage.getItem("token");
    if (token) {
      loginBtn.style.display = "none";
      registerBtn.style.display = "none";
      ordersBtn.style.display = "inline-block";
      logoutBtn.style.display = "inline-block";
    } else {
      loginBtn.style.display = "inline-block";
      registerBtn.style.display = "inline-block";
      ordersBtn.style.display = "none";
      logoutBtn.style.display = "none";
    }
  }

  function closeAllModals() {
    loginModal.style.display = "none";
    registerModal.style.display = "none";
    ordersModal.style.display = "none";
  }

  // === MODALS OPEN/CLOSE ===
  loginBtn?.addEventListener("click", () => loginModal.style.display = "flex");
  registerBtn?.addEventListener("click", () => registerModal.style.display = "flex");
  closeLogin?.addEventListener("click", () => loginModal.style.display = "none");
  closeRegister?.addEventListener("click", () => registerModal.style.display = "none");
  closeOrdersBtn?.addEventListener("click", () => ordersModal.style.display = "none");

  window.addEventListener("click", e => {
    if ([loginModal, registerModal, ordersModal].includes(e.target)) {
      e.target.style.display = "none";
    }
  });

  // === LOGOUT ===
  logoutBtn?.addEventListener("click", () => {
    localStorage.removeItem("token");
    updateAuthUI();
    showToast("Вы вышли из аккаунта");
  });

  // === LOGIN ===
  document.getElementById("login-submit")?.addEventListener("click", async () => {
    const email = document.getElementById("login-email").value;
    const password = document.getElementById("login-password").value;

    try {
      const res = await fetch(`${API_URL}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Ошибка входа");

      localStorage.setItem("token", data.access_token);
      loginModal.style.display = "none";
      updateAuthUI();
      showToast("Вход выполнен");
    } catch (err) {
      showToast(err.message);
    }
  });

  // === REGISTER ===
  document.getElementById("register-submit")?.addEventListener("click", async () => {
    const email = document.getElementById("register-email").value;
    const password = document.getElementById("register-password").value;

    try {
      const res = await fetch(`${API_URL}/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password, role: "user" })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Ошибка регистрации");

      localStorage.setItem("token", data.access_token);
      registerModal.style.display = "none";
      updateAuthUI();
      showToast("Регистрация успешна");
    } catch (err) {
      showToast(err.message);
    }
  });

  // === LOAD PRODUCTS ===
  async function loadProducts() {
    try {
      const res = await fetch(`${API_URL}/products/`);
      if (!res.ok) throw new Error("Ошибка загрузки товаров");
      const products = await res.json();
      displayProducts(products);
    } catch (err) {
      productsContainer.innerHTML = `<p>${err.message}</p>`;
    }
  }

  function displayProducts(products) {
    productsContainer.innerHTML = "";
    if (!products || !products.length) {
      productsContainer.innerHTML = "<p>Товары отсутствуют</p>";
      return;
    }

    products.forEach(p => {
      const card = document.createElement("div");
      card.className = "product-card";
      card.innerHTML = `
        <img src="${p.image ? `images/${p.image}` : 'assets/images/default.png'}" alt="${p.name}">
        <div class="info">
          <h3>${p.name}</h3>
          <p>${p.price} ₽</p>
          <button class="add-to-cart">Add</button>
        </div>
      `;
      card.querySelector(".add-to-cart").addEventListener("click", () => addToCart(p.id));
      productsContainer.appendChild(card);
    });
  }

  // === SEARCH ===
  searchInput?.addEventListener("input", e => {
    const q = e.target.value.trim();
    if (q.length < 2) return loadProducts();
    searchProducts(q);
  });

  async function searchProducts(query) {
    try {
      const res = await fetch(`${API_URL}/products/search?q=${encodeURIComponent(query)}`);
      if (!res.ok) throw new Error("Ошибка поиска");
      const products = await res.json();
      displayProducts(products);
    } catch (err) {
      console.error(err);
    }
  }

  // === ADD TO CART ===
  async function addToCart(productId) {
    const token = localStorage.getItem("token");
    if (!token) return showToast("Войдите чтобы добавить товар");

    try {
      const res = await fetch(`${API_URL}/cart/items`, {
        method: "POST",
        headers: { "Content-Type": "application/json", "Authorization": `Bearer ${token}` },
        body: JSON.stringify({ product_id: productId, quantity: 1 }),
      });
      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || "Ошибка добавления в корзину");
      }
      showToast("Товар добавлен!");
    } catch (err) {
      if (!handleUnauthorized(err)) showToast(err.message);
    }
  }

  // === ORDERS ===
  ordersBtn?.addEventListener("click", async () => {
    const token = localStorage.getItem("token");
    if (!token) return showToast("Войдите чтобы посмотреть заказы");

    try {
      const res = await fetch(`${API_URL}/orders/`, {
        headers: { "Authorization": `Bearer ${token}` }
      });
      if (!res.ok) throw { status: res.status, message: "Ошибка загрузки заказов" };
      const orders = await res.json();

      ordersList.innerHTML = "";
      if (orders && orders.length) {
        orders.forEach(o => {
          const li = document.createElement("li");
          li.innerHTML = `<strong>Заказ #${o.id}</strong> — ${o.status.toUpperCase()} — ${o.items.length} товаров — ${o.total_price} ₽`;
          ordersList.appendChild(li);
        });
      } else {
        ordersList.innerHTML = "<li>Заказы отсутствуют</li>";
      }
      ordersModal.style.display = "flex";
    } catch (err) {
      if (!handleUnauthorized(err)) showToast(err.message);
    }
  });

  

  // === INIT ===
  updateAuthUI();
  loadProducts();
});
