"""Exa.ai tool for generating bakery vendor training data.

Contains exhaustive bakery vendor dataset with detailed quality and reliability
reviews for fine-tuning the evaluation model.
"""

import os
import logging
import random
from typing import Optional

logger = logging.getLogger(__name__)

EXA_API_KEY = os.getenv("EXA_API_KEY")

# Comprehensive bakery ingredients
BAKERY_INGREDIENTS = [
    "flour", "bread flour", "cake flour", "pastry flour", "whole wheat flour",
    "almond flour", "coconut flour", "rye flour",
    "sugar", "brown sugar", "powdered sugar", "raw cane sugar",
    "butter", "unsalted butter", "european butter", "cultured butter",
    "eggs", "egg whites", "egg yolks",
    "yeast", "active dry yeast", "instant yeast", "fresh yeast",
    "vanilla extract", "vanilla beans", "vanilla paste",
    "chocolate", "dark chocolate", "milk chocolate", "cocoa powder", "chocolate chips",
    "cream", "heavy cream", "whipping cream", "sour cream",
    "milk", "whole milk", "buttermilk",
    "baking powder", "baking soda",
    "salt", "sea salt",
    "honey", "maple syrup", "molasses",
    "nuts", "almonds", "walnuts", "pecans", "hazelnuts",
    "dried fruit", "raisins", "cranberries",
    "spices", "cinnamon", "nutmeg", "cardamom", "ginger",
]

# Quality review templates - detailed quality assessments
QUALITY_REVIEWS = {
    "excellent": [
        "Exceptional quality that consistently exceeds expectations. Our head pastry chef specifically requests this supplier.",
        "Premium grade ingredients with remarkable consistency batch to batch. Perfect for fine dining desserts.",
        "Outstanding product quality - the difference is noticeable in our final baked goods. Customers comment on it.",
        "Top-tier supplier with impeccable quality standards. Lab-tested for purity and consistency.",
        "Best quality we've found in 15 years of baking. Worth every penny for the superior results.",
        "Artisan-quality ingredients that elevate our products. Won awards using their supplies.",
        "Pristine quality with full traceability. Meets all our strict quality requirements.",
        "Superior product - our croissants have never been flakier since switching to this supplier.",
        "Gold standard in the industry. Other bakeries ask us who our supplier is.",
        "Unmatched freshness and quality. Their quality control is evident in every delivery.",
    ],
    "good": [
        "Solid quality that meets professional bakery standards. Good value for the quality level.",
        "Reliable quality for everyday baking needs. Consistent enough for production runs.",
        "Good quality ingredients suitable for most bakery applications. Minor variations occasionally.",
        "Above average quality with reasonable pricing. Works well for our mid-range products.",
        "Quality meets expectations for commercial baking. No complaints from our bakers.",
        "Dependable quality for standard bakery operations. Passes our quality checks.",
        "Decent quality that works for high-volume production. Some batches better than others.",
        "Acceptable quality for the price point. Good for everyday baked goods.",
    ],
    "average": [
        "Average quality - works for basic baking but not for premium products.",
        "Standard commercial grade. Suitable for budget-conscious operations.",
        "Quality varies between shipments. Need to check each delivery carefully.",
        "Acceptable for high-volume, price-sensitive production. Not for specialty items.",
        "Middle-of-the-road quality. Works but won't impress discerning customers.",
        "Basic quality that gets the job done. Would upgrade for special orders.",
    ],
    "poor": [
        "Quality inconsistent - had to reject several shipments. Not recommended for quality-focused bakeries.",
        "Below expectations. Product doesn't perform well in our recipes.",
        "Poor quality control evident in deliveries. Affects our final product negatively.",
        "Disappointing quality for the price. Have received stale/degraded product.",
        "Quality issues have caused problems with our baked goods. Looking for alternatives.",
        "Not suitable for professional baking. Quality varies too much.",
    ],
}

# Reliability review templates - detailed reliability assessments
RELIABILITY_REVIEWS = {
    "excellent": [
        "Never missed a delivery in 5 years. They're our most dependable supplier by far.",
        "Clockwork reliability - deliveries always arrive on time, properly packaged.",
        "Exceptional reliability during supply chain disruptions. They always find a way.",
        "100% on-time delivery rate. They notify us proactively of any potential issues.",
        "Rock-solid reliability. We've built our production schedule around their consistency.",
        "Most reliable supplier we work with. Emergency orders handled without fail.",
        "Outstanding track record - zero delivery failures in hundreds of orders.",
        "Dependability is their hallmark. Weather, holidays, nothing stops them.",
        "Trusted partner for 10+ years. They've never let us down during rush seasons.",
        "Impeccable reliability with excellent communication. Always know order status.",
    ],
    "good": [
        "Generally reliable with occasional minor delays communicated in advance.",
        "Good reliability - maybe 1-2 late deliveries per year, always resolved quickly.",
        "Dependable for routine orders. Rush orders sometimes take longer.",
        "Reliable delivery schedule with good communication when issues arise.",
        "Solid reliability for a supplier of their size. Few complaints.",
        "Usually on time. Have backup supplier just in case but rarely needed.",
        "Good track record with delivery. Issues are handled professionally.",
        "Reliable enough for our needs. Occasional delays during peak seasons.",
    ],
    "average": [
        "Hit or miss on delivery times. Need to order extra lead time.",
        "Average reliability - plan for potential delays on important orders.",
        "Sometimes reliable, sometimes not. Communication could be better.",
        "Delivery schedule unpredictable. Have had to scramble several times.",
        "50/50 on time delivery. Good product when it arrives though.",
        "Reliability varies by season. Better in off-peak times.",
    ],
    "poor": [
        "Frequent delivery issues have disrupted our production multiple times.",
        "Unreliable delivery schedule caused us to miss customer orders.",
        "Poor reliability - switched to backup supplier permanently.",
        "Cannot depend on them for time-sensitive orders. Too risky.",
        "Delivery problems are chronic. Management doesn't seem to care.",
        "Had to cancel contract due to repeated delivery failures.",
    ],
}

# Comprehensive vendor database with detailed reviews
SAMPLE_VENDORS = [
    # === FLOUR VENDORS ===
    {
        "vendor_name": "Bay Area Flour Mills",
        "product": "flour",
        "price_per_unit": 0.45,
        "unit": "lb",
        "distance_miles": 15,
        "quality_score": 94,
        "reliability_score": 97,
        "certifications": ["USDA Organic", "Non-GMO Project Verified", "SQF Certified"],
        "description": "Premium organic flour supplier serving Bay Area bakeries since 1985. Stone-ground process preserves nutrients.",
        "reviews": {
            "quality": "Exceptional quality that consistently exceeds expectations. Our head pastry chef specifically requests this supplier. The stone-ground flour produces superior texture in our artisan breads.",
            "reliability": "Never missed a delivery in 5 years. They're our most dependable supplier by far. Even during the pandemic supply crunch, they came through.",
        },
        "order_accuracy": 99.5,
        "avg_delivery_days": 2,
        "years_in_business": 39,
    },
    {
        "vendor_name": "Artisan Grain Co",
        "product": "bread flour",
        "price_per_unit": 0.52,
        "unit": "lb",
        "distance_miles": 28,
        "quality_score": 96,
        "reliability_score": 94,
        "certifications": ["Organic", "Whole Grain Council", "Non-GMO"],
        "description": "Specialty bread flour supplier focusing on heritage wheat varieties. High protein content ideal for artisan breads.",
        "reviews": {
            "quality": "Premium grade ingredients with remarkable consistency batch to batch. Perfect for our sourdough and ciabatta. Protein levels exactly as specified.",
            "reliability": "Generally reliable with occasional minor delays communicated in advance. Their specialty products sometimes have longer lead times.",
        },
        "order_accuracy": 98.2,
        "avg_delivery_days": 3,
        "years_in_business": 12,
    },
    {
        "vendor_name": "Industrial Flour Corp",
        "product": "flour",
        "price_per_unit": 0.22,
        "unit": "lb",
        "distance_miles": 150,
        "quality_score": 68,
        "reliability_score": 92,
        "certifications": ["FDA Registered"],
        "description": "Large-scale flour production for commercial bakeries. Focus on volume and competitive pricing.",
        "reviews": {
            "quality": "Average quality - works for basic baking but not for premium products. Protein content varies between batches.",
            "reliability": "Good reliability - maybe 1-2 late deliveries per year, always resolved quickly. Large inventory means consistent availability.",
        },
        "order_accuracy": 96.0,
        "avg_delivery_days": 4,
        "years_in_business": 45,
    },
    {
        "vendor_name": "Budget Baking Supplies",
        "product": "flour",
        "price_per_unit": 0.28,
        "unit": "lb",
        "distance_miles": 80,
        "quality_score": 62,
        "reliability_score": 71,
        "certifications": [],
        "description": "Low-cost bulk flour for high-volume bakeries prioritizing cost over premium quality.",
        "reviews": {
            "quality": "Quality inconsistent - had to reject several shipments. Not recommended for quality-focused bakeries. Fine for cheap breads.",
            "reliability": "Hit or miss on delivery times. Need to order extra lead time. Communication when issues arise is poor.",
        },
        "order_accuracy": 89.0,
        "avg_delivery_days": 5,
        "years_in_business": 8,
    },
    {
        "vendor_name": "Golden Wheat Farms",
        "product": "whole wheat flour",
        "price_per_unit": 0.58,
        "unit": "lb",
        "distance_miles": 42,
        "quality_score": 91,
        "reliability_score": 93,
        "certifications": ["USDA Organic", "Certified Biodynamic"],
        "description": "Farm-to-bakery whole wheat flour. Single-origin wheat with full nutritional profile intact.",
        "reviews": {
            "quality": "Outstanding product quality - the difference is noticeable in our final baked goods. Rich, nutty flavor customers love.",
            "reliability": "Reliable delivery schedule with good communication when issues arise. Seasonal availability clearly communicated.",
        },
        "order_accuracy": 97.5,
        "avg_delivery_days": 3,
        "years_in_business": 22,
    },
    {
        "vendor_name": "Pastry Perfect Mills",
        "product": "cake flour",
        "price_per_unit": 0.65,
        "unit": "lb",
        "distance_miles": 35,
        "quality_score": 97,
        "reliability_score": 95,
        "certifications": ["SQF Level 3", "Kosher", "Non-GMO"],
        "description": "Ultra-fine cake flour with precise protein content for delicate cakes and pastries.",
        "reviews": {
            "quality": "Top-tier supplier with impeccable quality standards. Lab-tested for purity and consistency. Our cakes have never been lighter.",
            "reliability": "Rock-solid reliability. We've built our production schedule around their consistency. Zero surprises.",
        },
        "order_accuracy": 99.8,
        "avg_delivery_days": 2,
        "years_in_business": 28,
    },

    # === EGG VENDORS ===
    {
        "vendor_name": "Central Valley Eggs",
        "product": "eggs",
        "price_per_unit": 3.50,
        "unit": "dozen",
        "distance_miles": 45,
        "quality_score": 88,
        "reliability_score": 91,
        "certifications": ["Cage-Free", "Certified Humane", "USDA Grade A"],
        "description": "Family-owned egg farm with cage-free, pasture-raised eggs. Third-generation farmers.",
        "reviews": {
            "quality": "Solid quality that meets professional bakery standards. Good yolk color and shell strength. Occasional size variations.",
            "reliability": "Dependable for routine orders. Rush orders sometimes take longer. Good family business to work with.",
        },
        "order_accuracy": 95.5,
        "avg_delivery_days": 1,
        "years_in_business": 67,
    },
    {
        "vendor_name": "Heritage Hen Farms",
        "product": "eggs",
        "price_per_unit": 5.25,
        "unit": "dozen",
        "distance_miles": 22,
        "quality_score": 98,
        "reliability_score": 96,
        "certifications": ["Pasture-Raised", "Organic", "Animal Welfare Approved", "Non-GMO"],
        "description": "Premium pasture-raised eggs from heritage breed hens. Deep orange yolks with superior taste.",
        "reviews": {
            "quality": "Best quality we've found in 15 years of baking. Worth every penny for the superior results. Customers notice the difference in our custards.",
            "reliability": "100% on-time delivery rate. They notify us proactively of any potential issues. Truly exceptional service.",
        },
        "order_accuracy": 99.2,
        "avg_delivery_days": 1,
        "years_in_business": 18,
    },
    {
        "vendor_name": "Neighborhood Eggs",
        "product": "eggs",
        "price_per_unit": 4.50,
        "unit": "dozen",
        "distance_miles": 8,
        "quality_score": 82,
        "reliability_score": 68,
        "certifications": ["Local"],
        "description": "Small local farm with fresh daily delivery when available. Limited supply capacity.",
        "reviews": {
            "quality": "Good quality ingredients suitable for most bakery applications. Freshness is excellent when available. Supply limited.",
            "reliability": "Reliability varies by season. Better in off-peak times. Small operation means capacity constraints.",
        },
        "order_accuracy": 85.0,
        "avg_delivery_days": 1,
        "years_in_business": 5,
    },
    {
        "vendor_name": "Commercial Egg Distributors",
        "product": "eggs",
        "price_per_unit": 2.80,
        "unit": "dozen",
        "distance_miles": 95,
        "quality_score": 72,
        "reliability_score": 94,
        "certifications": ["USDA Grade A"],
        "description": "Large-scale egg distribution for commercial food service. Consistent supply chain.",
        "reviews": {
            "quality": "Standard commercial grade. Suitable for budget-conscious operations. Nothing special but gets the job done.",
            "reliability": "Outstanding track record - zero delivery failures in hundreds of orders. Large distribution network ensures availability.",
        },
        "order_accuracy": 97.0,
        "avg_delivery_days": 2,
        "years_in_business": 52,
    },
    {
        "vendor_name": "Sunrise Organic Eggs",
        "product": "eggs",
        "price_per_unit": 4.75,
        "unit": "dozen",
        "distance_miles": 55,
        "quality_score": 93,
        "reliability_score": 89,
        "certifications": ["USDA Organic", "Free-Range", "Non-GMO"],
        "description": "Certified organic eggs from free-range hens fed organic, non-GMO feed.",
        "reviews": {
            "quality": "Artisan-quality ingredients that elevate our products. Won awards using their supplies. Bright yolks with great structure.",
            "reliability": "Good track record with delivery. Issues are handled professionally. Occasional supply constraints in winter.",
        },
        "order_accuracy": 96.5,
        "avg_delivery_days": 2,
        "years_in_business": 14,
    },

    # === BUTTER VENDORS ===
    {
        "vendor_name": "Dairy Fresh Co",
        "product": "butter",
        "price_per_unit": 4.25,
        "unit": "lb",
        "distance_miles": 25,
        "quality_score": 95,
        "reliability_score": 93,
        "certifications": ["Grade AA", "rBST-Free", "American Humane Certified"],
        "description": "European-style cultured butter, perfect for pastries. Higher butterfat content than standard butter.",
        "reviews": {
            "quality": "Superior product - our croissants have never been flakier since switching to this supplier. 84% butterfat makes a difference.",
            "reliability": "Reliable enough for our needs. Occasional delays during peak seasons like holidays. Good communication.",
        },
        "order_accuracy": 97.8,
        "avg_delivery_days": 2,
        "years_in_business": 31,
    },
    {
        "vendor_name": "Artisan Butter House",
        "product": "cultured butter",
        "price_per_unit": 6.50,
        "unit": "lb",
        "distance_miles": 35,
        "quality_score": 99,
        "reliability_score": 85,
        "certifications": ["Organic", "Grass-Fed", "Small Batch", "Non-GMO"],
        "description": "Hand-churned artisan butter from heritage cows. Small-batch production ensures premium quality.",
        "reviews": {
            "quality": "Gold standard in the industry. Other bakeries ask us who our supplier is. Complex flavor profile unmatched by others.",
            "reliability": "Usually on time. Have backup supplier just in case but rarely needed. Small batch means occasional wait times.",
        },
        "order_accuracy": 94.0,
        "avg_delivery_days": 4,
        "years_in_business": 9,
    },
    {
        "vendor_name": "European Butter Imports",
        "product": "european butter",
        "price_per_unit": 7.80,
        "unit": "lb",
        "distance_miles": 180,
        "quality_score": 98,
        "reliability_score": 78,
        "certifications": ["AOC", "EU Organic", "PDO Protected"],
        "description": "Imported French and Irish butter for premium pastry applications. 86% butterfat.",
        "reviews": {
            "quality": "Pristine quality with full traceability. Meets all our strict quality requirements. The real deal from Europe.",
            "reliability": "Average reliability - plan for potential delays on important orders. Import logistics can be unpredictable.",
        },
        "order_accuracy": 92.0,
        "avg_delivery_days": 7,
        "years_in_business": 25,
    },
    {
        "vendor_name": "Valley Creamery",
        "product": "unsalted butter",
        "price_per_unit": 3.95,
        "unit": "lb",
        "distance_miles": 40,
        "quality_score": 86,
        "reliability_score": 96,
        "certifications": ["Grade AA", "rBST-Free"],
        "description": "Regional creamery producing consistent Grade AA butter for commercial baking.",
        "reviews": {
            "quality": "Above average quality with reasonable pricing. Works well for our mid-range products. Consistent performance.",
            "reliability": "Clockwork reliability - deliveries always arrive on time, properly packaged. Never an issue in 8 years.",
        },
        "order_accuracy": 98.5,
        "avg_delivery_days": 2,
        "years_in_business": 44,
    },
    {
        "vendor_name": "Budget Dairy Supply",
        "product": "butter",
        "price_per_unit": 3.20,
        "unit": "lb",
        "distance_miles": 120,
        "quality_score": 65,
        "reliability_score": 88,
        "certifications": ["USDA Grade A"],
        "description": "Economy butter for price-sensitive commercial operations. Standard quality.",
        "reviews": {
            "quality": "Basic quality that gets the job done. Would upgrade for special orders. Fine for everyday production bread.",
            "reliability": "Good reliability for a supplier of their size. Few complaints. Large inventory buffer.",
        },
        "order_accuracy": 95.0,
        "avg_delivery_days": 3,
        "years_in_business": 38,
    },

    # === SUGAR VENDORS ===
    {
        "vendor_name": "SugarTech Wholesale",
        "product": "sugar",
        "price_per_unit": 0.55,
        "unit": "lb",
        "distance_miles": 60,
        "quality_score": 85,
        "reliability_score": 90,
        "certifications": ["Fair Trade", "Non-GMO"],
        "description": "Bulk sugar supplier with competitive wholesale pricing. Fair trade certified.",
        "reviews": {
            "quality": "Quality meets expectations for commercial baking. No complaints from our bakers. Dissolves cleanly.",
            "reliability": "Solid reliability for a supplier of their size. Few complaints. Handle large orders well.",
        },
        "order_accuracy": 96.5,
        "avg_delivery_days": 3,
        "years_in_business": 27,
    },
    {
        "vendor_name": "Pure Cane Organics",
        "product": "raw cane sugar",
        "price_per_unit": 0.85,
        "unit": "lb",
        "distance_miles": 75,
        "quality_score": 94,
        "reliability_score": 91,
        "certifications": ["USDA Organic", "Fair Trade", "Non-GMO", "Vegan"],
        "description": "Organic raw cane sugar with natural molasses content. Minimally processed.",
        "reviews": {
            "quality": "Outstanding product quality - the difference is noticeable in our final baked goods. Adds depth of flavor.",
            "reliability": "Dependable for routine orders. Rush orders sometimes take longer due to organic sourcing constraints.",
        },
        "order_accuracy": 97.0,
        "avg_delivery_days": 4,
        "years_in_business": 16,
    },
    {
        "vendor_name": "Confectioners Supply Co",
        "product": "powdered sugar",
        "price_per_unit": 0.72,
        "unit": "lb",
        "distance_miles": 48,
        "quality_score": 92,
        "reliability_score": 95,
        "certifications": ["Kosher", "Non-GMO"],
        "description": "Fine 10X powdered sugar for icings, frostings, and delicate confections.",
        "reviews": {
            "quality": "Artisan-quality ingredients that elevate our products. Ultra-fine grind perfect for smooth icings.",
            "reliability": "Exceptional reliability during supply chain disruptions. They always find a way to deliver.",
        },
        "order_accuracy": 98.8,
        "avg_delivery_days": 2,
        "years_in_business": 35,
    },
    {
        "vendor_name": "Brown Sugar Direct",
        "product": "brown sugar",
        "price_per_unit": 0.68,
        "unit": "lb",
        "distance_miles": 55,
        "quality_score": 89,
        "reliability_score": 93,
        "certifications": ["Non-GMO", "Natural"],
        "description": "Premium dark and light brown sugar with real molasses. Soft, moist texture.",
        "reviews": {
            "quality": "Solid quality that meets professional bakery standards. Perfect moisture content for cookies.",
            "reliability": "100% on-time delivery rate. They notify us proactively of any potential issues.",
        },
        "order_accuracy": 97.5,
        "avg_delivery_days": 3,
        "years_in_business": 21,
    },

    # === YEAST VENDORS ===
    {
        "vendor_name": "Pacific Yeast Labs",
        "product": "yeast",
        "price_per_unit": 12.00,
        "unit": "lb",
        "distance_miles": 30,
        "quality_score": 98,
        "reliability_score": 97,
        "certifications": ["ISO 9001", "FSSC 22000", "Non-GMO"],
        "description": "Premium baker's yeast for artisan bread production. Consistent activity levels guaranteed.",
        "reviews": {
            "quality": "Unmatched freshness and quality. Their quality control is evident in every delivery. Perfect fermentation every time.",
            "reliability": "Most reliable supplier we work with. Emergency orders handled without fail. Cold chain always maintained.",
        },
        "order_accuracy": 99.9,
        "avg_delivery_days": 1,
        "years_in_business": 42,
    },
    {
        "vendor_name": "Fresh Yeast Direct",
        "product": "fresh yeast",
        "price_per_unit": 3.50,
        "unit": "lb",
        "distance_miles": 18,
        "quality_score": 96,
        "reliability_score": 94,
        "certifications": ["Organic Option", "Non-GMO"],
        "description": "Fresh compressed yeast delivered within 24 hours of production. Maximum vitality.",
        "reviews": {
            "quality": "Premium grade ingredients with remarkable consistency batch to batch. Perfect for our sourdough starters.",
            "reliability": "Trusted partner for 10+ years. They've never let us down during rush seasons. Daily delivery available.",
        },
        "order_accuracy": 98.5,
        "avg_delivery_days": 1,
        "years_in_business": 29,
    },
    {
        "vendor_name": "Instant Yeast Wholesale",
        "product": "instant yeast",
        "price_per_unit": 8.50,
        "unit": "lb",
        "distance_miles": 85,
        "quality_score": 88,
        "reliability_score": 92,
        "certifications": ["Kosher", "Halal"],
        "description": "Bulk instant dry yeast for high-volume commercial bakeries. Long shelf life.",
        "reviews": {
            "quality": "Good quality for the price point. Works for our mid-range products. Consistent activity.",
            "reliability": "Good reliability - maybe 1-2 late deliveries per year, always resolved quickly.",
        },
        "order_accuracy": 96.0,
        "avg_delivery_days": 3,
        "years_in_business": 33,
    },

    # === VANILLA VENDORS ===
    {
        "vendor_name": "Premium Extract Co",
        "product": "vanilla extract",
        "price_per_unit": 45.00,
        "unit": "pint",
        "distance_miles": 200,
        "quality_score": 99,
        "reliability_score": 86,
        "certifications": ["Pure Madagascar", "Organic", "Fair Trade"],
        "description": "Authentic Madagascar bourbon vanilla extract. Single-origin, cold-extracted.",
        "reviews": {
            "quality": "Gold standard in the industry. Other bakeries ask us who our supplier is. Incredible depth of flavor.",
            "reliability": "Average reliability - plan for potential delays on important orders. Madagascar sourcing has challenges.",
        },
        "order_accuracy": 94.5,
        "avg_delivery_days": 5,
        "years_in_business": 47,
    },
    {
        "vendor_name": "Vanilla Bean Direct",
        "product": "vanilla beans",
        "price_per_unit": 8.50,
        "unit": "bean",
        "distance_miles": 165,
        "quality_score": 97,
        "reliability_score": 82,
        "certifications": ["Grade A", "Organic", "Direct Trade"],
        "description": "Grade A Madagascar and Tahitian vanilla beans. Plump, oily, and aromatic.",
        "reviews": {
            "quality": "Exceptional quality that consistently exceeds expectations. Each bean is perfect for scraping.",
            "reliability": "Sometimes reliable, sometimes not. Communication could be better. Seasonal availability varies.",
        },
        "order_accuracy": 91.0,
        "avg_delivery_days": 6,
        "years_in_business": 19,
    },
    {
        "vendor_name": "Bakers Vanilla Supply",
        "product": "vanilla extract",
        "price_per_unit": 28.00,
        "unit": "pint",
        "distance_miles": 70,
        "quality_score": 85,
        "reliability_score": 94,
        "certifications": ["Pure Vanilla", "Kosher"],
        "description": "Pure vanilla extract for commercial baking. Good balance of quality and value.",
        "reviews": {
            "quality": "Above average quality with reasonable pricing. Works well for production baking.",
            "reliability": "Rock-solid reliability. We've built our production schedule around their consistency.",
        },
        "order_accuracy": 97.5,
        "avg_delivery_days": 2,
        "years_in_business": 36,
    },

    # === CHOCOLATE VENDORS ===
    {
        "vendor_name": "Cocoa Imports Direct",
        "product": "chocolate",
        "price_per_unit": 8.50,
        "unit": "lb",
        "distance_miles": 120,
        "quality_score": 96,
        "reliability_score": 83,
        "certifications": ["Rainforest Alliance", "Fair Trade", "UTZ"],
        "description": "Single-origin Belgian chocolate for premium baked goods. Multiple cacao percentages available.",
        "reviews": {
            "quality": "Pristine quality with full traceability. Meets all our strict quality requirements. True Belgian craftsmanship.",
            "reliability": "Hit or miss on delivery times. Need to order extra lead time. Import delays common.",
        },
        "order_accuracy": 93.0,
        "avg_delivery_days": 8,
        "years_in_business": 24,
    },
    {
        "vendor_name": "Artisan Chocolate Co",
        "product": "dark chocolate",
        "price_per_unit": 12.50,
        "unit": "lb",
        "distance_miles": 45,
        "quality_score": 99,
        "reliability_score": 91,
        "certifications": ["Organic", "Direct Trade", "Bean-to-Bar"],
        "description": "Small-batch bean-to-bar chocolate. Single origin with flavor notes detailed.",
        "reviews": {
            "quality": "Best quality we've found in 15 years of baking. Worth every penny for the superior results. Award-winning chocolate.",
            "reliability": "Generally reliable with occasional minor delays communicated in advance. Small batch production limits.",
        },
        "order_accuracy": 96.0,
        "avg_delivery_days": 4,
        "years_in_business": 11,
    },
    {
        "vendor_name": "Bulk Chocolate Supply",
        "product": "chocolate chips",
        "price_per_unit": 4.25,
        "unit": "lb",
        "distance_miles": 90,
        "quality_score": 78,
        "reliability_score": 95,
        "certifications": ["Kosher"],
        "description": "Commercial chocolate chips for high-volume cookie production. Consistent melt characteristics.",
        "reviews": {
            "quality": "Decent quality that works for high-volume production. Some batches better than others.",
            "reliability": "Outstanding track record - zero delivery failures in hundreds of orders. Always in stock.",
        },
        "order_accuracy": 98.0,
        "avg_delivery_days": 3,
        "years_in_business": 41,
    },
    {
        "vendor_name": "Premium Cocoa Works",
        "product": "cocoa powder",
        "price_per_unit": 6.75,
        "unit": "lb",
        "distance_miles": 55,
        "quality_score": 95,
        "reliability_score": 92,
        "certifications": ["Dutch Process", "Organic", "Fair Trade"],
        "description": "Dutch-process cocoa powder with rich, deep color. Alkalized for better flavor.",
        "reviews": {
            "quality": "Top-tier supplier with impeccable quality standards. Lab-tested for purity. Perfect for our chocolate cakes.",
            "reliability": "Reliable delivery schedule with good communication when issues arise.",
        },
        "order_accuracy": 97.0,
        "avg_delivery_days": 3,
        "years_in_business": 28,
    },

    # === DAIRY VENDORS ===
    {
        "vendor_name": "Local Cream Dairy",
        "product": "cream",
        "price_per_unit": 5.00,
        "unit": "quart",
        "distance_miles": 10,
        "quality_score": 93,
        "reliability_score": 96,
        "certifications": ["Grade A", "Local", "Grass-Fed"],
        "description": "Fresh heavy cream from local grass-fed cows. 40% butterfat for superior whipping.",
        "reviews": {
            "quality": "Outstanding product quality - the difference is noticeable in our final baked goods. Whips beautifully.",
            "reliability": "Impeccable reliability with excellent communication. Always know order status. Daily delivery.",
        },
        "order_accuracy": 98.5,
        "avg_delivery_days": 1,
        "years_in_business": 56,
    },
    {
        "vendor_name": "Premium Dairy Distributors",
        "product": "heavy cream",
        "price_per_unit": 4.50,
        "unit": "quart",
        "distance_miles": 35,
        "quality_score": 89,
        "reliability_score": 94,
        "certifications": ["Grade A", "rBST-Free"],
        "description": "Commercial heavy cream for food service. Consistent quality and availability.",
        "reviews": {
            "quality": "Solid quality that meets professional bakery standards. Reliable fat content.",
            "reliability": "Dependability is their hallmark. Weather, holidays, nothing stops them.",
        },
        "order_accuracy": 97.5,
        "avg_delivery_days": 1,
        "years_in_business": 48,
    },
    {
        "vendor_name": "Organic Valley Dairy",
        "product": "milk",
        "price_per_unit": 4.25,
        "unit": "gallon",
        "distance_miles": 65,
        "quality_score": 94,
        "reliability_score": 90,
        "certifications": ["USDA Organic", "Pasture-Raised", "Non-GMO"],
        "description": "Certified organic whole milk from pasture-raised cows. No artificial hormones.",
        "reviews": {
            "quality": "Premium grade ingredients with remarkable consistency. Makes our bread incredibly tender.",
            "reliability": "Good reliability for routine orders. Organic supply chain occasionally constrained.",
        },
        "order_accuracy": 96.0,
        "avg_delivery_days": 2,
        "years_in_business": 22,
    },
    {
        "vendor_name": "Cultured Cream Co",
        "product": "sour cream",
        "price_per_unit": 3.50,
        "unit": "lb",
        "distance_miles": 42,
        "quality_score": 91,
        "reliability_score": 93,
        "certifications": ["Grade A", "All Natural"],
        "description": "Traditional cultured sour cream. Perfect for cakes and coffee cakes.",
        "reviews": {
            "quality": "Artisan-quality ingredients that elevate our products. Real cultured flavor.",
            "reliability": "Exceptional reliability during supply chain disruptions. They always find a way.",
        },
        "order_accuracy": 97.0,
        "avg_delivery_days": 2,
        "years_in_business": 34,
    },
    {
        "vendor_name": "Buttermilk Farms",
        "product": "buttermilk",
        "price_per_unit": 3.25,
        "unit": "quart",
        "distance_miles": 28,
        "quality_score": 90,
        "reliability_score": 95,
        "certifications": ["Grade A", "Live Cultures"],
        "description": "Traditional churned buttermilk with live cultures. Essential for tender biscuits.",
        "reviews": {
            "quality": "Good quality ingredients suitable for most bakery applications. Real buttermilk tang.",
            "reliability": "100% on-time delivery rate. They notify us proactively of any potential issues.",
        },
        "order_accuracy": 98.0,
        "avg_delivery_days": 1,
        "years_in_business": 61,
    },

    # === NUT VENDORS ===
    {
        "vendor_name": "California Almond Growers",
        "product": "almonds",
        "price_per_unit": 7.50,
        "unit": "lb",
        "distance_miles": 85,
        "quality_score": 95,
        "reliability_score": 93,
        "certifications": ["California Grown", "Non-GMO", "Kosher"],
        "description": "Premium California almonds, whole and sliced. Direct from growers.",
        "reviews": {
            "quality": "Exceptional quality that consistently exceeds expectations. Fresh, crunchy, perfect flavor.",
            "reliability": "Reliable delivery schedule with good communication. Seasonal pricing variations.",
        },
        "order_accuracy": 97.5,
        "avg_delivery_days": 3,
        "years_in_business": 72,
    },
    {
        "vendor_name": "Pecan Processors Inc",
        "product": "pecans",
        "price_per_unit": 9.25,
        "unit": "lb",
        "distance_miles": 145,
        "quality_score": 92,
        "reliability_score": 89,
        "certifications": ["Georgia Grown", "Non-GMO"],
        "description": "Southern pecans, halves and pieces. Ideal for pies and pralines.",
        "reviews": {
            "quality": "Superior product - our pecan pies have never been better. Rich, buttery flavor.",
            "reliability": "Good track record with delivery. Issues handled professionally. Hurricane season delays possible.",
        },
        "order_accuracy": 95.5,
        "avg_delivery_days": 4,
        "years_in_business": 55,
    },
    {
        "vendor_name": "Oregon Walnut Co",
        "product": "walnuts",
        "price_per_unit": 6.80,
        "unit": "lb",
        "distance_miles": 110,
        "quality_score": 90,
        "reliability_score": 91,
        "certifications": ["Oregon Grown", "Organic Option"],
        "description": "Oregon-grown walnuts with mild, sweet flavor. Light color preferred by bakers.",
        "reviews": {
            "quality": "Solid quality that meets professional standards. Fresh harvest available in fall.",
            "reliability": "Generally reliable with minor delays communicated in advance.",
        },
        "order_accuracy": 96.0,
        "avg_delivery_days": 4,
        "years_in_business": 38,
    },
    {
        "vendor_name": "Hazelnut Haven",
        "product": "hazelnuts",
        "price_per_unit": 11.00,
        "unit": "lb",
        "distance_miles": 125,
        "quality_score": 96,
        "reliability_score": 87,
        "certifications": ["Oregon Grown", "Sustainably Farmed"],
        "description": "Oregon hazelnuts, whole and blanched. Perfect for praline and gianduja.",
        "reviews": {
            "quality": "Best quality we've found. Our hazelnut croissants are now famous locally.",
            "reliability": "Usually on time. Have backup supplier just in case. Harvest timing affects availability.",
        },
        "order_accuracy": 94.0,
        "avg_delivery_days": 5,
        "years_in_business": 29,
    },

    # === HONEY & SWEETENER VENDORS ===
    {
        "vendor_name": "Local Apiaries Honey",
        "product": "honey",
        "price_per_unit": 8.50,
        "unit": "lb",
        "distance_miles": 25,
        "quality_score": 97,
        "reliability_score": 85,
        "certifications": ["Local", "Raw", "Unfiltered"],
        "description": "Raw local honey from nearby apiaries. Seasonal varieties available.",
        "reviews": {
            "quality": "Unmatched freshness and quality. Their quality control is evident. Each batch is labeled by source.",
            "reliability": "Reliability varies by season. Better in off-peak times. Bees set the schedule.",
        },
        "order_accuracy": 93.0,
        "avg_delivery_days": 3,
        "years_in_business": 44,
    },
    {
        "vendor_name": "Pure Maple Farms",
        "product": "maple syrup",
        "price_per_unit": 18.00,
        "unit": "quart",
        "distance_miles": 180,
        "quality_score": 98,
        "reliability_score": 88,
        "certifications": ["Vermont Grade A", "Organic", "Pure"],
        "description": "Pure Vermont maple syrup. Grade A amber for baking. No additives.",
        "reviews": {
            "quality": "Gold standard in the industry. Real maple flavor that artificial can't match.",
            "reliability": "Good reliability for a seasonal product. Winter stock availability varies.",
        },
        "order_accuracy": 95.0,
        "avg_delivery_days": 5,
        "years_in_business": 89,
    },
    {
        "vendor_name": "Blackstrap Supply",
        "product": "molasses",
        "price_per_unit": 4.25,
        "unit": "quart",
        "distance_miles": 95,
        "quality_score": 88,
        "reliability_score": 94,
        "certifications": ["Unsulfured", "Non-GMO"],
        "description": "Unsulfured blackstrap molasses. Rich mineral content, deep flavor.",
        "reviews": {
            "quality": "Good quality ingredients suitable for gingerbread and dark breads.",
            "reliability": "Rock-solid reliability. We've built our production schedule around their consistency.",
        },
        "order_accuracy": 97.5,
        "avg_delivery_days": 3,
        "years_in_business": 52,
    },

    # === SPECIALTY FLOUR VENDORS ===
    {
        "vendor_name": "Almond Flour Direct",
        "product": "almond flour",
        "price_per_unit": 8.50,
        "unit": "lb",
        "distance_miles": 75,
        "quality_score": 94,
        "reliability_score": 92,
        "certifications": ["Blanched", "Super-Fine", "Gluten-Free", "Non-GMO"],
        "description": "Super-fine blanched almond flour for macarons and gluten-free baking.",
        "reviews": {
            "quality": "Top-tier supplier with impeccable quality standards. Perfect grind for French macarons.",
            "reliability": "Reliable delivery schedule with good communication when issues arise.",
        },
        "order_accuracy": 97.0,
        "avg_delivery_days": 3,
        "years_in_business": 15,
    },
    {
        "vendor_name": "Tropical Flour Co",
        "product": "coconut flour",
        "price_per_unit": 5.75,
        "unit": "lb",
        "distance_miles": 165,
        "quality_score": 91,
        "reliability_score": 84,
        "certifications": ["Organic", "Gluten-Free", "Fair Trade"],
        "description": "Organic coconut flour from sustainable sources. High fiber, low carb.",
        "reviews": {
            "quality": "Outstanding product quality - consistent moisture absorption. Works perfectly in our recipes.",
            "reliability": "Average reliability - import logistics can be unpredictable. Order ahead.",
        },
        "order_accuracy": 92.5,
        "avg_delivery_days": 6,
        "years_in_business": 12,
    },
    {
        "vendor_name": "Heritage Rye Mills",
        "product": "rye flour",
        "price_per_unit": 0.68,
        "unit": "lb",
        "distance_miles": 95,
        "quality_score": 93,
        "reliability_score": 91,
        "certifications": ["Stone-Ground", "Whole Grain", "Non-GMO"],
        "description": "Stone-ground rye flour for authentic European-style breads.",
        "reviews": {
            "quality": "Artisan-quality ingredients that elevate our products. Real rye flavor.",
            "reliability": "Dependable for routine orders. Heritage grain supplies occasionally limited.",
        },
        "order_accuracy": 96.5,
        "avg_delivery_days": 4,
        "years_in_business": 67,
    },

    # === LEAVENING VENDORS ===
    {
        "vendor_name": "Leavening Specialists",
        "product": "baking powder",
        "price_per_unit": 3.50,
        "unit": "lb",
        "distance_miles": 55,
        "quality_score": 92,
        "reliability_score": 96,
        "certifications": ["Aluminum-Free", "Non-GMO", "Kosher"],
        "description": "Double-acting aluminum-free baking powder. Consistent rise guaranteed.",
        "reviews": {
            "quality": "Premium grade ingredients with remarkable consistency. Perfect lift every time.",
            "reliability": "Never missed a delivery in 5 years. They're our most dependable supplier.",
        },
        "order_accuracy": 99.0,
        "avg_delivery_days": 2,
        "years_in_business": 41,
    },
    {
        "vendor_name": "Pure Soda Supply",
        "product": "baking soda",
        "price_per_unit": 0.85,
        "unit": "lb",
        "distance_miles": 40,
        "quality_score": 90,
        "reliability_score": 95,
        "certifications": ["USP Grade", "Non-GMO"],
        "description": "USP-grade baking soda for professional baking. Consistent purity.",
        "reviews": {
            "quality": "Solid quality that meets professional bakery standards. Pharmaceutical grade.",
            "reliability": "Clockwork reliability - deliveries always arrive on time, properly packaged.",
        },
        "order_accuracy": 98.5,
        "avg_delivery_days": 2,
        "years_in_business": 58,
    },

    # === SPICE VENDORS ===
    {
        "vendor_name": "Spice Route Imports",
        "product": "cinnamon",
        "price_per_unit": 12.00,
        "unit": "lb",
        "distance_miles": 145,
        "quality_score": 98,
        "reliability_score": 85,
        "certifications": ["Ceylon", "Organic", "Fair Trade"],
        "description": "True Ceylon cinnamon from Sri Lanka. Delicate, complex flavor.",
        "reviews": {
            "quality": "Best quality we've found in 15 years of baking. True Ceylon makes all the difference.",
            "reliability": "Sometimes reliable, sometimes not. Import delays common. Worth the wait.",
        },
        "order_accuracy": 92.0,
        "avg_delivery_days": 7,
        "years_in_business": 31,
    },
    {
        "vendor_name": "Bakers Spice Co",
        "product": "spices",
        "price_per_unit": 8.50,
        "unit": "lb",
        "distance_miles": 60,
        "quality_score": 89,
        "reliability_score": 94,
        "certifications": ["Non-Irradiated", "Non-GMO"],
        "description": "Complete line of baking spices. Nutmeg, ginger, cardamom, and more.",
        "reviews": {
            "quality": "Good quality for commercial baking. Fresh enough for our needs.",
            "reliability": "Outstanding track record - zero delivery failures in hundreds of orders.",
        },
        "order_accuracy": 97.5,
        "avg_delivery_days": 3,
        "years_in_business": 46,
    },
    {
        "vendor_name": "Ginger Gold Imports",
        "product": "ginger",
        "price_per_unit": 9.00,
        "unit": "lb",
        "distance_miles": 130,
        "quality_score": 94,
        "reliability_score": 88,
        "certifications": ["Organic", "Fair Trade"],
        "description": "Ground ginger and crystallized ginger. Spicy and aromatic.",
        "reviews": {
            "quality": "Top-tier supplier with impeccable quality standards. Intense ginger heat.",
            "reliability": "Good track record with delivery. Issues are handled professionally.",
        },
        "order_accuracy": 95.0,
        "avg_delivery_days": 5,
        "years_in_business": 23,
    },

    # === DRIED FRUIT VENDORS ===
    {
        "vendor_name": "Sun Valley Raisins",
        "product": "raisins",
        "price_per_unit": 3.50,
        "unit": "lb",
        "distance_miles": 95,
        "quality_score": 88,
        "reliability_score": 93,
        "certifications": ["California Grown", "Non-GMO"],
        "description": "California sun-dried raisins. Plump and sweet for breads and cookies.",
        "reviews": {
            "quality": "Solid quality that meets professional bakery standards. Good moisture content.",
            "reliability": "Reliable delivery schedule with good communication when issues arise.",
        },
        "order_accuracy": 96.5,
        "avg_delivery_days": 3,
        "years_in_business": 64,
    },
    {
        "vendor_name": "Dried Fruit Warehouse",
        "product": "cranberries",
        "price_per_unit": 5.25,
        "unit": "lb",
        "distance_miles": 110,
        "quality_score": 86,
        "reliability_score": 94,
        "certifications": ["Non-GMO", "No Preservatives"],
        "description": "Dried cranberries with reduced sugar options. Perfect for scones.",
        "reviews": {
            "quality": "Above average quality with reasonable pricing. Works well for our mid-range products.",
            "reliability": "Dependability is their hallmark. Weather, holidays, nothing stops them.",
        },
        "order_accuracy": 97.0,
        "avg_delivery_days": 4,
        "years_in_business": 28,
    },

    # === SALT VENDORS ===
    {
        "vendor_name": "Artisan Salt Company",
        "product": "sea salt",
        "price_per_unit": 4.50,
        "unit": "lb",
        "distance_miles": 85,
        "quality_score": 96,
        "reliability_score": 91,
        "certifications": ["Hand-Harvested", "Unrefined"],
        "description": "Hand-harvested sea salt from California coast. Mineral-rich and flaky.",
        "reviews": {
            "quality": "Exceptional quality that consistently exceeds expectations. Adds complexity.",
            "reliability": "Generally reliable with occasional minor delays communicated in advance.",
        },
        "order_accuracy": 96.0,
        "avg_delivery_days": 4,
        "years_in_business": 17,
    },
    {
        "vendor_name": "Commercial Salt Supply",
        "product": "salt",
        "price_per_unit": 0.35,
        "unit": "lb",
        "distance_miles": 50,
        "quality_score": 82,
        "reliability_score": 97,
        "certifications": ["Food Grade", "Kosher"],
        "description": "Food-grade salt for commercial baking operations. Consistent quality.",
        "reviews": {
            "quality": "Quality meets expectations for commercial baking. Standard table salt.",
            "reliability": "Most reliable supplier we work with. Emergency orders handled without fail.",
        },
        "order_accuracy": 99.0,
        "avg_delivery_days": 2,
        "years_in_business": 75,
    },
]


def _get_exa_client():
    """Get Exa.ai client."""
    if not EXA_API_KEY:
        return None
    try:
        from exa_py import Exa
        return Exa(api_key=EXA_API_KEY)
    except:
        return None


def search_bakery_vendors(ingredient: str, location: str = "California", num_results: int = 5) -> list[dict]:
    """Search for bakery ingredient vendors using Exa.ai or sample data."""
    client = _get_exa_client()

    if client:
        try:
            query = f"wholesale {ingredient} supplier for bakeries in {location}"
            results = client.search_and_contents(query=query, type="neural", num_results=num_results, text=True)
            vendors = []
            for i, result in enumerate(results.results):
                vendors.append({
                    "vendor_id": f"exa_{ingredient}_{i}",
                    "vendor_name": result.title or f"{ingredient.title()} Supplier {i+1}",
                    "product": ingredient,
                    "price_per_unit": random.uniform(0.5, 20.0),
                    "unit": "lb",
                    "distance_miles": random.randint(10, 150),
                    "quality_score": random.randint(70, 98),
                    "reliability_score": random.randint(70, 98),
                    "certifications": [],
                    "website": result.url,
                    "description": (result.text or "")[:300],
                })
            return vendors
        except Exception as e:
            logger.warning(f"Exa search failed: {e}")

    # Return filtered sample data
    return [
        {**v, "vendor_id": f"sample_{v['vendor_name'].lower().replace(' ', '_')}"}
        for v in SAMPLE_VENDORS
        if v["product"] == ingredient or ingredient in v["product"]
    ]


def generate_training_data(num_examples: int = 1000) -> list[dict]:
    """
    Generate comprehensive training data for Voyage AI fine-tuning.

    Creates 1000 preference triplets focused on quality and reliability
    for bakery ingredient evaluation.

    Args:
        num_examples: Number of training examples (default 1000)

    Returns:
        List of training examples in {query, positive, negative} format
    """
    training_data = []
    vendors = [{**v, "vendor_id": f"v_{i}"} for i, v in enumerate(SAMPLE_VENDORS)]

    def format_vendor_detailed(v: dict) -> str:
        """Format vendor with detailed reviews for training."""
        certs = ", ".join(v.get("certifications", [])) or "None"
        reviews = v.get("reviews", {})
        quality_review = reviews.get("quality", v.get("description", "No quality review available."))
        reliability_review = reviews.get("reliability", "No reliability review available.")

        return f"""
Vendor: {v['vendor_name']}
Product: {v['product']}
Quality Score: {v['quality_score']}/100
Reliability Score: {v['reliability_score']}/100
Price: ${v['price_per_unit']:.2f}/{v['unit']}
Distance: {v['distance_miles']} miles
Years in Business: {v.get('years_in_business', 'N/A')}
Order Accuracy: {v.get('order_accuracy', 'N/A')}%
Avg Delivery: {v.get('avg_delivery_days', 'N/A')} days
Certifications: {certs}

Quality Review: {quality_review}

Reliability Review: {reliability_review}
""".strip()

    # Define comprehensive query templates focused on quality and reliability
    quality_queries = [
        "Best quality {ingredient} supplier for premium artisan bakery",
        "Highest quality {ingredient} for award-winning pastry shop",
        "Top-rated {ingredient} supplier with excellent product quality",
        "Premium {ingredient} vendor for fine dining dessert production",
        "Superior quality {ingredient} for competition-level baking",
        "{ingredient} supplier with best quality reviews and ratings",
        "Exceptional {ingredient} quality for luxury bakery items",
        "Gold standard {ingredient} supplier for pastry perfection",
        "Best-in-class {ingredient} for professional baking excellence",
        "Highest rated {ingredient} vendor for quality-focused bakery",
        "Premium artisan {ingredient} for craft bakery production",
        "Top quality {ingredient} with consistent excellence",
        "Superior {ingredient} supplier for demanding pastry chefs",
        "Best quality {ingredient} regardless of price",
        "Elite {ingredient} vendor for premium baked goods",
    ]

    reliability_queries = [
        "Most reliable {ingredient} supplier for consistent bakery production",
        "Dependable {ingredient} vendor with perfect delivery record",
        "Trusted {ingredient} supplier that never misses deliveries",
        "Consistent {ingredient} supply for uninterrupted bakery operations",
        "Reliable {ingredient} vendor for daily bakery needs",
        "{ingredient} supplier with best on-time delivery history",
        "Most dependable {ingredient} source for production schedule",
        "Rock-solid {ingredient} supplier for reliable supply chain",
        "Trustworthy {ingredient} vendor for time-sensitive orders",
        "Consistent {ingredient} supplier for scheduled production runs",
        "Reliable {ingredient} with excellent order accuracy",
        "Dependable {ingredient} delivery for bakery operations",
        "Never-fail {ingredient} supplier for peace of mind",
        "Most consistent {ingredient} vendor in the region",
        "Reliable {ingredient} supply regardless of season",
    ]

    combined_queries = [
        "Best {ingredient} supplier balancing quality and reliability",
        "Top {ingredient} vendor for quality products with reliable delivery",
        "Premium {ingredient} supplier with dependable service",
        "High-quality {ingredient} vendor with excellent track record",
        "Best overall {ingredient} supplier for professional bakery",
        "Quality {ingredient} with consistent reliable delivery",
        "Top-rated {ingredient} for both product and service excellence",
        "Best {ingredient} vendor for discerning professional bakers",
        "Premium reliable {ingredient} supplier for serious bakeries",
        "Excellent {ingredient} quality and delivery performance",
    ]

    budget_quality_queries = [
        "Best {ingredient} quality at competitive prices",
        "Value {ingredient} supplier without compromising quality",
        "Affordable quality {ingredient} for growing bakery",
        "Budget-friendly {ingredient} with acceptable quality",
        "Cost-effective {ingredient} supplier maintaining standards",
    ]

    local_reliable_queries = [
        "Local {ingredient} supplier with reliable delivery",
        "Nearby {ingredient} vendor with good reliability",
        "Regional {ingredient} supplier with consistent service",
        "Close {ingredient} source with dependable delivery",
    ]

    # Generate quality-focused examples (40% of total)
    quality_examples = int(num_examples * 0.4)
    for i in range(quality_examples):
        ingredient = random.choice(BAKERY_INGREDIENTS)
        query_template = random.choice(quality_queries)
        query = query_template.format(ingredient=ingredient)

        # Sort vendors by quality for this ingredient type
        relevant_vendors = [v for v in vendors if ingredient in v["product"] or v["product"] in ingredient]
        if len(relevant_vendors) < 2:
            relevant_vendors = vendors

        sorted_by_quality = sorted(relevant_vendors, key=lambda x: x["quality_score"], reverse=True)

        if len(sorted_by_quality) >= 2:
            # Pick from top for positive, bottom for negative
            top_idx = min(i % 3, len(sorted_by_quality) - 1)
            bottom_idx = max(len(sorted_by_quality) - 1 - (i % 3), 0)
            if top_idx != bottom_idx:
                training_data.append({
                    "query": query,
                    "positive": format_vendor_detailed(sorted_by_quality[top_idx]),
                    "negative": format_vendor_detailed(sorted_by_quality[bottom_idx]),
                })

    # Generate reliability-focused examples (40% of total)
    reliability_examples = int(num_examples * 0.4)
    for i in range(reliability_examples):
        ingredient = random.choice(BAKERY_INGREDIENTS)
        query_template = random.choice(reliability_queries)
        query = query_template.format(ingredient=ingredient)

        relevant_vendors = [v for v in vendors if ingredient in v["product"] or v["product"] in ingredient]
        if len(relevant_vendors) < 2:
            relevant_vendors = vendors

        sorted_by_reliability = sorted(relevant_vendors, key=lambda x: x["reliability_score"], reverse=True)

        if len(sorted_by_reliability) >= 2:
            top_idx = min(i % 3, len(sorted_by_reliability) - 1)
            bottom_idx = max(len(sorted_by_reliability) - 1 - (i % 3), 0)
            if top_idx != bottom_idx:
                training_data.append({
                    "query": query,
                    "positive": format_vendor_detailed(sorted_by_reliability[top_idx]),
                    "negative": format_vendor_detailed(sorted_by_reliability[bottom_idx]),
                })

    # Generate combined quality+reliability examples (15% of total)
    combined_examples = int(num_examples * 0.15)
    for i in range(combined_examples):
        ingredient = random.choice(BAKERY_INGREDIENTS)
        query_template = random.choice(combined_queries)
        query = query_template.format(ingredient=ingredient)

        relevant_vendors = [v for v in vendors if ingredient in v["product"] or v["product"] in ingredient]
        if len(relevant_vendors) < 2:
            relevant_vendors = vendors

        # Score by combined quality and reliability
        sorted_combined = sorted(
            relevant_vendors,
            key=lambda x: x["quality_score"] * 0.5 + x["reliability_score"] * 0.5,
            reverse=True
        )

        if len(sorted_combined) >= 2:
            training_data.append({
                "query": query,
                "positive": format_vendor_detailed(sorted_combined[0]),
                "negative": format_vendor_detailed(sorted_combined[-1]),
            })

    # Generate remaining mixed examples
    while len(training_data) < num_examples:
        ingredient = random.choice(BAKERY_INGREDIENTS)

        # Randomly select query type
        query_type = random.choice(["quality", "reliability", "combined", "budget", "local"])

        if query_type == "quality":
            query = random.choice(quality_queries).format(ingredient=ingredient)
            sort_key = lambda x: x["quality_score"]
        elif query_type == "reliability":
            query = random.choice(reliability_queries).format(ingredient=ingredient)
            sort_key = lambda x: x["reliability_score"]
        elif query_type == "budget":
            query = random.choice(budget_quality_queries).format(ingredient=ingredient)
            sort_key = lambda x: x["quality_score"] * 0.6 - x["price_per_unit"] * 2
        elif query_type == "local":
            query = random.choice(local_reliable_queries).format(ingredient=ingredient)
            sort_key = lambda x: x["reliability_score"] * 0.6 - x["distance_miles"] * 0.1
        else:
            query = random.choice(combined_queries).format(ingredient=ingredient)
            sort_key = lambda x: x["quality_score"] * 0.5 + x["reliability_score"] * 0.5

        v1, v2 = random.sample(vendors, 2)
        better = v1 if sort_key(v1) > sort_key(v2) else v2
        worse = v2 if better == v1 else v1

        training_data.append({
            "query": query,
            "positive": format_vendor_detailed(better),
            "negative": format_vendor_detailed(worse),
        })

    logger.info(f"Generated {len(training_data)} training examples for bakery vendor evaluation")
    return training_data[:num_examples]


def get_sample_vendors() -> list[dict]:
    """Get sample bakery vendors for testing."""
    return [{**v, "vendor_id": f"sample_{i}"} for i, v in enumerate(SAMPLE_VENDORS)]
