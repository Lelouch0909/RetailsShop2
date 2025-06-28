/**
 * Likes and Reviews JavaScript
 * Handles dynamic likes and reviews functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    // Get product ID from the page
    const productId = document.querySelector('.like-btn')?.dataset.productId;
    
    if (!productId) return;
    
    // Initialize likes
    initializeLikes(productId);
    
    // Initialize reviews
    initializeReviews(productId);
    
    // Setup like button click handler
    setupLikeButton(productId);
    
    // Setup review form submission
    setupReviewForm(productId);
    
    // Setup star rating functionality
    setupStarRating();
});

/**
 * Initialize likes for a product
 */
function initializeLikes(productId) {
    fetch(`/get_likes/${productId}`)
        .then(response => response.json())
        .then(data => {
            // Update like count
            document.getElementById(`like-count-${productId}`).textContent = data.likes_count;
            
            // Update like icon if user has liked the product
            if (data.user_liked) {
                const likeIcon = document.getElementById(`like-icon-${productId}`);
                likeIcon.classList.remove('far');
                likeIcon.classList.add('fas');
                likeIcon.style.color = '#e74c3c'; // Red color for liked
            }
        })
        .catch(error => console.error('Error fetching likes:', error));
}

/**
 * Initialize reviews for a product
 */
function initializeReviews(productId) {
    fetch(`/get_reviews/${productId}`)
        .then(response => response.json())
        .then(data => {
            // Update average rating
            document.getElementById('average-rating').textContent = data.average_rating;
            
            // Update total reviews count
            document.getElementById('total-reviews').textContent = data.total_reviews;
            document.getElementById('review-count').textContent = `(${data.total_reviews})`;
            
            // Update rating distribution
            updateRatingDistribution(data.rating_distribution, data.total_reviews);
            
            // Update average stars
            updateAverageStars(data.average_rating);
            
            // Display reviews
            displayReviews(data.reviews);
            
            // Show/hide no reviews message
            const noReviewsMessage = document.getElementById('no-reviews-message');
            if (data.reviews.length === 0) {
                noReviewsMessage.style.display = 'block';
            } else {
                noReviewsMessage.style.display = 'none';
            }
            
            // Show/hide load more button
            const loadMoreButton = document.getElementById('load-more-reviews');
            if (data.reviews.length > 5) {
                loadMoreButton.style.display = 'block';
            } else {
                loadMoreButton.style.display = 'none';
            }
        })
        .catch(error => console.error('Error fetching reviews:', error));
}

/**
 * Update rating distribution bars
 */
function updateRatingDistribution(distribution, totalReviews) {
    if (totalReviews === 0) return;
    
    // Update 5-star bar
    const fiveStarCount = distribution[5] || 0;
    const fiveStarPercentage = (fiveStarCount / totalReviews) * 100;
    document.getElementById('five-star-bar').style.width = `${fiveStarPercentage}%`;
    document.getElementById('five-star-count').textContent = fiveStarCount;
    
    // Update 4-star bar
    const fourStarCount = distribution[4] || 0;
    const fourStarPercentage = (fourStarCount / totalReviews) * 100;
    document.getElementById('four-star-bar').style.width = `${fourStarPercentage}%`;
    document.getElementById('four-star-count').textContent = fourStarCount;
    
    // Update 3-star bar
    const threeStarCount = distribution[3] || 0;
    const threeStarPercentage = (threeStarCount / totalReviews) * 100;
    document.getElementById('three-star-bar').style.width = `${threeStarPercentage}%`;
    document.getElementById('three-star-count').textContent = threeStarCount;
    
    // Update 2-star bar
    const twoStarCount = distribution[2] || 0;
    const twoStarPercentage = (twoStarCount / totalReviews) * 100;
    document.getElementById('two-star-bar').style.width = `${twoStarPercentage}%`;
    document.getElementById('two-star-count').textContent = twoStarCount;
    
    // Update 1-star bar
    const oneStarCount = distribution[1] || 0;
    const oneStarPercentage = (oneStarCount / totalReviews) * 100;
    document.getElementById('one-star-bar').style.width = `${oneStarPercentage}%`;
    document.getElementById('one-star-count').textContent = oneStarCount;
}

/**
 * Update average stars display
 */
function updateAverageStars(averageRating) {
    const starsContainer = document.getElementById('average-stars');
    const stars = starsContainer.querySelectorAll('i');
    
    // Reset all stars
    stars.forEach(star => {
        star.className = 'far fa-star';
    });
    
    // Fill stars based on average rating
    const fullStars = Math.floor(averageRating);
    const hasHalfStar = averageRating - fullStars >= 0.5;
    
    // Fill full stars
    for (let i = 0; i < fullStars; i++) {
        stars[i].className = 'fas fa-star';
    }
    
    // Add half star if needed
    if (hasHalfStar && fullStars < 5) {
        stars[fullStars].className = 'fas fa-star-half-alt';
    }
}

/**
 * Display reviews in the reviews container
 */
function displayReviews(reviews) {
    const reviewsContainer = document.getElementById('reviews-container');
    const reviewHeader = reviewsContainer.querySelector('h3');
    const loadMoreButton = document.getElementById('load-more-reviews');
    
    // Clear existing reviews (except header and load more button)
    const children = Array.from(reviewsContainer.children);
    children.forEach(child => {
        if (child !== reviewHeader && child !== loadMoreButton && child.id !== 'no-reviews-message') {
            reviewsContainer.removeChild(child);
        }
    });
    
    // Add reviews
    reviews.forEach(review => {
        const reviewCard = document.createElement('div');
        reviewCard.className = 'review-card';
        reviewCard.innerHTML = `
            <div class="review-header">
                <div class="reviewer-info">
                    <strong>${review.user_name}</strong>
                    <span class="verified-badge"><i class="fas fa-check-circle"></i></span>
                </div>
                <div class="review-stars">
                    ${getStarsHTML(review.rating)}
                </div>
            </div>
            <p class="review-text">"${review.review_text}"</p>
            <span class="review-date">Posted on ${review.created_at}</span>
        `;
        
        // Insert after the header
        reviewsContainer.insertBefore(reviewCard, reviewHeader.nextSibling);
    });
}

/**
 * Get HTML for star rating
 */
function getStarsHTML(rating) {
    let html = '';
    for (let i = 1; i <= 5; i++) {
        if (i <= rating) {
            html += '<i class="fas fa-star"></i>';
        } else {
            html += '<i class="far fa-star"></i>';
        }
    }
    return html;
}

/**
 * Setup like button click handler
 */
function setupLikeButton(productId) {
    const likeButton = document.querySelector('.like-btn');
    if (!likeButton) return;
    
    likeButton.addEventListener('click', function() {
        fetch(`/like_product/${productId}`, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/json'
            }
        })
        .then(response => {
            if (response.status === 401) {
                // User not logged in
                window.location.href = '/login';
                return;
            }
            return response.json();
        })
        .then(data => {
            if (!data) return;
            
            // Update like count
            document.getElementById(`like-count-${productId}`).textContent = data.likes_count;
            
            // Update like icon
            const likeIcon = document.getElementById(`like-icon-${productId}`);
            if (data.action === 'liked') {
                likeIcon.classList.remove('far');
                likeIcon.classList.add('fas');
                likeIcon.style.color = '#e74c3c'; // Red color for liked
            } else {
                likeIcon.classList.remove('fas');
                likeIcon.classList.add('far');
                likeIcon.style.color = ''; // Reset color
            }
        })
        .catch(error => console.error('Error liking product:', error));
    });
}

/**
 * Setup review form submission
 */
function setupReviewForm(productId) {
    const reviewForm = document.getElementById('review-form');
    if (!reviewForm) return;
    
    reviewForm.addEventListener('submit', function(event) {
        event.preventDefault();
        
        const rating = document.getElementById('rating-value').value;
        const reviewText = document.getElementById('review-text').value;
        
        if (!rating || rating === '0') {
            alert('Please select a rating');
            return;
        }
        
        if (!reviewText.trim()) {
            alert('Please enter a review');
            return;
        }
        
        const formData = new FormData();
        formData.append('rating', rating);
        formData.append('review_text', reviewText);
        
        fetch(`/add_review/${productId}`, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: formData
        })
        .then(response => {
            if (response.status === 401) {
                // User not logged in
                window.location.href = '/login';
                return;
            }
            return response.json();
        })
        .then(data => {
            if (!data) return;
            
            // Reset form
            reviewForm.reset();
            resetStarRating();
            
            // Refresh reviews
            initializeReviews(productId);
            
            // Show success message
            alert(data.message);
        })
        .catch(error => console.error('Error submitting review:', error));
    });
}

/**
 * Setup star rating functionality
 */
function setupStarRating() {
    const stars = document.querySelectorAll('.star-rating i');
    if (stars.length === 0) return;
    
    stars.forEach(star => {
        star.addEventListener('mouseover', function() {
            const rating = parseInt(this.dataset.rating);
            highlightStars(rating);
        });
        
        star.addEventListener('mouseout', function() {
            const currentRating = parseInt(document.getElementById('rating-value').value);
            highlightStars(currentRating);
        });
        
        star.addEventListener('click', function() {
            const rating = parseInt(this.dataset.rating);
            document.getElementById('rating-value').value = rating;
            highlightStars(rating);
        });
    });
}

/**
 * Highlight stars up to the given rating
 */
function highlightStars(rating) {
    const stars = document.querySelectorAll('.star-rating i');
    
    stars.forEach((star, index) => {
        if (index < rating) {
            star.classList.remove('far');
            star.classList.add('fas');
        } else {
            star.classList.remove('fas');
            star.classList.add('far');
        }
    });
}

/**
 * Reset star rating
 */
function resetStarRating() {
    document.getElementById('rating-value').value = '0';
    highlightStars(0);
}