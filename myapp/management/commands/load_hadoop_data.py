# load_hadoop_data.py

from django.core.management.base import BaseCommand
from myapp.models import Product
import pandas as pd
from hdfs import InsecureClient
import json
import ast

class Command(BaseCommand):
    help = 'Load product data from Hadoop HDFS'

    def clean_images_data(self, images_data):
        """Clean and validate images data"""
        try:
            # If images_data is string, try to convert to dict
            if isinstance(images_data, str):
                try: 
                    # Try json.loads first
                    images_dict = json.loads(images_data)
                except json.JSONDecodeError:
                    try:
                        # If json.loads fails, try ast.literal_eval
                        images_dict = ast.literal_eval(images_data)
                    except:
                        print(f"Failed to parse images data: {images_data[:1000]}...")
                        return None
            elif isinstance(images_data, dict):
                images_dict = images_data
            else:
                print(f"Unexpected images data type: {type(images_data)}")
                return None

            # Validate structure
            cleaned_images = {
                'large': [],
                'hi_res': [],
                'thumb': []
            }

            for img_type in ['large', 'hi_res', 'thumb']:
                if img_type in images_dict and isinstance(images_dict[img_type], list):
                    cleaned_images[img_type] = [
                        img for img in images_dict[img_type]
                        if img and isinstance(img, str) and img.startswith('http')
                    ]

            return cleaned_images if any(cleaned_images.values()) else None

        except Exception as e:
            print(f"Error cleaning images data: {str(e)}")
            return None

    def handle(self, *args, **options):
        try:
            # Initialize HDFS client
            hdfs_client = InsecureClient('http://localhost:9870', user='pc')

            # Read data from HDFS
            with hdfs_client.read('/user/pc/fashion.csv') as reader:
                df = pd.read_csv(reader)

            self.stdout.write(self.style.SUCCESS(f'Successfully read {len(df)} records from Hadoop'))

            # Clear existing data
            #Product.objects.all().delete()
            #self.stdout.write(self.style.SUCCESS('Cleared existing products'))

            # Process and insert data
            records_created = 0
            for index, row in df.iterrows():
                try:
                    # Clean images data
                    images_data = self.clean_images_data(row['images'])
                    
                    # Handle details
                    details = row['details']
                    if isinstance(details, str):
                        try:
                            details = json.loads(details)
                        except json.JSONDecodeError:
                            try:
                                details = ast.literal_eval(details)
                            except:
                                details = None

                    # Create product
                    product = Product.objects.create(
                        main_category=row['main_category'],
                        title=row['title'],
                        average_rating=row['average_rating'] if pd.notna(row['average_rating']) else None,
                        rating_number=row['rating_number'] if pd.notna(row['rating_number']) else None,
                        price=row['price'] if pd.notna(row['price']) else None,
                        store=row['store'] if pd.notna(row['store']) else None,
                        details=details,
                        parent_asin=row['parent_asin'] if pd.notna(row['parent_asin']) else None,
                        images=images_data
                    )

                    records_created += 1

                    if records_created % 1000 == 0:
                        self.stdout.write(f'Processed {records_created} records...')

                except Exception as e:
                    print(f"Error processing record {index}: {str(e)}")
                    continue

            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully imported {records_created} products from Hadoop'
                )
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to import data: {str(e)}')
            )