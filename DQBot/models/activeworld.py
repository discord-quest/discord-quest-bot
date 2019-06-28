from DQBot.repo import TILE_SIZE, BlockType
from DQBot.action import ActionType, Direction, Action, ActionResult
from DQBot.models.entities import (
    ChestEntity,
    ENTITY_RELATIONSHIPS,
    EnemyEntity,
    PLAYER_MAX_HEALTH,
)
from DQBot.inventory import ItemStore, ItemCapability
from DQBot.tick import TickResult
from DQBot.conclusion import Conclusion

from tortoise.models import Model
from tortoise import fields
from tortoise.query_utils import Q

from math import sqrt

# The amount of tiles player around them players can see
VIEW_SIZE = (5, 5)

# A World a player is playing in. This inherits the blocks in it from World,
# but stores its own entities.
# This is what you should actually render for a player
class ActiveWorld(Model):
    world_name = fields.CharField(20)  # Right now maps aren't stored in the database
    player = fields.ForeignKeyField("models.Player", related_name="active_world")
    player_entity = fields.ForeignKeyField(
        "models.PlayerEntity", related_name="active_world"
    )
    exp_earned = fields.IntField(default=0)

    # Finds out which actions it is possible to take
    # Returns array of `Action`s
    async def possible_actions(self, world, item_repo):
        await self.fetch_related("player_entity")

        actions = []

        x, y = (self.player_entity.x, self.player_entity.y)

        surrounding_entities = await self.all_entities_with(
            Q(x__in=(x + 1, x - 1), y=y) | Q(y__in=(y + 1, y - 1), x=x)
        )

        entity_blocked_directions = [
            Direction.from_delta((x, y), (e.x, e.y)) for e in surrounding_entities
        ]

        if (
            not world.block_at(x, y + 1).collides()
            and Direction.DOWN not in entity_blocked_directions
        ):
            actions.append(Action.move(Direction.DOWN))

        if (
            not world.block_at(x, y - 1).collides()
            and Direction.UP not in entity_blocked_directions
        ):
            actions.append(Action.move(Direction.UP))

        if (
            not world.block_at(x + 1, y).collides()
            and Direction.RIGHT not in entity_blocked_directions
        ):
            actions.append(Action.move(Direction.RIGHT))

        if (
            not world.block_at(x - 1, y).collides()
            and Direction.LEFT not in entity_blocked_directions
        ):
            actions.append(Action.move(Direction.LEFT))

        for entity in surrounding_entities:
            if entity.__class__ is ChestEntity and not entity.opened:
                actions.append(
                    Action.open_chest(
                        Direction.from_delta((x, y), (entity.x, entity.y))
                    )
                )
            elif issubclass(entity.__class__, EnemyEntity):
                actions.append(
                    Action.melee_attack(
                        Direction.from_delta((x, y), (entity.x, entity.y))
                    )
                )

        if self.player_entity.health <= PLAYER_MAX_HEALTH:
            items = [
                item_repo.items[x.item_id]
                for x in await self.player_entity.inventory.all()
            ]

            if item_repo.find_capable(items, ItemCapability.HEAL) != None:
                actions.append(Action.heal())

        actions.append(Action.wait())

        return actions

    async def calc_items_exp(self, item_repo):
        items = [
            item_repo.items[x.item_id] for x in await self.player_entity.inventory.all()
        ]

        total = 0
        for item in items:
            total += item.tier

        return total

    # Perform the requested action in the world, ie move the player, kill the enemy
    async def take_action(self, action, world, item_repo):
        await self.fetch_related("player_entity")
        if action.type == ActionType.MOVE:
            x, y = action.direction.mutate((self.player_entity.x, self.player_entity.y))

            if x >= world.grid.shape[0] or y >= world.grid.shape[1]:
                self.exp_earned += await self.calc_items_exp(item_repo)

                return TickResult.conclude(Conclusion(True, self.exp_earned))

            # only save if no collisions
            if not await self.has_collision(x, y, world):
                self.player_entity.x = x
                self.player_entity.y = y

                await self.player_entity.save()

                return ActionResult.success()
            else:
                return ActionResult.error()
        elif action.type == ActionType.OPEN_CHEST:
            chest_x, chest_y = action.direction.mutate(
                (self.player_entity.x, self.player_entity.y)
            )
            chest = await self.chest_entities.filter(x=chest_x, y=chest_y).first()

            if chest != None and not chest.opened:
                loot = item_repo.roll_loot(chest.level)

                await self.player_entity.add_items(loot)

                chest.opened = True
                await chest.save()

                return ActionResult.got_loot(loot)
            else:
                return ActionResult.error()
        elif action.type == ActionType.MELEE_ATTACK:
            enemy_x, enemy_y = action.direction.mutate(
                (self.player_entity.x, self.player_entity.y)
            )

            enemy = await self.all_enemies_with(x=enemy_x, y=enemy_y)
            enemy = enemy[0]

            if enemy != None:
                items = [
                    item_repo.items[x.item_id]
                    for x in await self.player_entity.inventory.all()
                ]
                using = item_repo.find_capable(items, ItemCapability.MELEE_ATTACK)
                if using != None:
                    damage = using.damage
                else:
                    damage = 1

                dead = await enemy.take_damage(damage)

                if dead:
                    # Reward xp
                    await self.fetch_related("player")
                    self.player.exp += enemy.exp_reward
                    self.exp_earned += enemy.exp_reward

                    await self.save()
                    await self.player.save()

                return ActionResult.did_damage(damage, enemy)
            else:
                return ActionResult.error()
        elif action.type == ActionType.HEAL:
            # Find the item to use
            inv_entries = await self.player_entity.inventory.filter(quantity__gte=1)
            items = [item_repo.items[x.item_id] for x in inv_entries]
            using = item_repo.find_capable(items, ItemCapability.HEAL)

            # Heal that health
            self.player_entity.health = min(
                self.player_entity.health + using.amnt, PLAYER_MAX_HEALTH
            )
            await self.player_entity.save()

            # Destroy the item
            entry = next((x for x in inv_entries if x.item_id == using.id))
            entry.quantity -= 1

            if entry.quantity <= 0:
                await entry.delete()
            else:
                await entry.save()

            return ActionResult.heal(using.amnt)
        elif action.type == ActionType.WAIT:
            return ActionResult.success()
        else:
            raise NotImplementedError(
                "Action processing not yet implemented: %s" % action
            )

    async def do_tick(self, world, item_store):
        await self.fetch_related("player_entity")
        (x, y) = (self.player_entity.x, self.player_entity.y)

        results = []
        for enemy in await self.all_enemies_with():
            # check if in attack range
            in_range = abs(enemy.x - x) + abs(enemy.y - y) < 2
            if in_range:
                if enemy.attack_delay != 0:
                    if enemy.ticks_since_attack < enemy.attack_delay:
                        enemy.ticks_since_attack += 1
                        await enemy.save()
                        continue

                    # allowed to attack
                    enemy.ticks_since_attack = 0
                    await enemy.save()
                # attack player
                self.player_entity.health -= enemy.damage

                results.append(
                    TickResult.took_damage(enemy.damage, self.player_entity.health)
                )
                if self.player_entity.health <= 0:
                    results.append(
                        TickResult.conclude(Conclusion(False, self.exp_earned))
                    )
            else:
                # TODO: Proper line of sight test
                distance = sqrt(((x - enemy.x) ** 2) + ((y - enemy.y) ** 2))

                if distance <= enemy.vision_distance:
                    speed = enemy.speed
                    if enemy.speed < 1:
                        if enemy.ticks_since_move < (1 / enemy.speed):
                            enemy.ticks_since_move += 1
                            await enemy.save()
                            continue

                        enemy.ticks_since_move = 0
                        speed = 1

                    # TODO: Proper pathfinding
                    for i in range(0, speed):
                        direction = Direction.from_delta((enemy.x, enemy.y), (x, y))
                        (new_x, new_y) = direction.mutate((enemy.x, enemy.y))

                        if not await self.has_collision(new_x, new_y, world):
                            enemy.x, enemy.y = (new_x, new_y)

                    await enemy.save()

        if len(results) > 0:
            await self.player_entity.save()

        return results

    async def has_collision(self, x, y, world):
        if BlockType(world.grid[x, y]).collides():
            return True
        else:
            entities_in_direction = await self.all_entities_with(x=x, y=y)
            return len(entities_in_direction) > 0

    # Relationship helpers

    async def all_entities_with(self, *args, **kwargs):
        zombies = await self.zombie_entities.filter(*args, **kwargs)
        big_zombies = await self.bigzombie_entities.filter(*args, **kwargs)
        chests = await self.chest_entities.filter(*args, **kwargs)
        return zombies + big_zombies + chests

    async def all_enemies_with(self, *args, **kwargs):
        zombies = await self.zombie_entities.filter(*args, **kwargs)
        big_zombies = await self.bigzombie_entities.filter(*args, **kwargs)
        return zombies + big_zombies

    # Rendering code

    # Return an image
    # TODO: This shit is fucked.
    async def render(self, world, repo):
        await self.fetch_related("player_entity", *ENTITY_RELATIONSHIPS)

        # cut out the view around the player
        # TODO: Probably nicer looking ways to do this
        section_center = tuple(
            (a + 0.5) * TILE_SIZE for a in (self.player_entity.x, self.player_entity.y)
        )
        section_top_left = tuple(
            a - (((VIEW_SIZE[i] // 2) + 0.5) * TILE_SIZE)
            for i, a in enumerate(section_center)
        )

        section_size = tuple(VIEW_SIZE[i] * TILE_SIZE for i in (0, 1))

        lower_right_point = tuple(section_top_left[i] + section_size[i] for i in (0, 1))

        coords = section_top_left + lower_right_point
        image = world.image.crop(coords)

        lower_bounds = tuple(
            a - (VIEW_SIZE[i] // 2)
            for i, a in enumerate((self.player_entity.x, self.player_entity.y))
        )
        upper_bounds = tuple(
            a + (VIEW_SIZE[i] // 2)
            for i, a in enumerate((self.player_entity.x, self.player_entity.y))
        )

        entities = await self.all_entities_with(
            x__lte=upper_bounds[0] + 1,
            x__gte=lower_bounds[0] - 1,
            y__lte=upper_bounds[1] + 1,
            y__gte=lower_bounds[1] - 1,
        )
        for entity in entities:
            await self.paste_entity(entity, image, repo, lower_bounds, upper_bounds)

        await self.paste_entity(
            self.player_entity, image, repo, lower_bounds, upper_bounds
        )
        return image

    async def paste_entity(self, entity, image, repo, lower_bounds, upper_bounds):
        # bounds check
        if False in tuple(
            a >= lower_bounds[i] and a <= upper_bounds[i]
            for i, a in enumerate((entity.x, entity.y))
        ):
            return

        # translate to local world co-ords
        local_world_coords = (entity.x - lower_bounds[0], entity.y - lower_bounds[1])

        # then to local image co-ords
        image_coords = (
            (local_world_coords[0]) * TILE_SIZE,
            (local_world_coords[1]) * TILE_SIZE,
        )

        # get image to render
        entity_image = repo.entity(entity.get_name(), entity.get_state())

        # paste onto map
        image.paste(
            entity_image,
            tuple(int(a) for a in image_coords),
            entity_image.convert("RGBA"),
        )
