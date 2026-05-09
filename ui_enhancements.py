"""
UI/UX Enhancement System for ConcLand
Provides notifications, tooltips, feedback effects, and improved user experience
"""
import pyxel
import random
import math
from typing import List, Dict, Optional, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum

class NotificationType(Enum):
    """Types of notifications"""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    ACHIEVEMENT = "achievement"

@dataclass
class Notification:
    """Single notification"""
    message: str
    japanese_message: str
    type: NotificationType
    duration: int = 180  # frames (3 seconds at 60 FPS)
    timestamp: int = 0
    action_callback: Optional[Callable] = None

    def get_display_message(self, use_japanese: bool) -> str:
        """Get message in appropriate language"""
        return self.japanese_message if use_japanese else self.message

@dataclass
class TooltipContent:
    """Tooltip content"""
    title: str
    japanese_title: str
    description: str
    japanese_description: str
    stats: Dict[str, str] = field(default_factory=dict)

class NotificationSystem:
    """Manages game notifications and toasts"""
    def __init__(self, screen_width: int, screen_height: int, max_notifications: int = 3):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.max_notifications = max_notifications
        self.notifications: List[Notification] = []
        self.current_frame = 0

    def add_notification(self, notification: Notification):
        """Add a new notification"""
        notification.timestamp = self.current_frame
        self.notifications.insert(0, notification)  # Add to top

        # Remove old notifications
        if len(self.notifications) > self.max_notifications:
            self.notifications = self.notifications[:self.max_notifications]

    def notify(self, message: str, jp_message: str, notif_type: NotificationType = NotificationType.INFO,
               duration: int = 180, callback: Optional[Callable] = None):
        """Convenience method to add a notification"""
        notification = Notification(
            message=message,
            japanese_message=jp_message,
            type=notif_type,
            duration=duration,
            action_callback=callback
        )
        self.add_notification(notification)

    def update(self):
        """Update notification timers"""
        self.current_frame += 1

        # Remove expired notifications
        self.notifications = [
            n for n in self.notifications
            if self.current_frame - n.timestamp < n.duration
        ]

    def draw(self, use_japanese: bool = True):
        """Draw all active notifications"""
        y_offset = 10

        for i, notification in enumerate(self.notifications):
            # Calculate position (stack from top)
            y_pos = y_offset + i * 35

            # Calculate alpha based on remaining time
            age = self.current_frame - notification.timestamp
            remaining = notification.duration - age
            alpha = min(1.0, remaining / 30.0) if remaining < 30 else 1.0

            self._draw_notification(notification, y_pos, alpha, use_japanese)

    def _draw_notification(self, notification: Notification, y: int, alpha: float, use_japanese: bool):
        """Draw a single notification"""
        # Width based on message length
        message = notification.get_display_message(use_japanese)
        width = max(250, len(message) * 4 + 40)
        height = 30
        x = (self.screen_width - width) // 2

        # Color based on type
        color_map = {
            NotificationType.INFO: (6, 7),      # Gray background, white text
            NotificationType.SUCCESS: (3, 10),  # Green background, light green text
            NotificationType.WARNING: (9, 8),  # Orange background, yellow text
            NotificationType.ERROR: (8, 9),     # Red background, orange text
            NotificationType.ACHIEVEMENT: (13, 11)  # Purple background, pink text
        }

        bg_color, text_color = color_map.get(notification.type, (6, 7))

        # Draw notification background with rounded corners effect
        pyxel.rect(x, y, width, height, bg_color)
        pyxel.rectb(x, y, width, height, text_color)

        # Draw icon based on type
        icon_x = x + 8
        icon_y = y + 8
        self._draw_notification_icon(notification.type, icon_x, icon_y, text_color)

        # Draw message
        text_x = x + 30
        text_y = y + 10
        pyxel.text(text_x, text_y, message, text_color)

        # Draw progress bar
        if alpha < 1.0:
            bar_width = int(width * alpha)
            pyxel.rect(x, y + height - 2, bar_width, 2, text_color)

    def _draw_notification_icon(self, notif_type: NotificationType, x: int, y: int, color: int):
        """Draw icon for notification type"""
        if notif_type == NotificationType.INFO:
            # Circle with 'i'
            pyxel.circ(x + 4, y + 4, 6, color)
            pyxel.text(x + 2, y + 2, "i", 0)

        elif notif_type == NotificationType.SUCCESS:
            # Checkmark
            pyxel.text(x, y, "✓", color)

        elif notif_type == NotificationType.WARNING:
            # Exclamation mark
            pyxel.text(x + 2, y, "!", color)

        elif notif_type == NotificationType.ERROR:
            # X mark
            pyxel.text(x + 1, y + 1, "×", color)

        elif notif_type == NotificationType.ACHIEVEMENT:
            # Star
            self._draw_star(x + 4, y + 4, 6, color)

    def _draw_star(self, cx: int, cy: int, size: int, color: int):
        """Draw star shape"""
        points = []
        for i in range(10):
            angle = math.pi * 2 * i / 10 - math.pi / 2
            r = size if i % 2 == 0 else size // 2
            x = cx + int(math.cos(angle) * r)
            y = cy + int(math.sin(angle) * r)
            points.append((x, y))

        for i in range(0, len(points), 2):
            if i + 1 < len(points):
                pyxel.line(points[i][0], points[i][1], points[i + 1][0], points[i + 1][1], color)

class TooltipSystem:
    """Manages tooltips for game elements"""
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.current_tooltip: Optional[TooltipContent] = None
        self.tooltip_pos: Tuple[int, int] = (0, 0)
        self.show_delay = 30  # frames before showing tooltip
        self.current_delay = 0

    def set_tooltip(self, content: TooltipContent, x: int, y: int):
        """Set current tooltip"""
        self.current_tooltip = content
        self.tooltip_pos = (x, y)
        self.current_delay = 0

    def clear_tooltip(self):
        """Clear current tooltip"""
        self.current_tooltip = None
        self.current_delay = 0

    def update(self, mouse_x: int, mouse_y: int):
        """Update tooltip state"""
        if self.current_tooltip:
            self.current_delay += 1

            # Auto-hide after delay
            if self.current_delay > 300:  # 5 seconds
                self.clear_tooltip()

    def draw(self, use_japanese: bool = True):
        """Draw tooltip if ready"""
        if self.current_tooltip and self.current_delay >= self.show_delay:
            self._draw_tooltip(self.current_tooltip, self.tooltip_pos, use_japanese)

    def _draw_tooltip(self, content: TooltipContent, pos: Tuple[int, int], use_japanese: bool):
        """Draw tooltip content"""
        title = content.japanese_title if use_japanese else content.title
        description = content.japanese_description if use_japanese else content.description

        # Calculate dimensions
        padding = 8
        line_height = 10
        title_width = len(title) * 4
        desc_lines = self._wrap_text(description, 50)
        desc_height = len(desc_lines) * line_height

        width = max(title_width, max(len(line) * 4 for line in desc_lines)) + padding * 2
        height = 12 + desc_height + padding * 2

        # Position tooltip (avoid screen edges)
        x, y = pos
        x = min(x, self.screen_width - width - 10)
        y = min(y, self.screen_height - height - 10)
        if x < 10: x = 10
        if y < 10: y = 10

        # Draw background
        pyxel.rect(x, y, width, height, 0)
        pyxel.rectb(x, y, width, height, 7)

        # Draw title
        pyxel.text(x + padding, y + padding, title, 7)

        # Draw description
        for i, line in enumerate(desc_lines):
            pyxel.text(x + padding, y + padding + 12 + i * line_height, line, 6)

        # Draw stats if present
        if content.stats:
            stat_y = y + padding + 12 + desc_height + 5
            for i, (key, value) in enumerate(content.stats.items()):
                stat_text = f"{key}: {value}"
                pyxel.text(x + padding, stat_y + i * line_height, stat_text, 10)

    def _wrap_text(self, text: str, max_width: int) -> List[str]:
        """Wrap text to fit width"""
        lines = []
        current_line = ""

        for word in text.split():
            if len(current_line) + len(word) + 1 <= max_width:
                if current_line:
                    current_line += " " + word
                else:
                    current_line = word
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        return lines

class FeedbackEffect:
    """Visual feedback effect"""
    def __init__(self, x: int, y: int, effect_type: str, duration: int = 30):
        self.x = x
        self.y = y
        self.effect_type = effect_type  # "success", "error", "build", "demolish"
        self.duration = duration
        self.age = 0
        self.max_age = duration

    def update(self):
        """Update effect"""
        self.age += 1
        return self.age < self.duration

    def draw(self):
        """Draw effect"""
        progress = self.age / self.max_age
        alpha = 1.0 - progress

        if self.effect_type == "success":
            # Expanding green circle
            radius = int(20 * progress)
            if radius > 0:
                pyxel.circ(self.x, self.y, radius, 3)
                pyxel.circb(self.x, self.y, radius, 10)

        elif self.effect_type == "error":
            # Red X
            size = int(10 * (1 - progress))
            if size > 0:
                pyxel.line(self.x - size, self.y - size, self.x + size, self.y + size, 8)
                pyxel.line(self.x + size, self.y - size, self.x - size, self.y + size, 8)

        elif self.effect_type == "build":
            # Upward arrows
            arrow_offset = int(-15 * progress)
            pyxel.text(self.x - 2, self.y + arrow_offset, "↑", 10)

        elif self.effect_type == "demolish":
            # Downward particles
            for i in range(5):
                px = self.x + random.randint(-10, 10)
                py = self.y + int(20 * progress) + i * 5
                pyxel.rect(px, py, 2, 2, 8)

class FeedbackSystem:
    """Manages visual feedback effects"""
    def __init__(self):
        self.effects: List[FeedbackEffect] = []

    def add_effect(self, x: int, y: int, effect_type: str, duration: int = 30):
        """Add a feedback effect"""
        effect = FeedbackEffect(x, y, effect_type, duration)
        self.effects.append(effect)

    def update(self):
        """Update all effects"""
        self.effects = [e for e in self.effects if e.update()]

    def draw(self):
        """Draw all active effects"""
        for effect in self.effects:
            effect.draw()

class KeyboardShortcutHelper:
    """Displays keyboard shortcut hints"""
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.shortcuts = {
            "Movement": {"↑↓←→": "カーソル移動"},
            "Tools": {"1-9": "ツール選択", "0": "ブルドーザー"},
            "Actions": {"Z/Space": "配置", "X": "削除"},
            "Views": {"V": "表示切替"},
            "System": {"S": "統計", "Q": "終了", "O": "セーブ", "I": "ロード"}
        }
        self.show_help = False
        self.help_alpha = 0.0

    def toggle_help(self):
        """Toggle help display"""
        self.show_help = not self.show_help

    def update(self):
        """Update help display state"""
        if self.show_help and self.help_alpha < 1.0:
            self.help_alpha = min(1.0, self.help_alpha + 0.1)
        elif not self.show_help and self.help_alpha > 0.0:
            self.help_alpha = max(0.0, self.help_alpha - 0.1)

    def draw(self, use_japanese: bool = True):
        """Draw keyboard shortcuts help"""
        if self.help_alpha <= 0.01:
            return

        # Semi-transparent overlay
        overlay_alpha = int(self.help_alpha * 180)
        panel_width = 200
        panel_height = 180
        panel_x = (self.screen_width - panel_width) // 2
        panel_y = (self.screen_height - panel_height) // 2

        # Draw background
        pyxel.rect(panel_x, panel_y, panel_width, panel_height, 0)
        pyxel.rectb(panel_x, panel_y, panel_width, panel_height, 7)

        # Title
        title = "キーボードショートカット" if use_japanese else "Keyboard Shortcuts"
        title_x = (self.screen_width - len(title) * 4) // 2
        pyxel.text(title_x, panel_y + 10, title, 7)

        # Shortcuts
        y_offset = 30
        for category, shortcuts in self.shortcuts.items():
            # Category name
            cat_text = category
            pyxel.text(panel_x + 10, panel_y + y_offset, cat_text, 6)
            y_offset += 15

            # Shortcuts
            for key, action in shortcuts.items():
                # Key binding
                pyxel.text(panel_x + 20, panel_y + y_offset, key, 10)
                # Action
                pyxel.text(panel_x + 80, panel_y + y_offset, action, 7)
                y_offset += 10

            y_offset += 5

        # Close hint
        close_hint = "? キーで閉じる" if use_japanese else "Press ? to close"
        close_x = (self.screen_width - len(close_hint) * 4) // 2
        pyxel.text(close_x, panel_y + panel_height - 15, close_hint, 5)

class LoadingScreen:
    """Loading screen with progress bar"""
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.progress = 0.0
        self.message = "Loading..."
        self.jp_message = "ロード中..."

    def set_progress(self, progress: float, message: str = "", jp_message: str = ""):
        """Set loading progress (0.0 to 1.0)"""
        self.progress = max(0.0, min(1.0, progress))
        if message:
            self.message = message
        if jp_message:
            self.jp_message = jp_message

    def draw(self, use_japanese: bool = True):
        """Draw loading screen"""
        # Background
        pyxel.cls(0)

        # Loading text
        text = self.jp_message if use_japanese else self.message
        text_x = (self.screen_width - len(text) * 4) // 2
        text_y = self.screen_height // 2 - 20
        pyxel.text(text_x, text_y, text, 7)

        # Progress bar background
        bar_width = 200
        bar_height = 16
        bar_x = (self.screen_width - bar_width) // 2
        bar_y = self.screen_height // 2 + 10

        pyxel.rect(bar_x, bar_y, bar_width, bar_height, 0)
        pyxel.rectb(bar_x, bar_y, bar_width, bar_height, 7)

        # Progress bar fill
        fill_width = int(bar_width * self.progress)
        if fill_width > 0:
            pyxel.rect(bar_x + 1, bar_y + 1, fill_width - 2, bar_height - 2, 6)

        # Percentage
        pct_text = f"{int(self.progress * 100)}%"
        pct_x = (self.screen_width - len(pct_text) * 4) // 2
        pyxel.text(pct_x, bar_y + bar_height + 10, pct_text, 7)

class UIEnhancementSystem:
    """Main UI enhancement system that combines all enhancements"""
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Sub-systems
        self.notifications = NotificationSystem(screen_width, screen_height)
        self.tooltip = TooltipSystem(screen_width, screen_height)
        self.feedback = FeedbackSystem()
        self.shortcuts = KeyboardShortcutHelper(screen_width, screen_height)
        self.loading = LoadingScreen(screen_width, screen_height)

        # Settings
        self.use_japanese = True
        self.show_tooltips = True

    def update(self):
        """Update all UI enhancement systems"""
        self.notifications.update()
        self.tooltip.update(0, 0)  # Mouse position would be passed here
        self.feedback.update()
        self.shortcuts.update()

    def draw(self):
        """Draw all UI enhancements"""
        self.notifications.draw(self.use_japanese)
        if self.show_tooltips:
            self.tooltip.draw(self.use_japanese)
        self.feedback.draw()
        self.shortcuts.draw(self.use_japanese)

    def show_notification(self, message: str, jp_message: str, notif_type: NotificationType = NotificationType.INFO):
        """Convenience method to show notification"""
        self.notifications.notify(message, jp_message, notif_type)

    def show_feedback(self, x: int, y: int, effect_type: str):
        """Convenience method to show feedback effect"""
        self.feedback.add_effect(x, y, effect_type)

    def set_tooltip(self, content: TooltipContent, x: int, y: int):
        """Convenience method to set tooltip"""
        self.tooltip.set_tooltip(content, x, y)

    def toggle_shortcuts_help(self):
        """Toggle keyboard shortcuts help"""
        self.shortcuts.toggle_help()

# Example usage
if __name__ == "__main__":
    # Test UI enhancements
    ui_system = UIEnhancementSystem(320, 288)

    # Initialize Pyxel
    pyxel.init(320, 288, title="UI Enhancement Test")

    # Test notifications
    ui_system.show_notification("Welcome to ConcLand!", "ConcLandへようこそ！", NotificationType.SUCCESS)
    ui_system.show_notification("Press ? for help", "?キーでヘルプ", NotificationType.INFO)

    def update():
        ui_system.update()

        # Toggle help with ?
        if pyxel.btnp(pyxel.KEY_QUESTION):
            ui_system.toggle_shortcuts_help()

        # Quit with Q
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()

    def draw():
        pyxel.cls(0)
        ui_system.draw()

        # Test tooltip
        if pyxel.frame_count % 300 < 150:
            tooltip_content = TooltipContent(
                title="Residential Zone",
                japanese_title="住宅ゾーン",
                description="Provides housing for your citizens",
                japanese_description="市民に住宅を提供します",
                stats={"Population": "100", "Happiness": "80%"}
            )
            ui_system.set_tooltip(tooltip_content, 100, 100)

    pyxel.run(update, draw)
