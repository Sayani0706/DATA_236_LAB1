import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models.user import User
from app.models.restaurant import Restaurant
from app.models.review import Review
from app.models.preferences import UserPreference
from app.utils.auth import hash_password
import random

db = SessionLocal()

def seed():
    users_data = [
        {"name": "Alice Johnson", "email": "alice@example.com", "password": "pass123", "role": "user", "city": "San Jose", "state": "CA", "country": "United States", "gender": "Female", "languages": "English"},
        {"name": "Bob Smith", "email": "bob@example.com", "password": "pass123", "role": "user", "city": "San Francisco", "state": "CA", "country": "United States", "gender": "Male", "languages": "English, Spanish"},
        {"name": "Emily Chen", "email": "emily@example.com", "password": "pass123", "role": "user", "city": "San Jose", "state": "CA", "country": "United States", "gender": "Female", "languages": "English, Chinese"},
        {"name": "James Wilson", "email": "james@example.com", "password": "pass123", "role": "user", "city": "Oakland", "state": "CA", "country": "United States", "gender": "Male", "languages": "English"},
        {"name": "Sofia Martinez", "email": "sofia@example.com", "password": "pass123", "role": "user", "city": "San Jose", "state": "CA", "country": "United States", "gender": "Female", "languages": "English, Spanish"},
        {"name": "Carol White", "email": "carol@example.com", "password": "pass123", "role": "owner", "city": "San Jose", "state": "CA", "country": "United States", "gender": "Female", "languages": "English"},
        {"name": "David Lee", "email": "david@example.com", "password": "pass123", "role": "owner", "city": "San Francisco", "state": "CA", "country": "United States", "gender": "Male", "languages": "English, Chinese"},
        {"name": "Raj Patel", "email": "raj@example.com", "password": "pass123", "role": "owner", "city": "San Jose", "state": "CA", "country": "United States", "gender": "Male", "languages": "English, Hindi"},
        {"name": "Maria Garcia", "email": "maria@example.com", "password": "pass123", "role": "owner", "city": "Oakland", "state": "CA", "country": "United States", "gender": "Female", "languages": "English, Spanish"},
    ]

    users = []
    for u in users_data:
        existing = db.query(User).filter(User.email == u["email"]).first()
        if not existing:
            user = User(name=u["name"], email=u["email"], password=hash_password(u["password"]), role=u["role"], city=u["city"], state=u["state"], country=u["country"], gender=u["gender"], languages=u["languages"])
            db.add(user)
            db.commit()
            db.refresh(user)
            users.append(user)
        else:
            users.append(existing)

    prefs_data = [
        {"user_id": users[0].id, "cuisines": "Italian, Mexican", "price_range": "$$", "location": "San Jose, CA", "search_radius": 10, "dietary_needs": "none", "ambiance": "casual", "sort_preference": "rating"},
        {"user_id": users[1].id, "cuisines": "Chinese, Japanese", "price_range": "$$$", "location": "San Francisco, CA", "search_radius": 15, "dietary_needs": "vegetarian", "ambiance": "fine dining", "sort_preference": "popularity"},
        {"user_id": users[2].id, "cuisines": "Korean, Japanese", "price_range": "$$", "location": "San Jose, CA", "search_radius": 10, "dietary_needs": "none", "ambiance": "casual", "sort_preference": "rating"},
        {"user_id": users[3].id, "cuisines": "American, Italian", "price_range": "$", "location": "Oakland, CA", "search_radius": 5, "dietary_needs": "none", "ambiance": "casual", "sort_preference": "price"},
        {"user_id": users[4].id, "cuisines": "Mexican, Mediterranean", "price_range": "$$", "location": "San Jose, CA", "search_radius": 10, "dietary_needs": "vegetarian", "ambiance": "family-friendly", "sort_preference": "rating"},
    ]

    for p in prefs_data:
        existing = db.query(UserPreference).filter(UserPreference.user_id == p["user_id"]).first()
        if not existing:
            db.add(UserPreference(**p))
    db.commit()

    owner_ids = [users[5].id, users[6].id, users[7].id, users[8].id]

    restaurants_data = [
        {"name": "Pasta Paradise", "cuisine_type": "Italian", "address": "123 Main St", "city": "San Jose", "state": "CA", "zip": "95101", "description": "Authentic Italian pasta and wood-fired pizzas in a cozy setting", "hours": "Mon-Sun 11am-10pm", "contact": "408-111-2222", "pricing_tier": "$$", "amenities": "wifi, outdoor seating, romantic"},
        {"name": "Trattoria Roma", "cuisine_type": "Italian", "address": "456 Oak Ave", "city": "San Jose", "state": "CA", "zip": "95112", "description": "Family-owned Italian trattoria serving classic Roman dishes since 1995", "hours": "Tue-Sun 12pm-9pm", "contact": "408-222-3333", "pricing_tier": "$$", "amenities": "family-friendly, parking, wine bar"},
        {"name": "La Bella Italia", "cuisine_type": "Italian", "address": "789 Vineyard Rd", "city": "San Francisco", "state": "CA", "zip": "94102", "description": "Northern Italian cuisine with handmade pasta and seasonal ingredients", "hours": "Mon-Sat 5pm-11pm", "contact": "415-111-2222", "pricing_tier": "$$$", "amenities": "romantic, fine dining, wine cellar"},
        {"name": "Pizzeria Napoli", "cuisine_type": "Italian", "address": "321 Napoli Ln", "city": "San Jose", "state": "CA", "zip": "95128", "description": "Authentic Neapolitan pizza baked in a traditional wood-fired oven", "hours": "Mon-Sun 11am-11pm", "contact": "408-333-4444", "pricing_tier": "$", "amenities": "casual, takeout, delivery, family-friendly"},
        {"name": "Osteria Firenze", "cuisine_type": "Italian", "address": "654 Florence St", "city": "Oakland", "state": "CA", "zip": "94601", "description": "Tuscan-inspired dishes with fresh truffles and premium Italian wines", "hours": "Tue-Sun 5pm-10pm", "contact": "510-111-2222", "pricing_tier": "$$$", "amenities": "fine dining, romantic, reservations required"},
        {"name": "Mama Mia Kitchen", "cuisine_type": "Italian", "address": "987 Oregano Blvd", "city": "San Jose", "state": "CA", "zip": "95110", "description": "Home-style Italian cooking with generous portions and warm hospitality", "hours": "Mon-Sun 10am-10pm", "contact": "408-444-5555", "pricing_tier": "$", "amenities": "casual, family-friendly, takeout, delivery"},
        {"name": "Ristorante Milano", "cuisine_type": "Italian", "address": "159 Milano Ave", "city": "San Francisco", "state": "CA", "zip": "94103", "description": "Upscale Milanese cuisine with an extensive pasta and risotto menu", "hours": "Mon-Sat 5:30pm-11pm", "contact": "415-222-3333", "pricing_tier": "$$$", "amenities": "fine dining, romantic, wine bar"},
        {"name": "Dragon Palace", "cuisine_type": "Chinese", "address": "789 Elm St", "city": "San Francisco", "state": "CA", "zip": "94102", "description": "Traditional Chinese cuisine with dim sum and Cantonese specialties", "hours": "Mon-Sun 10am-11pm", "contact": "415-333-4444", "pricing_tier": "$", "amenities": "family-friendly, takeout, delivery"},
        {"name": "Golden Phoenix", "cuisine_type": "Chinese", "address": "258 Lotus Ave", "city": "San Jose", "state": "CA", "zip": "95116", "description": "Authentic Cantonese seafood and dim sum in a spacious dining hall", "hours": "Mon-Sun 9am-10pm", "contact": "408-555-6666", "pricing_tier": "$$", "amenities": "family-friendly, parking, dim sum"},
        {"name": "Szechuan House", "cuisine_type": "Chinese", "address": "357 Spice Rd", "city": "San Jose", "state": "CA", "zip": "95122", "description": "Bold and spicy Szechuan dishes with authentic flavors from Chengdu", "hours": "Mon-Sun 11am-10pm", "contact": "408-666-7777", "pricing_tier": "$", "amenities": "casual, takeout, delivery"},
        {"name": "Jade Garden", "cuisine_type": "Chinese", "address": "486 Bamboo St", "city": "San Francisco", "state": "CA", "zip": "94108", "description": "Elegant Shanghainese cuisine with xiaolongbao and delicate stir-fries", "hours": "Tue-Sun 11:30am-10pm", "contact": "415-444-5555", "pricing_tier": "$$", "amenities": "casual, romantic, reservations"},
        {"name": "Peking Duck House", "cuisine_type": "Chinese", "address": "741 Beijing Blvd", "city": "Oakland", "state": "CA", "zip": "94602", "description": "Specializing in crispy Peking duck and northern Chinese specialties", "hours": "Mon-Sun 11am-10pm", "contact": "510-222-3333", "pricing_tier": "$$", "amenities": "family-friendly, group dining, parking"},
        {"name": "Wonton Noodle Shop", "cuisine_type": "Chinese", "address": "852 Noodle Lane", "city": "San Jose", "state": "CA", "zip": "95113", "description": "Hong Kong style wonton noodles and congee served all day", "hours": "Mon-Sun 7am-9pm", "contact": "408-777-8888", "pricing_tier": "$", "amenities": "casual, takeout, breakfast"},
        {"name": "Sakura Garden", "cuisine_type": "Japanese", "address": "321 Pine St", "city": "San Francisco", "state": "CA", "zip": "94103", "description": "Premium sushi and Japanese kaiseki cuisine in an elegant atmosphere", "hours": "Mon-Sat 5pm-11pm", "contact": "415-444-5555", "pricing_tier": "$$$", "amenities": "fine dining, sake bar, romantic"},
        {"name": "Ramen Republic", "cuisine_type": "Japanese", "address": "963 Broth Blvd", "city": "San Jose", "state": "CA", "zip": "95129", "description": "Rich tonkotsu and miso ramen with slow-cooked broths and fresh toppings", "hours": "Mon-Sun 11am-11pm", "contact": "408-888-9999", "pricing_tier": "$", "amenities": "casual, takeout, late night"},
        {"name": "Tokyo Sushi Bar", "cuisine_type": "Japanese", "address": "147 Sushi St", "city": "San Francisco", "state": "CA", "zip": "94104", "description": "Omakase and a la carte sushi with fresh fish flown in daily from Japan", "hours": "Tue-Sun 5:30pm-11pm", "contact": "415-555-6666", "pricing_tier": "$$$", "amenities": "fine dining, omakase, sake bar, romantic"},
        {"name": "Izakaya Yuki", "cuisine_type": "Japanese", "address": "369 Sake Ave", "city": "San Jose", "state": "CA", "zip": "95126", "description": "Lively Japanese gastropub with yakitori, small plates and Japanese whisky", "hours": "Mon-Sun 5pm-12am", "contact": "408-999-0000", "pricing_tier": "$$", "amenities": "lively, casual, late night, sake bar"},
        {"name": "Tempura Zen", "cuisine_type": "Japanese", "address": "258 Crispy Rd", "city": "Oakland", "state": "CA", "zip": "94603", "description": "Specializing in light and crispy tempura and Japanese set meals", "hours": "Tue-Sun 11:30am-9:30pm", "contact": "510-333-4444", "pricing_tier": "$$", "amenities": "casual, family-friendly, parking"},
        {"name": "Taco Fiesta", "cuisine_type": "Mexican", "address": "654 Maple Ave", "city": "San Jose", "state": "CA", "zip": "95110", "description": "Authentic street tacos and traditional Mexican dishes with vibrant atmosphere", "hours": "Mon-Sun 9am-10pm", "contact": "408-555-6666", "pricing_tier": "$", "amenities": "casual, outdoor seating, family-friendly"},
        {"name": "Casa Mexicana", "cuisine_type": "Mexican", "address": "741 Fiesta Rd", "city": "San Francisco", "state": "CA", "zip": "94105", "description": "Upscale Mexican cuisine with modern interpretations of classic dishes", "hours": "Mon-Sun 11am-10pm", "contact": "415-666-7777", "pricing_tier": "$$", "amenities": "casual, margarita bar, outdoor seating"},
        {"name": "El Rancho Grill", "cuisine_type": "Mexican", "address": "852 Tortilla Blvd", "city": "San Jose", "state": "CA", "zip": "95111", "description": "Ranch-style Mexican BBQ with slow-cooked meats and fresh salsas", "hours": "Mon-Sun 10am-10pm", "contact": "408-101-2020", "pricing_tier": "$", "amenities": "casual, takeout, parking, family-friendly"},
        {"name": "Guadalajara Kitchen", "cuisine_type": "Mexican", "address": "963 Jalisco St", "city": "Oakland", "state": "CA", "zip": "94604", "description": "Western Mexican cuisine featuring birria, tortas ahogadas and tejuino", "hours": "Mon-Sun 8am-9pm", "contact": "510-444-5555", "pricing_tier": "$", "amenities": "casual, takeout, breakfast, family-friendly"},
        {"name": "Hacienda Real", "cuisine_type": "Mexican", "address": "123 Adobe Lane", "city": "San Jose", "state": "CA", "zip": "95127", "description": "Refined Mexican hacienda-style dining with premium tequilas and mezcals", "hours": "Tue-Sun 4pm-11pm", "contact": "408-202-3030", "pricing_tier": "$$$", "amenities": "fine dining, tequila bar, romantic, reservations"},
        {"name": "Spice Route", "cuisine_type": "Indian", "address": "258 Saffron St", "city": "San Jose", "state": "CA", "zip": "95116", "description": "Rich and aromatic Indian curries and tandoor specialties from North and South India", "hours": "Mon-Sun 11:30am-10pm", "contact": "408-888-9999", "pricing_tier": "$$", "amenities": "halal, vegetarian options, family-friendly"},
        {"name": "Taj Mahal Dining", "cuisine_type": "Indian", "address": "357 Curry Ave", "city": "San Francisco", "state": "CA", "zip": "94107", "description": "Royal Mughlai cuisine with rich curries, kebabs and freshly baked naan", "hours": "Mon-Sun 12pm-10pm", "contact": "415-777-8888", "pricing_tier": "$$", "amenities": "halal, vegetarian, family-friendly, delivery"},
        {"name": "Chennai Express", "cuisine_type": "Indian", "address": "486 Dosa Blvd", "city": "San Jose", "state": "CA", "zip": "95117", "description": "Authentic South Indian dosas, idlis and filter coffee in a casual setting", "hours": "Mon-Sun 8am-9pm", "contact": "408-303-4040", "pricing_tier": "$", "amenities": "vegetarian, vegan options, casual, takeout"},
        {"name": "Punjab Palace", "cuisine_type": "Indian", "address": "741 Tandoor Rd", "city": "Oakland", "state": "CA", "zip": "94605", "description": "Hearty Punjabi dishes with clay oven breads and signature butter chicken", "hours": "Mon-Sun 11am-10pm", "contact": "510-555-6666", "pricing_tier": "$$", "amenities": "halal, family-friendly, delivery, parking"},
        {"name": "Bombay Bistro", "cuisine_type": "Indian", "address": "852 Mumbai Lane", "city": "San Francisco", "state": "CA", "zip": "94109", "description": "Modern Indian street food inspired by the flavors of Mumbai", "hours": "Mon-Sun 11am-10pm", "contact": "415-888-9999", "pricing_tier": "$", "amenities": "casual, takeout, delivery, vegan options"},
        {"name": "Seoul Kitchen", "cuisine_type": "Korean", "address": "369 Kimchi Blvd", "city": "San Francisco", "state": "CA", "zip": "94105", "description": "Authentic Korean BBQ and traditional dishes in a lively social setting", "hours": "Mon-Sun 12pm-12am", "contact": "415-999-0000", "pricing_tier": "$$", "amenities": "bbq, casual, lively, group dining"},
        {"name": "K-BBQ House", "cuisine_type": "Korean", "address": "147 Bulgogi St", "city": "San Jose", "state": "CA", "zip": "95118", "description": "All-you-can-eat Korean BBQ with premium cuts and unlimited banchan", "hours": "Mon-Sun 11:30am-11pm", "contact": "408-404-5050", "pricing_tier": "$$", "amenities": "bbq, group dining, lively, casual"},
        {"name": "Bibimbap Corner", "cuisine_type": "Korean", "address": "258 Hanok Rd", "city": "San Jose", "state": "CA", "zip": "95119", "description": "Cozy Korean spot known for stone pot bibimbap and comforting soups", "hours": "Mon-Sat 11am-9pm", "contact": "408-505-6060", "pricing_tier": "$", "amenities": "casual, takeout, vegetarian options"},
        {"name": "Gangnam Eats", "cuisine_type": "Korean", "address": "963 Seoul Ave", "city": "San Francisco", "state": "CA", "zip": "94110", "description": "Trendy Korean fusion restaurant with modern takes on classic Korean dishes", "hours": "Mon-Sun 12pm-11pm", "contact": "415-101-1111", "pricing_tier": "$$", "amenities": "lively, casual, delivery"},
        {"name": "Green Leaf Cafe", "cuisine_type": "American", "address": "987 Cedar Rd", "city": "San Jose", "state": "CA", "zip": "95128", "description": "100% vegan menu with fresh organic ingredients and casual atmosphere", "hours": "Mon-Fri 8am-8pm, Sat-Sun 9am-7pm", "contact": "408-666-7777", "pricing_tier": "$", "amenities": "vegan, vegetarian, gluten-free, casual, wifi"},
        {"name": "Sunset Terrace", "cuisine_type": "American", "address": "741 Hilltop Dr", "city": "San Francisco", "state": "CA", "zip": "94107", "description": "Stunning rooftop restaurant with panoramic city views and modern American cuisine", "hours": "Mon-Sun 4pm-11pm", "contact": "415-101-2020", "pricing_tier": "$$$", "amenities": "outdoor seating, romantic, views, cocktail bar"},
        {"name": "Veggie Delight", "cuisine_type": "American", "address": "852 Garden Way", "city": "San Jose", "state": "CA", "zip": "95126", "description": "Creative plant-based dishes with extensive vegan and vegetarian options", "hours": "Mon-Sat 10am-9pm", "contact": "408-202-3030", "pricing_tier": "$$", "amenities": "vegan, vegetarian, gluten-free, casual, wifi"},
        {"name": "The Burger Joint", "cuisine_type": "American", "address": "963 Burger Blvd", "city": "San Jose", "state": "CA", "zip": "95129", "description": "Juicy handcrafted burgers with locally sourced beef and creative toppings", "hours": "Mon-Sun 11am-11pm", "contact": "408-303-4040", "pricing_tier": "$", "amenities": "casual, family-friendly, takeout, delivery, wifi"},
        {"name": "Smokehouse BBQ", "cuisine_type": "American", "address": "159 Hickory Lane", "city": "Oakland", "state": "CA", "zip": "94606", "description": "Slow-smoked meats with house-made sauces and Southern-style sides", "hours": "Mon-Sun 11am-10pm", "contact": "510-666-7777", "pricing_tier": "$$", "amenities": "casual, family-friendly, parking, takeout"},
        {"name": "The Diner", "cuisine_type": "American", "address": "357 Classic Ave", "city": "San Jose", "state": "CA", "zip": "95130", "description": "Classic American diner with all-day breakfast, burgers and milkshakes", "hours": "Mon-Sun 6am-11pm", "contact": "408-606-7070", "pricing_tier": "$", "amenities": "casual, breakfast, family-friendly, takeout"},
        {"name": "Farm to Table", "cuisine_type": "American", "address": "486 Organic Blvd", "city": "San Francisco", "state": "CA", "zip": "94111", "description": "Seasonally inspired menu featuring locally sourced organic produce and meats", "hours": "Tue-Sun 5pm-10pm", "contact": "415-202-3030", "pricing_tier": "$$$", "amenities": "fine dining, organic, romantic, wine pairing"},
        {"name": "Comfort Kitchen", "cuisine_type": "American", "address": "741 Homestyle Rd", "city": "Oakland", "state": "CA", "zip": "94607", "description": "Soul food and American comfort classics with generous portions", "hours": "Mon-Sun 9am-10pm", "contact": "510-777-8888", "pricing_tier": "$", "amenities": "casual, family-friendly, takeout, delivery"},
        {"name": "Candlelight Bistro", "cuisine_type": "French", "address": "147 Rosewood Ln", "city": "San Francisco", "state": "CA", "zip": "94104", "description": "Romantic French bistro with candlelit tables and classic French cuisine", "hours": "Tue-Sun 5pm-11pm", "contact": "415-777-8888", "pricing_tier": "$$$", "amenities": "romantic, fine dining, wine cellar"},
        {"name": "Cafe Paris", "cuisine_type": "French", "address": "258 Eiffel St", "city": "San Jose", "state": "CA", "zip": "95131", "description": "Casual French cafe serving crepes, croissants and French onion soup", "hours": "Mon-Sun 7am-9pm", "contact": "408-707-8080", "pricing_tier": "$$", "amenities": "casual, breakfast, outdoor seating, wifi"},
        {"name": "Le Petit Chef", "cuisine_type": "French", "address": "369 Bordeaux Ave", "city": "San Francisco", "state": "CA", "zip": "94112", "description": "Intimate French restaurant with classic Lyonnaise dishes and exceptional wine list", "hours": "Tue-Sat 5:30pm-10pm", "contact": "415-303-4040", "pricing_tier": "$$$", "amenities": "fine dining, romantic, wine bar, reservations"},
        {"name": "Boulangerie Moderne", "cuisine_type": "French", "address": "963 Pastry Lane", "city": "Oakland", "state": "CA", "zip": "94608", "description": "Artisan French bakery and bistro serving fresh pastries and light lunch", "hours": "Mon-Sat 6:30am-7pm", "contact": "510-888-9999", "pricing_tier": "$", "amenities": "casual, breakfast, takeout, wifi"},
        {"name": "Pho Saigon", "cuisine_type": "Vietnamese", "address": "159 Mekong St", "city": "San Jose", "state": "CA", "zip": "95122", "description": "Authentic Vietnamese pho and banh mi in a warm and welcoming environment", "hours": "Mon-Sun 8am-9pm", "contact": "408-404-5050", "pricing_tier": "$", "amenities": "casual, takeout, delivery, family-friendly"},
        {"name": "Hanoi Kitchen", "cuisine_type": "Vietnamese", "address": "357 Halong Blvd", "city": "San Francisco", "state": "CA", "zip": "94113", "description": "Northern Vietnamese cuisine featuring bun cha, banh cuon and Vietnamese coffee", "hours": "Mon-Sun 9am-9pm", "contact": "415-404-5050", "pricing_tier": "$", "amenities": "casual, takeout, delivery"},
        {"name": "Saigon Nights", "cuisine_type": "Vietnamese", "address": "486 Ho Chi Minh Ave", "city": "San Jose", "state": "CA", "zip": "95123", "description": "Modern Vietnamese restaurant with creative fusion dishes and signature cocktails", "hours": "Mon-Sun 11am-11pm", "contact": "408-808-9090", "pricing_tier": "$$", "amenities": "casual, lively, cocktail bar, outdoor seating"},
        {"name": "Pho 99", "cuisine_type": "Vietnamese", "address": "741 Beef Broth Rd", "city": "Oakland", "state": "CA", "zip": "94609", "description": "No-frills pho shop with rich broths simmered for 24 hours", "hours": "Mon-Sun 7am-8pm", "contact": "510-999-0000", "pricing_tier": "$", "amenities": "casual, takeout, early morning"},
        {"name": "Mediterranean Breeze", "cuisine_type": "Mediterranean", "address": "357 Olive St", "city": "San Francisco", "state": "CA", "zip": "94108", "description": "Fresh Mediterranean mezze, grilled meats and seafood with a warm coastal vibe", "hours": "Mon-Sun 11am-10pm", "contact": "415-505-6060", "pricing_tier": "$$", "amenities": "outdoor seating, halal, healthy options, casual"},
        {"name": "Aegean Taverna", "cuisine_type": "Mediterranean", "address": "852 Santorini Blvd", "city": "San Jose", "state": "CA", "zip": "95132", "description": "Greek-inspired Mediterranean dining with fresh seafood and wood-fired dishes", "hours": "Mon-Sun 11:30am-10pm", "contact": "408-909-1010", "pricing_tier": "$$", "amenities": "casual, outdoor seating, family-friendly, parking"},
        {"name": "Mezze Lounge", "cuisine_type": "Mediterranean", "address": "963 Hummus Lane", "city": "San Francisco", "state": "CA", "zip": "94114", "description": "Trendy Mediterranean small plates bar with an extensive selection of mezze", "hours": "Mon-Sun 4pm-12am", "contact": "415-606-7070", "pricing_tier": "$$", "amenities": "casual, cocktail bar, lively, outdoor seating"},
        {"name": "Istanbul Grill", "cuisine_type": "Mediterranean", "address": "147 Ottoman Ave", "city": "Oakland", "state": "CA", "zip": "94610", "description": "Authentic Turkish grills, kebabs and baklava in a warm traditional setting", "hours": "Mon-Sun 11am-10pm", "contact": "510-101-2020", "pricing_tier": "$$", "amenities": "halal, family-friendly, casual, delivery"},
        {"name": "Thai Orchid", "cuisine_type": "Thai", "address": "486 Bangkok Ave", "city": "San Francisco", "state": "CA", "zip": "94109", "description": "Traditional Thai cuisine with rich curries, fresh pad thai and fragrant soups", "hours": "Tue-Sun 11am-10pm", "contact": "415-606-7070", "pricing_tier": "$$", "amenities": "vegetarian options, casual, delivery, takeout"},
        {"name": "Bangkok Garden", "cuisine_type": "Thai", "address": "258 Lemongrass Rd", "city": "San Jose", "state": "CA", "zip": "95133", "description": "Colorful Thai restaurant with street food favorites and Thai tea bar", "hours": "Mon-Sun 11am-10pm", "contact": "408-111-1212", "pricing_tier": "$", "amenities": "casual, takeout, delivery, vegan options"},
        {"name": "Lotus Thai Kitchen", "cuisine_type": "Thai", "address": "369 Jasmine Blvd", "city": "Oakland", "state": "CA", "zip": "94611", "description": "Family-run Thai kitchen with homestyle recipes passed down for generations", "hours": "Mon-Sat 11am-9pm", "contact": "510-212-3030", "pricing_tier": "$", "amenities": "casual, family-friendly, takeout, vegetarian"},
        {"name": "Siam Palace", "cuisine_type": "Thai", "address": "741 Royal Thai St", "city": "San Francisco", "state": "CA", "zip": "94115", "description": "Upscale Thai dining with royal Thai recipes and premium seafood dishes", "hours": "Tue-Sun 5pm-11pm", "contact": "415-707-8080", "pricing_tier": "$$$", "amenities": "fine dining, romantic, reservations, parking"},
        {"name": "Taqueria El Sol", "cuisine_type": "Mexican", "address": "852 Sunshine Blvd", "city": "San Jose", "state": "CA", "zip": "95134", "description": "Neighborhood taqueria with freshly made tortillas and traditional fillings", "hours": "Mon-Sun 7am-10pm", "contact": "408-313-4141", "pricing_tier": "$", "amenities": "casual, breakfast, takeout, family-friendly"},
        {"name": "Oaxaca Table", "cuisine_type": "Mexican", "address": "963 Mole Lane", "city": "San Francisco", "state": "CA", "zip": "94116", "description": "Specializing in Oaxacan cuisine including tlayudas, mole negro and mezcal cocktails", "hours": "Tue-Sun 12pm-10pm", "contact": "415-808-9090", "pricing_tier": "$$", "amenities": "casual, mezcal bar, vegetarian options"},
        {"name": "Pacific Grill", "cuisine_type": "American", "address": "159 Coastline Dr", "city": "San Francisco", "state": "CA", "zip": "94117", "description": "California-inspired seafood and grills with fresh locally caught fish", "hours": "Mon-Sun 11:30am-10pm", "contact": "415-909-1010", "pricing_tier": "$$$", "amenities": "seafood, outdoor seating, romantic, fine dining"},
        {"name": "The Breakfast Club", "cuisine_type": "American", "address": "357 Morning Ave", "city": "San Jose", "state": "CA", "zip": "95135", "description": "All-day breakfast haven with creative egg dishes, pancakes and fresh juices", "hours": "Mon-Sun 6am-3pm", "contact": "408-414-5151", "pricing_tier": "$", "amenities": "casual, breakfast, family-friendly, wifi"},
        {"name": "Steakhouse 101", "cuisine_type": "American", "address": "486 Prime Cut Rd", "city": "San Francisco", "state": "CA", "zip": "94118", "description": "Premium dry-aged steaks with classic sides and an extensive whiskey collection", "hours": "Mon-Sun 5pm-11pm", "contact": "415-010-1111", "pricing_tier": "$$$$", "amenities": "fine dining, romantic, whiskey bar, reservations"},
        {"name": "Wings and Things", "cuisine_type": "American", "address": "741 Crispy Blvd", "city": "Oakland", "state": "CA", "zip": "94612", "description": "Creative chicken wings with 20 plus sauces and a lively sports bar atmosphere", "hours": "Mon-Sun 11am-12am", "contact": "510-313-4141", "pricing_tier": "$", "amenities": "casual, sports bar, lively, takeout, delivery"},
        {"name": "Moroccan Nights", "cuisine_type": "Moroccan", "address": "852 Marrakech Rd", "city": "San Francisco", "state": "CA", "zip": "94119", "description": "Exotic Moroccan tagines, couscous and mint tea in a beautifully decorated setting", "hours": "Tue-Sun 5pm-11pm", "contact": "415-111-3131", "pricing_tier": "$$", "amenities": "romantic, halal, casual, group dining"},
        {"name": "Ethiopian Blue Nile", "cuisine_type": "Ethiopian", "address": "963 Injera St", "city": "Oakland", "state": "CA", "zip": "94613", "description": "Authentic Ethiopian stews and vegetarian dishes served on traditional injera bread", "hours": "Mon-Sun 11am-10pm", "contact": "510-414-5252", "pricing_tier": "$", "amenities": "vegan, vegetarian, halal, casual, family-friendly"},
        {"name": "Peruvian Kitchen", "cuisine_type": "Peruvian", "address": "147 Lima Ave", "city": "San Francisco", "state": "CA", "zip": "94120", "description": "Vibrant Peruvian cuisine with ceviche, lomo saltado and pisco sours", "hours": "Mon-Sun 12pm-10pm", "contact": "415-212-3232", "pricing_tier": "$$", "amenities": "casual, lively, cocktail bar, outdoor seating"},
        {"name": "Greek Islands", "cuisine_type": "Greek", "address": "258 Mykonos Blvd", "city": "San Jose", "state": "CA", "zip": "95136", "description": "Classic Greek dishes including moussaka, souvlaki and fresh Greek salads", "hours": "Mon-Sun 11am-10pm", "contact": "408-515-6262", "pricing_tier": "$$", "amenities": "casual, outdoor seating, family-friendly"},
        {"name": "Sushi Zen", "cuisine_type": "Japanese", "address": "369 Zen Garden Rd", "city": "San Jose", "state": "CA", "zip": "95137", "description": "Peaceful sushi restaurant with minimalist decor and traditional Japanese flavors", "hours": "Mon-Sun 11:30am-10pm", "contact": "408-616-7373", "pricing_tier": "$$", "amenities": "casual, romantic, sake bar, reservations"},
        {"name": "Brazilian Churrasco", "cuisine_type": "Brazilian", "address": "486 Copacabana Ave", "city": "San Francisco", "state": "CA", "zip": "94121", "description": "All-you-can-eat Brazilian rodizio with tableside carving and a full salad bar", "hours": "Mon-Sun 12pm-10pm", "contact": "415-313-4343", "pricing_tier": "$$$", "amenities": "group dining, family-friendly, casual, parking"},
        {"name": "Spanish Tapas Bar", "cuisine_type": "Spanish", "address": "741 Barcelona St", "city": "San Francisco", "state": "CA", "zip": "94122", "description": "Authentic Spanish tapas, paella and sangria in a lively social atmosphere", "hours": "Mon-Sun 4pm-12am", "contact": "415-414-5454", "pricing_tier": "$$", "amenities": "lively, casual, cocktail bar, group dining"},
        {"name": "Lebanese Cedar", "cuisine_type": "Lebanese", "address": "852 Beirut Blvd", "city": "San Jose", "state": "CA", "zip": "95138", "description": "Fresh Lebanese mezze, shawarma and grills with warm Middle Eastern hospitality", "hours": "Mon-Sun 11am-10pm", "contact": "408-717-8484", "pricing_tier": "$", "amenities": "halal, vegetarian, casual, takeout, delivery"},
        {"name": "Himalayan Kitchen", "cuisine_type": "Nepalese", "address": "963 Everest Rd", "city": "Oakland", "state": "CA", "zip": "94614", "description": "Nepalese and Tibetan dishes including momo dumplings, dal bhat and yak meat", "hours": "Tue-Sun 11am-9:30pm", "contact": "510-515-6565", "pricing_tier": "$", "amenities": "casual, vegetarian, halal, family-friendly"},
        {"name": "Caribbean Splash", "cuisine_type": "Caribbean", "address": "147 Reggae Ave", "city": "Oakland", "state": "CA", "zip": "94615", "description": "Vibrant Caribbean jerk chicken, rice and peas and tropical cocktails", "hours": "Mon-Sun 11am-10pm", "contact": "510-616-7676", "pricing_tier": "$", "amenities": "casual, lively, takeout, cocktail bar"},
        {"name": "German Bier Haus", "cuisine_type": "German", "address": "258 Bavaria St", "city": "San Francisco", "state": "CA", "zip": "94123", "description": "Authentic German sausages, schnitzel and pretzels with craft German beers on tap", "hours": "Mon-Sun 11am-12am", "contact": "415-515-6666", "pricing_tier": "$$", "amenities": "casual, beer garden, lively, group dining"},
        {"name": "Afghan Kabul", "cuisine_type": "Afghan", "address": "369 Kabul Lane", "city": "San Jose", "state": "CA", "zip": "95139", "description": "Traditional Afghan kabobs, mantu dumplings and qabili pulao rice dishes", "hours": "Mon-Sun 11am-10pm", "contact": "408-818-9595", "pricing_tier": "$", "amenities": "halal, casual, family-friendly, takeout"},
        {"name": "Fusion 360", "cuisine_type": "Fusion", "address": "486 Innovation Blvd", "city": "San Francisco", "state": "CA", "zip": "94124", "description": "Creative Asian-Western fusion cuisine with inventive cocktails and a modern vibe", "hours": "Mon-Sun 12pm-11pm", "contact": "415-616-7777", "pricing_tier": "$$$", "amenities": "lively, cocktail bar, romantic"},
        {"name": "Seafood Shack", "cuisine_type": "Seafood", "address": "741 Fisherman Rd", "city": "San Francisco", "state": "CA", "zip": "94125", "description": "Fresh clam chowder, fish and chips, lobster rolls and Bay Area seafood classics", "hours": "Mon-Sun 10am-10pm", "contact": "415-717-8888", "pricing_tier": "$$", "amenities": "casual, outdoor seating, family-friendly, takeout"},
        {"name": "Pizza Republic", "cuisine_type": "Italian", "address": "852 Dough St", "city": "Oakland", "state": "CA", "zip": "94616", "description": "New York style pizza by the slice and whole pies with creative toppings", "hours": "Mon-Sun 10am-12am", "contact": "510-717-8787", "pricing_tier": "$", "amenities": "casual, takeout, delivery, late night"},
        {"name": "Middle Eastern Grill", "cuisine_type": "Middle Eastern", "address": "963 Falafel Ave", "city": "San Jose", "state": "CA", "zip": "95140", "description": "Fresh falafel, shawarma and kebabs with house-made sauces and fresh pita", "hours": "Mon-Sun 10am-10pm", "contact": "408-919-1010", "pricing_tier": "$", "amenities": "halal, vegan options, casual, takeout, delivery"},
        {"name": "Dim Sum Palace", "cuisine_type": "Chinese", "address": "147 Bamboo Rd", "city": "San Jose", "state": "CA", "zip": "95141", "description": "Bustling dim sum palace with over 80 varieties served fresh from steamer carts", "hours": "Mon-Sun 8am-3pm", "contact": "408-020-2121", "pricing_tier": "$", "amenities": "family-friendly, dim sum, casual, parking"},
        {"name": "Crepe Corner", "cuisine_type": "French", "address": "258 Bretagne St", "city": "San Francisco", "state": "CA", "zip": "94126", "description": "Sweet and savory crepes made to order with fresh seasonal fillings", "hours": "Mon-Sun 8am-9pm", "contact": "415-818-9999", "pricing_tier": "$", "amenities": "casual, breakfast, takeout, wifi"},
        {"name": "Hawaiian Poke Bowl", "cuisine_type": "Hawaiian", "address": "369 Aloha Blvd", "city": "San Jose", "state": "CA", "zip": "95142", "description": "Fresh Hawaiian poke bowls with sushi-grade fish and tropical toppings", "hours": "Mon-Sun 10am-9pm", "contact": "408-121-2222", "pricing_tier": "$", "amenities": "casual, healthy, takeout, delivery, vegan options"},
        {"name": "Izakaya Hana", "cuisine_type": "Japanese", "address": "486 Cherry Blossom Ln", "city": "San Francisco", "state": "CA", "zip": "94127", "description": "Cozy Japanese pub serving grilled skewers, sashimi and premium Japanese sake", "hours": "Mon-Sun 5pm-12am", "contact": "415-919-0101", "pricing_tier": "$$", "amenities": "casual, sake bar, lively, late night"},
        {"name": "Curry House", "cuisine_type": "Indian", "address": "741 Turmeric Rd", "city": "Oakland", "state": "CA", "zip": "94617", "description": "Quick and flavorful Indian curries with a rotating menu of regional specialties", "hours": "Mon-Sun 11am-9pm", "contact": "510-818-9898", "pricing_tier": "$", "amenities": "casual, takeout, delivery, vegetarian, halal"},
        {"name": "The Wine Bar", "cuisine_type": "American", "address": "852 Vineyard Lane", "city": "San Francisco", "state": "CA", "zip": "94128", "description": "Sophisticated wine bar with small plates, artisan cheese boards and charcuterie", "hours": "Mon-Sun 3pm-12am", "contact": "415-020-2020", "pricing_tier": "$$$", "amenities": "romantic, fine dining, wine bar, casual"},
        {"name": "Noodle House", "cuisine_type": "Asian", "address": "963 Ramen Blvd", "city": "San Jose", "state": "CA", "zip": "95143", "description": "Pan-Asian noodle shop with ramen, udon, laksa and pad see ew", "hours": "Mon-Sun 11am-10pm", "contact": "408-222-3333", "pricing_tier": "$", "amenities": "casual, takeout, delivery, vegetarian"},
        {"name": "Tandoori Flames", "cuisine_type": "Indian", "address": "147 Tikka Rd", "city": "San Jose", "state": "CA", "zip": "95144", "description": "Specializing in clay oven tandoori dishes and North Indian street food", "hours": "Mon-Sun 11am-10pm", "contact": "408-323-4444", "pricing_tier": "$$", "amenities": "halal, casual, delivery, takeout"},
        {"name": "Poke Paradise", "cuisine_type": "Hawaiian", "address": "258 Maui Blvd", "city": "San Francisco", "state": "CA", "zip": "94129", "description": "Build-your-own poke bowls with fresh toppings and signature sauces", "hours": "Mon-Sun 10am-9pm", "contact": "415-121-2323", "pricing_tier": "$", "amenities": "casual, healthy, takeout, vegan options"},
        {"name": "The Taco Stand", "cuisine_type": "Mexican", "address": "369 Cilantro Ave", "city": "Oakland", "state": "CA", "zip": "94618", "description": "Simple and delicious street-style tacos with homemade salsas and fresh tortillas", "hours": "Mon-Sun 8am-9pm", "contact": "510-919-1010", "pricing_tier": "$", "amenities": "casual, takeout, breakfast, outdoor seating"},
        {"name": "Soba Noodle Bar", "cuisine_type": "Japanese", "address": "486 Buckwheat Ln", "city": "San Jose", "state": "CA", "zip": "95145", "description": "Handmade soba noodles served hot or cold with seasonal Japanese accompaniments", "hours": "Tue-Sun 11:30am-9pm", "contact": "408-424-5555", "pricing_tier": "$$", "amenities": "casual, healthy, vegetarian options, quiet"},
        {"name": "Churros and More", "cuisine_type": "Mexican", "address": "741 Cinnamon St", "city": "San Francisco", "state": "CA", "zip": "94130", "description": "Mexican dessert cafe with churros, horchata, and sweet tamales", "hours": "Mon-Sun 9am-10pm", "contact": "415-222-4444", "pricing_tier": "$", "amenities": "casual, dessert, takeout, family-friendly"},
        {"name": "Banh Mi Saigon", "cuisine_type": "Vietnamese", "address": "852 Baguette Blvd", "city": "San Jose", "state": "CA", "zip": "95146", "description": "Crispy banh mi sandwiches with fresh herbs and Vietnamese-style fillings", "hours": "Mon-Sun 7am-7pm", "contact": "408-525-6666", "pricing_tier": "$", "amenities": "casual, takeout, breakfast, delivery"},
        {"name": "Uptown Bistro", "cuisine_type": "American", "address": "963 Uptown Ave", "city": "Oakland", "state": "CA", "zip": "94619", "description": "Neighborhood bistro with seasonal American dishes and a rotating craft beer list", "hours": "Mon-Sun 11am-11pm", "contact": "510-020-3030", "pricing_tier": "$$", "amenities": "casual, beer bar, outdoor seating, family-friendly"},
    ]

    restaurants = []
    for i, r in enumerate(restaurants_data):
        existing = db.query(Restaurant).filter(Restaurant.name == r["name"]).first()
        if not existing:
            owner_id = owner_ids[i % len(owner_ids)]
            restaurant = Restaurant(**r, owner_id=owner_id, is_claimed=True)
            db.add(restaurant)
            db.commit()
            db.refresh(restaurant)
            restaurants.append(restaurant)
        else:
            restaurants.append(existing)

    review_comments = [
        "Absolutely loved it! Will definitely come back.",
        "Great food and wonderful service. Highly recommend!",
        "The flavors were authentic and portions were generous.",
        "A hidden gem in the neighborhood. Fantastic experience.",
        "Good food but service was a bit slow. Still worth visiting.",
        "One of the best restaurants I have been to in the Bay Area!",
        "Fresh ingredients and amazing presentation. 10 out of 10.",
        "Perfect spot for a date night. Romantic and delicious.",
        "The chef really knows their craft. Everything was outstanding.",
        "Great value for money. Will be back with friends.",
        "Decent food but nothing too special. Average experience.",
        "Loved the atmosphere and the food was spot on.",
        "The staff were incredibly friendly and attentive.",
        "Authentic flavors that remind me of eating back home.",
        "Creative menu with unique twists on classic dishes.",
        "Best restaurant in this part of town without a doubt.",
        "Portions are huge and everything tastes fresh.",
        "Came here for my birthday and had an amazing time.",
        "The desserts alone are worth the visit.",
        "Solid and consistent every single time I come here.",
    ]

    reviewer_ids = [users[0].id, users[1].id, users[2].id, users[3].id, users[4].id]

    for i, restaurant in enumerate(restaurants):
        num_reviews = random.randint(2, 5)
        used_reviewers = []
        for j in range(num_reviews):
            reviewer_id = reviewer_ids[j % len(reviewer_ids)]
            if reviewer_id in used_reviewers:
                continue
            used_reviewers.append(reviewer_id)
            existing = db.query(Review).filter(Review.user_id == reviewer_id, Review.restaurant_id == restaurant.id).first()
            if not existing:
                review = Review(
                    user_id=reviewer_id,
                    restaurant_id=restaurant.id,
                    rating=random.randint(3, 5),
                    comment=review_comments[(i + j) % len(review_comments)]
                )
                db.add(review)
    db.commit()

    total_restaurants = db.query(Restaurant).count()
    total_reviews = db.query(Review).count()
    total_users = db.query(User).count()

    print("Seed completed successfully!")
    print(f"Total Users: {total_users}")
    print(f"Total Restaurants: {total_restaurants}")
    print(f"Total Reviews: {total_reviews}")

seed()
db.close()
