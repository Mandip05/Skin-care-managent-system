import requests
import logging

class ECommerceIntegration:
    def sync_product(self, product_data):
        try:
            response = requests.post("https://api.ecommerce-platform.com/products",
                                   json=product_data, timeout=5)
            logging.info(f"Product synced: {product_data['name']}")
            return response.status_code == 200
        except Exception as e:
            logging.error(f"E-commerce sync failed: {e}")
            return False