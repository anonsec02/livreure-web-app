// Livreure Platform - Main JavaScript File
// API Configuration
const API_BASE_URL = 'https://anonsec02.pythonanywhere.com/api';
const WHATSAPP_NUMBER = '+22241377131';

// Global State
let currentUser = null;
let currentUserType = null;
let currentScreen = 'welcome';
let cartItems = [];
let isLoading = false;

// Initialize Application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Initialize language
    initializeLanguage();
    
    // Setup event listeners
    setupEventListeners();
    
    // Check for existing session
    checkExistingSession();
    
    // Hide loading screen
    setTimeout(() => {
        hideLoadingScreen();
    }, 2000);
    
    // Load initial data
    loadInitialData();
}

function setupEventListeners() {
    // Language switcher
    document.querySelectorAll('.lang-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const lang = e.target.getAttribute('data-lang');
            changeLanguage(lang);
        });
    });
    
    // Auth form submission
    const authForm = document.getElementById('auth-form');
    if (authForm) {
        authForm.addEventListener('submit', handleAuthSubmit);
    }
    
    // Search functionality
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(handleSearch, 300));
    }
    
    // Filter toggles
    const filterToggle = document.querySelector('.filter-toggle');
    if (filterToggle) {
        filterToggle.addEventListener('click', toggleFilters);
    }
    
    // Category filters
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', handleCategoryFilter);
    });
    
    // User menu toggle
    document.querySelectorAll('.user-menu-btn').forEach(btn => {
        btn.addEventListener('click', toggleUserMenu);
    });
    
    // Status toggles
    const restaurantToggle = document.getElementById('restaurant-status-toggle');
    if (restaurantToggle) {
        restaurantToggle.addEventListener('change', toggleRestaurantStatus);
    }
    
    const deliveryToggle = document.getElementById('delivery-status-toggle');
    if (deliveryToggle) {
        deliveryToggle.addEventListener('change', toggleDeliveryStatus);
    }
    
    // Chat functionality
    const chatInputField = document.getElementById('chat-input-field');
    if (chatInputField) {
        chatInputField.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                sendChatMessage();
            }
        });
    }
    
    // Close modals on outside click
    document.addEventListener('click', (e) => {
        if (e.target.classList.contains('modal')) {
            closeModal();
        }
    });
    
    // Close dropdowns on outside click
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.user-menu')) {
            document.querySelectorAll('.user-menu').forEach(menu => {
                menu.classList.remove('active');
            });
        }
    });
}

// Loading Screen Management
function hideLoadingScreen() {
    const loadingScreen = document.getElementById('loading-screen');
    if (loadingScreen) {
        loadingScreen.classList.add('hidden');
        setTimeout(() => {
            loadingScreen.style.display = 'none';
        }, 500);
    }
}

function showLoadingScreen() {
    const loadingScreen = document.getElementById('loading-screen');
    if (loadingScreen) {
        loadingScreen.style.display = 'flex';
        loadingScreen.classList.remove('hidden');
    }
}

// Screen Management
function showScreen(screenId) {
    // Hide all screens
    document.querySelectorAll('.screen').forEach(screen => {
        screen.classList.remove('active');
    });
    
    // Show target screen
    const targetScreen = document.getElementById(screenId);
    if (targetScreen) {
        targetScreen.classList.add('active');
        currentScreen = screenId;
    }
}

function showWelcomeScreen() {
    showScreen('welcome-screen');
}

function showUserForm(userType) {
    currentUserType = userType;
    showScreen('auth-screen');
    
    // Update auth screen title based on user type
    const authTitle = document.getElementById('auth-title');
    const authSubtitle = document.getElementById('auth-subtitle');
    
    if (authTitle && authSubtitle) {
        switch (userType) {
            case 'customer':
                authTitle.textContent = t('login') + ' - ' + t('customer');
                authSubtitle.textContent = t('customer_desc');
                break;
            case 'restaurant':
                authTitle.textContent = t('login') + ' - ' + t('restaurant');
                authSubtitle.textContent = t('restaurant_desc');
                break;
            case 'delivery':
                authTitle.textContent = t('login') + ' - ' + t('delivery_agent');
                authSubtitle.textContent = t('delivery_agent_desc');
                break;
        }
    }
}

// Authentication Management
function switchAuthTab(tab) {
    const loginTab = document.querySelector('.auth-tab:first-child');
    const registerTab = document.querySelector('.auth-tab:last-child');
    const nameGroup = document.getElementById('name-group');
    const confirmPasswordGroup = document.getElementById('confirm-password-group');
    const phoneGroup = document.getElementById('phone-group');
    const authBtn = document.getElementById('auth-btn');
    
    if (tab === 'login') {
        loginTab.classList.add('active');
        registerTab.classList.remove('active');
        nameGroup.style.display = 'none';
        confirmPasswordGroup.style.display = 'none';
        phoneGroup.style.display = 'none';
        authBtn.textContent = t('login');
    } else {
        loginTab.classList.remove('active');
        registerTab.classList.add('active');
        nameGroup.style.display = 'flex';
        confirmPasswordGroup.style.display = 'flex';
        phoneGroup.style.display = 'flex';
        authBtn.textContent = t('register');
    }
}

function togglePassword() {
    const passwordInput = document.getElementById('password');
    const toggleBtn = document.querySelector('.password-toggle i');
    
    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        toggleBtn.className = 'fas fa-eye-slash';
    } else {
        passwordInput.type = 'password';
        toggleBtn.className = 'fas fa-eye';
    }
}

async function handleAuthSubmit(e) {
    e.preventDefault();
    
    if (isLoading) return;
    
    const isLogin = document.querySelector('.auth-tab.active').textContent.trim() === t('login');
    const formData = new FormData(e.target);
    
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    
    if (!email || !password) {
        showNotification(t('required_field'), 'error');
        return;
    }
    
    if (!isLogin) {
        const name = document.getElementById('name').value;
        const confirmPassword = document.getElementById('confirm-password').value;
        const phone = document.getElementById('phone').value;
        
        if (!name || !confirmPassword || !phone) {
            showNotification(t('required_field'), 'error');
            return;
        }
        
        if (password !== confirmPassword) {
            showNotification(t('password_mismatch'), 'error');
            return;
        }
    }
    
    try {
        setLoading(true);
        
        const endpoint = isLogin ? '/auth/login' : '/auth/register';
        const payload = {
            email,
            password,
            user_type: currentUserType
        };
        
        if (!isLogin) {
            payload.name = document.getElementById('name').value;
            payload.phone = document.getElementById('phone').value;
        }
        
        const response = await apiRequest(endpoint, 'POST', payload);
        
        if (response.success) {
            currentUser = response.user;
            localStorage.setItem('livreure_token', response.token);
            localStorage.setItem('livreure_user', JSON.stringify(response.user));
            
            showNotification(isLogin ? t('login_success') : t('register_success'), 'success');
            
            // Redirect to appropriate dashboard
            setTimeout(() => {
                redirectToDashboard(currentUserType);
            }, 1000);
        } else {
            showNotification(response.message || t('error_occurred'), 'error');
        }
    } catch (error) {
        console.error('Auth error:', error);
        showNotification(t('network_error'), 'error');
    } finally {
        setLoading(false);
    }
}

function redirectToDashboard(userType) {
    switch (userType) {
        case 'customer':
            showScreen('customer-dashboard');
            loadCustomerData();
            break;
        case 'restaurant':
            showScreen('restaurant-dashboard');
            loadRestaurantData();
            break;
        case 'delivery':
            showScreen('delivery-dashboard');
            loadDeliveryData();
            break;
    }
}

function checkExistingSession() {
    const token = localStorage.getItem('livreure_token');
    const user = localStorage.getItem('livreure_user');
    
    if (token && user) {
        try {
            currentUser = JSON.parse(user);
            currentUserType = currentUser.user_type;
            redirectToDashboard(currentUserType);
        } catch (error) {
            console.error('Session error:', error);
            logout();
        }
    }
}

function logout() {
    currentUser = null;
    currentUserType = null;
    cartItems = [];
    
    localStorage.removeItem('livreure_token');
    localStorage.removeItem('livreure_user');
    
    showWelcomeScreen();
    showNotification(t('logout'), 'info');
}

// API Request Handler
async function apiRequest(endpoint, method = 'GET', data = null) {
    const token = localStorage.getItem('livreure_token');
    
    const config = {
        method,
        headers: {
            'Content-Type': 'application/json',
        }
    };
    
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    
    if (data && method !== 'GET') {
        config.body = JSON.stringify(data);
    }
    
    try {
        const response = await fetch(API_BASE_URL + endpoint, config);
        
        if (response.status === 401) {
            logout();
            throw new Error('Unauthorized');
        }
        
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// Customer Dashboard Functions
async function loadCustomerData() {
    try {
        // Update user name
        const customerName = document.getElementById('customer-name');
        if (customerName && currentUser) {
            customerName.textContent = currentUser.name || t('customer');
        }
        
        // Load restaurants
        await loadRestaurants();
        
        // Load user orders
        await loadUserOrders();
        
    } catch (error) {
        console.error('Error loading customer data:', error);
    }
}

async function loadRestaurants() {
    try {
        const response = await apiRequest('/restaurants');
        
        if (response.success) {
            displayRestaurants(response.restaurants);
        }
    } catch (error) {
        console.error('Error loading restaurants:', error);
    }
}

function displayRestaurants(restaurants) {
    const restaurantsGrid = document.getElementById('restaurants-grid');
    if (!restaurantsGrid) return;
    
    restaurantsGrid.innerHTML = '';
    
    restaurants.forEach(restaurant => {
        const restaurantCard = createRestaurantCard(restaurant);
        restaurantsGrid.appendChild(restaurantCard);
    });
}

function createRestaurantCard(restaurant) {
    const card = document.createElement('div');
    card.className = 'restaurant-card';
    card.onclick = () => openRestaurantModal(restaurant.id);
    
    card.innerHTML = `
        <div class="restaurant-image">
            <img src="${restaurant.image || 'https://via.placeholder.com/300x200/D4AF37/000000?text=' + restaurant.name}" alt="${restaurant.name}">
            <div class="restaurant-status ${restaurant.is_open ? 'open' : 'closed'}">
                ${restaurant.is_open ? t('open') : t('closed')}
            </div>
        </div>
        <div class="restaurant-info">
            <h3>${restaurant.name}</h3>
            <p class="restaurant-category">${restaurant.category}</p>
            <div class="restaurant-meta">
                <div class="rating">
                    <i class="fas fa-star"></i>
                    <span>${restaurant.rating || '4.5'}</span>
                </div>
                <div class="delivery-time">
                    <i class="fas fa-clock"></i>
                    <span>${restaurant.delivery_time || '30-45'} ${t('minutes')}</span>
                </div>
                <div class="delivery-fee">
                    <i class="fas fa-motorcycle"></i>
                    <span>${restaurant.delivery_fee || '100'} ${t('ouguiya')}</span>
                </div>
            </div>
        </div>
    `;
    
    return card;
}

async function openRestaurantModal(restaurantId) {
    try {
        const response = await apiRequest(`/restaurants/${restaurantId}`);
        
        if (response.success) {
            displayRestaurantModal(response.restaurant);
        }
    } catch (error) {
        console.error('Error loading restaurant details:', error);
    }
}

function displayRestaurantModal(restaurant) {
    const modal = document.getElementById('restaurant-modal');
    const modalName = document.getElementById('modal-restaurant-name');
    const restaurantDetails = document.getElementById('restaurant-details');
    
    if (!modal || !modalName || !restaurantDetails) return;
    
    modalName.textContent = restaurant.name;
    
    restaurantDetails.innerHTML = `
        <div class="restaurant-header">
            <img src="${restaurant.image || 'https://via.placeholder.com/400x200/D4AF37/000000?text=' + restaurant.name}" alt="${restaurant.name}">
            <div class="restaurant-info">
                <h2>${restaurant.name}</h2>
                <p>${restaurant.description || ''}</p>
                <div class="restaurant-meta">
                    <span class="rating">
                        <i class="fas fa-star"></i>
                        ${restaurant.rating || '4.5'}
                    </span>
                    <span class="delivery-time">
                        <i class="fas fa-clock"></i>
                        ${restaurant.delivery_time || '30-45'} ${t('minutes')}
                    </span>
                </div>
            </div>
        </div>
        <div class="menu-section">
            <h3>${t('menu')}</h3>
            <div class="menu-items" id="modal-menu-items">
                ${restaurant.menu_items ? restaurant.menu_items.map(item => createMenuItemCard(item)).join('') : ''}
            </div>
        </div>
    `;
    
    modal.classList.add('active');
}

function createMenuItemCard(item) {
    return `
        <div class="menu-item-card">
            <img src="${item.image || 'https://via.placeholder.com/150x150/D4AF37/000000?text=' + item.name}" alt="${item.name}">
            <div class="menu-item-info">
                <h4>${item.name}</h4>
                <p>${item.description || ''}</p>
                <div class="menu-item-footer">
                    <span class="price">${item.price} ${t('ouguiya')}</span>
                    <button class="add-to-cart-btn" onclick="addToCart(${item.id}, '${item.name}', ${item.price})">
                        <i class="fas fa-plus"></i>
                        ${t('add')}
                    </button>
                </div>
            </div>
        </div>
    `;
}

function closeModal() {
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        modal.classList.remove('active');
    });
}

// Cart Management
function addToCart(itemId, itemName, itemPrice) {
    const existingItem = cartItems.find(item => item.id === itemId);
    
    if (existingItem) {
        existingItem.quantity += 1;
    } else {
        cartItems.push({
            id: itemId,
            name: itemName,
            price: itemPrice,
            quantity: 1
        });
    }
    
    updateCartDisplay();
    showNotification(`${itemName} ${t('add')} ${t('shopping_cart')}`, 'success');
}

function removeFromCart(itemId) {
    cartItems = cartItems.filter(item => item.id !== itemId);
    updateCartDisplay();
}

function updateCartQuantity(itemId, quantity) {
    const item = cartItems.find(item => item.id === itemId);
    if (item) {
        if (quantity <= 0) {
            removeFromCart(itemId);
        } else {
            item.quantity = quantity;
        }
        updateCartDisplay();
    }
}

function updateCartDisplay() {
    const cartCount = document.getElementById('cart-count');
    const cartTotal = document.getElementById('cart-total');
    const cartItems = document.getElementById('cart-items');
    
    const totalItems = cartItems.reduce((sum, item) => sum + item.quantity, 0);
    const totalPrice = cartItems.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    
    if (cartCount) {
        cartCount.textContent = totalItems;
        cartCount.style.display = totalItems > 0 ? 'block' : 'none';
    }
    
    if (cartTotal) {
        cartTotal.textContent = `${totalPrice} ${t('ouguiya')}`;
    }
    
    if (cartItems) {
        cartItems.innerHTML = cartItems.length > 0 
            ? cartItems.map(item => createCartItemElement(item)).join('')
            : `<p class="empty-cart">${t('shopping_cart')} ${t('empty')}</p>`;
    }
}

function createCartItemElement(item) {
    return `
        <div class="cart-item">
            <div class="cart-item-info">
                <h4>${item.name}</h4>
                <p class="cart-item-price">${item.price} ${t('ouguiya')}</p>
            </div>
            <div class="cart-item-controls">
                <button onclick="updateCartQuantity(${item.id}, ${item.quantity - 1})">
                    <i class="fas fa-minus"></i>
                </button>
                <span class="quantity">${item.quantity}</span>
                <button onclick="updateCartQuantity(${item.id}, ${item.quantity + 1})">
                    <i class="fas fa-plus"></i>
                </button>
            </div>
            <button class="remove-item" onclick="removeFromCart(${item.id})">
                <i class="fas fa-trash"></i>
            </button>
        </div>
    `;
}

function toggleCart() {
    const cartSidebar = document.getElementById('cart-sidebar');
    if (cartSidebar) {
        cartSidebar.classList.toggle('active');
    }
}

async function proceedToCheckout() {
    if (cartItems.length === 0) {
        showNotification(t('shopping_cart') + ' ' + t('empty'), 'warning');
        return;
    }
    
    try {
        setLoading(true);
        
        const orderData = {
            items: cartItems,
            total: cartItems.reduce((sum, item) => sum + (item.price * item.quantity), 0)
        };
        
        const response = await apiRequest('/orders', 'POST', orderData);
        
        if (response.success) {
            cartItems = [];
            updateCartDisplay();
            toggleCart();
            showNotification(t('order_placed'), 'success');
        } else {
            showNotification(response.message || t('error_occurred'), 'error');
        }
    } catch (error) {
        console.error('Checkout error:', error);
        showNotification(t('network_error'), 'error');
    } finally {
        setLoading(false);
    }
}

// Restaurant Dashboard Functions
async function loadRestaurantData() {
    try {
        // Update restaurant name
        const restaurantName = document.getElementById('restaurant-name');
        if (restaurantName && currentUser) {
            restaurantName.textContent = currentUser.restaurant_name || t('restaurant');
        }
        
        // Load restaurant stats
        await loadRestaurantStats();
        
        // Load restaurant orders
        await loadRestaurantOrders();
        
        // Load menu items
        await loadMenuItems();
        
    } catch (error) {
        console.error('Error loading restaurant data:', error);
    }
}

async function loadRestaurantStats() {
    try {
        const response = await apiRequest('/restaurant/stats');
        
        if (response.success) {
            updateRestaurantStats(response.stats);
        }
    } catch (error) {
        console.error('Error loading restaurant stats:', error);
    }
}

function updateRestaurantStats(stats) {
    const todayOrders = document.getElementById('today-orders');
    const pendingOrders = document.getElementById('pending-orders');
    const todayRevenue = document.getElementById('today-revenue');
    const restaurantRating = document.getElementById('restaurant-rating');
    
    if (todayOrders) todayOrders.textContent = stats.today_orders || '0';
    if (pendingOrders) pendingOrders.textContent = stats.pending_orders || '0';
    if (todayRevenue) todayRevenue.textContent = stats.today_revenue || '0';
    if (restaurantRating) restaurantRating.textContent = stats.rating || '0.0';
}

async function loadRestaurantOrders() {
    try {
        const response = await apiRequest('/restaurant/orders');
        
        if (response.success) {
            displayRestaurantOrders(response.orders);
        }
    } catch (error) {
        console.error('Error loading restaurant orders:', error);
    }
}

function displayRestaurantOrders(orders) {
    const ordersList = document.getElementById('restaurant-orders-list');
    if (!ordersList) return;
    
    ordersList.innerHTML = orders.length > 0
        ? orders.map(order => createRestaurantOrderCard(order)).join('')
        : `<p class="no-orders">${t('no_orders')}</p>`;
}

function createRestaurantOrderCard(order) {
    return `
        <div class="order-card">
            <div class="order-header">
                <h4>${t('order')} #${order.id}</h4>
                <span class="order-status ${order.status}">${t(order.status)}</span>
            </div>
            <div class="order-details">
                <p><strong>${t('customer')}:</strong> ${order.customer_name}</p>
                <p><strong>${t('total')}:</strong> ${order.total} ${t('ouguiya')}</p>
                <p><strong>${t('time')}:</strong> ${formatTime(order.created_at)}</p>
            </div>
            <div class="order-items">
                ${order.items.map(item => `
                    <div class="order-item">
                        <span>${item.name} x${item.quantity}</span>
                        <span>${item.price * item.quantity} ${t('ouguiya')}</span>
                    </div>
                `).join('')}
            </div>
            <div class="order-actions">
                ${order.status === 'pending' ? `
                    <button onclick="updateOrderStatus(${order.id}, 'preparing')" class="btn-accept">
                        ${t('accept')}
                    </button>
                    <button onclick="updateOrderStatus(${order.id}, 'cancelled')" class="btn-reject">
                        ${t('reject')}
                    </button>
                ` : ''}
                ${order.status === 'preparing' ? `
                    <button onclick="updateOrderStatus(${order.id}, 'ready')" class="btn-ready">
                        ${t('mark_ready')}
                    </button>
                ` : ''}
            </div>
        </div>
    `;
}

async function updateOrderStatus(orderId, status) {
    try {
        setLoading(true);
        
        const response = await apiRequest(`/orders/${orderId}/status`, 'PUT', { status });
        
        if (response.success) {
            showNotification(t('order_updated'), 'success');
            await loadRestaurantOrders();
        } else {
            showNotification(response.message || t('error_occurred'), 'error');
        }
    } catch (error) {
        console.error('Error updating order status:', error);
        showNotification(t('network_error'), 'error');
    } finally {
        setLoading(false);
    }
}

function showRestaurantTab(tabName) {
    // Hide all tab contents
    document.querySelectorAll('#restaurant-dashboard .tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Remove active class from all tab buttons
    document.querySelectorAll('#restaurant-dashboard .tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab content
    const targetTab = document.getElementById(`restaurant-${tabName}-tab`);
    if (targetTab) {
        targetTab.classList.add('active');
    }
    
    // Add active class to clicked button
    const targetBtn = document.querySelector(`#restaurant-dashboard .tab-btn[onclick="showRestaurantTab('${tabName}')"]`);
    if (targetBtn) {
        targetBtn.classList.add('active');
    }
}

function toggleRestaurantStatus() {
    const toggle = document.getElementById('restaurant-status-toggle');
    const statusText = toggle.nextElementSibling;
    
    if (toggle.checked) {
        statusText.textContent = t('open');
        updateRestaurantStatus(true);
    } else {
        statusText.textContent = t('closed');
        updateRestaurantStatus(false);
    }
}

async function updateRestaurantStatus(isOpen) {
    try {
        const response = await apiRequest('/restaurant/status', 'PUT', { is_open: isOpen });
        
        if (response.success) {
            showNotification(
                isOpen ? t('restaurant_opened') : t('restaurant_closed'), 
                'success'
            );
        }
    } catch (error) {
        console.error('Error updating restaurant status:', error);
    }
}

// Delivery Dashboard Functions
async function loadDeliveryData() {
    try {
        // Update delivery agent name
        const deliveryName = document.getElementById('delivery-name');
        if (deliveryName && currentUser) {
            deliveryName.textContent = currentUser.name || t('delivery_agent');
        }
        
        // Load delivery stats
        await loadDeliveryStats();
        
        // Load available orders
        await loadAvailableOrders();
        
    } catch (error) {
        console.error('Error loading delivery data:', error);
    }
}

async function loadDeliveryStats() {
    try {
        const response = await apiRequest('/delivery/stats');
        
        if (response.success) {
            updateDeliveryStats(response.stats);
        }
    } catch (error) {
        console.error('Error loading delivery stats:', error);
    }
}

function updateDeliveryStats(stats) {
    const completedDeliveries = document.getElementById('completed-deliveries');
    const todayEarnings = document.getElementById('today-earnings');
    const deliveryRating = document.getElementById('delivery-rating');
    const avgDeliveryTime = document.getElementById('avg-delivery-time');
    
    if (completedDeliveries) completedDeliveries.textContent = stats.completed_deliveries || '0';
    if (todayEarnings) todayEarnings.textContent = stats.today_earnings || '0';
    if (deliveryRating) deliveryRating.textContent = stats.rating || '0.0';
    if (avgDeliveryTime) avgDeliveryTime.textContent = stats.avg_delivery_time || '0';
}

async function loadAvailableOrders() {
    try {
        const response = await apiRequest('/delivery/available-orders');
        
        if (response.success) {
            displayAvailableOrders(response.orders);
        }
    } catch (error) {
        console.error('Error loading available orders:', error);
    }
}

function displayAvailableOrders(orders) {
    const ordersList = document.getElementById('available-orders-list');
    if (!ordersList) return;
    
    ordersList.innerHTML = orders.length > 0
        ? orders.map(order => createAvailableOrderCard(order)).join('')
        : `<p class="no-orders">${t('no_available_orders')}</p>`;
}

function createAvailableOrderCard(order) {
    return `
        <div class="available-order-card">
            <div class="order-info">
                <h4>${t('order')} #${order.id}</h4>
                <p><strong>${t('restaurant')}:</strong> ${order.restaurant_name}</p>
                <p><strong>${t('customer')}:</strong> ${order.customer_name}</p>
                <p><strong>${t('delivery_address')}:</strong> ${order.delivery_address}</p>
                <p><strong>${t('total')}:</strong> ${order.total} ${t('ouguiya')}</p>
                <p><strong>${t('delivery_fee')}:</strong> ${order.delivery_fee} ${t('ouguiya')}</p>
            </div>
            <div class="order-distance">
                <i class="fas fa-map-marker-alt"></i>
                <span>${order.distance || '2.5'} km</span>
            </div>
            <button onclick="acceptDeliveryOrder(${order.id})" class="accept-order-btn">
                ${t('accept_order')}
            </button>
        </div>
    `;
}

async function acceptDeliveryOrder(orderId) {
    try {
        setLoading(true);
        
        const response = await apiRequest(`/delivery/accept-order/${orderId}`, 'POST');
        
        if (response.success) {
            showNotification(t('order_accepted'), 'success');
            await loadAvailableOrders();
            showDeliveryTab('current');
        } else {
            showNotification(response.message || t('error_occurred'), 'error');
        }
    } catch (error) {
        console.error('Error accepting order:', error);
        showNotification(t('network_error'), 'error');
    } finally {
        setLoading(false);
    }
}

function showDeliveryTab(tabName) {
    // Hide all tab contents
    document.querySelectorAll('#delivery-dashboard .tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Remove active class from all tab buttons
    document.querySelectorAll('#delivery-dashboard .tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab content
    const targetTab = document.getElementById(`delivery-${tabName}-tab`);
    if (targetTab) {
        targetTab.classList.add('active');
    }
    
    // Add active class to clicked button
    const targetBtn = document.querySelector(`#delivery-dashboard .tab-btn[onclick="showDeliveryTab('${tabName}')"]`);
    if (targetBtn) {
        targetBtn.classList.add('active');
    }
}

function toggleDeliveryStatus() {
    const toggle = document.getElementById('delivery-status-toggle');
    const statusText = document.getElementById('status-text');
    
    if (toggle.checked) {
        statusText.textContent = t('available');
        updateDeliveryStatus(true);
    } else {
        statusText.textContent = t('unavailable');
        updateDeliveryStatus(false);
    }
}

async function updateDeliveryStatus(isAvailable) {
    try {
        const response = await apiRequest('/delivery/status', 'PUT', { is_available: isAvailable });
        
        if (response.success) {
            showNotification(
                isAvailable ? t('now_available') : t('now_unavailable'), 
                'success'
            );
        }
    } catch (error) {
        console.error('Error updating delivery status:', error);
    }
}

// Search and Filter Functions
function handleSearch(e) {
    const query = e.target.value.toLowerCase();
    const restaurantCards = document.querySelectorAll('.restaurant-card');
    
    restaurantCards.forEach(card => {
        const restaurantName = card.querySelector('h3').textContent.toLowerCase();
        const restaurantCategory = card.querySelector('.restaurant-category').textContent.toLowerCase();
        
        if (restaurantName.includes(query) || restaurantCategory.includes(query)) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
}

function toggleFilters() {
    const filtersPanel = document.getElementById('filters-panel');
    if (filtersPanel) {
        filtersPanel.classList.toggle('active');
    }
}

function handleCategoryFilter(e) {
    const category = e.target.getAttribute('data-category');
    const restaurantCards = document.querySelectorAll('.restaurant-card');
    
    // Update active filter button
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    e.target.classList.add('active');
    
    // Filter restaurants
    restaurantCards.forEach(card => {
        const restaurantCategory = card.querySelector('.restaurant-category').textContent.toLowerCase();
        
        if (category === 'all' || restaurantCategory.includes(category.replace('-', ' '))) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
}

// Support Chat Functions
function toggleSupportChat() {
    const chatWindow = document.getElementById('chat-window');
    if (chatWindow) {
        chatWindow.classList.toggle('active');
    }
}

function sendChatMessage() {
    const inputField = document.getElementById('chat-input-field');
    const message = inputField.value.trim();
    
    if (!message) return;
    
    // Add user message to chat
    addChatMessage(message, 'user');
    
    // Clear input
    inputField.value = '';
    
    // Simulate bot response or redirect to WhatsApp
    setTimeout(() => {
        const whatsappUrl = `https://wa.me/${WHATSAPP_NUMBER.replace('+', '')}?text=${encodeURIComponent(message)}`;
        window.open(whatsappUrl, '_blank');
        
        addChatMessage(t('redirecting_whatsapp'), 'bot');
    }, 1000);
}

function addChatMessage(message, sender) {
    const chatMessages = document.getElementById('chat-messages');
    if (!chatMessages) return;
    
    const messageElement = document.createElement('div');
    messageElement.className = `message ${sender}-message`;
    messageElement.innerHTML = `<p>${message}</p>`;
    
    chatMessages.appendChild(messageElement);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// User Menu Functions
function toggleUserMenu() {
    const userMenus = document.querySelectorAll('.user-menu');
    userMenus.forEach(menu => {
        menu.classList.toggle('active');
    });
}

// Utility Functions
function setLoading(loading) {
    isLoading = loading;
    const authBtn = document.getElementById('auth-btn');
    
    if (authBtn) {
        if (loading) {
            authBtn.disabled = true;
            authBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> ' + t('loading');
        } else {
            authBtn.disabled = false;
            const isLogin = document.querySelector('.auth-tab.active').textContent.trim() === t('login');
            authBtn.textContent = isLogin ? t('login') : t('register');
        }
    }
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas fa-${getNotificationIcon(type)}"></i>
            <span>${message}</span>
        </div>
        <button class="notification-close" onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    // Add to page
    document.body.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 5000);
}

function getNotificationIcon(type) {
    switch (type) {
        case 'success': return 'check-circle';
        case 'error': return 'exclamation-circle';
        case 'warning': return 'exclamation-triangle';
        default: return 'info-circle';
    }
}

function formatTime(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleTimeString(currentLanguage === 'ar' ? 'ar-MR' : currentLanguage, {
        hour: '2-digit',
        minute: '2-digit'
    });
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Load initial data
async function loadInitialData() {
    try {
        // Load any initial data needed for the app
        console.log('Loading initial data...');
    } catch (error) {
        console.error('Error loading initial data:', error);
    }
}

// Export functions for global access
window.showUserForm = showUserForm;
window.showWelcomeScreen = showWelcomeScreen;
window.switchAuthTab = switchAuthTab;
window.togglePassword = togglePassword;
window.logout = logout;
window.toggleCart = toggleCart;
window.addToCart = addToCart;
window.removeFromCart = removeFromCart;
window.updateCartQuantity = updateCartQuantity;
window.proceedToCheckout = proceedToCheckout;
window.openRestaurantModal = openRestaurantModal;
window.closeModal = closeModal;
window.toggleFilters = toggleFilters;
window.handleCategoryFilter = handleCategoryFilter;
window.toggleUserMenu = toggleUserMenu;
window.showRestaurantTab = showRestaurantTab;
window.showDeliveryTab = showDeliveryTab;
window.toggleRestaurantStatus = toggleRestaurantStatus;
window.toggleDeliveryStatus = toggleDeliveryStatus;
window.updateOrderStatus = updateOrderStatus;
window.acceptDeliveryOrder = acceptDeliveryOrder;
window.toggleSupportChat = toggleSupportChat;
window.sendChatMessage = sendChatMessage;

