import stripe
from django.conf import settings
from .models import Payment

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_stripe_product(name, description):
    """Создание продукта в Stripe"""
    product = stripe.Product.create(
        name=name,
        description=description or '',
    )
    return product.id


def create_stripe_price(product_id, amount):
    """Создание цены в Stripe (amount в копейках)"""
    price = stripe.Price.create(
        product=product_id,
        unit_amount=int(amount * 100),
        currency='usd',
    )
    return price.id


def create_checkout_session(price_id, success_url, cancel_url):
    """Создание сессии для оплаты"""
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price': price_id,
            'quantity': 1,
        }],
        mode='payment',
        success_url=success_url,
        cancel_url=cancel_url,
    )
    return session.id, session.url


def create_payment_for_course(user, course, success_url, cancel_url):
    """Основная функция: создает продукт, цену, сессию и запись Payment"""
    product_id = create_stripe_product(course.title, course.description or '')
    price_id = create_stripe_price(product_id, course.price)

    session_id, session_url = create_checkout_session(price_id, success_url, cancel_url)

    payment = Payment.objects.create(
        user=user,
        course=course,
        amount=course.price,
        payment_method='transfer',
        stripe_product_id=product_id,
        stripe_price_id=price_id,
        stripe_session_id=session_id,
        payment_url=session_url,
        status='pending',
    )
    return payment