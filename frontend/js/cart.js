const cartContainer = document.getElementById("cart-items");
const totalItemsEl = document.getElementById("total-items");
const totalPriceEl = document.getElementById("total-price");
const checkoutBtn = document.getElementById("checkout-btn");

// ===== Модальное окно оплаты =====
const paymentModal = document.getElementById("payment-modal");
const modalTotalPrice = document.getElementById("modal-total-price");
const payBtn = document.getElementById("pay-btn");
const closeModalBtn = document.getElementById("close-modal-btn");

// ===== Загрузка корзины =====
async function loadCart() {
  const token = localStorage.getItem("token");
  if (!token) {
    cartContainer.innerHTML = "<p>Войдите, чтобы посмотреть корзину</p>";
    totalItemsEl.textContent = "0";
    totalPriceEl.textContent = "0 ₽";
    return;
  }

  try {
    const res = await fetch("http://127.0.0.1:8000/cart/", {
      headers: { "Authorization": `Bearer ${token}` }
    });

    if (!res.ok) {
      const data = await res.json();
      throw new Error(data.detail || "Ошибка загрузки корзины");
    }

    const cart = await res.json();
    const items = cart.items || cart;

    if (!items || items.length === 0) {
      cartContainer.innerHTML = "<p>Корзина пуста</p>";
      totalItemsEl.textContent = "0";
      totalPriceEl.textContent = "0 ₽";
      return;
    }

    cartContainer.innerHTML = items.map(item => {
      const product = item.product || {};
      return `
        <div class="cart-item" data-id="${item.id}" data-price="${product.price || 0}">
          <img src="${product.image ? `images/${product.image}` : 'assets/images/default.png'}" alt="${product.name || 'Товар'}">
          <div class="cart-info">
            <div class="cart-top">
              <h3>${product.name || 'Товар'}</h3>
              <div class="quantity-controls">
                <button class="decrease">-</button>
                <span>${item.quantity}</span>
                <button class="increase">+</button>
              </div>
            </div>
            <p>${product.price != null ? product.price + ' ₽' : 'Цена не указана'}</p>
          </div>
        </div>
      `;
    }).join("");

    setupQuantityButtons();
    updateTotals();
  } catch (err) {
    console.error(err);
    cartContainer.innerHTML = `<p>${err.message}</p>`;
  }
}

// ===== Количество товаров =====
function setupQuantityButtons() {
  document.querySelectorAll(".cart-item").forEach(itemEl => {
    const id = itemEl.dataset.id;
    const span = itemEl.querySelector("span");
    const increaseBtn = itemEl.querySelector(".increase");
    const decreaseBtn = itemEl.querySelector(".decrease");

    increaseBtn.addEventListener("click", async () => {
      const quantity = parseInt(span.textContent) + 1;
      await updateItem(id, quantity, span, itemEl);
    });

    decreaseBtn.addEventListener("click", async () => {
      const quantity = parseInt(span.textContent) - 1;
      await updateItem(id, quantity, span, itemEl);
    });
  });
}

async function updateItem(itemId, quantity, spanEl, itemEl) {
  const token = localStorage.getItem("token");
  if (!token) return;

  try {
    const res = await fetch(`http://127.0.0.1:8000/cart/items/${itemId}`, {
      method: "PUT",
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ quantity })
    });

    if (!res.ok) {
      const data = await res.json();
      throw new Error(data.detail || "Ошибка обновления");
    }

    if (quantity <= 0) {
      itemEl.remove();
      if (!cartContainer.querySelector(".cart-item")) {
        cartContainer.innerHTML = "<p>Корзина пуста</p>";
      }
    } else {
      spanEl.textContent = quantity;
    }

    updateTotals();
  } catch (err) {
    console.error(err);
    alert(err.message);
  }
}

// ===== Итоги корзины =====
function updateTotals() {
  const items = document.querySelectorAll(".cart-item");
  let totalItems = 0;
  let totalPrice = 0;

  items.forEach(item => {
    const quantity = parseInt(item.querySelector("span").textContent);
    const price = parseFloat(item.dataset.price);
    totalItems += quantity;
    totalPrice += price * quantity;
  });

  totalItemsEl.textContent = totalItems;
  totalPriceEl.textContent = totalPrice + " ₽";
}

// ===== Оформление заказа =====
checkoutBtn?.addEventListener("click", () => {
  const totalPrice = parseFloat(totalPriceEl.textContent);
  if (totalPrice === 0) return alert("Корзина пуста");

  modalTotalPrice.textContent = totalPrice + " ₽";
  paymentModal.style.display = "flex";
});

payBtn.addEventListener("click", async () => {
  const token = localStorage.getItem("token");
  if (!token) return alert("Войдите чтобы оплатить");

  try {
    const res = await fetch("http://127.0.0.1:8000/orders/", {
      method: "POST",
      headers: { "Authorization": `Bearer ${token}` }
    });
    if (!res.ok) {
      const data = await res.json();
      throw new Error(data.detail || "Ошибка оплаты");
    }
    alert("Оплата прошла успешно!");
    paymentModal.style.display = "none";
    loadCart(); // очищаем корзину
  } catch (err) {
    console.error(err);
    alert(err.message);
  }
});

closeModalBtn.addEventListener("click", () => {
  paymentModal.style.display = "none";
});

window.addEventListener("click", (e) => {
  if (e.target === paymentModal) paymentModal.style.display = "none";
});

// ===== INIT =====
loadCart();
