import itertools
import os
import sys
import typing as tp
import click

from aiohttp import web
from loguru import logger

from . import app
from .utils.dotenv import try_load_envfile


LogLevel = tp.Literal["TRACE", "DEBUG", "INFO", "WARNING", "ERROR"]


def logger_from_str(logger_text: str) -> list[tuple[LogLevel, str]]:
    """
    Helper function to deconstruct string input argument(s) to logger configuration.

    Examples:
    - logger_from_str("ERROR,errors.log") -> [("ERROR", "errors.log)]
    - logger_from_str("ERROR,errors.log;INFO,info.log") -> [("ERROR", "errors.log), ("INFO", "info.log")]
    """
    res = []
    for item in logger_text.split(";"):
        assert "," in item, f'logger text must be in format "LEVEL,filename" - current value is "{logger_text}"'
        level, filename = item.split(",", 1)
        level = level.upper()
        res.append((level, filename))  # type: ignore
    return res


@click.command("Run Alice skill STAR COURIER")
@click.option(
    "--port",
    "-p",
    envvar="PORT",
    type=int,
    default=8000,
    show_default=True,
    show_envvar=True,
    help="Service port number",
)
@click.option(
    "--host",
    envvar="HOST",
    default="127.0.0.1",
    show_default=True,
    show_envvar=True,
    help="Service HOST address",
)
@click.option(
    "--logger_verbosity",
    "-v",
    type=click.Choice(("TRACE", "DEBUG", "INFO", "WARNING", "ERROR")),
    envvar="LOGGER_VERBOSITY",
    default="DEBUG",
    show_default=True,
    show_envvar=True,
    help="Logger verbosity",
)
@click.option(
    "--add_logger",
    "-l",
    "additional_loggers",
    type=logger_from_str,
    envvar="ADDITIONAL_LOGGERS",
    multiple=True,
    default=[],
    show_default="[]",
    show_envvar=True,
    help="Add logger in format LEVEL,path/to/logfile",
)
def main(
        port: int,
        host: str,
        logger_verbosity: LogLevel,
        additional_loggers: list[tuple[LogLevel, str]]
):
    """
    Alice skill main function, performs configuration
    via command line parameters and environment variables.
    """
    additional_loggers = list(itertools.chain.from_iterable(additional_loggers))
    if __name__ in ("__main__", "test_fastapi.__main__"):
        web.run_app(app, host=host, port=port)
    else:
        if logger_verbosity != "DEBUG":
            logger.remove()
            logger.add(sys.stderr, level=logger_verbosity)
        for log_level, filename in additional_loggers:
            logger.add(filename, level=log_level)


if __name__ in ("__main__", "test_fastapi.__main__"):
    try_load_envfile(os.environ.get("ENVFILE", ".env"))
    main()
