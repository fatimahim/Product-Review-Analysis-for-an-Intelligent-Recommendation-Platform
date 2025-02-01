from django.db.models import Count
from djongo import models as djongo_models
from django.db import models
from db_connection import db
#product_collection=db['sample']
from djongo import models
from pymongo import MongoClient
from db_connection import db
from django.db import models


# Create your models here.

product_collection=db['sample']
class Product(models.Model):
    product_id = models.CharField(max_length=255, unique=True)
    user_rating = models.IntegerField()  # Assuming user_rating is an integer
    review_title = models.CharField(max_length=255, null=True, blank=True)
    review_text = models.TextField(null=True, blank=True)
    review_images = models.JSONField(null=True, blank=True)  # Storing review images as JSON if they are arrays
    product_images = models.JSONField(null=True, blank=True)  # JSON for handling multiple image URLs
    product_title = models.CharField(max_length=255)
    category = models.CharField(max_length=255, null=True, blank=True)
    product_average_rating = models.FloatField(default=0.0)
    store = models.CharField(max_length=255, null=True, blank=True)
    sentiment = models.CharField(max_length=50, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    

    

    def __str__(self):
        return self.product_title

    class Meta:
        db_table = 'sample'  # MongoDB collection name
        managed = False  # Important for MongoDB integration

    def get_rating_status(self):
        """Determine rating status based on average rating"""
        rating = self.product_average_rating or self.average_rating
        if rating is None:
            return "No ratings"
        elif rating >= 4.5:
            return "Excellent"
        elif rating >= 4.0:
            return "Good"
        elif rating >= 3.0:
            return "Average"
        else:
            return "Poor"

    def get_main_image(self):
        try:
            # If product_images is a string, convert it to a dictionary
            if isinstance(self.product_images, str):
                import ast
                product_images = ast.literal_eval(self.product_images)
            else:
                product_images = self.product_images

            # Check if hi_res images exist and are not empty
            if isinstance(product_images, dict) and 'hi_res' in product_images:
                images = product_images['hi_res']
                return images[0] if images else '/static/default-product.jpg'
            
            # If no hi_res images, check for other potential image formats
            if isinstance(product_images, dict):
                for img_type in ['large', 'thumb', 'main']:
                    if img_type in product_images and product_images[img_type]:
                        return product_images[img_type][0]
            
            # If images are stored directly as a list
            if isinstance(product_images, list) and product_images:
                return product_images[0]
            
            return '/static/default-product.jpg'
        
        except Exception as e:
            print(f"Error processing product images: {e}")
            return '/static/default-product.jpg'
    @classmethod
    def get_categories(cls):
        """
        Retrieve unique categories with their product counts and the first product's image.
        """
        # Retrieve categories with the count of products
        categories = cls.objects.values('category') \
            .annotate(num_products=Count('id')) \
            .order_by('-num_products')

        for category in categories:
            category_name = category.get('category')
            
            # Get the first product in this category (limit to 1)
            first_product = cls.objects.filter(category=category_name).first()

            # Get the image for the first product in the category
            category_image = first_product.get_main_image() if first_product else None
            category['category_image'] = category_image

        return list(categories)

    def get_all_images(self):
        """Get all available images"""
        try:
            # Convert string to dictionary if necessary
            if isinstance(self.product_images, str):
                import ast
                product_images = ast.literal_eval(self.product_images)
            else:
                product_images = self.product_images

            all_images = set()
            
            if isinstance(product_images, dict):
                for img_type in ['hi_res', 'large', 'thumb', 'main']:
                    if product_images.get(img_type):
                        all_images.update(product_images[img_type])
            elif isinstance(product_images, list):
                all_images.update(product_images)
            
            return list(all_images)
        except Exception as e:
            print(f"Error getting all images: {str(e)}")
            return []
    

