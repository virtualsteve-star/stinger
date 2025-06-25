#!/usr/bin/env python3
"""
Unit tests for KeywordListFilter
Tests all functionality including inline keywords, file loading, and error handling.
"""

import pytest
import tempfile
import os
from pathlib import Path
from src.filters.keyword_list import KeywordListFilter
from src.utils.exceptions import FilterError

@pytest.mark.asyncio
async def test_inline_keywords_basic():
    config = {
        'name': 'test_filter',
        'type': 'keyword_list',
        'enabled': True,
        'keywords': ['idiot', 'stupid', 'useless'],
        'on_error': 'block'
    }
    filter_obj = KeywordListFilter(config)
    result = await filter_obj.run("You are an idiot!")
    assert result.action == 'block'
    assert 'idiot' in result.reason
    result = await filter_obj.run("Hello, how are you?")
    assert result.action == 'allow'
    assert result.reason == 'no keyword matches'

@pytest.mark.asyncio
async def test_inline_keywords_case_sensitive():
    config = {
        'name': 'test_filter',
        'type': 'keyword_list',
        'enabled': True,
        'keywords': ['Idiot', 'Stupid'],
        'case_sensitive': True,
        'on_error': 'block'
    }
    filter_obj = KeywordListFilter(config)
    result = await filter_obj.run("You are an Idiot!")
    assert result.action == 'block'
    result = await filter_obj.run("You are an idiot!")
    assert result.action == 'allow'

@pytest.mark.asyncio
async def test_phrase_matching():
    config = {
        'name': 'test_filter',
        'type': 'keyword_list',
        'enabled': True,
        'keywords': ['shut up', 'go away', 'leave me alone'],
        'on_error': 'block'
    }
    filter_obj = KeywordListFilter(config)
    result = await filter_obj.run("Please shut up and listen!")
    assert result.action == 'block'
    assert 'shut up' in result.reason
    result = await filter_obj.run("Please shut the door!")
    assert result.action == 'allow'

@pytest.mark.asyncio
async def test_file_loading_basic():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("idiot\nstupid\nuseless\n")
        temp_file = f.name
    try:
        config = {
            'name': 'test_filter',
            'type': 'keyword_list',
            'enabled': True,
            'keywords_file': temp_file,
            'on_error': 'block'
        }
        filter_obj = KeywordListFilter(config)
        result = await filter_obj.run("You are an idiot!")
        assert result.action == 'block'
        result = await filter_obj.run("Hello, how are you?")
        assert result.action == 'allow'
    finally:
        os.unlink(temp_file)

@pytest.mark.asyncio
async def test_multiple_matches():
    config = {
        'name': 'test_filter',
        'type': 'keyword_list',
        'enabled': True,
        'keywords': ['idiot', 'stupid', 'useless'],
        'on_error': 'block'
    }
    filter_obj = KeywordListFilter(config)
    result = await filter_obj.run("You are an idiot and stupid!")
    assert result.action == 'block'
    assert 'idiot' in result.reason
    assert 'stupid' in result.reason 