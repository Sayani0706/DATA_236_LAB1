# MongoDB Schema Design

## Collections

### users
```json
{
  "_id": ObjectId,
  "name": "string",
  "email": "string (unique index)",
  "password": "string (bcrypt hashed)",
  "role": "string (user|owner)",
  "phone": "string",
  "about_me": "string",
  "city": "string",
  "state": "string",
  "country": "string",
  "languages": "string",
  "gender": "string",
  "profile_picture": "string",
  "created_at": ISODate,
  "preferences": {
    "cuisines": "string",
    "price_range": "string",
    "location": "string",
    "search_radius": "number",
    "dietary_needs": "string",
    "ambiance": "string",
    "sort_preference": "string"
  }
}
```

Indexes:
- `email` (unique)
- `role`

### restaurants
```json
{
  "_id": ObjectId,
  "owner_id": ObjectId,
  "name": "string",
  "cuisine_type": "string",
  "address": "string",
  "city": "string",
  "state": "string",
  "zip": "string",
  "description": "string",
  "hours": "string",
  "contact": "string",
  "pricing_tier": "string",
  "amenities": "string",
  "is_claimed": "boolean",
  "view_count": "number",
  "created_at": ISODate,
  "photos": [
    {
      "photo_url": "string",
      "uploaded_at": ISODate
    }
  ]
}
```

Indexes:
- `owner_id`
- `name` (text index)
- `cuisine_type`
- `city`

### reviews
```json
{
  "_id": ObjectId,
  "user_id": ObjectId,
  "restaurant_id": ObjectId,
  "rating": "number (1-5)",
  "comment": "string",
  "review_date": ISODate,
  "updated_at": ISODate,
  "photos": [
    {
      "photo_url": "string"
    }
  ]
}
```

Indexes:
- `user_id`
- `restaurant_id`
- Compound index: `[user_id, restaurant_id]` (unique)

### favorites
```json
{
  "_id": ObjectId,
  "user_id": ObjectId,
  "restaurant_id": ObjectId,
  "saved_at": ISODate
}
```

Indexes:
- `user_id`
- Compound index: `[user_id, restaurant_id]` (unique)

### sessions
```json
{
  "_id": ObjectId,
  "user_id": ObjectId,
  "token": "string",
  "created_at": ISODate,
  "expires_at": ISODate,
  "ip_address": "string",
  "user_agent": "string"
}
```

Indexes:
- `user_id`
- `token` (unique)
- `expires_at` (TTL index for automatic cleanup)

### chat_history
```json
{
  "_id": ObjectId,
  "user_id": ObjectId,
  "message": "string",
  "role": "string (user|assistant)",
  "created_at": ISODate
}
```

Indexes:
- `user_id`
- `created_at`

## Design Decisions

1. Embedded preferences in users document for faster lookups
2. Embedded photos arrays to avoid separate collections
3. TTL index on sessions for automatic cleanup of expired sessions
4. Compound indexes for unique constraints (user + restaurant combinations)
5. Text index on restaurant name for search functionality
