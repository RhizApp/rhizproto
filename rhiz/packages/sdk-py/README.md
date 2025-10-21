# Rhiz SDK (Python)

Official Python SDK for Rhiz Protocol API.

## Installation

```bash
pip install rhiz-sdk
# or
poetry add rhiz-sdk
```

## Quick Start

```python
from rhiz_sdk import RhizClient

# Initialize client
client = RhizClient(
    api_url="http://localhost:8000",
    api_key="your-api-key"  # optional
)

# Find path between entities
path = client.graph.find_path(
    from_entity="entity_1",
    to_entity="entity_2",
    max_hops=6,
    min_strength=0.5
)

# Get entity neighbors
neighbors = client.graph.get_neighbors("entity_1")

# Get trust metrics
metrics = client.analytics.get_trust_metrics("entity_1")
```

## API Reference

### Graph Operations

```python
# Find shortest path
path = client.graph.find_path(
    from_entity="entity_1",
    to_entity="entity_2",
    max_hops=6,
    min_strength=0.5,
    relationship_types=["professional"],
    exclude_entities=["entity_3"]
)

# Get neighbors
neighbors = client.graph.get_neighbors("entity_1", min_strength=0.7)
```

### Entity Operations

```python
# Create entity
entity = client.entities.create(
    id="entity_1",
    type="person",
    name="Alice",
    bio="Founder at StartupX"
)

# Get entity
entity = client.entities.get("entity_1")

# Update entity
updated = client.entities.update(
    "entity_1",
    name="Alice Smith",
    bio="CEO at StartupX"
)
```

### Analytics Operations

```python
# Get trust health
health = client.analytics.get_trust_health("entity_1")

# Get trust metrics
metrics = client.analytics.get_trust_metrics("entity_1")

# Get network stats
stats = client.analytics.get_network_stats()
```

## Async Support

```python
from rhiz_sdk import AsyncRhizClient

async with AsyncRhizClient(api_url="http://localhost:8000") as client:
    path = await client.graph.find_path(
        from_entity="entity_1",
        to_entity="entity_2"
    )
```

## Error Handling

```python
from rhiz_sdk import RhizError

try:
    path = client.graph.find_path(
        from_entity="entity_1",
        to_entity="entity_2"
    )
except RhizError as e:
    print(f"Rhiz API Error: {e.message}")
    print(f"Status: {e.status_code}")
```

## License

MIT

