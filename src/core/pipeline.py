from typing import List
from dataclasses import dataclass
import os
import time
import threading
from pathlib import Path
from .base_filter import BaseFilter, FilterResult
from .config import ConfigLoader
from .hot_reload import HotReloadManager
from ..utils.exceptions import PipelineError

@dataclass
class PipelineResult:
    action: str
    reason: str
    filter_results: List[FilterResult]
    content: str

class FilterPipeline:
    def __init__(self, filters: List[BaseFilter], debug: bool = False):
        self.filters = [f for f in filters if f.enabled]
        self.debug = debug
    
    async def process(self, content: str) -> PipelineResult:
        """Process content through all filters."""
        if not content:
            content = ""
        
        filter_results = []
        highest_action = 'allow'
        highest_reason = 'All filters passed'
        
        for filter_obj in self.filters:
            try:
                result = await filter_obj.run_safe(content)
                filter_results.append(result)
                if self.debug:
                    print(f"[Pipeline][DEBUG] {result.filter_name} ({result.filter_type}): {result.action} ({result.reason})")
                else:
                    print(f"[Pipeline] {result.filter_name}: {result.action} ({result.reason})")
                
                # If filter blocks, stop processing
                if result.action == 'block':
                    return PipelineResult(
                        action='block',
                        reason=f"{result.filter_name} ({result.filter_type}): {result.reason}",
                        filter_results=filter_results,
                        content=content
                    )
                
                # Update content if modified
                if result.modified_content is not None:
                    content = result.modified_content
                    
                if result.action == 'warn' and highest_action != 'warn':
                    highest_action = 'warn'
                    highest_reason = f"{result.filter_name} ({result.filter_type}): {result.reason}"
                
            except Exception as e:
                # If filter fails and is configured to block on error
                if filter_obj.on_error == 'block':
                    return PipelineResult(
                        action='block',
                        reason=f'Pipeline error: {str(e)}',
                        filter_results=filter_results,
                        content=content
                    )
        
        # If we get here, all filters passed
        return PipelineResult(
            action=highest_action,
            reason=highest_reason,
            filter_results=filter_results,
            content=content
        )

class HotReloadPipeline:
    """Pipeline with hot reload capability for configuration changes."""
    
    def __init__(self, config_path: str, debug: bool = False):
        self.config_path = config_path
        self.debug = debug
        self.pipeline = None
        self.config_loader = ConfigLoader()
        self.hot_reload_manager = HotReloadManager()
        self._lock = threading.Lock()
        
        # Initial load
        self._reload_config()
        
        # Start hot reload if enabled
        if self._should_enable_hot_reload():
            self._start_hot_reload()
    
    def _should_enable_hot_reload(self) -> bool:
        """Check if hot reload should be enabled."""
        return (
            '--hot-reload' in os.sys.argv or
            os.environ.get('STINGER_HOT_RELOAD') == '1'
        )
    
    def _start_hot_reload(self):
        """Start the hot reload system."""
        try:
            # Get initial config
            initial_config = self.config_loader.load(self.config_path)
            
            # Start watching the config file
            success = self.hot_reload_manager.start_watching(
                self.config_path,
                initial_config,
                self._on_config_changed
            )
            
            if success and self.debug:
                print(f"[HotReload] Started watching: {self.config_path}")
            elif not success:
                print(f"[HotReload] Failed to start watching: {self.config_path}")
                
        except Exception as e:
            if self.debug:
                print(f"[HotReload] Error starting hot reload: {e}")
    
    def _on_config_changed(self, new_config: dict):
        """Callback when configuration changes."""
        try:
            with self._lock:
                # Validate and reload the configuration
                if self.hot_reload_manager.reload_config(new_config):
                    # Rebuild the pipeline with new config
                    filters = self.config_loader.build_filters(new_config)
                    self.pipeline = FilterPipeline(filters, debug=self.debug)
                    
                    if self.debug:
                        print(f"[HotReload] Pipeline rebuilt with {len(filters)} filters")
                        print(f"[HotReload] Active filters: {[f.name for f in filters if f.enabled]}")
                else:
                    if self.debug:
                        print(f"[HotReload] Configuration reload failed, keeping previous pipeline")
                        
        except Exception as e:
            if self.debug:
                print(f"[HotReload] Error rebuilding pipeline: {e}")
    
    def _reload_config(self):
        """Reload configuration and rebuild pipeline."""
        try:
            with self._lock:
                config = self.config_loader.load(self.config_path)
                filters = self.config_loader.build_filters(config)
                self.pipeline = FilterPipeline(filters, debug=self.debug)
                
                if self.debug:
                    print(f"[HotReload] Initial configuration loaded from {self.config_path}")
                    print(f"[HotReload] Active filters: {[f.name for f in filters if f.enabled]}")
                    
        except Exception as e:
            if self.debug:
                print(f"[HotReload] Failed to load initial config: {e}")
            raise PipelineError(f"Failed to load configuration: {e}")
    
    async def process(self, content: str) -> PipelineResult:
        """Process content through filters, with hot reload capability."""
        # Process with current pipeline
        if self.pipeline is None:
            raise PipelineError("No pipeline available")
        
        return await self.pipeline.process(content)
    
    def stop(self):
        """Stop the hot reload system."""
        self.hot_reload_manager.stop_watching()
        if self.debug:
            print("[HotReload] Hot reload stopped")
    
    def get_status(self) -> dict:
        """Get hot reload status."""
        return self.hot_reload_manager.get_status() 