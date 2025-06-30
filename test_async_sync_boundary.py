#!/usr/bin/env python3
"""
Test to verify that the async/sync boundary fix works correctly.
"""

import asyncio
import pytest
from src.stinger.core.pipeline import GuardrailPipeline


async def test_sync_method_called_from_async_context():
    """Test that calling sync methods from async context raises appropriate error."""
    pipeline = GuardrailPipeline.from_preset("customer_service")
    
    # This should raise a RuntimeError because we're calling a sync method from async context
    with pytest.raises(RuntimeError, match="Cannot call input pipeline sync method from async context"):
        pipeline.check_input("Hello, world!")
    
    # This should also raise a RuntimeError
    with pytest.raises(RuntimeError, match="Cannot call output pipeline sync method from async context"):
        pipeline.check_output("Here's your response")


def test_sync_method_called_from_sync_context():
    """Test that calling sync methods from sync context works correctly."""
    pipeline = GuardrailPipeline.from_preset("customer_service")
    
    # This should work fine
    result = pipeline.check_input("Hello, world!")
    assert isinstance(result, dict)
    assert 'blocked' in result
    
    # This should also work fine
    result = pipeline.check_output("Here's your response")
    assert isinstance(result, dict)
    assert 'blocked' in result


async def test_async_method_called_from_async_context():
    """Test that calling async methods from async context works correctly."""
    pipeline = GuardrailPipeline.from_preset("customer_service")
    
    # This should work fine
    result = await pipeline.check_input_async("Hello, world!")
    assert isinstance(result, dict)
    assert 'blocked' in result
    
    # This should also work fine
    result = await pipeline.check_output_async("Here's your response")
    assert isinstance(result, dict)
    assert 'blocked' in result


if __name__ == "__main__":
    # Run the sync context test
    print("Testing sync method from sync context...")
    test_sync_method_called_from_sync_context()
    print("✓ Sync method from sync context works correctly")
    
    # Run the async context test
    print("Testing sync method from async context...")
    asyncio.run(test_sync_method_called_from_async_context())
    print("✓ Sync method from async context properly raises error")
    
    # Run the async method test
    print("Testing async method from async context...")
    asyncio.run(test_async_method_called_from_async_context())
    print("✓ Async method from async context works correctly")
    
    print("\nAll tests passed! The async/sync boundary fix is working correctly.") 