# Hyperion
# Copyright (C) 2025 Arian Ott <arian.ott@ieee.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import asyncio
from pyartnet import ArtNetNode


async def main():
    async with ArtNetNode.create("127.0.0.1", 6454) as node:
        # Create universe 0
        universe = node.add_universe(0)

        # Add a channel to the universe which consists of 3 values
        # Default size of a value is 8Bit (0..255) so this would fill
        # the DMX values 1..3 of the universe
        channel = universe.add_channel(start=1, width=3)

        # Fade channel to 255,0,0 in 5s
        # The fade will automatically run in the background
        channel.add_fade([255, 0, 0], 1000)

        # this can be used to wait till the fade is complete
        await channel


asyncio.run(main())
