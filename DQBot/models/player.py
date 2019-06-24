from tortoise.models import Model
from tortoise import fields

class Player(Model):
	discord_uuid = fields.CharField(20, pk=True)