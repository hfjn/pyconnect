from pyconnect.config import _checkstr_to_checker, SanityError,\
        BaseConfig, SinkConfig, csv_line_reader

from inspect import signature
import pytest
import logging


def test_checkstr_to_checker():
    # for now we just make sure parsing is successful and returns a callable
    # that evaluates correctly

    checker = _checkstr_to_checker('{value}>0')
    assert callable(checker), 'needs to return a callable!'
    checker_signature = signature(checker)
    assert len(checker_signature.parameters) == 1, 'needs 1 argument!'

    # this should not raise
    checker(dict(value=1))

    # this should
    with pytest.raises(SanityError):
        checker(dict(value=-1))


def test_checkstr_fails_on_malicious_code():
    # We cannot actually test for all possible ways to trick the checkstr
    # parser.
    # People implementing the abstract classes have to make sure their checkers
    # don't do bad stuff. In the end they're, hopefully, using the code
    # themselves so they're better off not fooling around.

    injection = 'import os\nos.listdir("/")'

    # CASE1: checkstring is malicious
    checker = _checkstr_to_checker(injection)
    with pytest.raises(Exception):
        checker({})

    # CASE2: value is malicious
    # Okay, who ever is trying to do this, will do so with their own
    # config on their own server... doesn't sound all too likely but what the
    # heck let's check it anyway
    checker = _checkstr_to_checker('{value}>0')

    # CASE2_a: value is a malicious string
    # Values are turned into their representation before being put
    # into the expression, so a simple string won't do it
    with pytest.raises(Exception):
        checker({'value': injection + '\n1'})

    # CASE2_b: value is a malicious object which implements __repr__
    # No Idea how this could possibly happen via a config file, but you
    # never know...
    with pytest.raises(Exception):
        SmartInjector = type('SmartInjector', tuple(),
                             {'__repr__': (lambda self: injection + '\n1')})
        checker({'value': SmartInjector()})


def test_csv_line_reader():
    line = ('localhost,otherhost:1234/asdf, "yetanotherhost/blubb",'
            ' there-is-more/where/that/came%20/from ')

    fields = [
        'localhost', 'otherhost:1234/asdf', 'yetanotherhost/blubb',
        'there-is-more/where/that/came%20/from'
    ]
    reader = csv_line_reader()
    assert fields == reader(line)


def test_host_splitting():
    servers = ('localhost,otherhost:1234/asdf, "user:pw@yetanotherhost/blubb",'
               ' there-is-more/where/that/came%20/from?blah=blubb&foo=bar ')
    servers_list = [
        'localhost', 'otherhost:1234/asdf', 'user:pw@yetanotherhost/blubb',
        'there-is-more/where/that/came%20/from?blah=blubb&foo=bar'
    ]

    config = SinkConfig(bootstrap_servers=servers,
                        schema_registry='localhost', flush_interval=1,
                        group_id='groupid', topics='topics')

    assert config.bootstrap_servers == servers_list


def test_sanity_check_success():
    config = SinkConfig(bootstrap_servers='localhost',
                        schema_registry='localhost', flush_interval=1,
                        group_id='groupid', topics='topics')

    assert config.flush_interval == 1


def test_sanity_check_failure(caplog):
    caplog.set_level(logging.DEBUG)
    with pytest.raises(SanityError):
        BaseConfig(bootstrap_servers='localhost', schema_registry='localhost',
                   flush_interval=-1)


def test_sanity_check_failure_subclass(caplog):
    caplog.set_level(logging.DEBUG)
    with pytest.raises(SanityError):
        SinkConfig(bootstrap_servers='localhost', schema_registry='locahlost',
                   flush_interval=-1, group_id='groupid', topics='topics')