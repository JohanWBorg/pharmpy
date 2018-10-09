#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
============================
The CLI interface of PharmPy
============================

Yes, CLI is still anticipated to be the main interface.

Definitions
===========
"""

import argparse
import logging
import sys
from pathlib import Path
from textwrap import dedent

from pharmpy import __version__
from pharmpy import Model


class CLI:
    """Manages main CLI interface.

    Idea is that main interface is subcommand-based. As is popular nowadays (see Git!).

    *However...* all subcommands shall be invokable without stepping through :func:`CLI.__init__`,
    and thus easy to install symlinks for (à la PsN). Noth that I would *recommend* it, but...
    """

    def __init__(self, args=None):
        """Initialize and parse command line arguments"""

        self.log = logging.getLogger()
        if args is None:
            self.log.debug('CLI mode: sys.argv')
            args = sys.argv
        else:
            self.log.debug('CLI mode: args')
            args = [__file__] + list(args)
        self.log.debug('CLI args=%r', args)

        parser = argparse.ArgumentParser(
            usage=dedent("""
            pharmpy <command> [<args>]
              (or) pharmpy help <command>

            Common PharmPy commands used to operate on model files:

                sumo       Summarize a model/run
                clone      Clone a model file (e.g. updating inits)
                execute    Execute default task/workflow


            Miscellanelous other commands:

                version    PharmPy version information

            Some/all commands may be symlinked on your install.
            """).strip(),
            description='PharmPy CLI interface',
            formatter_class=argparse.RawTextHelpFormatter
        )
        parser.add_argument('command', help='Subcommand of PharmPy to run')

        # prevent fail of validation via excluding subcommand args for now
        args = parser.parse_args(sys.argv[1:2])

        # dispatch pattern!
        self._check_command(args.command, parser)
        getattr(self, args.command)()

    def help(self, help=False):
        """Subcommand for built-in help on PharmPy or other subcommand."""

        parser = argparse.ArgumentParser(
            description=dedent("""
                PharmPy help central

                PharmPy is...
            """).strip())
        parser.add_argument('command', help='Subcommand of PharmPy to get helptext for')

        self.args = self._parse_args(parser)

    def sumo(self, help=False):
        """Subcommand for... good old sumo rebooted! What's not to love?"""

        parser = argparse.ArgumentParser(description='Summarize a model or run')
        parser = self._common_args(parser)

        self.args = self._parse_args(parser)
        raise NotImplemented('Not yet!')

    def clone(self, help=False):
        """Subcommand to clone a model/update initial estimates."""

        parser = argparse.ArgumentParser(description='Duplicate a model')
        parser = self._common_args(parser)
        parser.add_argument(
            '--ui', '--update_inits', action='store_true',
            help='Update initial estimates'
        )
        parser.add_argument(
            'out_file', metavar='OUT', nargs=1, action='store',
            help='file to output',
        )

        self.args = self._parse_args(parser)
        raise NotImplemented('Not yet!')

    def execute(self, help=False):
        """Subcommand to execute a model default task/workflow."""

        parser = argparse.ArgumentParser(description='Execute default task/workflow')
        parser = self._common_args(parser)

        self.args = self._parse_args(parser)
        raise NotImplemented('Not yet!')

    def version(self, help=False):
        """Subcommand to print PharmPy version (and brag a little bit)."""

        print(dedent("""
            Version: %s
            Authors: Gunnar Yngman <gunnar.yngman@farmbio.uu.se>
                     Rikard Nordgren <rikard.nordgren@farmbio.uu.se>
        """ % (__version__,)
        ).strip())

    def _common_args(self, parser):
        """Adds in commond arguments on *parser*.

        Of special importance is the verbosity arguments, to set logging level for this (root)
        logger. All other parts of PharmPy will get their messages filtered through this.
        """

        parser.add_argument(
            'file', metavar='FILE', nargs=1, action='store',
            help='model file to operate on',
        )
        verbosity_group = parser.add_mutually_exclusive_group()
        verbosity_group.add_argument(
            '-v', '--verbose',
            action='store_const', dest='loglevel', const=logging.INFO,
            default=logging.WARNING,
            help='print additional info',
        )
        verbosity_group.add_argument(
            '--debug',
            action='store_const', dest='loglevel', const=logging.DEBUG,
            help='show debug messages',
        )

        return parser

    def _parse_args(self, parser):
        """Returns parsed arguments of subcommand + common arguments."""

        args = parser.parse_args(sys.argv[2:])
        self.log = getLogger(self.args.level, show_traceback=True)
        self.debug('args=%r', args)

        self.file = Path(args.file).resolve()
        self.log.debug('file=%r' % self.file)
        self.model = Model(self.file)
        self.log.info('%r read' % self.model)

        return self.args

    def _check_command(self, command, parser):
        """Check if *command* exists, i.e. is a method of this class.

        .. note:: Any method beginning with ``_`` is a helper method and thus, *not a command*!
        """

        if command.startswith('_') or not hasattr(self, command):
            print('Unrecognized PharmPy command! Please consult the built-in help command.')
            parser.print_help()
            exit(1)


def getLogger(level, show_traceback=False):
    """Initialize CLI logger configuration and return logger.

    *Returns already configurated logger if already configurated.*

    Logger **mustn't be configurated** if imported as library (e.g. set handlers and such), since
    that should bubble up into the lap of whomever is at the top. As a CLI however, we are the very
    top!

    Args:
        level: Level from :mod:`logging`.
        show_traceback: Default is to hide all traceback.

    Even if hiding traceback, the exception + message is still shown.
    """

    logger = logging.getLogger(__file__)
    logger.setLevel(level)
    if logger.hasHandlers():
        return logger

    if level <= logging.DEBUG:
        fmt = ('%(message)s\t[from %(name)s:%(lineno)d (%(levelname)s)]')
    else:
        fmt = '%(message)s'

    if not show_traceback:
        def _no_traceback(exception_type, exception, traceback):
            logger.critical('%s: %s', exception_type.__name__, exception)

        sys.excepthook = _no_traceback

    msg = logging.StreamHandler(sys.stdout)
    err = logging.StreamHandler(sys.stderr)
    err.setLevel(logging.WARNING)
    msg.addFilter(lambda record: record.levelno <= logging.INFO)
    msg.setFormatter(logging.Formatter(fmt))
    err.setFormatter(logging.Formatter(fmt))

    logger.addHandler(msg)
    logger.addHandler(err)

    return logger


def main(args=None):
    """Invoked by ``__main__.py`` and entry point of binary.

    Use *args* to bypass :attr:`sys.argv` to implement argument parsing from non-standard source.
    """

    CLI(args)
