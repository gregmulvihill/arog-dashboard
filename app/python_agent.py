"""
Python Agent - Interactive Python execution with history
Notebook-style interface for task execution
"""
import sys
import io
import traceback
import json
from datetime import datetime
from typing import Dict, List
from pathlib import Path
from contextlib import redirect_stdout, redirect_stderr


class PythonAgent:
    """Interactive Python agent with execution history"""

    def __init__(self, history_file: str = "sessions/agent_history.json"):
        self.history_file = Path(history_file)
        self.history_file.parent.mkdir(parents=True, exist_ok=True)

        # Persistent namespace for code execution
        self.namespace = {
            '__name__': '__main__',
            '__builtins__': __builtins__,
        }

        # Pre-import commonly used libraries
        self._init_namespace()

        # Load history
        self.history = self._load_history()

    def _init_namespace(self):
        """Pre-load common libraries into namespace"""
        import_code = """
import os
import sys
import json
import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional

# Data manipulation
try:
    import pandas as pd
    import numpy as np
except ImportError:
    pass

# Add utility functions
def help_agent():
    '''Available pre-loaded modules and functions'''
    return {
        'modules': ['os', 'sys', 'json', 're', 'Path', 'datetime'],
        'functions': ['help_agent', 'list_vars'],
        'note': 'All executed code persists in namespace between runs'
    }

def list_vars():
    '''List all variables in current namespace'''
    return {k: type(v).__name__ for k, v in globals().items()
            if not k.startswith('_')}
"""
        try:
            exec(import_code, self.namespace)
        except Exception as e:
            print(f"Namespace initialization warning: {e}")

    def _load_history(self) -> List[Dict]:
        """Load execution history from file"""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []

    def _save_history(self):
        """Save execution history to file"""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.history[-1000:], f, indent=2)  # Keep last 1000 entries
        except Exception as e:
            print(f"Failed to save history: {e}")

    async def execute(self, code: str) -> Dict:
        """Execute Python code and return result"""
        timestamp = datetime.now().isoformat()

        # Capture stdout and stderr
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()

        result = {
            'timestamp': timestamp,
            'code': code,
            'output': None,
            'stdout': None,
            'stderr': None,
            'error': None,
            'success': False
        }

        try:
            # Redirect output
            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                # Try to evaluate as expression first (for interactive results)
                try:
                    output = eval(code, self.namespace)
                    result['output'] = repr(output) if output is not None else None
                    result['success'] = True
                except SyntaxError:
                    # If not an expression, execute as statement
                    exec(code, self.namespace)
                    result['success'] = True

            # Capture any printed output
            stdout_text = stdout_capture.getvalue()
            stderr_text = stderr_capture.getvalue()

            if stdout_text:
                result['stdout'] = stdout_text
            if stderr_text:
                result['stderr'] = stderr_text

        except Exception as e:
            result['error'] = {
                'type': type(e).__name__,
                'message': str(e),
                'traceback': traceback.format_exc()
            }
            result['success'] = False

        # Add to history
        self.history.append(result)
        self._save_history()

        return result

    async def get_history(self, limit: int = 50) -> List[Dict]:
        """Get execution history"""
        return self.history[-limit:]

    async def clear_history(self):
        """Clear execution history"""
        self.history = []
        if self.history_file.exists():
            self.history_file.unlink()

    async def reset_namespace(self):
        """Reset the execution namespace"""
        self.namespace.clear()
        self._init_namespace()

    async def cleanup(self):
        """Cleanup resources"""
        self._save_history()
