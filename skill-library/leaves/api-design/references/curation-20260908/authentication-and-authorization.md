# Optional reference; current entrypoint and project brief take precedence.

## Authentication and Authorization

### Token-Based Auth

```
# Bearer token in Authorization header
GET /api/v1/users
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...

# API key (for server-to-server)
GET /api/v1/data
X-API-Key: sk_live_abc123
```

### Authorization Patterns

```typescript
// Resource-level: check ownership
app.get("/api/v1/orders/:id", async (req, res) => {
  const order = await Order.findById(req.params.id);
  if (!order) return res.status(404).json({ error: { code: "not_found" } });
  if (order.userId !== req.user.id) return res.status(403).json({ error: { code: "forbidden" } });
  return res.json({ data: order });
});

// Role-based: check permissions
app.delete("/api/v1/users/:id", requireRole("admin"), async (req, res) => {
  await User.delete(req.params.id);
  return res.status(204).send();
});
```

