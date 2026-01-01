"""
Core constants for the Alwesam-Talabat project
"""

# Pagination
MAX_PRODUCTS_PER_PAGE = 12
MAX_ORDERS_PER_PAGE = 20
MAX_CATEGORIES_PER_PAGE = 15

# Cart
MAX_CART_ITEMS = 50
MAX_QUANTITY_PER_ITEM = 100

# Caching
DEFAULT_CACHE_TIMEOUT = 60 * 15  # 15 minutes
HOME_CATEGORIES_CACHE_TIMEOUT = 60 * 30  # 30 minutes
PRODUCT_CACHE_TIMEOUT = 60 * 10  # 10 minutes

# Images
MAX_IMAGE_SIZE = (800, 800)
IMAGE_QUALITY = 85
THUMBNAIL_SIZE = (300, 300)

# Rate Limiting
LOGIN_RATE_LIMIT = '5/m'  # 5 attempts per minute
CART_RATE_LIMIT = '30/m'  # 30 requests per minute

# Unit Types (NEW)
UNIT_TYPE_CARTON = 'carton'
UNIT_TYPE_PIECE = 'piece'

UNIT_TYPE_CHOICES = [
    (UNIT_TYPE_PIECE, 'قطعة'),
    (UNIT_TYPE_CARTON, 'كرتونة'),
]

# Order Status (NEW)
ORDER_STATUS_PENDING = 'pending'
ORDER_STATUS_CONFIRMED = 'confirmed'
ORDER_STATUS_SHIPPED = 'shipped'
ORDER_STATUS_DELIVERED = 'delivered'
ORDER_STATUS_CANCELLED = 'cancelled'

ORDER_STATUS_CHOICES = (
    (ORDER_STATUS_PENDING, 'قيد الانتظار'),
    (ORDER_STATUS_CONFIRMED, 'تم التأكيد'),
    (ORDER_STATUS_SHIPPED, 'تم الشحن'),
    (ORDER_STATUS_DELIVERED, 'تم التسليم'),
    (ORDER_STATUS_CANCELLED, 'تم الإلغاء'),
)

# Product Variant Types (NEW)
VARIANT_TYPE_COLOR = 'color'

VARIANT_TYPE_CHOICES = [
    (VARIANT_TYPE_COLOR, 'اللون'),
]

# Default Values (NEW)
DEFAULT_PCS_CARTON = 24
