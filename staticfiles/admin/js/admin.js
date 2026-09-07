static %}
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Admin Panel - BorewellMart{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="{% static 'admin/css/admin.css' %}">
    {% block extra_css %}{% endblock %}
</head>
<body>
    <!-- Sidebar -->
    <aside class="sidebar">
        <div class="sidebar-brand">
            <i class="bi bi-droplet-fill"></i>
            <h5>BorewellMart</h5>
        </div>

        <nav class="sidebar-nav">
            <div class="nav-section">
                <div class="nav-section-title">Main</div>
                <a href="{% url 'admin_dashboard' %}" class="sidebar-link {% block nav_dashboard %}{% endblock %}">
                    <i class="bi bi-grid-1x2-fill"></i>
                    <span>Dashboard</span>
                </a>
                <a href="{% url 'admin_all_vendors' %}" class="sidebar-link {% block nav_vendors %}{% endblock %}">
                    <i class="bi bi-people-fill"></i>
                    <span>Vendors</span>
                </a>
                <a href="{% url 'vendor_payments_list' %}" class="sidebar-link {% block nav_payments %}{% endblock %}">
                    <i class="bi bi-credit-card-fill"></i>
                    <span>Payments</span>
                </a>
            </div>

            <div class="nav-section">
                <div class="nav-section-title">Management</div>
                <a href="{% url 'admin_cities' %}" class="sidebar-link {% block nav_cities %}{% endblock %}">
                    <i class="bi bi-geo-alt-fill"></i>
                    <span>Cities</span>
                </a>
                <a href="{% url 'admin_categories' %}" class="sidebar-link {% block nav_categories %}{% endblock %}">
                    <i class="bi bi-list-task"></i>
                    <span>Categories</span>
                </a>
                <a href="{% url 'admin_services' %}" class="sidebar-link {% block nav_services %}{% endblock %}">
                    <i class="bi bi-tools"></i>
                    <span>Services</span>
                </a>
                <a href="{% url 'admin_blogs' %}" class="sidebar-link {% block nav_blogs %}{% endblock %}">
                    <i class="bi bi-file-text-fill"></i>
                    <span>Blogs</span>
                </a>
            </div>

            <div class="nav-section">
                <div class="nav-section-title">Quick Actions</div>
                <a href="{% url 'bulk_vendor_registration' %}" class="sidebar-link {% block nav_bulk %}{% endblock %}">
                    <i class="bi bi-upload"></i>
                    <span>Bulk Registration</span>
                </a>
            </div>

            <div class="nav-section">

               
                <a href="{% url 'logout' %}" class="sidebar-link">
                    <i class="bi bi-box-arrow-right"></i>
                    <span>Logout</span>
                </a>
            </div>
        </nav>
    </aside>

    <!-- Sidebar Overlay for Mobile -->
    <div class="sidebar-overlay" id="sidebarOverlay"></div>

    <!-- Main Content -->
    <main class="main-content">
        <!-- Top Header -->
        <header class="top-header">
            <div class="d-flex align-items-center">
                <!-- Mobile Hamburger Button -->
                <button class="mobile-toggle" id="mobileToggle" aria-label="Toggle sidebar">
                    <span></span>
                    <span></span>
                    <span></span>
                </button>
                <div class="page-title">
                    <h1>{% block page_title %}Dashboard{% endblock %}</h1>
                    <p>{% block page_subtitle %}Welcome back, Administrator{% endblock %}</p>
                </div>
            </div>
            <div class="header-actions">
                <a href="{% url 'home' %}" class="header-btn">
                    <i class="bi bi-eye"></i>
                    <span>View Site</span>
                </a>
                <div class="dropdown">
                    <button class="btn btn-outline-secondary dropdown-toggle" type="button" data-bs-toggle="dropdown">
                        <div class="user-avatar">A</div>
                        <span>Admin</span>
                        <i class="bi bi-chevron-down"></i>
                    </button>
                    <ul class="dropdown-menu dropdown-menu-end">
                        <li><h6 class="dropdown-header">Welcome, Admin</h6></li>
                        <li><hr class="dropdown-divider"></li>
                        <li><a class="dropdown-item" href="{% url 'home' %}"><i class="bi bi-eye"></i> View Site</a></li>
                        <li><a class="dropdown-item" href="#"><i class="bi bi-gear"></i> Settings</a></li>
                        <li><hr class="dropdown-divider"></li>
                        <li><a class="dropdown-item text-danger" href="{% url 'logout' %}"><i class="bi bi-box-arrow-right"></i> Logout</a></li>
                    </ul>
                </div>
            </div>
        </header>

        <!-- Content Area -->
        <div class="content-area">
            {% if messages %}
            <div class="messages-container">
                {% for message in messages %}
                <div class="alert alert-{{ message.tags }} alert-dismissible fade show" role="alert">
                    {{ message }}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
                {% endfor %}
            </div>
            {% endif %}

            {% block content %}{% endblock %}
        </div>
    </main>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js">