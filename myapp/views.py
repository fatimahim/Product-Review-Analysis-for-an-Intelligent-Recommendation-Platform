from django.shortcuts import render,HttpResponse
from django.shortcuts import render
from django.db.models import Q
from .models import Product
from django.db.models import Count  
import time
import json
from django.http import Http404
from pymongo import MongoClient
# Create your views here.

from db_connection import db  # Ensure this is your MongoDB connection
import json

def home(request):
    # Retrieve from MongoDB directly
    product_collection = db['sample']  # Your MongoDB collection
    
    # Find excellent products directly in MongoDB
    excellent_products_cursor = product_collection.find({
        'product_average_rating': {'$gte': 4.5}
    }).sort('product_average_rating', -1).limit(7)
    
    # Convert cursor to list and process images
    excellent_products = []
    for product in excellent_products_cursor:
        # Process product images
        try:
            if isinstance(product.get('product_images'), str):
                import ast
                product_images = ast.literal_eval(product['product_images'])
            else:
                product_images = product.get('product_images', {})
            
            # Get main image
            main_image = ''
            if isinstance(product_images, dict):
                if product_images.get('hi_res'):
                    main_image = product_images['hi_res'][0]
                elif product_images.get('large'):
                    main_image = product_images['large'][0]
            elif isinstance(product_images, list) and product_images:
                main_image = product_images[0]
            
            # Determine rating status
            rating = product.get('product_average_rating', 0)
            if rating >= 4.5:
                rating_status = "Excellent"
            elif rating >= 4.0:
                rating_status = "Good"
            elif rating >= 3.0:
                rating_status = "Average"
            else:
                rating_status = "Poor"
            # Get price and handle missing price or empty value
           
            # Handle price field in home view
            price = product.get('price', 'N/A')
            if isinstance(price, float) and math.isnan(price):
             price = 'N/A'

            # Prepare product dictionary
            processed_product = {
                'product_title': product.get('product_title', 'Unnamed Product'),
                'product_average_rating': rating,
                'rating_status': rating_status,
                'main_image': main_image or '/static/default-product.jpg',
                'category': product.get('category', 'Uncategorized'),
                'price': price
            }
            
            excellent_products.append(processed_product)
        
        except Exception as e:
            print(f"Error processing product: {e}")
    
    context = {
        'excellent_products': excellent_products,
        'background_image': 'image (6).png',
    }
    
    return render(request, 'home.html', context)




def product_search(request):
    query = request.GET.get('q', '')
    products = []
    
    if query:
        pipeline = [
            {
                "$match": {
                    "$or": [
                        {"product_title": {"$regex": query, "$options": "i"}},
                        {"store": {"$regex": query, "$options": "i"}}
                    ]
                }
            },
            {
                "$group": {
                    "_id": "$product_id",
                    "product_title": {"$first": "$product_title"},
                    "product_images": {"$first": "$product_images"},
                    "category": {"$first": "$category"},
                    "average_rating": {"$first": "$product_average_rating"},
                    "store": {"$first": "$store"},
                    "reviews_count": {"$sum": 1}
                }
            },
            {
                "$sort": {
                    "reviews_count": -1
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "product_id": "$_id",
                    "product_title": 1,
                    "product_images": 1,
                    "category": 1,
                    "average_rating": 1,
                    "store": 1,
                    "reviews_count": 1
                }
            }
        ]
        
        raw_products = list(product_collection.aggregate(pipeline))
        
        for product in raw_products:
            try:
                # Process product_images
                product_images = product.get('product_images', {})
                if isinstance(product_images, str):
                    try:
                        product_images = json.loads(product_images.replace("'", '"'))
                    except json.JSONDecodeError:
                        product_images = {}
                
                # Comprehensive image fallback logic
                image_keys_priority = ['hi_res', 'large', 'thumb']
                processed_product_image = {}
                
                for key in image_keys_priority:
                    images = product_images.get(key, [])
                    if images and isinstance(images, list):
                        processed_product_image[key] = images
                
                # Ensure at least one image type is present
                if not processed_product_image:
                    processed_product_image = {'thumb': []}
                
                processed_product = {
                    'product_id': str(product.get('product_id')),
                    'product_title': product.get('product_title', 'Unnamed Product'),
                    'product_image': processed_product_image,
                    'average_rating': product.get('average_rating', 0),
                    'reviews_count': product.get('reviews_count', 0)
                }
                
                products.append(processed_product)
            
            except Exception as e:
                print(f"Error processing product: {e}")
    
    context = {
        'query': query,
        'products': products,
    }
    return render(request, 'search.html', context)

def stores_view(request):
    # Get a list of all the unique stores
    stores = Product.objects.values('store').annotate(num_products=Count('store')).order_by('-num_products')

    # Handle search functionality
    query = request.GET.get('q', '')
    if query:
        stores = stores.filter(store__icontains=query)

    context = {
        'stores': stores,
        'query': query,
    }
    return render(request, 'stores.html', context)


def categories_view(request):
    # Get the search query and category filter
    query = request.GET.get('q', '')
    category_filter = request.GET.get('category', None)

    if category_filter:
        # If a category is selected, fetch products for that category
        pipeline = [
            {"$match": {"category": category_filter}},  # Match products by category
            {
                "$group": {
                    "_id": "$product_id",
                    "product_title": {"$first": "$product_title"},
                    "product_images": {"$first": "$product_images"},
                    "category": {"$first": "$category"},
                    "product_average_rating": {"$first": "$product_average_rating"},
                    "store": {"$first": "$store"},
                    "reviews_count": {"$sum": 1}
                }
            },
            {
                "$sort": {
                    "reviews_count": -1
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "product_id": "$_id",
                    "product_title": 1,
                    "product_images": 1,
                    "category": 1,
                    "product_average_rating": 1,
                    "store": 1,
                    "reviews_count": 1
                }
            },

            {"$limit": 50},
        ]
        products = list(product_collection.aggregate(pipeline))
        # Process product images
        
        processed_products = []
        for product in products:
            product_images = product.get('product_images', {})
            price = product.get('price', 'N/A')
            if isinstance(price, float) and math.isnan(price):
                       price = 'N/A'
            if isinstance(product_images, str):
                try:
                    
                    product_images = json.loads(product_images.replace("'", '"'))  # Fix single quotes
                except json.JSONDecodeError:
                    product_images = {}

            # Comprehensive image fallback logic
            image_keys_priority = ['hi_res', 'large', 'thumb']
            processed_product_image = {}

            for key in image_keys_priority:
                images = product_images.get(key, [])
                if images and isinstance(images, list):
                    processed_product_image[key] = images

            # Ensure at least one image type is present
            if not processed_product_image:
                processed_product_image = {'thumb': []}

            # Extract the main image with fallback
            main_image = None
            for key in image_keys_priority:
                if processed_product_image.get(key):
                    main_image = processed_product_image[key][0]
                    break

            # Process the product dictionary with images
            processed_product = {
                'product_id': str(product.get('product_id', product.get('_id'))),
                'product_title': product.get('product_title', 'Unnamed Product'),
                'product_average_rating': product.get('product_average_rating', 0),
                'category': product.get('category', 'Uncategorized'),
                'price': price,
                'product_images': processed_product_image,
                'get_main_image': main_image,  # Correct image URL
                'reviews_count': product.get('reviews_count', 0),  # Adding review count
            }
            processed_products.append(processed_product)
        context = {
            'category': category_filter,
            'products': processed_products,
            'query': query,
        }
        return render(request, 'categories.html', context)
    
    
    else:
        # If no category is selected, list all categories
        pipeline = [
            {
                "$group": {
                    "_id": "$category",
                    "num_products": {"$sum": 1},
                    "first_product": {"$first": "$$ROOT"},
                }
            },
            {"$sort": {"num_products": -1}},  # Sort by number of products in descending order
            {
                "$project": {
                    "category": "$_id",
                    "num_products": 1,
                    "first_product_images": "$first_product.product_images",
                }
            },
        ]
        raw_categories = list(product_collection.aggregate(pipeline))

        categories = []
        for category in raw_categories:
            try:
                product_images = category.get("first_product_images", {})
                
                if isinstance(product_images, str):
                    try:
                        product_images = json.loads(product_images.replace("'", '"'))
                    except json.JSONDecodeError:
                        product_images = {}

                # Select the best available image
                image_keys_priority = ["hi_res", "large", "thumb"]
                processed_category_image = None

                for key in image_keys_priority:
                    images = product_images.get(key, [])
                    if images and isinstance(images, list) and images[0]:
                        processed_category_image = images[0]
                        break

                processed_category = {
                    "category": category.get("category", "Uncategorized"),
                    "num_products": category.get("num_products", 0),
                    "category_image": processed_category_image,
                }

                categories.append(processed_category)

            except Exception as e:
                print(f"Error processing category: {e}")

        # Apply search filter if a query exists
        if query:
            categories = [category for category in categories if query.lower() in category["category"].lower()]

        context = {
            'categories': categories,
            'query': query,
        }

        return render(request, 'categories.html', context)
import math

import json


def products_view(request):
    top_products = list(product_collection.find().sort('product_average_rating', -1).limit(50))
    client.close()

    # Convert MongoDB documents to a format that can be easily used in the template
    products = []
    for product in top_products:
        try:
            # Handle price field for NaN
            price = product.get('price', 'N/A')
            if isinstance(price, float) and math.isnan(price):
                price = 'N/A'

            # Parse product_images if it's a string
            product_images = product.get('product_images', {})
            if isinstance(product_images, str):
                try:
                    product_images = json.loads(product_images.replace("'", '"'))  # Fix single quotes
                except json.JSONDecodeError:
                    product_images = {}

            # Comprehensive image fallback logic
            image_keys_priority = ['hi_res', 'large', 'thumb']
            processed_product_image = {}

            for key in image_keys_priority:
                images = product_images.get(key, [])
                if images and isinstance(images, list):
                    processed_product_image[key] = images

            # Ensure at least one image type is present
            if not processed_product_image:
                processed_product_image = {'thumb': []}

            # Extract the main image with fallback
            main_image = None
            for key in image_keys_priority:
                if processed_product_image.get(key):
                    main_image = processed_product_image[key][0]
                    break

            # Process the product dictionary
            processed_product = {
                'product_id': str(product.get('product_id', product.get('_id'))),
                'product_title': product.get('product_title', 'Unnamed Product'),
                'product_average_rating': product.get('product_average_rating', 0),
                'category': product.get('category', 'Uncategorized'),
                'price': price,
                'product_images': processed_product_image,
                'get_main_image': main_image,  # Correct image URL
            }

            products.append(processed_product)

        except Exception as e:
            print(f"Error processing product: {e}")

    context = {'products': products}
    return render(request, 'products.html', context)




# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['Products']
product_collection = db['sample']  

def product_details(request, product_id):
    # MongoDB aggregation pipeline to calculate sentiment counts and fetch product data
    pipeline = [
        {
            "$match": {
                "product_id": product_id  
            }
        },
        {
            "$group": {
                "_id": "$product_id",  
                "product_title": {"$first": "$product_title"},
                "price": {"$first": "$price"},
                "product_images": {"$first": "$product_images"}, 
                "category": {"$first": "$category"},
                "average_rating": {"$first": "$product_average_rating"},
                "store": {"$first": "$store"},
                "positive_reviews": {
                    "$sum": {"$cond": [{"$eq": ["$Sentiment", "positive"]}, 1, 0]}
                },
                "neutral_reviews": {
                    "$sum": {"$cond": [{"$eq": ["$Sentiment", "neutral"]}, 1, 0]}
                },
                "negative_reviews": {
                    "$sum": {"$cond": [{"$eq": ["$Sentiment", "negative"]}, 1, 0]}
                },
            }
        },
        {
            "$project": {
                "_id": 0,  # Exclude the MongoDB `_id` field
                "product_id": "$_id", 
                "product_title": 1,
                "product_images": 1,
                "category": 1,
                "average_rating": 1,
                "store": 1,
                "positive_reviews": 1,
                "neutral_reviews": 1,
                "negative_reviews": 1,
                "price": 1,
            }
        }
    ]
    
    # Apply the aggregation pipeline to get product details and sentiment counts
    product_data = list(product_collection.aggregate(pipeline))
    
    if not product_data:
        return render(request, '404.html', status=404)  # Optional: handle not found
    
    product = product_data[0]  # Extract the first (and only) product
    
    # Process product images
    product_images = product.get('product_images', {})
    if isinstance(product_images, str):
        try:
            product_images = json.loads(product_images.replace("'", '"'))
        except json.JSONDecodeError:
            product_images = {}
    
    # Comprehensive image fallback logic
    image_keys_priority = ['hi_res', 'large', 'thumb']
    processed_product_image = {}
    
    for key in image_keys_priority:
        images = product_images.get(key, [])
        if images and isinstance(images, list):
            processed_product_image[key] = images
    
    # Ensure at least one image type is present
    if not processed_product_image:
        processed_product_image = {'thumb': []}
    
    # Select the main image
    main_image = None
    for key in image_keys_priority:
        if processed_product_image.get(key):
            main_image = processed_product_image[key][0]
            break
    
    # Update product with processed images
    product['product_images'] = main_image if main_image else None
    price = product.get('price', 'N/A')
    if isinstance(price, float) and math.isnan(price):
        price = 'N/A'  # Or you can set it to None if you prefer
    product['price'] = price
    
    # Fetch the reviews for this product
    reviews = list(product_collection.find(
        {"product_id": product_id},
        {"_id": 0, "review_title": 1, "review_text": 1, "Sentiment": 1}
    ))
    
    if product and 'price' in product:
        # Check if price is not NaN and is a number
        try:
            product['price'] = float(product['price'])
            if math.isnan(product['price']):
                product['price'] = None
        except (TypeError, ValueError):
            product['price'] = None
    return render(request, 'product_details.html', {"product": product, "reviews": reviews})
