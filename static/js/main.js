// static/js/main.js

// Auto-hide flash messages after 5 seconds
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(() => {
        const alerts = document.querySelectorAll('.flash-message, .alert-dismissible');
        alerts.forEach(alert => {
            if (alert && !alert.classList.contains('no-auto-hide')) {
                alert.style.transition = 'opacity 0.5s';
                alert.style.opacity = '0';
                setTimeout(() => {
                    if (alert.parentNode) alert.remove();
                }, 500);
            }
        });
    }, 5000);
});

// Update cart quantity with confirmation
function updateCartQuantity(productId) {
    const quantity = document.getElementById(`quantity-${productId}`).value;
    if (quantity < 0) {
        alert('Quantity cannot be negative');
        return false;
    }
    return true;
}

// Add to cart animation
function addToCartAnimation(button) {
    button.innerHTML = '<i class="fas fa-check"></i> Added!';
    button.classList.add('btn-success');
    setTimeout(() => {
        button.innerHTML = '<i class="fas fa-shopping-cart"></i> Add to Cart';
        button.classList.remove('btn-success');
    }, 2000);
}

// Product image zoom on hover
document.addEventListener('DOMContentLoaded', function() {
    const productImages = document.querySelectorAll('.product-card img, .category-card img');
    productImages.forEach(img => {
        img.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.05)';
            this.style.transition = 'transform 0.3s';
        });
        img.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
        });
    });
});

// Search functionality
function searchProducts() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const products = document.querySelectorAll('.product-card');

    products.forEach(product => {
        const title = product.querySelector('h4, h5')?.textContent.toLowerCase();
        if (title && title.includes(searchTerm)) {
            product.style.display = 'block';
        } else {
            product.style.display = 'none';
        }
    });
}

// Filter products by price
function filterByPrice() {
    const maxPrice = document.getElementById('priceFilter').value;
    const products = document.querySelectorAll('.product-card');

    products.forEach(product => {
        const priceElement = product.querySelector('.price');
        if (priceElement) {
            const price = parseInt(priceElement.textContent.replace('৳', ''));
            if (price <= maxPrice || maxPrice === 'all') {
                product.style.display = 'block';
            } else {
                product.style.display = 'none';
            }
        }
    });
}

// Add to wishlist (local storage)
function toggleWishlist(productId, productName, productPrice, productImage) {
    let wishlist = JSON.parse(localStorage.getItem('wishlist') || '[]');
    const exists = wishlist.some(item => item.id === productId);

    if (exists) {
        wishlist = wishlist.filter(item => item.id !== productId);
        alert(`${productName} removed from wishlist`);
    } else {
        wishlist.push({
            id: productId,
            name: productName,
            price: productPrice,
            image: productImage
        });
        alert(`${productName} added to wishlist`);
    }

    localStorage.setItem('wishlist', JSON.stringify(wishlist));
    updateWishlistCount();
}

// Update wishlist count
function updateWishlistCount() {
    const wishlist = JSON.parse(localStorage.getItem('wishlist') || '[]');
    const countElement = document.getElementById('wishlist-count');
    if (countElement) {
        countElement.textContent = wishlist.length;
    }
}

// Load wishlist on wishlist page
function loadWishlist() {
    const wishlist = JSON.parse(localStorage.getItem('wishlist') || '[]');
    const container = document.getElementById('wishlist-container');

    if (container) {
        if (wishlist.length === 0) {
            container.innerHTML = '<div class="text-center"><p>Your wishlist is empty</p><a href="/" class="btn btn-gold">Continue Shopping</a></div>';
            return;
        }

        let html = '<div class="row">';
        wishlist.forEach(item => {
            html += `
                <div class="col-md-3 mb-4">
                    <div class="product-card">
                        <img src="${item.image}" alt="${item.name}">
                        <div class="content">
                            <h5>${item.name}</h5>
                            <p class="price">৳${item.price}</p>
                            <button onclick="addToCartFromWishlist(${item.id})" class="btn btn-gold btn-sm">Add to Cart</button>
                            <button onclick="toggleWishlist(${item.id}, '${item.name}', ${item.price}, '${item.image}')" class="btn btn-danger btn-sm">Remove</button>
                        </div>
                    </div>
                </div>
            `;
        });
        html += '</div>';
        container.innerHTML = html;
    }
}

// Add to cart from wishlist
function addToCartFromWishlist(productId) {
    fetch(`/add_to_cart/${productId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `quantity=1`
    })
    .then(response => {
        if (response.redirected) {
            window.location.href = response.url;
        }
    });
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    updateWishlistCount();
    if (window.location.pathname.includes('wishlist')) {
        loadWishlist();
    }
});