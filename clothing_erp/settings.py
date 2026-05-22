import os
from pathlib import Path
from django.utils.translation import gettext_lazy as _

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-replace-with-secure-key-in-production'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['cloud.sobirjon.codes', 'localhost', '127.0.0.1', "*"]

# Application definition
INSTALLED_APPS = [
    # Jazzmin (admin panel uchun)
    'jazzmin',

    # Django asosiy dasturlari
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Tashqi dasturlar
    'import_export',
    'django_filters',
    'rest_framework',
    'simple_history',
    'django_countries',
    'colorfield',

    # Loyiha ilovalari
    'apps.core',
    'apps.inventory',
    'apps.sales',
    'apps.purchase',
    'apps.finance',
    'apps.hr',
    'apps.dashboard',
    'apps.settings',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',  # Til uchun middleware
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',  # Tarix uchun
]

ROOT_URLCONF = 'clothing_erp.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',  # Til uchun
            ],
        },
    },
]

WSGI_APPLICATION = 'clothing_erp.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'uz'

TIME_ZONE = 'Asia/Tashkent'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Qo'llab-quvvatlanadigan tillar
LANGUAGES = (
    ('uz', 'O\'zbek'),
    ('ru', 'Русский'),
    ('en', 'English'),
)

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static_root')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Jazzmin sozlamalari
JAZZMIN_SETTINGS = {
    # title of the window (Will default to current_admin_site.site_title if absent or None)
    "site_title": "Kiyim-Kechak ERP Admin",

    # Title on the login screen (19 chars max) (defaults to current_admin_site.site_header if absent or None)
    "site_header": "Kiyim-Kechak ERP",

    # Title on the brand (19 chars max) (defaults to current_admin_site.site_header if absent or None)
    "site_brand": "Kiyim-Kechak ERP",

    # Logo to use for your site, must be present in static files
    "site_logo": None,

    # CSS classes that are applied to the logo
    "site_logo_classes": "img-circle",

    # Logo to use for login form in dark themes
    "login_logo": None,

    # Copyright on the footer
    "copyright": "Kiyim-Kechak ERP",

    # The model admin to search from the search bar
    "search_model": "auth.User",

    # Field name on user model that contains avatar ImageField/URLField/Charfield or a callable that receives the user
    "user_avatar": None,

    ############
    # Top Menu #
    ############
    # Links to put along the top menu
    "topmenu_links": [
        # Url that gets reversed (Permissions can be added)
        {"name": _("Dashboard"), "url": "admin:index", "permissions": ["auth.view_user"]},

        # External url that opens in a new window (Permissions can be added)
        {"name": _("Support"), "url": "https://github.com/ashurovasabina", "new_window": True},

        # App with dropdown menu to all its models pages
        {"app": "inventory"},
        {"app": "sales"},
        {"app": "purchase"},
        {"app": "finance"},
        {"app": "hr"},
    ],

    #############
    # Side Menu #
    #############
    # Whether to display the side menu
    "show_sidebar": True,

    # Whether to aut expand the menu
    "navigation_expanded": True,

    # Custom icons for side menu apps/models
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "inventory.product": "fas fa-tshirt",
        "inventory.category": "fas fa-tags",
        "inventory.warehouse": "fas fa-warehouse",
        "sales.order": "fas fa-shopping-cart",
        "sales.customer": "fas fa-user-tie",
        "purchase.supplier": "fas fa-truck",
        "purchase.purchaseorder": "fas fa-file-invoice",
        "finance.invoice": "fas fa-file-invoice-dollar",
        "finance.payment": "fas fa-money-bill-wave",
        "hr.employee": "fas fa-id-card",
    },

    # Custom CSS files
    "custom_css": None,

    # Custom JS files
    "custom_js": [
        "js/charts/chart.min.js",
        "js/dashboard.js",
    ],

    # Show language chooser
    "language_chooser": True,
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-primary",
    "accent": "accent-primary",
    "navbar": "navbar-dark",
    "no_navbar_border": False,
    "navbar_fixed": True,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark-primary",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "default",
    "dark_mode_theme": None,
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success",
    },
}

# Language chooser qo'shish
JAZZMIN_SETTINGS.update({
    "language_chooser": True,
})

# Admin interfeysda tilni o'zgartirish uchun kontekst protsessorni qo'shish
TEMPLATES[0]['OPTIONS']['context_processors'].append('django.template.context_processors.i18n')

# Django modellarini tarjima qilish uchun middleware
MIDDLEWARE.insert(
    MIDDLEWARE.index('django.middleware.common.CommonMiddleware'),
    'django.middleware.locale.LocaleMiddleware'
)

LOGIN_URL = "admin:login"
LOGIN_REDIRECT_URL = "dashboard:index"
LOGOUT_REDIRECT_URL = "admin:login"
