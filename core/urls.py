from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Home and general pages
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('borewell-faqs/', views.borewell_faqs, name='borewell_faqs'),
    
    # Authentication
    path('register/', views.register_choice, name='register_choice'),
    path('register/customer/', views.register, name='register'),
    path('register/vendor/', views.vendor_user_register, name='vendor_user_register'),
    path('login/', views.custom_login, name='login'),
    path('logout/', views.custom_logout, name='logout'),

    # Password Reset
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    
    # Cities
    path('cities/', views.city_list, name='city_list'),
    path('cities/<int:city_id>/', views.city_detail, name='city_detail'),
    
    # Services
    path('services/', views.service_list, name='service_list'),
    path('services/subcategory/<str:subcategory_id>/', views.subcategory_detail, name='subcategory_detail'),
    path('services/subservice/<str:subservice_id>/', views.subservice_detail, name='subservice_detail'),
    path('services/<str:service_id>/', views.service_detail, name='service_detail'),
    
    # Vendors
    path('vendors/', views.vendor_list, name='vendor_list'),
    path('vendors/<int:vendor_id>/', views.vendor_detail, name='vendor_detail'),
    
    # Booking
    path('book/<int:vendor_id>/<str:subservice_id>/', views.book_service, name='book_service'),
    path('booking/<int:booking_id>/payment/', views.booking_payment, name='booking_payment'),

    # Dashboards
    path('dashboard/customer/', views.customer_dashboard, name='customer_dashboard'),
    path('dashboard/customer/profile/', views.customer_profile, name='customer_profile'),
    path('dashboard/customer/profile/edit/', views.customer_profile_edit, name='customer_profile_edit'),
    path('dashboard/vendor/', views.vendor_dashboard, name='vendor_dashboard'),
    path('dashboard/vendor/communities/', views.vendor_communities, name='vendor_communities'),
    path('dashboard/vendor/bookings/', views.vendor_bookings, name='vendor_bookings'),
    path('dashboard/vendor/services/', views.vendor_services, name='vendor_services'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),

    # Admin vendor management (using dashboard/admin prefix to avoid conflict with Django admin)
    path('dashboard/admin/vendors/all/', views.all_vendors, name='admin_all_vendors'),
    path('dashboard/admin/customers/all/', views.all_customers, name='admin_all_customers'),
    path('dashboard/admin/customers/<int:customer_id>/edit/', views.admin_customer_edit, name='admin_customer_edit'),
    path('dashboard/admin/customers/<int:customer_id>/activate/', views.admin_customer_activate, name='admin_customer_activate'),
    path('dashboard/admin/customers/<int:customer_id>/deactivate/', views.admin_customer_deactivate, name='admin_customer_deactivate'),
    path('dashboard/admin/customers/<int:customer_id>/delete/', views.admin_customer_delete, name='admin_customer_delete'),
    path('dashboard/admin/vendors/<int:vendor_id>/edit/', views.admin_vendor_edit, name='admin_vendor_edit'),
    path('dashboard/admin/vendors/<int:vendor_id>/approve/', views.approve_vendor, name='approve_vendor'),
    path('dashboard/admin/vendors/<int:vendor_id>/reject/', views.reject_vendor, name='reject_vendor'),
    path('dashboard/admin/vendors/<int:vendor_id>/suspend/', views.suspend_vendor, name='suspend_vendor'),
    path('dashboard/admin/vendors/<int:vendor_id>/activate/', views.activate_vendor, name='activate_vendor'),
    path('dashboard/admin/vendors/<int:vendor_id>/delete/', views.delete_vendor, name='delete_vendor'),
    path('dashboard/admin/bulk-registration/', views.bulk_vendor_registration, name='bulk_vendor_registration'),

    # Admin payment management
    path('dashboard/admin/payments/', views.vendor_payments_list, name='vendor_payments_list'),
    path('dashboard/admin/payments/<int:payment_id>/', views.vendor_payment_detail, name='vendor_payment_detail'),
    
    # Vendor management
    path('vendor/', views.vendor_dashboard, name='vendor_redirect'),
    path('vendor/profile/edit/', views.vendor_profile_edit, name='vendor_profile_edit'),
    path('vendor/register/', views.vendor_register, name='vendor_register'),
    path('vendor/payment/', views.vendor_payment_page, name='vendor_payment_page'),
    path('vendor/payment/create-order/', views.create_razorpay_order, name='create_razorpay_order'),
    path('api/create-order/', views.create_razorpay_order, name='api_create_order'),
    path('api/verify-payment/', views.verify_razorpay_payment, name='api_verify_payment'),
    path('vendor/payment/callback/', views.vendor_payment_callback, name='vendor_payment_callback'),
    path('vendor/service/add/', views.vendor_service_add, name='vendor_service_add'),
    path('vendor/service/<int:service_id>/edit/', views.vendor_service_edit, name='vendor_service_edit'),
    path('vendor/service/<int:service_id>/delete/', views.vendor_service_delete, name='vendor_service_delete'),
    path('vendor/gallery/add/', views.vendor_gallery_add, name='vendor_gallery_add'),
    path('vendor/gallery/<int:gallery_id>/delete/', views.vendor_gallery_delete, name='vendor_gallery_delete'),
    
    # Booking status
    path('booking/<int:booking_id>/<str:status>/', views.booking_update_status, name='booking_update_status'),
    
    # Favorites
    path('favorite/<int:vendor_id>/add/', views.add_favorite, name='add_favorite'),
    path('favorite/<int:vendor_id>/remove/', views.remove_favorite, name='remove_favorite'),
    
    # Reviews
    path('review/<int:vendor_id>/add/', views.add_review, name='add_review'),
    path('review/<int:vendor_id>/add/<int:booking_id>/', views.add_review, name='add_review_with_booking'),
    
    # Search
    path('search/', views.search, name='search'),
    
    # Blogs
    path('blogs/', views.blog_list, name='blog_list'),
    path('blogs/<slug:slug>/', views.blog_detail, name='blog_detail'),
    
    # Enquiries
    path('enquiry/send/<int:vendor_id>/', views.send_enquiry, name='send_enquiry'),
    path('enquiry/vendor/', views.vendor_enquiries, name='vendor_enquiries'),
    path('enquiry/respond/<int:enquiry_id>/', views.respond_enquiry, name='respond_enquiry'),
    path('enquiry/customer/', views.customer_enquiries, name='customer_enquiries'),

    # Notifications
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/<int:enquiry_id>/dismiss/', views.dismiss_notification, name='dismiss_notification'),

    # Custom Admin Pages
    path('dashboard/admin/cities/', views.admin_cities, name='admin_cities'),
    path('dashboard/admin/sectors/', views.admin_sectors, name='admin_sectors'),
    path('dashboard/admin/services-list/', views.admin_services_list, name='admin_services_list'),
    path('dashboard/admin/subservices/', views.admin_subservices, name='admin_subservices'),
    path('dashboard/admin/categories/', views.admin_categories, name='admin_categories'),
    path('dashboard/admin/services/', views.admin_services, name='admin_services'),
    path('dashboard/admin/blogs/', views.admin_blogs, name='admin_blogs'),
    path('dashboard/admin/visitors/', views.admin_visitors, name='admin_visitors'),

    # City CRUD
    path('dashboard/admin/cities/add/', views.admin_cities, name='admin_city_add'),
    path('dashboard/admin/cities/<int:city_id>/edit/', views.admin_cities, name='admin_city_edit'),
    path('dashboard/admin/cities/<int:city_id>/delete/', views.admin_cities, name='admin_city_delete'),

    # Category CRUD
    path('dashboard/admin/categories/add/', views.admin_categories, name='admin_category_add'),
    path('dashboard/admin/categories/<str:category_id>/edit/', views.admin_categories, name='admin_category_edit'),
    path('dashboard/admin/categories/<str:category_id>/delete/', views.admin_categories, name='admin_category_delete'),

    # Subcategory CRUD
    path('dashboard/admin/subcategories/add/', views.admin_categories, name='admin_subcategory_add'),
    path('dashboard/admin/subcategories/<int:subcategory_id>/edit/', views.admin_categories, name='admin_subcategory_edit'),
    path('dashboard/admin/subcategories/<int:subcategory_id>/delete/', views.admin_categories, name='admin_subcategory_delete'),

    # Service CRUD
    path('dashboard/admin/services/add/', views.admin_services, name='admin_service_add'),
    path('dashboard/admin/services/<str:service_id>/edit/', views.admin_services, name='admin_service_edit'),
    path('dashboard/admin/services/<str:service_id>/delete/', views.admin_services, name='admin_service_delete'),
    path('dashboard/admin/subservices/<str:subservice_id>/data/', views.admin_subservice_data, name='admin_subservice_data'),

    # Blog CRUD
    path('dashboard/admin/blogs/add/', views.admin_blogs, name='admin_blog_add'),
    path('dashboard/admin/blogs/<int:blog_id>/edit/', views.admin_blogs, name='admin_blog_edit'),
    path('dashboard/admin/blogs/<int:blog_id>/delete/', views.admin_blogs, name='admin_blog_delete'),
    path('dashboard/admin/blogs/<int:blog_id>/data/', views.admin_blog_data, name='admin_blog_data'),

    # Vendor Plans
    path('vendor/plans/', views.vendor_plans, name='vendor_plans'),
    path('vendor/plans/create/', views.create_plan, name='create_plan'),
    path('vendor/plans/<int:plan_id>/', views.plan_detail, name='plan_detail'),
    path('vendor/plans/<int:plan_id>/edit/', views.edit_plan, name='edit_plan'),
    path('vendor/plans/<int:plan_id>/renew/', views.renew_plan, name='renew_plan'),
    path('vendor/plans/<int:plan_id>/notifications/', views.plan_notifications, name='plan_notifications'),

    # OTP Verification
    path('send-otp/', views.send_otp, name='send_otp'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),

    # API - Cities by State
    path('api/cities-by-state/', views.cities_by_state, name='cities_by_state'),

    # Test pages for custom errors
    path('404/', views.custom_404_view, name='test_404'),
    path('500/', views.custom_500_view, name='test_500'),

    # Policy Pages (Razorpay Compliance)
    path('terms/', views.terms_and_conditions, name='terms_and_conditions'),
    path('privacy/', views.privacy_policy, name='privacy_policy'),
    path('cancellation-refund/', views.cancellation_refund_policy, name='cancellation_refund_policy'),

    # Communities
    path('communities/', views.community_list, name='community_list'),
    path('communities/<slug:community_slug>/', views.community_detail, name='community_detail'),
    path('communities/<slug:community_slug>/join/', views.join_community, name='join_community'),
    path('communities/<slug:community_slug>/leave/', views.leave_community, name='leave_community'),
    path('communities/<slug:community_slug>/post/', views.create_community_post, name='create_community_post'),
    path('communities/post/<int:post_id>/like/', views.like_community_post, name='like_community_post'),
    path('communities/post/<int:post_id>/comment/', views.comment_on_post, name='comment_on_post'),
    path('communities/post/<int:post_id>/delete/', views.delete_post, name='delete_post'),
    path('dashboard/admin/communities/', views.admin_communities, name='admin_communities'),
    path('dashboard/admin/communities/create/', views.admin_create_community, name='admin_create_community'),
    path('dashboard/admin/communities/<slug:community_slug>/edit/', views.admin_edit_community, name='admin_edit_community'),
    path('dashboard/admin/communities/<slug:community_slug>/delete/', views.admin_delete_community, name='admin_delete_community'),

    # Community Forum
    path('forum/', views.forum_home, name='forum_home'),
    path('forum/category/<str:category_slug>/', views.forum_category, name='forum_category'),
    path('forum/thread/<str:thread_slug>/', views.forum_thread, name='forum_thread'),
    path('forum/create/', views.forum_create_thread, name='forum_create_thread'),
    path('forum/edit/<str:thread_slug>/', views.forum_edit_thread, name='forum_edit_thread'),
    path('forum/reply/<str:thread_slug>/', views.forum_reply, name='forum_reply'),
    path('forum/vote/', views.forum_vote, name='forum_vote'),
    path('forum/thread/<str:thread_slug>/best/<int:post_id>/', views.forum_mark_best_answer, name='forum_mark_best_answer'),
    path('forum/post/<int:post_id>/best/', views.forum_mark_best_answer, name='forum_mark_best_answer'),
    path('forum/thread/<str:thread_slug>/mark-solved/', views.forum_mark_solved, name='forum_mark_solved'),
    path('forum/thread/<str:thread_slug>/close/', views.forum_close_thread, name='forum_close_thread'),
    path('forum/thread/<str:thread_slug>/reopen/', views.forum_reopen_thread, name='forum_reopen_thread'),
    path('forum/post/<int:post_id>/edit/', views.forum_edit_post, name='forum_edit_post'),
    path('forum/thread/<str:thread_slug>/delete/', views.forum_delete_thread, name='forum_delete_thread'),
    path('forum/post/<int:post_id>/delete/', views.forum_delete_post, name='forum_delete_post'),
]
