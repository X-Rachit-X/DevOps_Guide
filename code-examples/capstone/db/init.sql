-- Data model from Chapter 35 sections 9-11 (User, Product, Order, OrderItem) + idempotency key.
CREATE TABLE IF NOT EXISTS users (
  id         SERIAL PRIMARY KEY,
  email      TEXT UNIQUE NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS products (
  id         SERIAL PRIMARY KEY,
  name       TEXT NOT NULL,
  price      NUMERIC(12,2) NOT NULL,
  stock      INTEGER NOT NULL DEFAULT 0,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TYPE order_status AS ENUM ('PENDING','PROCESSING','COMPLETED','FAILED','CANCELLED');
CREATE TABLE IF NOT EXISTS orders (
  id              SERIAL PRIMARY KEY,
  user_id         INTEGER NOT NULL REFERENCES users(id),
  status          order_status NOT NULL DEFAULT 'PENDING',
  total_amount    NUMERIC(12,2) NOT NULL,
  idempotency_key TEXT UNIQUE,          -- UNIQUE makes duplicate POSTs safe
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS order_items (
  id         SERIAL PRIMARY KEY,
  order_id   INTEGER NOT NULL REFERENCES orders(id),
  product_id INTEGER NOT NULL REFERENCES products(id),
  quantity   INTEGER NOT NULL CHECK (quantity > 0),
  price      NUMERIC(12,2) NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_orders_user ON orders(user_id);
INSERT INTO users (email) VALUES ('demo@example.com') ON CONFLICT DO NOTHING;
INSERT INTO products (name, price, stock) VALUES ('Widget', 9.99, 100) ON CONFLICT DO NOTHING;
