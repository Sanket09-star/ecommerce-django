from django.shortcuts import render
from store.models import Product, ReviewRating

def home(request):
    products = Product.objects.filter(is_available=True).order_by('created_date')
    
    # Create a dictionary to store reviews for each product
    product_reviews = {}
    for product in products:
        product_reviews[product.id] = ReviewRating.objects.filter(product_id=product.id, status=True)

    context = {
        'products': products,
        'product_reviews': product_reviews,  # Pass the dictionary to the context
    }
    return render(request, 'home.html', context)