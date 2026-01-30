document.addEventListener("DOMContentLoaded", () => {
  const API_URL = "http://127.0.0.1:8000";
  const productsContainer = document.getElementById("products");
  const searchInput = document.getElementById("searchInput");

  // auth buttons
  const loginBtn = document.getElementById("login-btn");
  const registerBtn = document.getElementById("register-btn");
  const logoutBtn = document.getElementById("logout-btn");
  const ordersBtn = document.getElementById("orders-btn");

  // modals
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
      alert("Сессия истекла. Войдите снова.");

      loginBtn.style.display = "inline-block";
      registerBtn.style.display = "inline-block";
      ordersBtn.style.display = "none";
      logoutBtn.style.display = "none";

      loginModal.style.display = "none";
      registerModal.style.display = "none";
      ordersModal.style.display = "none";
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

  // === MODALS OPEN/CLOSE ===
  loginBtn?.addEventListener("click", () => loginModal.style.display = "flex");
  registerBtn?.addEventListener("click", () => registerModal.style.display = "flex");
  closeLogin?.addEventListener("click", () => loginModal.style.display = "none");
  closeRegister?.addEventListener("click", () => registerModal.style.display = "none");
  closeOrdersBtn?.addEventListener("click", () => ordersModal.style.display = "none");
  window.addEventListener("click", e => {
    if (e.target === loginModal) loginModal.style.display = "none";
    if (e.target === registerModal) registerModal.style.display = "none";
    if (e.target === ordersModal) ordersModal.style.display = "none";
  });

  // === LOGOUT ===
  logoutBtn?.addEventListener("click", () => {
    localStorage.removeItem("token");
    updateAuthUI();
    alert("Вы вышли из аккаунта");
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
      alert("Вход выполнен");
    } catch (err) {
      alert(err.message);
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
      alert("Регистрация успешна");
    } catch (err) {
      alert(err.message);
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
    if (!products.length) {
      productsContainer.innerHTML = "<p>No products found</p>";
      return;
    }

    productsContainer.innerHTML = products.map(p => `
      <div class="product-card">
        <img src="${p.image ? `images/${p.image}` : 'assets/images/default.png'}" alt="${p.name}">
        <div class="info">
          <h3>${p.name}</h3>
          <p>${p.price} ₽</p>
          <button class="add-to-cart" data-id="${p.id}">Add</button>
        </div>
      </div>
    `).join("");

    document.querySelectorAll(".add-to-cart").forEach(btn => {
      btn.addEventListener("click", () => addToCart(btn.dataset.id));
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
    if (!token) return alert("Войдите чтобы добавить товар");

    try {
      const res = await fetch(`${API_URL}/cart/items`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify({ product_id: productId, quantity: 1 }),
      });
      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || "Ошибка добавления в корзину");
      }
      alert("Товар добавлен!");
    } catch (err) {
      if (!handleUnauthorized(err)) alert(err.message);
    }
  }

  // === ORDERS ===
  ordersBtn?.addEventListener("click", async () => {
    const token = localStorage.getItem("token");
    if (!token) return alert("Войдите чтобы посмотреть заказы");

    try {
      const res = await fetch(`${API_URL}/orders/`, {
        headers: { "Authorization": `Bearer ${token}` }
      });
      if (!res.ok) throw { status: res.status, message: "Ошибка загрузки заказов" };
      const orders = await res.json();

      ordersList.innerHTML = Array.isArray(orders) && orders.length
        ? orders.map(o => `
          <li>
            <strong>Заказ #${o.id}</strong> — ${o.status.toUpperCase()} — ${o.items.length} товаров — ${o.total_price} ₽
          </li>
        `).join("")
        : "<li>Заказы отсутствуют</li>";

      ordersModal.style.display = "flex";
    } catch (err) {
      if (!handleUnauthorized(err)) alert(err.message);
    }
  });

  // === INIT ===
  updateAuthUI();
  loadProducts();
});
