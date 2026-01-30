const API_URL = "http://127.0.0.1:8000";
const container = document.getElementById("product");

const id = new URLSearchParams(window.location.search).get("id");

async function loadProduct() {
    const res = await fetch(`${API_URL}/products/${id}`);
    const product = await res.json();

    container.innerHTML = `
        <div class="product-card" style="max-width:400px;margin:2rem auto;">
            <img src="${product.image_url || 'https://via.placeholder.com/300'}">
            <div class="info">
                <h3>${product.name}</h3>
                <p>${product.price} ₽</p>
                <button class="add-to-cart">Добавить в корзину</button>
            </div>
        </div>
    `;

    container.querySelector(".add-to-cart").onclick = addToCart;
}

async function addToCart() {
    const token = localStorage.getItem("token");
    if (!token) {
        location.href = "login.html";
        return;
    }

    await fetch(`${API_URL}/cart/add`, {
        method: "POST",
        headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ product_id: Number(id), quantity: 1 })
    });

    alert("Добавлено в корзину");
}

loadProduct();
