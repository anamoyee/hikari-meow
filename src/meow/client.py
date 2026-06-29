from typing import TYPE_CHECKING

import hikari

if TYPE_CHECKING:
	from .view import View


class Client:
	""""""

	bot: hikari.GatewayBot

	_unbound_views: dict[str, View]
	"""dict[custom_id, View]"""
	_bound_views: dict[hikari.Snowflake, View]
	"""dict[message_id, View]"""

	def __init__(self, bot: hikari.GatewayBot) -> None:
		self.bot = bot

		self._unbound_views = {}
		self._bound_views = {}

		self.bot.subscribe(hikari.InteractionCreateEvent, self._on_interaction)

	async def _on_interaction(self, event: hikari.InteractionCreateEvent) -> None:
		if isinstance(event.interaction, hikari.ComponentInteraction):
			await self._on_component_interaction(event)

		if isinstance(event.interaction, hikari.ModalInteraction):
			await self._on_modal_interaction(event)

		return

	async def _on_component_interaction(self, event: hikari.InteractionCreateEvent) -> None:
		inter = event.interaction
		assert isinstance(inter, hikari.ComponentInteraction)

		if view := self._bound_views.get(inter.message_id):
			await view._on_interaction(event)

		if view := self._unbound_views.get(inter.custom_id):
			await view._on_interaction(event)

	async def _on_modal_interaction(self, event: hikari.InteractionCreateEvent) -> None:
		inter = event.interaction
		assert isinstance(inter, hikari.ModalInteraction)

		msg = "Modal interactions are not implemented yet."
		raise NotImplementedError(msg)
