# Entity Relationship Diagram

The diagram below renders on GitHub.

```mermaid
erDiagram
    User ||--|| Profile : has
    User }o--o{ Group : "belongs to"
    User ||--o{ Order : places
    User ||--o{ Rating : writes
    User ||--o{ WishlistItem : saves
    User ||--o{ RecentlyViewed : views
    Category ||--o{ Subcategory : contains
    Subcategory ||--o{ Product : contains
    Product ||--o{ Rating : receives
    Product ||--o{ WishlistItem : appears_in
    Product ||--o{ RecentlyViewed : appears_in
    Product ||--o{ OrderItem : listed_in
    Order ||--o{ OrderItem : contains

    Group {
        string name
    }
    Profile {
        int user_id
        string phone
        text shipping_address
        string shipping_city
        string shipping_postcode
        string shipping_country
        image avatar
    }
    Category {
        string name
        string slug
    }
    Subcategory {
        int category_id
        string name
        string slug
    }
    Product {
        int subcategory_id
        string name
        string brand
        decimal price
        string size_variant
        string color
        int stock
        image image
    }
    Rating {
        int user_id
        int product_id
        int stars
        text comment
    }
    WishlistItem {
        int user_id
        int product_id
    }
    RecentlyViewed {
        int user_id
        int product_id
        datetime viewed_at
    }
    Order {
        int user_id
        string reference_number
        string status
        decimal total
        string ship_full_name
    }
    OrderItem {
        int order_id
        int product_id
        int quantity
        decimal unit_price
    }
```

The cart is not a table. It lives in the session so a guest can use it. At checkout the
session cart becomes an Order with its OrderItems.

Roles are not a field either. Employee and Owner are rows in Django's own Group table, and
each one carries the permission that opens the backoffice, so a user's role is which group
they are in. A customer is in neither.
