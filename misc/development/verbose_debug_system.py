"""
Verbose Debug and CLI Mode System for ConcLand
Provides detailed logging, LLM-friendly output, and command-line interface
"""
import sys
import logging
import json
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
import traceback

class LogLevel(Enum):
    """Logging levels"""
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3
    CRITICAL = 4

class OutputFormat(Enum):
    """Output formats for verbose mode"""
    TEXT = "text"
    JSON = "json"
    STRUCTURED = "structured"

@dataclass
class GameStateSnapshot:
    """Snapshot of game state for debugging"""
    timestamp: int
    frame_count: int
    funds: int
    population: int
    employment_rate: float
    gdp: int
    rci_demand: Dict[str, int]
    view_mode: int
    selected_tool: int
    cursor_position: tuple
    map_size: int

@dataclass
class SystemEvent:
    """Record of a system event"""
    event_type: str
    timestamp: int
    source: str
    data: Dict[str, Any]
    stack_trace: Optional[str] = None

class VerboseDebugSystem:
    """Comprehensive debug and logging system"""
    def __init__(self, enabled: bool = False, log_file: str = "concland_debug.log"):
        self.enabled = enabled
        self.log_file = log_file
        self.current_level = LogLevel.DEBUG

        # Event tracking
        self.events: List[SystemEvent] = []
        self.max_events = 1000

        # Performance monitoring
        self.frame_times: List[float] = []
        self.max_frame_times = 300

        # State snapshots
        self.state_snapshots: List[GameStateSnapshot] = []
        self.max_snapshots = 50

        # Counters
        self.counters: Dict[str, int] = {}

        # Setup logging
        self._setup_logging()

    def _setup_logging(self):
        """Setup Python logging system"""
        if not self.enabled:
            return

        # Create logger
        self.logger = logging.getLogger("ConcLand")
        self.logger.setLevel(logging.DEBUG)

        # File handler
        try:
            file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)

            # Console handler
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)

            # Formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)

            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)

        except Exception as e:
            print(f"Failed to setup logging: {e}")

    def enable(self):
        """Enable verbose debug mode"""
        self.enabled = True
        self._setup_logging()
        self.log(LogLevel.INFO, "VerboseDebugSystem", "Debug mode enabled")

    def disable(self):
        """Disable verbose debug mode"""
        self.log(LogLevel.INFO, "VerboseDebugSystem", "Debug mode disabled")
        self.enabled = False

    def log(self, level: LogLevel, source: str, message: str, data: Optional[Dict] = None):
        """Log a message with specified level"""
        if not self.enabled:
            return

        level_map = {
            LogLevel.DEBUG: logging.DEBUG,
            LogLevel.INFO: logging.INFO,
            LogLevel.WARNING: logging.WARNING,
            LogLevel.ERROR: logging.ERROR,
            LogLevel.CRITICAL: logging.CRITICAL
        }

        # Format message
        log_message = f"[{source}] {message}"
        if data:
            log_message += f" | Data: {json.dumps(data, ensure_ascii=False)}"

        # Log to Python logger
        if hasattr(self, 'logger'):
            self.logger.log(level_map[level], log_message)

        # Record event
        event = SystemEvent(
            event_type=level.name,
            timestamp=0,  # Would use actual timestamp
            source=source,
            data=data or {}
        )
        self._add_event(event)

        # Update counter
        counter_key = f"{source}_{level.name}"
        self.counters[counter_key] = self.counters.get(counter_key, 0) + 1

    def _add_event(self, event: SystemEvent):
        """Add event to history"""
        self.events.append(event)

        # Trim if necessary
        if len(self.events) > self.max_events:
            self.events = self.events[-self.max_events:]

    def record_frame_time(self, frame_time: float):
        """Record frame processing time"""
        self.frame_times.append(frame_time)
        if len(self.frame_times) > self.max_frame_times:
            self.frame_times = self.frame_times[-self.max_frame_times:]

    def get_performance_stats(self) -> Dict[str, float]:
        """Get performance statistics"""
        if not self.frame_times:
            return {"avg_fps": 0, "min_fps": 0, "max_fps": 0}

        avg_time = sum(self.frame_times) / len(self.frame_times)
        min_time = min(self.frame_times)
        max_time = max(self.frame_times)

        return {
            "avg_fps": 1.0 / avg_time if avg_time > 0 else 0,
            "min_fps": 1.0 / max_time if max_time > 0 else 0,
            "max_fps": 1.0 / min_time if min_time > 0 else 0,
            "avg_frame_time": avg_time,
            "samples": len(self.frame_times)
        }

    def capture_state(self, game_state: GameStateSnapshot):
        """Capture game state snapshot"""
        self.state_snapshots.append(game_state)

        if len(self.state_snapshots) > self.max_snapshots:
            self.state_snapshots = self.state_snapshots[-self.max_snapshots:]

    def get_recent_events(self, count: int = 10) -> List[SystemEvent]:
        """Get recent events"""
        return self.events[-count:]

    def get_counters(self) -> Dict[str, int]:
        """Get all counters"""
        return self.counters.copy()

    def export_debug_data(self) -> Dict[str, Any]:
        """Export all debug data as dictionary"""
        return {
            "events": [asdict(event) for event in self.events[-100:]],
            "performance": self.get_performance_stats(),
            "counters": self.counters,
            "snapshots": [asdict(snapshot) for snapshot in self.state_snapshots[-10:]]
        }

class CLIMode:
    """Command-line interface mode for LLM interaction"""
    def __init__(self, verbose_system: VerboseDebugSystem):
        self.verbose = verbose_system
        self.active = False
        self.command_history: List[str] = []
        self.max_history = 100

        # Command registry
        self.commands: Dict[str, Callable] = {
            'help': self.cmd_help,
            'status': self.cmd_status,
            'info': self.cmd_info,
            'set': self.cmd_set,
            'get': self.cmd_get,
            'log': self.cmd_log,
            'export': self.cmd_export,
            'perf': self.cmd_perf,
            'clear': self.cmd_clear,
            'exit': self.cmd_exit
        }

    def activate(self):
        """Activate CLI mode"""
        self.active = True
        print("=== ConcLand CLI Mode ===")
        print("Type 'help' for available commands")
        self.verbose.log(LogLevel.INFO, "CLI", "CLI mode activated")

    def deactivate(self):
        """Deactivate CLI mode"""
        self.active = False
        self.verbose.log(LogLevel.INFO, "CLI", "CLI mode deactivated")

    def process_command(self, command: str) -> str:
        """Process a CLI command"""
        # Add to history
        self.command_history.append(command)
        if len(self.command_history) > self.max_history:
            self.command_history = self.command_history[-self.max_history:]

        # Parse command
        parts = command.strip().split()
        if not parts:
            return "No command provided"

        cmd_name = parts[0].lower()
        args = parts[1:]

        # Execute command
        if cmd_name in self.commands:
            try:
                result = self.commands[cmd_name](args)
                self.verbose.log(LogLevel.INFO, "CLI", f"Command: {cmd_name}", {"args": args, "result": result})
                return result
            except Exception as e:
                error_msg = f"Error executing command: {str(e)}"
                self.verbose.log(LogLevel.ERROR, "CLI", error_msg, {"command": cmd_name, "traceback": traceback.format_exc()})
                return error_msg
        else:
            return f"Unknown command: {cmd_name}. Type 'help' for available commands."

    # Command implementations
    def cmd_help(self, args: List[str]) -> str:
        """Show help information"""
        help_text = """
Available Commands:
  help           - Show this help message
  status         - Show current game status
  info <topic>   - Get information about a topic
  set <var> <val> - Set a variable
  get <var>      - Get a variable value
  log [level]    - Show or set log level
  export [file]  - Export debug data to file
  perf           - Show performance statistics
  clear          - Clear screen/history
  exit           - Exit CLI mode

Examples:
  status
  info water_supply
  set funds 1000000
  get population
  export debug_data.json
"""
        return help_text.strip()

    def cmd_status(self, args: List[str]) -> str:
        """Show current game status"""
        # This would integrate with actual game state
        return """
ConcLand Game Status:
  Mode: Running
  FPS: 60
  Population: 1000
  Funds: ¥50,000
  Employment: 85%
  RCI Demand: R:+5 C:-2 I:+3
"""

    def cmd_info(self, args: List[str]) -> str:
        """Get information about a topic"""
        if not args:
            return "Usage: info <topic>\nAvailable topics: water_supply, underground, crime, fire, city_status, all"

        topic = args[0]
        # This would integrate with actual game systems
        info_map = {
            "water_supply": "Water Supply: 3.05% coverage, 100 supply, 0 demand",
            "underground": "Underground: 1 station, development level 0",
            "crime": "Crime: Current level - Town",
            "fire": "Fire: 1 station, 0 total fires",
            "city_status": "City Status: Town (町)",
            "all": "All systems operational"
        }
        return info_map.get(topic, f"Unknown topic: {topic}")

    def cmd_set(self, args: List[str]) -> str:
        """Set a variable value"""
        if len(args) < 2:
            return "Usage: set <variable> <value>"
        var, value = args[0], args[1]
        # This would integrate with actual game state
        return f"Set {var} = {value}"

    def cmd_get(self, args: List[str]) -> str:
        """Get a variable value"""
        if not args:
            return "Usage: get <variable>"
        var = args[0]
        # This would integrate with actual game state
        return f"{var} = <value>"

    def cmd_log(self, args: List[str]) -> str:
        """Show or set log level"""
        if not args:
            return f"Current log level: {self.verbose.current_level.name}"
        try:
            level = LogLevel[args[0].upper()]
            self.verbose.current_level = level
            return f"Log level set to {level.name}"
        except KeyError:
            return f"Invalid level. Available: {', '.join(l.name for l in LogLevel)}"

    def cmd_export(self, args: List[str]) -> str:
        """Export debug data"""
        filename = args[0] if args else "debug_export.json"
        try:
            data = self.verbose.export_debug_data()
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return f"Exported debug data to {filename}"
        except Exception as e:
            return f"Export failed: {str(e)}"

    def cmd_perf(self, args: List[str]) -> str:
        """Show performance statistics"""
        stats = self.verbose.get_performance_stats()
        return f"""
Performance Statistics:
  Average FPS: {stats['avg_fps']:.1f}
  Min FPS: {stats['min_fps']:.1f}
  Max FPS: {stats['max_fps']:.1f}
  Average Frame Time: {stats['avg_frame_time']*1000:.2f}ms
  Samples: {stats['samples']}
"""

    def cmd_clear(self, args: List[str]) -> str:
        """Clear screen or history"""
        if "history" in args:
            self.command_history.clear()
            return "Command history cleared"
        else:
            return "\n" * 50  # Clear screen effect

    def cmd_exit(self, args: List[str]) -> str:
        """Exit CLI mode"""
        self.deactivate()
        return "CLI mode deactivated. Return to normal game mode."

class LLMInterface:
    """LLM-friendly interface for structured data output"""
    def __init__(self, verbose_system: VerboseDebugSystem):
        self.verbose = verbose_system
        self.output_format = OutputFormat.STRUCTURED

    def set_format(self, format: OutputFormat):
        """Set output format"""
        self.output_format = format

    def format_game_state(self, state: GameStateSnapshot) -> str:
        """Format game state for LLM consumption"""
        if self.output_format == OutputFormat.JSON:
            return json.dumps(asdict(state), indent=2, ensure_ascii=False)
        elif self.output_format == OutputFormat.STRUCTURED:
            return self._format_structured(state)
        else:  # TEXT
            return self._format_text(state)

    def _format_structured(self, state: GameStateSnapshot) -> str:
        """Format as structured text"""
        return f"""
=== ConcLand Game State ===
Timestamp: {state.timestamp}
Frame: {state.frame_count}

Economy:
  Funds: ¥{state.funds:,}
  GDP: ¥{state.gdp:,}
  Employment: {state.employment_rate*100:.1f}%

Population:
  Total: {state.population:,}

Development:
  RCI Demand: R={state.rci_demand.get('R', 0):+d} C={state.rci_demand.get('C', 0):+d} I={state.rci_demand.get('I', 0):+d}

Interface:
  View Mode: {state.view_mode}
  Selected Tool: {state.selected_tool}
  Cursor: ({state.cursor_position[0]}, {state.cursor_position[1]})

Map:
  Size: {state.map_size}x{state.map_size}
"""

    def _format_text(self, state: GameStateSnapshot) -> str:
        """Format as plain text"""
        return f"ConcLand State - Frame {state.frame_count}: Funds ¥{state.funds}, Pop {state.population}, Employment {state.employment_rate*100:.1f}%"

    def format_events(self, events: List[SystemEvent]) -> str:
        """Format events for LLM consumption"""
        if self.output_format == OutputFormat.JSON:
            return json.dumps([asdict(e) for e in events], indent=2, ensure_ascii=False)
        else:
            lines = ["=== Recent Events ==="]
            for event in events:
                lines.append(f"[{event.event_type}] {event.source}: {json.dumps(event.data)}")
            return "\n".join(lines)

# Integration example
class IntegratedDebugSystem:
    """Integrated debug system combining all components"""
    def __init__(self):
        self.verbose = VerboseDebugSystem(enabled=False)
        self.cli = CLIMode(self.verbose)
        self.llm = LLMInterface(self.verbose)

    def enable_debug(self):
        """Enable full debug mode"""
        self.verbose.enable()
        self.cli.activate()

    def process_command(self, command: str) -> str:
        """Process CLI command"""
        return self.cli.process_command(command)

    def get_llm_output(self, state: GameStateSnapshot) -> str:
        """Get LLM-friendly output"""
        return self.llm.format_game_state(state)

# Example usage
if __name__ == "__main__":
    # Create integrated debug system
    debug = IntegratedDebugSystem()
    debug.enable_debug()

    # Simulate some activity
    debug.verbose.log(LogLevel.INFO, "Test", "Testing verbose system")
    debug.verbose.log(LogLevel.WARNING, "Test", "Warning message", {"value": 42})
    debug.verbose.record_frame_time(0.016)  # 60 FPS
    debug.verbose.record_frame_time(0.020)

    # Capture state
    state = GameStateSnapshot(
        timestamp=1234567890,
        frame_count=1000,
        funds=50000,
        population=1000,
        employment_rate=0.85,
        gdp=1000000,
        rci_demand={"R": 5, "C": -2, "I": 3},
        view_mode=0,
        selected_tool=1,
        cursor_position=(50, 50),
        map_size=100
    )
    debug.verbose.capture_state(state)

    # CLI commands
    print("\n=== CLI Commands ===")
    print(debug.process_command("help"))
    print(debug.process_command("status"))
    print(debug.process_command("perf"))

    # LLM output
    print("\n=== LLM Output ===")
    print(debug.get_llm_output(state))

    # Export
    print(debug.process_command("export test_debug.json"))
