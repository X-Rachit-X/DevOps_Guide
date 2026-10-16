const cached = await redis.get(key);

if (cached) {
  return JSON.parse(cached);
}

const product = await db.product.findUnique({
  where: { id }
});

await redis.set(
  key,
  JSON.stringify(product),
  { EX: 300 }
);

return product;
