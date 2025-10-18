"""Data models for scraped fashion products."""

from dataclasses import dataclass, asdict, field
from typing import List, Optional
from datetime import datetime


@dataclass
class Product:
    """Represents a fashion product from an e-commerce site."""

    name: str
    main_category: Optional[str] = None  # Men, Women, Kids
    clothing_type: Optional[str] = None  # Shirts, Trousers, Frocks, Sarees, etc.
    price: Optional[str] = None
    original_price: Optional[str] = None
    colors: List[str] = field(default_factory=list)
    sizes: List[str] = field(default_factory=list)
    brand: Optional[str] = None
    image_url: Optional[str] = None
    product_url: Optional[str] = None
    availability: Optional[str] = None
    description: Optional[str] = None
    site_name: str = ""
    scraped_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self):
        """Convert product to dictionary."""
        data = asdict(self)
        # Convert lists to comma-separated strings for CSV compatibility
        if data['colors']:
            data['colors_list'] = ', '.join(data['colors'])
        if data['sizes']:
            data['sizes_list'] = ', '.join(data['sizes'])
        return data

    def __repr__(self):
        return f"Product(name='{self.name}', category='{self.main_category}', type='{self.clothing_type}', price='{self.price}', colors={len(self.colors)})"


@dataclass
class CategoryInfo:
    """Category information."""
    name: str
    url: str
    parent_category: Optional[str] = None  # Men, Women, Kids


@dataclass
class ScrapingResult:
    """Results from scraping a site."""

    site_name: str
    site_url: str
    products: List[Product]
    total_products: int
    categories_scraped: List[str] = field(default_factory=list)
    scraped_at: str = field(default_factory=lambda: datetime.now().isoformat())
    errors: List[str] = field(default_factory=list)

    def to_dict(self):
        """Convert result to dictionary."""
        return {
            "site_name": self.site_name,
            "site_url": self.site_url,
            "total_products": self.total_products,
            "categories_scraped": self.categories_scraped,
            "scraped_at": self.scraped_at,
            "errors": self.errors,
            "products": [p.to_dict() for p in self.products]
        }
