from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QPlainTextEdit


class AppendOnlyTextEdit(QPlainTextEdit):
    realTextEdited = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.cursorPositionChanged.connect(self.on_cursor_position_changed)
        self.setUndoRedoEnabled(False)
        self.setContextMenuPolicy(Qt.NoContextMenu)
        self.previous_text = self.toPlainText()
        self.textChanged.connect(self.on_text_changed)

    def on_cursor_position_changed(self):
        self.move_cursor_to_end()

    def move_cursor_to_end(self):
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.setTextCursor(cursor)

    def set_text(self, text: str):
        self.previous_text = text
        self.setPlainText(text)

    def on_text_changed(self):
        current_text = self.toPlainText()
        if len(current_text) < len(self.previous_text) or not (
            current_text[-1:] == "0"
            or current_text[-1:] == "1"
            or current_text[-1:] == "\n"
        ):
            self.blockSignals(True)
            self.setPlainText(self.previous_text)
            self.blockSignals(False)
            cursor = self.textCursor()
            cursor.movePosition(QTextCursor.End)
            self.setTextCursor(cursor)
        else:
            same_event = self.previous_text == current_text
            if not same_event:
                self.previous_text = current_text
                self.realTextEdited.emit(current_text)
