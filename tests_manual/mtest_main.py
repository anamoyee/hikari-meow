import asyncio
import os
import pathlib as p

import hikari
import meow
from nya_scope import Scope
from rich.traceback import install as rich_traceback_install


class Config__(Scope):
	TEXT_CHANNEL_ID = 1145433324320464898

	@staticmethod
	def get_token():
		path = p.Path(__file__).parent.parent / "TEST_TOKEN.txt"

		if not path.is_file():
			raise RuntimeError(f"Path to test token doesnt exist or is not a file: {path!r}")

		return path.read_text().strip()


async def main() -> None:
	rich_traceback_install(
		width=os.get_terminal_size().columns,
	)

	BOT = hikari.GatewayBot(
		Config__.get_token(),
	)
	MCL = meow.Meow(BOT)

	await BOT.start(
		activity=hikari.Activity(
			name=f"Manual testing {meow.__name__!r}",
			type=hikari.ActivityType.CUSTOM,
		),
	)

	text_channel = await BOT.rest.fetch_channel(Config__.TEXT_CHANNEL_ID)

	if True:  # tests

		async def t1_send_message():
			await text_channel.send("content")

		await t1_send_message()

	await BOT.close()


if __name__ == "__main__":
	asyncio.run(main())
