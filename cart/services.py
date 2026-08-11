from dataclasses import dataclass

from products.models import Product, ProductSize, ProductVariant, Size, VariantSize


class InvalidProductSelection(ValueError):
    """Raised when a variant/size selection does not belong to a product."""


@dataclass(frozen=True)
class ProductSelection:
    variant: ProductVariant | None
    size: Size | None
    pcs_carton: int
    length_label: str
    is_length_only: bool


def _selection_id(value, label):
    if value in (None, ''):
        return None
    try:
        value = int(value)
    except (TypeError, ValueError) as exc:
        raise InvalidProductSelection(f'{label} غير صحيح') from exc
    if value < 1:
        raise InvalidProductSelection(f'{label} غير صحيح')
    return value


def resolve_product_selection(
    product: Product,
    *,
    variant_id=None,
    size_id=None,
    size_name='',
) -> ProductSelection:
    """Resolve an authoritative product selection and its carton quantity.

    IDs are preferred. ``size_name`` is accepted only for compatibility with
    carts created before size IDs were stored in localStorage.
    """
    variant_id = _selection_id(variant_id, 'النمط')
    size_id = _selection_id(size_id, 'المقاس')
    size_name = (size_name or '').strip()

    variant = None
    if variant_id is not None:
        variant = ProductVariant.objects.filter(
            pk=variant_id,
            product=product,
            is_available=True,
        ).first()
        if variant is None:
            raise InvalidProductSelection('النمط المحدد غير متاح لهذا المنتج')
        size_prices = VariantSize.objects.filter(variant=variant).select_related('size')
        default_pcs_carton = variant.pcs_carton
    else:
        if product.variants.filter(is_available=True).exists():
            raise InvalidProductSelection('يرجى اختيار نمط المنتج أولاً')
        size_prices = ProductSize.objects.filter(product=product).select_related('size')
        default_pcs_carton = product.pcs_carton

    size_price = None
    if size_id is not None:
        size_price = size_prices.filter(size_id=size_id).first()
        if size_price is None:
            raise InvalidProductSelection('المقاس المحدد غير متاح لهذا المنتج')
    elif size_name:
        matches = list(size_prices.filter(size__name=size_name)[:2])
        if len(matches) != 1:
            raise InvalidProductSelection('المقاس المحدد غير متاح لهذا المنتج')
        size_price = matches[0]
    elif size_prices.exists():
        raise InvalidProductSelection('يرجى اختيار المقاس أولاً')

    if size_price is not None:
        is_length_only = size_price.pcs_carton is None
        return ProductSelection(
            variant=variant,
            size=size_price.size,
            pcs_carton=size_price.pcs_carton or 1,
            length_label=(
                variant.get_length_label()
                if variant
                else product.get_length_label()
            ),
            is_length_only=is_length_only,
        )

    return ProductSelection(
        variant=variant,
        size=None,
        pcs_carton=default_pcs_carton,
        length_label=(
            variant.get_length_label()
            if variant
            else product.get_length_label()
        ),
        is_length_only=False,
    )
