# Users/chatbot.py
import google.generativeai as genai
from django.conf import settings
from Products.models import Product, Category, Review, Stock
from orders.models import Order, OrderItem
from Users.models import User
from django.db.models import Avg, Count, Sum
from django.core.cache import cache
from functools import wraps
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)

def cache_database_query(timeout=300):  # 5 minutes default cache timeout
    """
    Decorator to cache database query results
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create a unique cache key based on function name and arguments
            cache_key = f"chatbot_{func.__name__}_{hash(str(args) + str(kwargs))}"
            
            # Try to get cached result
            result = cache.get(cache_key)
            if result is not None:
                logger.debug(f"Cache hit for {cache_key}")
                return result
            
            # If no cache, execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, timeout)
            logger.debug(f"Cache miss for {cache_key}, cached new result")
            return result
        return wrapper
    return decorator

class ChatbotSingleton:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = FarmToHomeChatbot()
        return cls._instance

class FarmToHomeChatbot:
    def __init__(self):
        try:
            # Configure the API
            genai.configure(api_key=settings.GEMINI_API_KEY)
            
            # Set up the model with the correct model name
            self.model = genai.GenerativeModel('models/gemini-1.5-pro')  # Updated model name
            
            # Get database information
            self.update_database_context()
            
            logger.info("Chatbot initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing chatbot: {str(e)}")
            raise

    @cache_database_query(timeout=300)  # Cache for 5 minutes
    def get_product_statistics(self):
        """Get cached product statistics"""
        total_products = Product.objects.filter(is_active=True).count()
        categories = Category.objects.filter(is_active=True)
        
        category_info = []
        for category in categories:
            products_in_category = category.products.filter(is_active=True)
            avg_price = products_in_category.aggregate(Avg('price'))['price__avg']
            price_display = f"₹{avg_price:.2f}" if avg_price is not None else "Price not available"
            
            category_info.append({
                'name': category.name,
                'product_count': products_in_category.count(),
                'avg_price': price_display
            })
        
        return {
            'total_products': total_products,
            'categories': category_info
        }

    @cache_database_query(timeout=300)  # Cache for 5 minutes
    def get_order_statistics(self):
        """Get cached order statistics"""
        return {
            'total_orders': Order.objects.count() or 0,
            'delivered_orders': Order.objects.filter(delivery_status='delivered').count() or 0,
            'pending_orders': Order.objects.filter(delivery_status='pending').count() or 0
        }

    def update_database_context(self):
        """Update context with cached database information"""
        try:
            # Get cached statistics
            product_stats = self.get_product_statistics()
            order_stats = self.get_order_statistics()
            
            # Format category information
            category_info = [
                f"- {cat['name']}: {cat['product_count']} products (Avg. price: {cat['avg_price']})"
                for cat in product_stats['categories']
            ]

            self.context = f"""You are a helpful assistant for the Farm to Home e-commerce platform.
            
            Current Platform Statistics:
            - Total Active Products: {product_stats['total_products']}
            - Total Orders: {order_stats['total_orders']}
            - Delivered Orders: {order_stats['delivered_orders']}
            - Pending Orders: {order_stats['pending_orders']}
            
            Available Categories:
            {chr(10).join(category_info) if category_info else "No categories available"}
            
            I can help you with:
            1. Product information and availability
            2. Order status and tracking
            3. Product categories and pricing
            4. Delivery information
            5. Product reviews and ratings
            
            Please ask me anything about our products or services!"""
            
        except Exception as e:
            logger.error(f"Error updating database context: {str(e)}")
            self.context = "Basic assistant context - Database information unavailable"

    @cache_database_query(timeout=60)  # Cache for 1 minute
    def get_product_info(self, product_name):
        """Get cached product information"""
        try:
            product = Product.objects.filter(name__icontains=product_name, is_active=True).first()
            if product:
                # Get stock information with safe handling
                try:
                    stock = Stock.objects.get(product=product)
                    stock_status = f"In Stock ({stock.quantity} available)" if stock.is_in_stock else "Out of Stock"
                except Stock.DoesNotExist:
                    stock_status = "Stock information unavailable"

                # Get review information with safe handling
                avg_rating = product.average_rating or 0
                review_count = Review.objects.filter(product=product).count() or 0

                # Safe format the price
                price_display = f"₹{product.price:.2f}" if product.price is not None else "Price not available"

                return {
                    'name': product.name,
                    'category': product.category.name if product.category else 'Uncategorized',
                    'price': price_display,
                    'seller': product.seller.username if product.seller else 'Unknown seller',
                    'stock_status': stock_status,
                    'avg_rating': f"{avg_rating:.1f}/5",
                    'review_count': review_count,
                    'description': product.description or 'No description available'
                }
            return None
        except Exception as e:
            logger.error(f"Error getting product info: {str(e)}")
            return None

    @cache_database_query(timeout=60)  # Cache for 1 minute
    def get_order_info(self, order_id):
        """Get cached order information"""
        try:
            order = Order.objects.get(id=order_id)
            items = OrderItem.objects.filter(order=order)
            
            if not items.exists():
                return None

            items_info = []
            for item in items:
                # Safe format the price
                price_display = f"₹{item.total_price:.2f}" if item.total_price is not None else "Price not available"
                items_info.append({
                    'quantity': item.quantity,
                    'product_name': item.product.name,
                    'price': price_display
                })

            # Safe format the total amount
            total_display = f"₹{order.total_amount:.2f}" if order.total_amount is not None else "Total not available"

            return {
                'order_id': order.id,
                'date': order.order_date.strftime('%Y-%m-%d %H:%M'),
                'status': order.delivery_status.title(),
                'payment_status': order.payment_status.title(),
                'total_amount': total_display,
                'items': items_info
            }
        except Order.DoesNotExist:
            return None
        except Exception as e:
            logger.error(f"Error getting order info: {str(e)}")
            return None

    def format_product_response(self, product_info):
        """Format cached product information into response string"""
        if not product_info:
            return "Sorry, I couldn't find that product."
        
        return f"""
        Product Information:
        Name: {product_info['name']}
        Category: {product_info['category']}
        Price: {product_info['price']}
        Seller: {product_info['seller']}
        Stock Status: {product_info['stock_status']}
        Average Rating: {product_info['avg_rating']} ({product_info['review_count']} reviews)
        Description: {product_info['description']}
        """

    def format_order_response(self, order_info):
        """Format cached order information into response string"""
        if not order_info:
            return "Sorry, I couldn't find that order."
        
        items_text = "\n".join([
            f"- {item['quantity']}x {item['product_name']} ({item['price']})"
            for item in order_info['items']
        ])

        return f"""
        Order #{order_info['order_id']} Information:
        Date: {order_info['date']}
        Status: {order_info['status']}
        Payment Status: {order_info['payment_status']}
        Total Amount: {order_info['total_amount']}
        
        Items:
        {items_text}
        """

    def get_response(self, message):
        try:
            # Update context before responding
            self.update_database_context()
            
            # Check for specific queries
            message_lower = message.lower()
            
            # Product query
            if any(word in message_lower for word in ['product', 'price', 'availability']):
                # Try to extract product name
                words = message_lower.split()
                for word in words:
                    if len(word) > 3:  # Avoid checking very short words
                        product_info = self.get_product_info(word)
                        if product_info:
                            return self.format_product_response(product_info)

            # Order query
            if 'order' in message_lower and '#' in message:
                try:
                    order_id = int(message.split('#')[1].split()[0])
                    order_info = self.get_order_info(order_id)
                    if order_info:
                        return self.format_order_response(order_info)
                except (IndexError, ValueError):
                    pass

            # Generate response using AI
            complete_prompt = f"{self.context}\n\nUser: {message}\nAssistant:"
            response = self.model.generate_content(complete_prompt)
            
            return response.text if response and response.text else "I apologize, but I couldn't generate a response. Please try again."
            
        except Exception as e:
            logger.error(f"Error in Gemini API: {str(e)}")
            return "I apologize, but I'm having trouble processing your request. Please try again later."

    def test_connection(self):
        """Test the API connection and model availability"""
        try:
            # List all available models
            logger.info("Available models:")
            for model in genai.list_models():
                if 'generateContent' in model.supported_generation_methods:
                    logger.info(f"- {model.name}")
            
            # Test simple generation
            test_prompt = "Hello, are you working?"
            response = self.model.generate_content(test_prompt)
            
            if response and response.text:
                logger.info(f"Test response received: {response.text[:100]}...")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Connection test failed: {str(e)}")
            return False

    def reset_conversation(self):
        """Reset the conversation history"""
        try:
            self.chat = self.model.start_chat(history=[])
            return True
        except Exception as e:
            print(f"Error resetting conversation: {str(e)}")
            return False