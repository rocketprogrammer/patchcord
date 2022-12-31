"""

Litecord
Copyright (C) 2018-2021  Luna Mendes and Litecord Contributors

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

import asyncio
import argparse
from sys import argv

from logbook import Logger

from run import app, init_app_db
from manage.cmd.migration import migration
from manage.cmd import users, invites

log = Logger(__name__)


def init_parser():
    parser = argparse.ArgumentParser()
    subparser = parser.add_subparsers(help="operations")

    migration(subparser)
    users.setup(subparser)
    invites.setup(subparser)

    return parser


def main(config):
    """Start the script"""
    loop = asyncio.get_event_loop()

    parser = init_parser()

    loop.run_until_complete(init_app_db(app))

    async def _ctx_wrapper(fake_app, args):
        async with app.app_context():
            return await args.func(fake_app, args)

    try:
        if len(argv) < 2:
            parser.print_help()
            return

        args = parser.parse_args()
        return loop.run_until_complete(_ctx_wrapper(app, args))
    except Exception:
        log.exception("error while running command")
        return 1
    finally:
        loop.run_until_complete(app.db.close())
