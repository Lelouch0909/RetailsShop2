// Modern Category Page JavaScript

document.addEventListener('DOMContentLoaded', function() {
    initCategoryFeatures();
});

function initCategoryFeatures() {
    initFilters();
    initViewToggle();
    initScrollToTop();
    initQuickView();
    initWishlist();
    initNewsletterForm();
}

// Initialize Filters
function initFilters() {
    const sortFilter = document.getElementById('sortFilter');
    const priceFilter = document.getElementById('priceFilter');

    if (sortFilter) {
        sortFilter.addEventListener('change', function() {
            sortProducts(this.value);
        });
    }

    if (priceFilter) {
        priceFilter.addEventListener('change', function() {
            filterByPrice(this.value);
        });
    }
}

// Sort Products
function sortProducts(sortBy) {
    const productsGrid = document.getElementById('productsGrid');
    const products = Array.from(productsGrid.children);

    products.sort((a, b) => {
        switch (sortBy) {
            case 'price-low':
                return parseFloat(a.dataset.price) - parseFloat(b.dataset.price);
            case 'price-high':
                return parseFloat(b.dataset.price) - parseFloat(a.dataset.price);
            case 'name':
                return a.dataset.name.localeCompare(b.dataset.name);
            case 'newest':
                // Sort by date attribute if available, otherwise reverse the order
                if (a.dataset.date && b.dataset.date) {
                    return new Date(b.dataset.date) - new Date(a.dataset.date);
                }
                // If no date attribute, just reverse the current order
                return -1;
            default:
                return 0;
        }
    });

    // Re-append sorted products
    products.forEach(product => {
        productsGrid.appendChild(product);
    });

    // Add animation
    animateProducts();
}

// Filter by Price
function filterByPrice(priceRange) {
    const products = document.querySelectorAll('.product-card-modern');

    products.forEach(product => {
        const price = parseFloat(product.dataset.price);
        let show = true;

        switch (priceRange) {
            case '0-25':
                show = price >= 0 && price <= 12500;
                break;
            case '25-50':
                show = price > 12500 && price <= 25000;
                break;
            case '50-100':
                show = price > 25000 && price <= 50000;
                break;
            case '100-plus':
                show = price > 50000;
                break;
            default:
                show = true;
        }

        if (show) {
            product.style.display = 'block';
            product.style.animation = 'fadeInUp 0.6s ease forwards';
        } else {
            product.style.display = 'none';
        }
    });
}

// View Toggle (Grid/List)
function initViewToggle() {
    const viewButtons = document.querySelectorAll('.view-btn');
    const productsGrid = document.getElementById('productsGrid');

    viewButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            // Update active button
            viewButtons.forEach(b => b.classList.remove('active'));
            this.classList.add('active');

            // Update grid view
            const view = this.dataset.view;
            if (view === 'list') {
                productsGrid.classList.add('list-view');
            } else {
                productsGrid.classList.remove('list-view');
            }

            // Animate transition
            animateProducts();
        });
    });
}

// Animate Products
function animateProducts() {
    const products = document.querySelectorAll('.product-card-modern');
    products.forEach((product, index) => {
        product.style.animation = 'none';
        product.offsetHeight; // Trigger reflow
        product.style.animation = `fadeInUp 0.6s ease ${index * 0.1}s forwards`;
    });
}

// Scroll to Top
function initScrollToTop() {
    // Create scroll to top button
    const scrollBtn = document.createElement('button');
    scrollBtn.className = 'scroll-to-top';
    scrollBtn.innerHTML = '<i class="fas fa-arrow-up"></i>';
    scrollBtn.title = 'Retour en haut';
    document.body.appendChild(scrollBtn);

    // Show/hide on scroll
    window.addEventListener('scroll', function() {
        if (window.pageYOffset > 300) {
            scrollBtn.classList.add('show');
        } else {
            scrollBtn.classList.remove('show');
        }
    });

    // Scroll to top on click
    scrollBtn.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
}

// Quick View Modal
function initQuickView() {
    const quickViewBtns = document.querySelectorAll('.quick-view');

    quickViewBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();

            const productId = this.dataset.productId;
            openQuickView(productId);
        });
    });
}

function openQuickView(productId) {
    // Create modal
    const modal = document.createElement('div');
    modal.className = 'quick-view-modal';
    modal.innerHTML = `
        <div class="quick-view-overlay">
            <div class="quick-view-content">
                <button class="close-modal">&times;</button>
                <div class="loading-spinner">
                    <div class="loading"></div>
                    <p>Chargement...</p>
                </div>
            </div>
        </div>
    `;

    document.body.appendChild(modal);

    // Close modal handlers
    const closeBtn = modal.querySelector('.close-modal');
    const overlay = modal.querySelector('.quick-view-overlay');

    closeBtn.addEventListener('click', () => closeQuickView(modal));
    overlay.addEventListener('click', (e) => {
        if (e.target === overlay) closeQuickView(modal);
    });

    // Escape key to close
    document.addEventListener('keydown', function escHandler(e) {
        if (e.key === 'Escape') {
            closeQuickView(modal);
            document.removeEventListener('keydown', escHandler);
        }
    });

    // Simulate loading product data
    setTimeout(() => {
        loadQuickViewContent(modal, productId);
    }, 800);
}

function loadQuickViewContent(modal, productId) {
    const content = modal.querySelector('.quick-view-content');
    content.innerHTML = `
        <button class="close-modal">&times;</button>
        <div class="quick-view-grid">
            <div class="quick-view-image">
                <img src="/static/image/product/tshirt/tshirt1.jpg" alt="Product">
            </div>
            <div class="quick-view-info">
                <h3>Nom du Produit</h3>
                <div class="rating">
                    <div class="stars">
                        <i class="fas fa-star"></i>
                        <i class="fas fa-star"></i>
                        <i class="fas fa-star"></i>
                        <i class="fas fa-star"></i>
                        <i class="fas fa-star-half-alt"></i>
                    </div>
                    <span>4.5 (127 avis)</span>
                </div>
                <div class="price">
                    <span class="current-price">29€</span>
                    <span class="original-price">39€</span>
                </div>
                <p class="description">Description du produit...</p>
                <div class="quick-actions">
                    <button class="btn-primary">Ajouter au panier</button>
                    <a href="/view_product/${productId}" class="btn-secondary">Voir plus</a>
                </div>
            </div>
        </div>
    `;

    // Re-attach close handler
    const closeBtn = content.querySelector('.close-modal');
    closeBtn.addEventListener('click', () => closeQuickView(modal));
}

function closeQuickView(modal) {
    modal.style.animation = 'modalFadeOut 0.3s ease forwards';
    setTimeout(() => {
        document.body.removeChild(modal);
    }, 300);
}

// Wishlist functionality
function initWishlist() {
    const wishlistBtns = document.querySelectorAll('.add-wishlist');

    wishlistBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();

            const icon = this.querySelector('i');
            const isActive = this.classList.contains('active');

            if (isActive) {
                this.classList.remove('active');
                icon.className = 'far fa-heart';
                showToast('Retiré des favoris', 'info');
            } else {
                this.classList.add('active');
                icon.className = 'fas fa-heart';
                showToast('Ajouté aux favoris', 'success');
            }

            // Add animation
            this.style.transform = 'scale(1.2)';
            setTimeout(() => {
                this.style.transform = 'scale(1)';
            }, 200);
        });
    });
}

// Newsletter form
function initNewsletterForm() {
    const newsletterForm = document.querySelector('.newsletter-form');

    if (newsletterForm) {
        newsletterForm.addEventListener('submit', function(e) {
            e.preventDefault();

            const email = this.querySelector('.newsletter-input').value;
            const btn = this.querySelector('.newsletter-btn');

            if (!email || !isValidEmail(email)) {
                showToast('Veuillez entrer une adresse email valide', 'error');
                return;
            }

            // Simulate submission
            btn.innerHTML = '<div class="loading"></div>';
            btn.disabled = true;

            setTimeout(() => {
                btn.innerHTML = 'Inscrit !';
                showToast('Merci pour votre inscription !', 'success');
                this.querySelector('.newsletter-input').value = '';

                setTimeout(() => {
                    btn.innerHTML = 'S\'inscrire';
                    btn.disabled = false;
                }, 2000);
            }, 1500);
        });
    }
}

// Utility Functions
function isValidEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function showToast(message, type = 'info') {
    // Remove existing toasts
    const existingToasts = document.querySelectorAll('.toast');
    existingToasts.forEach(toast => toast.remove());

    // Create new toast
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <div class="toast-content">
            <i class="fas fa-${getToastIcon(type)}"></i>
            <span>${message}</span>
        </div>
    `;

    document.body.appendChild(toast);

    // Auto remove after 3 seconds
    setTimeout(() => {
        if (toast.parentNode) {
            toast.style.animation = 'toastSlideOut 0.3s ease forwards';
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.remove();
                }
            }, 300);
        }
    }, 3000);
}

function getToastIcon(type) {
    switch (type) {
        case 'success': return 'check-circle';
        case 'error': return 'exclamation-circle';
        case 'info': return 'info-circle';
        default: return 'info-circle';
    }
}

// CSS Animations
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes modalFadeOut {
        from {
            opacity: 1;
            transform: scale(1);
        }
        to {
            opacity: 0;
            transform: scale(0.9);
        }
    }

    @keyframes toastSlideOut {
        from {
            transform: translateX(0);
        }
        to {
            transform: translateX(100%);
        }
    }

    .quick-view-modal {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.8);
        z-index: 9999;
        display: flex;
        align-items: center;
        justify-content: center;
        animation: modalFadeIn 0.3s ease;
    }

    .quick-view-overlay {
        width: 100%;
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 20px;
    }

    .quick-view-content {
        background: white;
        border-radius: 16px;
        max-width: 800px;
        width: 100%;
        max-height: 80vh;
        overflow-y: auto;
        position: relative;
        padding: 40px;
    }

    .close-modal {
        position: absolute;
        top: 20px;
        right: 20px;
        background: none;
        border: none;
        font-size: 24px;
        cursor: pointer;
        color: #666;
        z-index: 10;
    }

    .loading-spinner {
        text-align: center;
        padding: 60px 20px;
    }

    .loading-spinner p {
        margin-top: 20px;
        color: #666;
    }

    .quick-view-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 40px;
        align-items: start;
    }

    .quick-view-image img {
        width: 100%;
        border-radius: 12px;
    }

    .quick-view-info h3 {
        font-size: 24px;
        margin-bottom: 16px;
    }

    .quick-view-info .rating {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 16px;
    }

    .quick-view-info .price {
        margin-bottom: 16px;
    }

    .quick-view-info .current-price {
        font-size: 24px;
        font-weight: bold;
        color: #000;
    }

    .quick-view-info .original-price {
        font-size: 18px;
        color: #999;
        text-decoration: line-through;
        margin-left: 8px;
    }

    .quick-actions {
        display: flex;
        gap: 12px;
        margin-top: 24px;
    }

    .btn-secondary {
        background: transparent;
        color: #000;
        border: 2px solid #000;
        padding: 12px 24px;
        border-radius: 8px;
        text-decoration: none;
        font-weight: 600;
        transition: all 0.3s ease;
    }

    .btn-secondary:hover {
        background: #000;
        color: white;
    }

    @media (max-width: 768px) {
        .quick-view-grid {
            grid-template-columns: 1fr;
            gap: 20px;
        }

        .quick-view-content {
            padding: 20px;
            margin: 10px;
        }

        .quick-actions {
            flex-direction: column;
        }
    }
`;
document.head.appendChild(style);
