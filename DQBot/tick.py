from enum import Enum


class TickResultType(Enum):
    TOOK_DAMAGE = 1


class TickResult:
    def __init__(self, type, args):
        self.type = type
        if self.type == TickResultType.TOOK_DAMAGE:
            self.damage = args[0]
            self.new_health = args[1]

    def took_damage(damage, now_at):
        return TickResult(TickResultType.TOOK_DAMAGE, (damage, now_at))

    def mutate_embed(self, embed):
        if self.type == TickResultType.TOOK_DAMAGE:
            embed.add_field(
                name=("Took %s damage!" % self.damage),
                value=("Now at %s health" % self.new_health),
            )
        return embed  # TODO
