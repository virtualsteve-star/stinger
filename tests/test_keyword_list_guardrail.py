#!/usr/bin/env python3
"""
Unit tests for KeywordListGuardrail
Tests all functionality including inline keywords, file loading, and error handling.
"""

import os
import tempfile
from pathlib import Path

import pytest

from src.stinger.guardrails.keyword_list import KeywordListGuardrail
from src.stinger.utils.exceptions import GuardrailError


@pytest.mark.asyncio
async def test_inline_keywords_basic():
    config = {
        "name": "test_filter",
        "type": "keyword_list",
        "enabled": True,
        "keywords": ["idiot", "stupid", "useless"],
        "on_error": "block",
    }
    guardrail_obj = KeywordListGuardrail(config)
    result = await guardrail_obj.analyze("You are an idiot!")
    assert result.blocked == True
    assert "idiot" in result.reason
    result = await guardrail_obj.analyze("Hello, how are you?")
    assert result.blocked == False
    assert result.reason == "No keyword matches found"


@pytest.mark.asyncio
async def test_inline_keywords_case_sensitive():
    config = {
        "name": "test_filter",
        "type": "keyword_list",
        "enabled": True,
        "keywords": ["Idiot", "Stupid"],
        "case_sensitive": True,
        "on_error": "block",
    }
    guardrail_obj = KeywordListGuardrail(config)
    result = await guardrail_obj.analyze("You are an Idiot!")
    assert result.blocked == True
    result = await guardrail_obj.analyze("You are an idiot!")
    assert result.blocked == False


@pytest.mark.asyncio
async def test_phrase_matching():
    config = {
        "name": "test_filter",
        "type": "keyword_list",
        "enabled": True,
        "keywords": ["shut up", "go away", "leave me alone"],
        "on_error": "block",
    }
    guardrail_obj = KeywordListGuardrail(config)
    result = await guardrail_obj.analyze("Please shut up and listen!")
    assert result.blocked == True
    assert "shut up" in result.reason
    result = await guardrail_obj.analyze("Please shut the door!")
    assert result.blocked == False


@pytest.mark.asyncio
async def test_file_loading_basic():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("idiot\nstupid\nuseless\n")
        temp_file = f.name
    try:
        config = {
            "name": "test_filter",
            "type": "keyword_list",
            "enabled": True,
            "keywords_file": temp_file,
            "on_error": "block",
        }
        guardrail_obj = KeywordListGuardrail(config)
        result = await guardrail_obj.analyze("You are an idiot!")
        assert result.blocked == True
        result = await guardrail_obj.analyze("Hello, how are you?")
        assert result.blocked == False
    finally:
        os.unlink(temp_file)


@pytest.mark.asyncio
async def test_multiple_matches():
    config = {
        "name": "test_filter",
        "type": "keyword_list",
        "enabled": True,
        "keywords": ["idiot", "stupid", "useless"],
        "on_error": "block",
    }
    guardrail_obj = KeywordListGuardrail(config)
    result = await guardrail_obj.analyze("You are an idiot and stupid!")
    assert result.blocked == True
    assert "idiot" in result.reason
    assert "stupid" in result.reason
