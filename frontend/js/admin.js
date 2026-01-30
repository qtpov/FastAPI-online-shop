const adminGrid = document.getElementById('productsGrid');

async function loadAdminProducts(){
  const res = await fetch('http://localhost:8000/api/products');
  const products = await res.json();
  adminGrid.innerHTML = products.map(p=>`
    <div class="product-card">
      <div class="product-image"><img src="${p.image || 'assets/images/default.png'}"></div>
      <div class="product-info">
        <h3 class="product-name">${p.name}</h3>
        <p class="product-price">$${p.price.toFixed(2)}</p>
        <button class="add-to-cart" onclick="deleteProduct(${p.id})">Delete</button>
      </div>
    </div>
  `).join('');
}

async function deleteProduct(id){
  await fetch(`http://localhost:8000/api/products/${id}`, { method:'DELETE' });
  loadAdminProducts();
}

loadAdminProducts();
