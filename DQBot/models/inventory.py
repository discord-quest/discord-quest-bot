from tortoise.models import Model
from tortoise import fields

class InventoryEntry(Model):
	item_id = fields.IntField()
	player_entity = fields.ForeignKeyField('models.PlayerEntity', related_name='inventory')
	quantity = fields.IntField()
	# TODO: Other fields, ie stat tracking, etc?
	class Meta:
		unique_together = (("item_id", "player_entity"))

	def __str__(self):
		return "<Item #%s * %s>" % (self.item_id, self.quantity)

	__repr__ = __str__