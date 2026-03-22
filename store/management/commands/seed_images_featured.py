"""
Seed command to add Unsplash images and mark bestseller products.
Maps products to cyber/security/networking gadget images from Unsplash.
"""
from django.core.management.base import BaseCommand
from store.models import Product


class Command(BaseCommand):
	help = 'Add Unsplash images to products and mark bestsellers'

	# Map keywords/categories to Unsplash image URLs (cybersecurity/IT gadgets theme)
	IMAGE_MAPPING = {
		'pwnagotchi': 'https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=600&h=600&fit=crop',  # Raspberry Pi
		'flipper': 'https://images.unsplash.com/photo-1550258987-920a2eae3975?w=600&h=600&fit=crop',  # Tech gadget
		'ir blaster': 'https://images.unsplash.com/photo-1597872200969-2b65d56bd16b?w=600&h=600&fit=crop',  # Electronics
		'wifi pineapple': 'https://images.unsplash.com/photo-1547180143-fc3ee5ce6d4c?w=600&h=600&fit=crop',  # Networking
		'usb rubber ducky': 'https://images.unsplash.com/photo-1531746790731-6c087fecd65a?w=600&h=600&fit=crop',  # USB device
		'proxmark': 'https://images.unsplash.com/photo-1550258987-920a2eae3975?w=600&h=600&fit=crop',  # Electronics
		'nrf24': 'https://images.unsplash.com/photo-1597872200969-2b65d56bd16b?w=600&h=600&fit=crop',  # Hardware
		'router': 'https://images.unsplash.com/photo-1606986628025-35d57e735ae0?w=600&h=600&fit=crop',  # Networking
		'switch': 'https://images.unsplash.com/photo-1606986628025-35d57e735ae0?w=600&h=600&fit=crop',  # Network
		'antenna': 'https://images.unsplash.com/photo-1547180143-fc3ee5ce6d4c?w=600&h=600&fit=crop',  # Tech
		'cable': 'https://images.unsplash.com/photo-1593642632823-8f785ba67e45?w=600&h=600&fit=crop',  # Cables
		'connector': 'https://images.unsplash.com/photo-1593642632823-8f785ba67e45?w=600&h=600&fit=crop',  # Hardware
		'raspberry': 'https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=600&h=600&fit=crop',  # SBC
		'pcap': 'https://images.unsplash.com/photo-1550258987-920a2eae3975?w=600&h=600&fit=crop',  # Electronics
		'adapter': 'https://images.unsplash.com/photo-1593642632823-8f785ba67e45?w=600&h=600&fit=crop',  # Connectors
		'security': 'https://images.unsplash.com/photo-1516321318423-f06f70fafffe?w=600&h=600&fit=crop',  # Cyber
		'hack': 'https://images.unsplash.com/photo-1516321318423-f06f70fafffe?w=600&h=600&fit=crop',  # Security
		'forensic': 'https://images.unsplash.com/photo-1550258987-920a2eae3975?w=600&h=600&fit=crop',  # Tech
		'drone': 'https://images.unsplash.com/photo-1579088284722-e3fb3fe8e718?w=600&h=600&fit=crop',  # Drones
		'camera': 'https://images.unsplash.com/photo-1606986628025-35d57e735ae0?w=600&h=600&fit=crop',  # Surveillance
		'microphone': 'https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=600&h=600&fit=crop',  # Audio
		'sensor': 'https://images.unsplash.com/photo-1597872200969-2b65d56bd16b?w=600&h=600&fit=crop',  # IOT
		'display': 'https://images.unsplash.com/photo-1545235917-27898b81ca38?w=600&h=600&fit=crop',  # Monitor
		'keyboard': 'https://images.unsplash.com/photo-1587829191301-0d1c09e4b032?w=600&h=600&fit=crop',  # Keyboard
		'mouse': 'https://images.unsplash.com/photo-1615313917007-11d4b4dc1eb9?w=600&h=600&fit=crop',  # Peripherals
	}

	# Default image for unknown products
	DEFAULT_IMAGE = 'https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=600&h=600&fit=crop'

	def handle(self, *args, **options):
		products = Product.objects.filter(active=True)
		updated = 0
		featured_count = 0

		for product in products:
			# Find matching image URL based on product name/tags
			image_url = self.DEFAULT_IMAGE
			product_lower = (product.name + ' ' + product.tags).lower()

			for keyword, url in self.IMAGE_MAPPING.items():
				if keyword in product_lower:
					image_url = url
					break

			# Update image
			if not product.image_url:
				product.image_url = image_url
				updated += 1

			# Mark high-margin products as featured/bestseller
			# Top products by margin: Pwnagotchi, IR Blaster, Flipper (120%+ margins)
			if product.margin_pct >= 120 and featured_count < 8:
				product.is_featured = True
				product.is_bestseller = True
				featured_count += 1
			# Secondary tier: 80-120% margin
			elif 80 <= product.margin_pct < 120 and featured_count < 15:
				product.is_featured = True
				featured_count += 1

			product.save()

		self.stdout.write(
			self.style.SUCCESS(
				f'✓ Updated {updated} products with images\n'
				f'✓ Marked {featured_count} as featured/bestseller'
			)
		)
