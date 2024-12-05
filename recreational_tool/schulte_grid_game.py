import sys
import random
import time
import os
import json
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QComboBox, QMessageBox, QGridLayout)
from PyQt5.QtCore import QTimer

class SchulteGridGame(QWidget):
    def __init__(self):
        super().__init__()
        self.grid_size = 5
        self.start_time = None
        self.timer_label = None
        self.current_number_label = None
        self.message_label = None
        self.timer_running = False
        self.times = []
        self.stats_dir = "stats"
        self.stats_file_template = os.path.join(self.stats_dir, "schulte_grid_stats_{}.json")
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Schulte Grid")

        # 创建主布局，分为左侧和右侧
        main_layout = QHBoxLayout()

        # 创建左侧的控制面板
        left_layout = QVBoxLayout()

        # Grid size control
        grid_size_layout = QHBoxLayout()
        grid_size_label = QLabel("Grid Size:", self)
        self.grid_size_combo = QComboBox(self)
        self.grid_size_combo.addItems([str(i) for i in range(3, 10)])
        self.grid_size_combo.setCurrentIndex(self.grid_size - 3)
        grid_size_layout.addWidget(grid_size_label)
        grid_size_layout.addWidget(self.grid_size_combo)

        # Start button
        start_button = QPushButton('Start', self)
        start_button.clicked.connect(self.reset_game)

        # Labels for statistics
        self.timer_label = QLabel("Time: 0.000s", self)
        self.current_number_label = QLabel("Current Number: 1", self)
        self.shortest_time_label = QLabel("Shortest Time: N/A", self)
        self.last_5_avg_label = QLabel("Last 5 Avg Time: N/A", self)
        self.history_avg_label = QLabel("History Avg Time: N/A", self)

        left_layout.addLayout(grid_size_layout)
        left_layout.addWidget(start_button)
        left_layout.addWidget(self.timer_label)
        left_layout.addWidget(self.current_number_label)
        left_layout.addWidget(self.shortest_time_label)
        left_layout.addWidget(self.last_5_avg_label)
        left_layout.addWidget(self.history_avg_label)

        # 创建右侧的数字格
        self.grid_layout = QGridLayout()
        self.message_label = QLabel("", self)

        right_layout = QVBoxLayout()
        right_layout.addLayout(self.grid_layout)
        right_layout.addWidget(self.message_label)

        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)

        self.setLayout(main_layout)
        self.reset_game()

    def reset_game(self):
        self.grid_size = int(self.grid_size_combo.currentText())
        self.load_stats()
        self.numbers = list(range(1, self.grid_size * self.grid_size + 1))
        random.shuffle(self.numbers)
        self.current_number = 1
        self.start_time = time.time()
        self.timer_running = True
        self.message_label.setText("")
        self.current_number_label.setText("Current Number: 1")

        for i in reversed(range(self.grid_layout.count())):
            self.grid_layout.itemAt(i).widget().setParent(None)

        self.buttons = []
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                number = self.numbers.pop()
                button = QPushButton(str(number), self)
                button.setFixedSize(60, 60)
                button.setStyleSheet("font-size: 20px")
                button.clicked.connect(lambda checked, num=number, btn=button: self.check_number(num, btn))
                self.grid_layout.addWidget(button, i, j)

        self.update_timer()

    def check_number(self, number, button):
        if number == self.current_number:
            button.setStyleSheet("background-color: lightgreen; font-size: 20px")
            self.current_number += 1
            self.current_number_label.setText(f"Current Number: {self.current_number}")
            if self.current_number > self.grid_size * self.grid_size:
                elapsed_time = time.time() - self.start_time
                self.timer_running = False
                self.message_label.setText(f"Congratulations! Finish time: {elapsed_time:.3f} s!")
                self.record_time(elapsed_time)
        else:
            self.message_label.setText("Wrong number! Try again.")

    def update_timer(self):
        if self.timer_running:
            elapsed_time = time.time() - self.start_time
            self.timer_label.setText(f"Time: {elapsed_time:.3f}s")
            QTimer.singleShot(10, self.update_timer)

    def record_time(self, elapsed_time):
        self.times.append(elapsed_time)
        self.save_stats()
        self.update_stats_labels()

    def save_stats(self):
        os.makedirs(self.stats_dir, exist_ok=True)
        stats = {"times": self.times}
        stats_file = self.stats_file_template.format(self.grid_size)
        with open(stats_file, "w") as f:
            json.dump(stats, f)

    def load_stats(self):
        self.times = []
        stats_file = self.stats_file_template.format(self.grid_size)
        if os.path.exists(stats_file):
            with open(stats_file, "r") as f:
                stats = json.load(f)
                self.times = stats.get("times", [])
        self.update_stats_labels()

    def update_stats_labels(self):
        if self.times:
            shortest_time = min(self.times)
            last_5_avg = sum(self.times[-5:]) / min(len(self.times), 5)
            history_avg = sum(self.times) / len(self.times)

            self.shortest_time_label.setText(f"Shortest Time: {shortest_time:.3f}s")
            self.last_5_avg_label.setText(f"Last 5 Avg Time: {last_5_avg:.3f}s")
            self.history_avg_label.setText(f"History Avg Time: {history_avg:.3f}s")
        else:
            self.shortest_time_label.setText("Shortest Time: N/A")
            self.last_5_avg_label.setText("Last 5 Avg Time: N/A")
            self.history_avg_label.setText("History Avg Time: N/A")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    game = SchulteGridGame()
    game.show()
    sys.exit(app.exec_())