from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel

class SmartGridUI(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.label = QLabel('Aca se va a mostrar el progreso de los agentes')
        layout.addWidget(self.label)

        # Button to perform actions
        btn_action = QPushButton('Pruebita')
        btn_action.clicked.connect(self.perform_agent_action)
        layout.addWidget(btn_action)

        self.setLayout(layout)
        self.setWindowTitle('Qt UI Test')
        self.show()

    def perform_agent_action(self):
        pass

def main():
    app = QApplication([])

    ui = SmartGridUI()

    app.exec_()

if __name__ == '__main__':
    main()
