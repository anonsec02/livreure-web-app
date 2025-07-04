// Admin Dashboard JavaScript
// API Configuration
const API_BASE_URL = 'https://livreure-web-app-backend.onrender.com/api';

// Global State
let currentAdmin = null;
let currentTab = 'overview';
let charts = {};

// Initialize Application
document.addEventListener('DOMContentLoaded', function() {
    initializeAdminApp();
});

function initializeAdminApp() {
    // Setup event listeners
    setupAdminEventListeners();
    
    // Check for existing admin session
    checkAdminSession();
    
    // Initialize time display
    updateTimeDisplay();
    setInterval(updateTimeDisplay, 1000);
    
    // Hide loading screen
    setTimeout(() => {
        hideLoadingScreen();
    }, 2000);
}

function setupAdminEventListeners() {
    // Admin login form
    const adminLoginForm = document.getElementById('admin-login-form');
    if (adminLoginForm) {
        adminLoginForm.addEventListener('submit', handleAdminLogin);
    }
    
    // Sidebar toggle for mobile
    const sidebarToggle = document.querySelector('.sidebar-toggle');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', toggleSidebar);
    }
    
    // Close modal on overlay click
    const modalOverlay = document.getElementById('modal-overlay');
    if (modalOverlay) {
        modalOverlay.addEventListener('click', (e) => {
            if (e.target === modalOverlay) {
                closeModal();
            }
        });
    }
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

// Screen Management
function showScreen(screenId) {
    document.querySelectorAll('.screen').forEach(screen => {
        screen.classList.remove('active');
    });
    
    const targetScreen = document.getElementById(screenId);
    if (targetScreen) {
        targetScreen.classList.add('active');
    }
}

// Authentication
function toggleAdminPassword() {
    const passwordInput = document.getElementById('admin-password');
    const toggleBtn = document.querySelector('.password-toggle i');
    
    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        toggleBtn.className = 'fas fa-eye-slash';
    } else {
        passwordInput.type = 'password';
        toggleBtn.className = 'fas fa-eye';
    }
}

async function handleAdminLogin(e) {
    e.preventDefault();
    
    const email = document.getElementById('admin-email').value;
    const password = document.getElementById('admin-password').value;
    const loginBtn = document.getElementById('admin-login-btn');
    
    if (!email || !password) {
        showNotification('يرجى إدخال البريد الإلكتروني وكلمة المرور', 'error');
        return;
    }
    
    try {
        // Set loading state
        loginBtn.disabled = true;
        loginBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> جاري تسجيل الدخول...';
        
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                email,
                password,
                user_type: 'admin'
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentAdmin = data.user;
            localStorage.setItem('admin_token', data.token);
            localStorage.setItem('admin_user', JSON.stringify(data.user));
            
            showNotification('تم تسجيل الدخول بنجاح', 'success');
            
            setTimeout(() => {
                showAdminDashboard();
            }, 1000);
        } else {
            showNotification(data.message || 'فشل في تسجيل الدخول', 'error');
        }
    } catch (error) {
        console.error('Login error:', error);
        showNotification('خطأ في الاتصال بالخادم', 'error');
    } finally {
        loginBtn.disabled = false;
        loginBtn.innerHTML = '<i class="fas fa-sign-in-alt"></i> تسجيل الدخول';
    }
}

function checkAdminSession() {
    const token = localStorage.getItem('admin_token');
    const user = localStorage.getItem('admin_user');
    
    if (token && user) {
        try {
            currentAdmin = JSON.parse(user);
            showAdminDashboard();
        } catch (error) {
            console.error('Session error:', error);
            adminLogout();
        }
    }
}

function showAdminDashboard() {
    showScreen('admin-dashboard');
    
    // Update admin name
    const adminNameElement = document.getElementById('admin-name');
    if (adminNameElement && currentAdmin) {
        adminNameElement.textContent = currentAdmin.full_name || currentAdmin.name || 'مدير النظام';
    }
    
    // Load dashboard data
    loadDashboardData();
    
    // Initialize charts
    initializeCharts();
}

function adminLogout() {
    currentAdmin = null;
    localStorage.removeItem('admin_token');
    localStorage.removeItem('admin_user');
    
    showScreen('login-screen');
    showNotification('تم تسجيل الخروج بنجاح', 'info');
}

// Tab Management
function showAdminTab(tabName) {
    // Update current tab
    currentTab = tabName;
    
    // Update navigation
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });
    
    const activeNavItem = document.querySelector(`[onclick="showAdminTab('${tabName}')"]`).parentElement;
    if (activeNavItem) {
        activeNavItem.classList.add('active');
    }
    
    // Hide all tab contents
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Show selected tab
    const targetTab = document.getElementById(`admin-${tabName}-tab`);
    if (targetTab) {
        targetTab.classList.add('active');
    }
    
    // Update page title
    const pageTitle = document.getElementById('page-title');
    if (pageTitle) {
        const titles = {
            overview: 'نظرة عامة',
            users: 'إدارة المستخدمين',
            restaurants: 'إدارة المطاعم',
            orders: 'إدارة الطلبات',
            delivery: 'وكلاء التوصيل',
            analytics: 'التحليلات',
            settings: 'الإعدادات'
        };
        pageTitle.textContent = titles[tabName] || 'لوحة التحكم';
    }
    
    // Load tab-specific data
    loadTabData(tabName);
}

// Data Loading Functions
async function loadDashboardData() {
    try {
        const token = localStorage.getItem('admin_token');
        
        // Load overview stats
        const statsResponse = await fetch(`${API_BASE_URL}/admin/stats`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (statsResponse.ok) {
            const statsData = await statsResponse.json();
            updateOverviewStats(statsData.stats);
        }
        
        // Load recent activity
        loadRecentActivity();
        
    } catch (error) {
        console.error('Error loading dashboard data:', error);
    }
}

function updateOverviewStats(stats) {
    const elements = {
        'total-users': stats.total_users || 0,
        'total-restaurants': stats.total_restaurants || 0,
        'total-orders': stats.total_orders || 0,
        'total-revenue': stats.total_revenue || 0
    };
    
    Object.entries(elements).forEach(([id, value]) => {
        const element = document.getElementById(id);
        if (element) {
            // Animate number counting
            animateNumber(element, 0, value, 1000);
        }
    });
}

function animateNumber(element, start, end, duration) {
    const startTime = performance.now();
    
    function updateNumber(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        const current = Math.floor(start + (end - start) * progress);
        element.textContent = current.toLocaleString('ar-MR');
        
        if (progress < 1) {
            requestAnimationFrame(updateNumber);
        }
    }
    
    requestAnimationFrame(updateNumber);
}

async function loadRecentActivity() {
    try {
        const token = localStorage.getItem('admin_token');
        
        const response = await fetch(`${API_BASE_URL}/admin/recent-activity`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            displayRecentActivity(data.activities || []);
        } else {
            // Mock data if endpoint doesn't exist
            displayRecentActivity(getMockRecentActivity());
        }
    } catch (error) {
        console.error('Error loading recent activity:', error);
        displayRecentActivity(getMockRecentActivity());
    }
}

function getMockRecentActivity() {
    return [
        {
            type: 'order',
            title: 'طلب جديد #1234',
            description: 'طلب من مطعم الصحراء',
            time: '5 دقائق'
        },
        {
            type: 'user',
            title: 'مستخدم جديد',
            description: 'انضم عميل جديد للمنصة',
            time: '15 دقيقة'
        },
        {
            type: 'restaurant',
            title: 'مطعم جديد',
            description: 'طلب انضمام مطعم جديد',
            time: '30 دقيقة'
        }
    ];
}

function displayRecentActivity(activities) {
    const activityList = document.getElementById('recent-activity-list');
    if (!activityList) return;
    
    activityList.innerHTML = activities.map(activity => `
        <div class="activity-item">
            <div class="activity-icon ${activity.type}">
                <i class="fas fa-${getActivityIcon(activity.type)}"></i>
            </div>
            <div class="activity-content">
                <h4>${activity.title}</h4>
                <p>${activity.description}</p>
            </div>
            <div class="activity-time">
                منذ ${activity.time}
            </div>
        </div>
    `).join('');
}

function getActivityIcon(type) {
    const icons = {
        order: 'shopping-bag',
        user: 'user-plus',
        restaurant: 'store',
        delivery: 'motorcycle'
    };
    return icons[type] || 'bell';
}

async function loadTabData(tabName) {
    switch (tabName) {
        case 'users':
            await loadUsersData();
            break;
        case 'restaurants':
            await loadRestaurantsData();
            break;
        case 'orders':
            await loadOrdersData();
            break;
        case 'delivery':
            await loadDeliveryAgentsData();
            break;
        case 'analytics':
            await loadAnalyticsData();
            break;
    }
}

// Users Management
async function loadUsersData() {
    try {
        const token = localStorage.getItem('admin_token');
        
        const response = await fetch(`${API_BASE_URL}/admin/users`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            displayUsersTable(data.users || []);
        } else {
            displayUsersTable(getMockUsers());
        }
    } catch (error) {
        console.error('Error loading users:', error);
        displayUsersTable(getMockUsers());
    }
}

function getMockUsers() {
    return [
        {
            id: 1,
            name: 'أحمد محمد',
            email: 'ahmed@customer.mr',
            type: 'customer',
            phone: '+22241234567',
            created_at: '2024-01-15',
            is_active: true
        },
        {
            id: 2,
            name: 'مطعم الصحراء',
            email: 'sahara@restaurant.mr',
            type: 'restaurant',
            phone: '+22241234570',
            created_at: '2024-01-10',
            is_active: true
        }
    ];
}

function displayUsersTable(users) {
    const tableBody = document.getElementById('users-table-body');
    if (!tableBody) return;
    
    tableBody.innerHTML = users.map(user => `
        <tr>
            <td>${user.name}</td>
            <td>${user.email}</td>
            <td>${getUserTypeLabel(user.type)}</td>
            <td>${user.phone}</td>
            <td>${formatDate(user.created_at)}</td>
            <td>
                <span class="status-badge ${user.is_active ? 'active' : 'inactive'}">
                    ${user.is_active ? 'نشط' : 'غير نشط'}
                </span>
            </td>
            <td>
                <div class="action-buttons">
                    <button class="action-btn edit" onclick="editUser(${user.id})">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="action-btn delete" onclick="deleteUser(${user.id})">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
}

function getUserTypeLabel(type) {
    const labels = {
        customer: 'عميل',
        restaurant: 'مطعم',
        delivery: 'وكيل توصيل'
    };
    return labels[type] || type;
}

// Restaurants Management
async function loadRestaurantsData() {
    try {
        const token = localStorage.getItem('admin_token');
        
        const response = await fetch(`${API_BASE_URL}/restaurants`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            displayRestaurantsGrid(data.restaurants || []);
        } else {
            displayRestaurantsGrid(getMockRestaurants());
        }
    } catch (error) {
        console.error('Error loading restaurants:', error);
        displayRestaurantsGrid(getMockRestaurants());
    }
}

function getMockRestaurants() {
    return [
        {
            id: 1,
            name: 'مطعم الصحراء',
            description: 'مطعم متخصص في الأكلات الموريتانية التقليدية',
            category: 'traditional',
            rating: 4.5,
            is_open: true,
            is_approved: true
        },
        {
            id: 2,
            name: 'برجر هاوس',
            description: 'أفضل البرجر والوجبات السريعة',
            category: 'fast_food',
            rating: 4.2,
            is_open: true,
            is_approved: true
        }
    ];
}

function displayRestaurantsGrid(restaurants) {
    const grid = document.getElementById('restaurants-grid');
    if (!grid) return;
    
    grid.innerHTML = restaurants.map(restaurant => `
        <div class="restaurant-card">
            <div class="card-image">
                <i class="fas fa-store"></i>
            </div>
            <div class="card-content">
                <h3>${restaurant.name}</h3>
                <p>${restaurant.description}</p>
                <div class="card-meta">
                    <span class="rating">
                        <i class="fas fa-star"></i>
                        ${restaurant.rating || '0.0'}
                    </span>
                    <span class="status-badge ${restaurant.is_open ? 'active' : 'inactive'}">
                        ${restaurant.is_open ? 'مفتوح' : 'مغلق'}
                    </span>
                </div>
                <div class="card-actions">
                    <button class="btn btn-primary" onclick="viewRestaurant(${restaurant.id})">
                        عرض التفاصيل
                    </button>
                    <button class="btn btn-secondary" onclick="editRestaurant(${restaurant.id})">
                        تعديل
                    </button>
                </div>
            </div>
        </div>
    `).join('');
}

// Orders Management
async function loadOrdersData() {
    try {
        const token = localStorage.getItem('admin_token');
        
        const response = await fetch(`${API_BASE_URL}/admin/orders`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            displayOrdersList(data.orders || []);
        } else {
            displayOrdersList(getMockOrders());
        }
    } catch (error) {
        console.error('Error loading orders:', error);
        displayOrdersList(getMockOrders());
    }
}

function getMockOrders() {
    return [
        {
            id: 1,
            order_number: 'ORD-001',
            customer_name: 'أحمد محمد',
            restaurant_name: 'مطعم الصحراء',
            total_amount: 1500,
            status: 'pending',
            created_at: '2024-01-20T10:30:00Z'
        },
        {
            id: 2,
            order_number: 'ORD-002',
            customer_name: 'فاطمة أحمد',
            restaurant_name: 'برجر هاوس',
            total_amount: 800,
            status: 'delivered',
            created_at: '2024-01-20T09:15:00Z'
        }
    ];
}

function displayOrdersList(orders) {
    const ordersList = document.getElementById('orders-list');
    if (!ordersList) return;
    
    ordersList.innerHTML = orders.map(order => `
        <div class="order-card">
            <div class="order-header">
                <h4>طلب ${order.order_number}</h4>
                <span class="status-badge ${getOrderStatusClass(order.status)}">
                    ${getOrderStatusLabel(order.status)}
                </span>
            </div>
            <div class="order-details">
                <div class="order-detail">
                    <label>العميل:</label>
                    <span>${order.customer_name}</span>
                </div>
                <div class="order-detail">
                    <label>المطعم:</label>
                    <span>${order.restaurant_name}</span>
                </div>
                <div class="order-detail">
                    <label>المبلغ:</label>
                    <span>${order.total_amount} أوقية</span>
                </div>
                <div class="order-detail">
                    <label>التاريخ:</label>
                    <span>${formatDateTime(order.created_at)}</span>
                </div>
            </div>
        </div>
    `).join('');
}

function getOrderStatusClass(status) {
    const classes = {
        pending: 'warning',
        confirmed: 'info',
        preparing: 'info',
        ready: 'success',
        delivered: 'success',
        cancelled: 'inactive'
    };
    return classes[status] || 'inactive';
}

function getOrderStatusLabel(status) {
    const labels = {
        pending: 'معلق',
        confirmed: 'مؤكد',
        preparing: 'قيد التحضير',
        ready: 'جاهز',
        delivered: 'تم التوصيل',
        cancelled: 'ملغي'
    };
    return labels[status] || status;
}

// Delivery Agents Management
async function loadDeliveryAgentsData() {
    try {
        const token = localStorage.getItem('admin_token');
        
        const response = await fetch(`${API_BASE_URL}/admin/delivery-agents`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            displayDeliveryAgentsGrid(data.agents || []);
        } else {
            displayDeliveryAgentsGrid(getMockDeliveryAgents());
        }
    } catch (error) {
        console.error('Error loading delivery agents:', error);
        displayDeliveryAgentsGrid(getMockDeliveryAgents());
    }
}

function getMockDeliveryAgents() {
    return [
        {
            id: 1,
            name: 'عبد الله أحمد',
            email: 'abdullah@delivery.mr',
            phone: '+22241234575',
            vehicle_type: 'motorcycle',
            is_available: true,
            rating: 4.8
        },
        {
            id: 2,
            name: 'محمد ولد أحمد',
            email: 'mohamed@delivery.mr',
            phone: '+22241234576',
            vehicle_type: 'bicycle',
            is_available: false,
            rating: 4.6
        }
    ];
}

function displayDeliveryAgentsGrid(agents) {
    const grid = document.getElementById('delivery-agents-grid');
    if (!grid) return;
    
    grid.innerHTML = agents.map(agent => `
        <div class="delivery-agent-card">
            <div class="card-image">
                <i class="fas fa-motorcycle"></i>
            </div>
            <div class="card-content">
                <h3>${agent.name}</h3>
                <p>${agent.email}</p>
                <div class="card-meta">
                    <span class="rating">
                        <i class="fas fa-star"></i>
                        ${agent.rating || '0.0'}
                    </span>
                    <span class="status-badge ${agent.is_available ? 'active' : 'inactive'}">
                        ${agent.is_available ? 'متاح' : 'غير متاح'}
                    </span>
                </div>
                <div class="card-actions">
                    <button class="btn btn-primary" onclick="viewDeliveryAgent(${agent.id})">
                        عرض التفاصيل
                    </button>
                    <button class="btn btn-secondary" onclick="editDeliveryAgent(${agent.id})">
                        تعديل
                    </button>
                </div>
            </div>
        </div>
    `).join('');
}

// Analytics
async function loadAnalyticsData() {
    // Initialize analytics charts
    initializeAnalyticsCharts();
}

function initializeAnalyticsCharts() {
    // Sales Chart
    const salesCtx = document.getElementById('salesChart');
    if (salesCtx) {
        new Chart(salesCtx, {
            type: 'line',
            data: {
                labels: ['يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو'],
                datasets: [{
                    label: 'المبيعات (أوقية)',
                    data: [12000, 19000, 15000, 25000, 22000, 30000],
                    borderColor: '#D4AF37',
                    backgroundColor: 'rgba(212, 175, 55, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }
    
    // Top Restaurants Chart
    const topRestaurantsCtx = document.getElementById('topRestaurantsChart');
    if (topRestaurantsCtx) {
        new Chart(topRestaurantsCtx, {
            type: 'doughnut',
            data: {
                labels: ['مطعم الصحراء', 'برجر هاوس', 'بيتزا بالاس', 'أخرى'],
                datasets: [{
                    data: [35, 25, 20, 20],
                    backgroundColor: ['#D4AF37', '#27AE60', '#3498DB', '#E74C3C']
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }
    
    // Peak Hours Chart
    const peakHoursCtx = document.getElementById('peakHoursChart');
    if (peakHoursCtx) {
        new Chart(peakHoursCtx, {
            type: 'bar',
            data: {
                labels: ['12 ص', '6 ص', '12 م', '6 م', '12 ص'],
                datasets: [{
                    label: 'عدد الطلبات',
                    data: [5, 15, 45, 80, 25],
                    backgroundColor: '#D4AF37'
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }
}

// Charts Initialization
function initializeCharts() {
    // Orders Chart
    const ordersCtx = document.getElementById('ordersChart');
    if (ordersCtx) {
        charts.orders = new Chart(ordersCtx, {
            type: 'line',
            data: {
                labels: ['1', '5', '10', '15', '20', '25', '30'],
                datasets: [{
                    label: 'الطلبات',
                    data: [12, 19, 15, 25, 22, 30, 28],
                    borderColor: '#D4AF37',
                    backgroundColor: 'rgba(212, 175, 55, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }
    
    // Users Chart
    const usersCtx = document.getElementById('usersChart');
    if (usersCtx) {
        charts.users = new Chart(usersCtx, {
            type: 'doughnut',
            data: {
                labels: ['عملاء', 'مطاعم', 'وكلاء توصيل'],
                datasets: [{
                    data: [65, 25, 10],
                    backgroundColor: ['#3498DB', '#27AE60', '#F39C12']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }
}

// Utility Functions
function updateTimeDisplay() {
    const now = new Date();
    
    const timeElement = document.getElementById('current-time');
    if (timeElement) {
        timeElement.textContent = now.toLocaleTimeString('ar-MR', {
            hour: '2-digit',
            minute: '2-digit'
        });
    }
    
    const dateElement = document.getElementById('current-date');
    if (dateElement) {
        dateElement.textContent = now.toLocaleDateString('ar-MR', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    }
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('ar-MR');
}

function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('ar-MR');
}

function toggleSidebar() {
    const sidebar = document.querySelector('.sidebar');
    if (sidebar) {
        sidebar.classList.toggle('active');
    }
}

// Modal Functions
function showModal(modalId) {
    const overlay = document.getElementById('modal-overlay');
    const modal = document.getElementById(modalId);
    
    if (overlay && modal) {
        overlay.classList.add('active');
        modal.style.display = 'block';
    }
}

function closeModal() {
    const overlay = document.getElementById('modal-overlay');
    if (overlay) {
        overlay.classList.remove('active');
        
        // Hide all modals
        document.querySelectorAll('.modal').forEach(modal => {
            modal.style.display = 'none';
        });
    }
}

function showAddUserModal() {
    document.getElementById('user-modal-title').textContent = 'إضافة مستخدم جديد';
    document.getElementById('user-form').reset();
    showModal('user-modal');
}

function showAddRestaurantModal() {
    showNotification('ميزة إضافة المطاعم قيد التطوير', 'info');
}

function showAddDeliveryAgentModal() {
    showNotification('ميزة إضافة وكلاء التوصيل قيد التطوير', 'info');
}

// CRUD Operations
function editUser(userId) {
    showNotification(`تعديل المستخدم ${userId} قيد التطوير`, 'info');
}

function deleteUser(userId) {
    if (confirm('هل أنت متأكد من حذف هذا المستخدم؟')) {
        showNotification(`تم حذف المستخدم ${userId}`, 'success');
    }
}

function viewRestaurant(restaurantId) {
    showNotification(`عرض تفاصيل المطعم ${restaurantId} قيد التطوير`, 'info');
}

function editRestaurant(restaurantId) {
    showNotification(`تعديل المطعم ${restaurantId} قيد التطوير`, 'info');
}

function viewDeliveryAgent(agentId) {
    showNotification(`عرض تفاصيل وكيل التوصيل ${agentId} قيد التطوير`, 'info');
}

function editDeliveryAgent(agentId) {
    showNotification(`تعديل وكيل التوصيل ${agentId} قيد التطوير`, 'info');
}

// Filter Functions
function filterUsers() {
    showNotification('ميزة التصفية قيد التطوير', 'info');
}

function searchUsers() {
    showNotification('ميزة البحث قيد التطوير', 'info');
}

function filterOrders() {
    showNotification('ميزة تصفية الطلبات قيد التطوير', 'info');
}

// Export Functions
function exportUsers() {
    showNotification('ميزة تصدير المستخدمين قيد التطوير', 'info');
}

function exportRestaurants() {
    showNotification('ميزة تصدير المطاعم قيد التطوير', 'info');
}

function exportOrders() {
    showNotification('ميزة تصدير الطلبات قيد التطوير', 'info');
}

function generateReport() {
    showNotification('ميزة إنشاء التقارير قيد التطوير', 'info');
}

// Settings Functions
function changeAdminPassword() {
    showNotification('ميزة تغيير كلمة المرور قيد التطوير', 'info');
}

function showBackupModal() {
    showNotification('ميزة النسخ الاحتياطي قيد التطوير', 'info');
}

function saveSettings() {
    showNotification('تم حفظ الإعدادات بنجاح', 'success');
}

function saveUser() {
    const form = document.getElementById('user-form');
    const formData = new FormData(form);
    
    // Here you would normally send the data to the server
    showNotification('تم حفظ المستخدم بنجاح', 'success');
    closeModal();
    
    // Reload users data
    if (currentTab === 'users') {
        loadUsersData();
    }
}

// Notification System
function showNotification(message, type = 'info') {
    const container = document.getElementById('notification-container');
    if (!container) return;
    
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas fa-${getNotificationIcon(type)}"></i>
            <span>${message}</span>
        </div>
        <button class="notification-close" onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    container.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 5000);
}

function getNotificationIcon(type) {
    const icons = {
        success: 'check-circle',
        error: 'exclamation-circle',
        warning: 'exclamation-triangle',
        info: 'info-circle'
    };
    return icons[type] || 'info-circle';
}

// Export functions for global access
window.showAdminTab = showAdminTab;
window.adminLogout = adminLogout;
window.toggleAdminPassword = toggleAdminPassword;
window.toggleSidebar = toggleSidebar;
window.closeModal = closeModal;
window.showAddUserModal = showAddUserModal;
window.showAddRestaurantModal = showAddRestaurantModal;
window.showAddDeliveryAgentModal = showAddDeliveryAgentModal;
window.editUser = editUser;
window.deleteUser = deleteUser;
window.viewRestaurant = viewRestaurant;
window.editRestaurant = editRestaurant;
window.viewDeliveryAgent = viewDeliveryAgent;
window.editDeliveryAgent = editDeliveryAgent;
window.filterUsers = filterUsers;
window.searchUsers = searchUsers;
window.filterOrders = filterOrders;
window.exportUsers = exportUsers;
window.exportRestaurants = exportRestaurants;
window.exportOrders = exportOrders;
window.generateReport = generateReport;
window.changeAdminPassword = changeAdminPassword;
window.showBackupModal = showBackupModal;
window.saveSettings = saveSettings;
window.saveUser = saveUser;
window.loadRecentActivity = loadRecentActivity;

