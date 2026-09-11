# FastAPI PostgreSQL CRUD API

![Tests](https://github.com/zxnxgstu/fastapi-postgresql-crud/actions/workflows/tests.yml/badge.svg)

REST API для управления товарами, созданный на FastAPI с PostgreSQL.

## Technologies

- Python 3.13
- FastAPI
- PostgreSQL
- SQLAlchemy
- Pydantic
- Alembic
- Docker
- Docker Compose
- Pytest
- GitHub Actions

## Features
- User registration
- User login
- JWT authentication
- Password hashing
- Protected product management endpoints
- Current user endpoint
- Create products
- Get all products
- Get product by ID
- Update products
- Delete products
- Search products by name
- Filter products by stock status
- Pagination
- Input validation
- HTTP error handling
- Database migrations with Alembic
- Docker support
- Automated tests
- CI with GitHub Actions
- User roles: `user` and `admin`
- Role-based access control
- Admin-only user management
- Admin can change user roles
- Product categories
- Products can be assigned to categories
- Product filtering by category
- Admin-only category creation
- Shopping cart
- Add products to cart
- Update cart item quantity
- Remove products from cart
- User-specific cart isolation
- Order creation from shopping cart
- Order history
- Order item price snapshots
- Automatic cart cleanup after checkout
- Admin order management
- Order status management
- Product stock quantity
- Stock validation when adding products to cart
- Automatic stock reduction after order creation
- Automatic out-of-stock status when quantity reaches zero
- Shipping address for orders
- Shipping city, street and postal code stored with each order
- Shipping address validation during checkout
- Product search by name
- Product filtering by category and stock status
- Product sorting by id, name, price and stock quantity
- Pagination with skip and limit
- Query parameter validation
- Order filtering by status
- Pagination for user orders
- Pagination for admin order management
- Order query parameter validation
- Promo codes with percentage discounts
- Admin-only promo code creation
- Active/inactive promo code validation
- Promo code discounts applied during checkout
- Applied promo code and discount stored in orders
- Order cancellation for users and admins
- Automatic stock restoration after order cancellation
- Protection against repeated cancellation
- Completed orders cannot be cancelled
- Direct cancelled status updates are blocked
- User wishlist / favorite products
- Add products to wishlist
- Remove products from wishlist
- Duplicate wishlist items are prevented
- Wishlist data is isolated between users
- Product reviews and ratings
- Rating validation from 1 to 5
- Users can create, update and delete their own reviews
- Duplicate reviews for the same product are prevented
- Average product rating
- Product review count
- Product price history
- Automatic price change tracking
- Old and new prices stored for each change
- Price history endpoint for products
- Unchanged prices do not create duplicate history entries
- Price drop notifications for wishlist products
- Automatic notification when a product price decreases
- No notification when price increases
- Users can view their own notifications
- Notifications can be marked as read
- Order payment simulation
- One payment per order
- Payment amount stored with each payment
- Successful payment automatically changes order status to paid
- Duplicate payments are prevented
- Cancelled and completed orders cannot be paid
- Users cannot pay another user's order
- Payment refunds
- Paid orders can be refunded
- Refunded payments are stored with refunded status
- Refund automatically cancels the order
- Refund restores product stock
- Duplicate refunds are prevented
- Paid orders cannot be cancelled without refund
- Users cannot refund another user's order
- Order status workflow
- Valid order status transitions are enforced
- Orders must be paid before they can be shipped
- Shipped orders can be completed
- Invalid status transitions return 400 Bad Request
- Completed and cancelled orders cannot be moved back to previous states
- Order status history
- Every order status change is stored in the database
- Initial pending status is recorded when an order is created
- Payment records pending -> paid
- Admin status changes record paid -> shipped -> completed
- Order cancellation records -> cancelled
- Payment refund records paid -> cancelled
- Users can view status history only for their own orders
- Saved user addresses
- Users can create, update, list, and delete delivery addresses
- The first saved address automatically becomes the default
- Users can switch the default delivery address
- Deleting the default address automatically selects another saved address
- Users cannot access or modify another user's addresses
- Orders can be created using a saved address_id
- Orders can automatically use the user's default address
- Shipping address data is copied into the order at creation time
- Delivery methods
- Public list of active delivery methods
- Admins can create, update, enable, and disable delivery methods
- Delivery methods support custom prices
- Orders can use a selected delivery method
- Delivery price is included in order total_price
- Payment amount includes delivery price
- Orders store delivery method code, name, and price as a snapshot
- Inactive delivery methods cannot be used for new orders
- Customer order notes
- Users can add an optional comment when creating an order
- Customer notes are stored with the order
- Notes are limited to 500 characters
- Invalid oversized notes are rejected with validation error
- Order totals breakdown
- Orders store subtotal before discounts
- Discount amount is calculated and stored separately
- Delivery price is stored separately
- Final total_price is calculated as subtotal - discount_amount + delivery_price
- Promo code discounts apply only to product subtotal
- Payment amount uses the final order total
- Order item line totals
- Each order item stores its unit price, quantity, and line_total
- line_total is calculated as price × quantity
- Order item totals are preserved as part of the order snapshot
- Order shipment tracking
- Admins can add a shipping carrier and tracking number
- Tracking can only be added to shipped orders
- Regular users cannot modify shipment tracking
- Tracking information is returned with order data
- Estimated delivery date
- Admins can set an estimated delivery date for shipped orders
- Estimated delivery dates cannot be in the past
- Regular users cannot modify the estimated delivery date
- Estimated delivery date is returned with order data
- Shipment events history
- Admins can add shipment events for shipped orders
- Supported shipment statuses: picked_up, in_transit, out_for_delivery, delivered
- Shipment events can include an optional comment
- Users can view shipment history only for their own orders
- Regular users cannot create shipment events
- Shipment events cannot be added before an order is shipped
- Shipment delivery synchronization
- A delivered shipment event automatically completes the order
- The shipped -> completed transition is stored in order status history
- Duplicate delivered events are rejected
- Shipment events cannot be added after an order is completed
- Shipment tracking history
- Every tracking update is stored in history
- Users can view tracking history only for their own orders
- Shipment events follow a strict status sequence
- Valid sequence: picked_up -> in_transit -> out_for_delivery -> delivered
- Skipping statuses or moving backwards is rejected
- Actual delivery timestamp
- delivered_at is stored when a delivered shipment event is created
- delivered_at is returned with order data
- Admin store statistics
- Admins can view total users, products, orders, completed orders, and total revenue
- Revenue is calculated only from completed orders
- Top selling products for admins
- Products are ranked by total units sold
- Revenue is calculated from completed orders
- Results can be limited with the limit query parameter
- Daily sales statistics for admins
- Completed orders are grouped by delivery date
- Revenue and order count are calculated per day
- The number of days can be controlled with the days query parameter
- Order status statistics for admins
- Orders are grouped by status
- Admins can view the number of pending, paid, shipped, completed, and cancelled orders

## API endpoints

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| POST | `/register` | Register new user | No |
| POST | `/login` | Login and get JWT token | No |
| GET | `/me` | Get current user | Yes |
| GET | `/users` | Get all users | Admin |
| PATCH | `/users/{user_id}/role` | Change user role | Admin |
| GET | `/products` | Get products | No |
| GET | `/products/{product_id}` | Get product by ID | No |
| POST | `/products` | Create product | Yes |
| PUT | `/products/{product_id}` | Update product | Yes |
| DELETE | `/products/{product_id}` | Delete product | Admin |
| GET | `/categories` | Get all categories | No |
| GET | `/categories/{category_id}` | Get category by ID | No |
| POST | `/categories` | Create category | Admin |
| GET | `/cart` | Get current user's cart | Yes |
| POST | `/cart` | Add product to cart | Yes |
| PATCH | `/cart/{item_id}` | Update cart item quantity | Yes |
| DELETE | `/cart/{item_id}` | Remove item from cart | Yes |
| POST | `/orders` | Create order from cart | Yes |
| GET | `/orders` | Get current user's orders | Yes |
| GET | `/orders/{order_id}` | Get current user's order | Yes |
| GET | `/admin/orders` | Get all orders | Admin |
| PATCH | `/admin/orders/{order_id}/status` | Change order status | Admin |

## Product filtering and pagination

Products can be filtered by name, stock status and category:

```text
GET /products?search=Keyboard&in_stock=true&category_id=1&skip=0&limit=10
```text
GET /products?search=Keyboard&in_stock=true&category_id=1&skip=0&limit=10
```

The project currently includes 143 automated API tests.