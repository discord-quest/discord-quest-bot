# Rendering a world

Calling `RenderServer.process_render(ActiveWorld)` will return the URL of that ActiveWorld's current view.
There should only ever be one RenderServer and it is kept in `App`.

# Taking an action

Calling `ActiveWorld.take_action(Action)` will perform that action and return an ActionResult.

## Possible actions/results

### Move

```
Action.move(Direction)
```

Move the player in the given direction

Possible results:
	- Success
	- Error (There is a collision in that direction)

### Open Chest

```
Action.open_chest(Direction)
```

Open the chest directly next to the player in that direction.

Possible results:
	- Got_Loot
		- result.loot is an array of items found from chest
	- Error (No chest there)

# Items

Every type of item inherits from `Item` and should be registered in `ItemStore`.

They all have an ID (unique), a friendly name (shown to players), a tier (used for loot generation) and a list of Capabilities.

Each capability will likely add more attributes:

## Capabilities

### Melee Attack

Can attack in a one-block radius. Adds `damage` attribute.

# DB related Snippets

```python3
# Get ActiveWorld from discord id
active_world = await ActiveWorld.filter(player__discord_id='...').first()
# You also probably want to .prefetch_related('entities', 'player_entity', 'player_entity__inventory')

# Get player's inventory
await active_world.fetch_related('player_entity')
player_entity = active_world.player_entity
inventory = await player_entity.inventory.all() # Array of InventoryEntries, one per type of item

# Get the type of item from an InventoryEntry
# Requires ItemStore which should (ideally) be kept only in App
item = item_store.items[entry.item_id]

```