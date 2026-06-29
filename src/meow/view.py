from __future__ import annotations

import dataclasses
from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import Any, override

import hikari

type AsyncFn[*Ts, R] = Callable[[*Ts], Awaitable[R]]
type Fn[*Ts, R] = Callable[[*Ts], R]


async def anop(*_, **__) -> None:
	pass


class ViewItem(ABC):
	@abstractmethod
	def _to_hikari_builder(self) -> hikari.api.ComponentBuilder: ...


class _ContainsItemsMixin:
	_items: list[ViewItem]

	def __init__(self, *items: ViewItem) -> None:
		self._items = list(items)

	def __call__[T: ViewItem](self, item: T) -> T:
		return self.add_item(item)

	def add_item[T: ViewItem](self, item: T) -> T:
		if isinstance(item, Container):
			msg = "Cannot add a container to another container."
			raise TypeError(msg)

		self._items.append(item)

		return item


class Container(ViewItem, _ContainsItemsMixin):
	_items: list[ViewItem]

	def __init__(self, *items: ViewItem) -> None:
		self._items = list(items)

	@override
	def add_item[T: ViewItem](self, item: T) -> T:
		if isinstance(item, Container):
			msg = "Cannot add a container to another container."
			raise TypeError(msg)

		return super().add_item(item)


class View(_ContainsItemsMixin): ...


@dataclass
class TextItem(ViewItem):
	content: str


@dataclass
class Button:
	label: str
	style: hikari.ButtonStyle

	def __call__(self, f: ButtonItem.Callback) -> Fn[ButtonItem.Callback, ButtonItem]:
		return self.impl(f)

	def impl(self, f: ButtonItem.Callback) -> Fn[ButtonItem.Callback, ButtonItem]:
		return ButtonItem(
			**{
				k: v
				for k, v in dataclasses.asdict(self).items()
				if k != "callback"  # safeguad for `ButtonItem.impl` to work overriding the callback instead of raising a TypeError
			},
			callback=f,
		)


@dataclass
class ButtonItem(Button, ViewItem):
	type Callback = AsyncFn[hikari.ComponentInteraction, None]

	callback: Callback = field(default=anop)


class ViewContext:
	# TODO: wrap interaction, is it here where to handle stuff like "first response" vs "all following responses"?
	#       Think if better to drop the first response handling, in favour of doing it manually, or some other response manager solution, because what is done currently (any subsequent responses being a reply) can *implicitly* ignore ephemeral flag which is annoying & impossible to type

	_interaction: hikari.ComponentInteraction
	_view: View

	@property
	def view(self) -> View:
		return self._view


#### USAGE


def main():
	my_view = View(
		kw1=True,
		*(
			container1 := Container(),
			container2 := Container(),
		),
	)

	@container1
	@ButtonItem.from_template(Button(label="Click me 2!", style=hikari.ButtonStyle.PRIMARY))
	async def _(view: View, ctx: ViewContext, btn: ButtonItem):
		btn.label = "Thanks for clicking 2"

		ctx.update_message()  # should edit the message with the new components from the view

	@my_view
	# @ButtonItem.from_super(Button(label="Click me!", style=hikari.ButtonStyle.PRIMARY))
	@Button(label="Click me!", style=hikari.ButtonStyle.PRIMARY)  # type: ignore
	async def _(
		view: View,
		ctx: ViewContext,
		btn: ButtonItem,  # should be a mutable ref to the view's button, being the one that was clicked, therefore the line below (btn.label = "Thanks for clicking") should be possible
	):
		btn.label = "Thanks for clicking"

		ctx.update_message()  # should edit the message with the new components from the view
