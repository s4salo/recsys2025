import sys
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QTextEdit
)

from api_controller import analyze_ninjas_api, analyze_sentiment_analysis_api
from response_comparer import compare_api_results


class SentimentAnalyzerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """Инициализация интерфейса"""
        self.setWindowTitle("Sentiment API Tester")
        self.setGeometry(100, 100, 600, 400)

        app_font = QApplication.font()
        app_font.setPointSize(10)
        QApplication.setFont(app_font)

        # Основной виджет
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # Основной layout
        layout = QVBoxLayout()
        main_widget.setLayout(layout)

        # Поле ввода текста
        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("Введите текст")
        layout.addWidget(self.text_input)

        # Layout для кнопок
        button_layout = QHBoxLayout()

        self.btn_ninjas = QPushButton("API Ninjas")
        self.btn_ninjas.clicked.connect(self.call_ninjas_api)
        button_layout.addWidget(self.btn_ninjas)

        self.btn_sentiment = QPushButton("Sentiment Analysis")
        self.btn_sentiment.clicked.connect(self.call_sentiment_api)
        button_layout.addWidget(self.btn_sentiment)

        self.btn_compare = QPushButton("Сравнить оба")
        self.btn_compare.clicked.connect(self.compare_apis)
        button_layout.addWidget(self.btn_compare)

        layout.addLayout(button_layout)

        # Область для вывода результатов
        self.output_area = QTextEdit()
        self.output_area.setReadOnly(True)
        layout.addWidget(self.output_area)

    def append_output(self, text):
        """Добавление текста в вывод"""
        current_text = self.output_area.toPlainText()
        if current_text:
            self.output_area.setText(current_text + "\n" + text)
        else:
            self.output_area.setText(text)

    def format_api_result(self, result: dict, api_name: str) -> str:
        """Форматирует результат API для вывода"""
        if not result or not result.get('success'):
            error_msg = result.get('error', 'Unknown error') if result else 'No response'
            return f"{api_name} - ERROR: {error_msg}"

        try:
            if api_name == "API Ninjas":
                data = result['data']
                sentiment = data.get('sentiment', 'Unknown')
                score = data.get('score', 0)
                return f"{api_name} - Sentiment: {sentiment}, Score: {score:.3f}"

            elif api_name == "Sentiment Analysis":
                data = result['data']
                if isinstance(data, list) and len(data) > 0:
                    predictions = data[0].get('predictions', [])
                    if predictions:
                        best = max(predictions, key=lambda x: x.get('probability', 0))
                        sentiment = best.get('prediction', 'Unknown')
                        probability = best.get('probability', 0)
                        return f"{api_name} - Sentiment: {sentiment}, Probability: {probability:.3f}"

            return f"{api_name} - Невозможно прочесть ответ"

        except (KeyError, TypeError, IndexError) as e:
            return f"{api_name} - Parse error: {str(e)}"

    def call_ninjas_api(self):
        """Вызов API Ninjas"""
        text = self.text_input.text().strip()
        if not text:
            self.output_area.setText("Ошибка: Введите текст")
            return

        self.btn_ninjas.setEnabled(False)
        self.output_area.clear()

        # Выполняем запрос
        result = analyze_ninjas_api(text)
        output = self.format_api_result(result, "API Ninjas")
        self.output_area.setText(output)

        self.btn_ninjas.setEnabled(True)

    def call_sentiment_api(self):
        """Вызов Sentiment Analysis API"""
        text = self.text_input.text().strip()
        if not text:
            self.output_area.setText("Ошибка: Введите текст")
            return

        self.btn_sentiment.setEnabled(False)
        self.output_area.clear()

        # Выполняем запрос
        result = analyze_sentiment_analysis_api(text)
        output = self.format_api_result(result, "Sentiment Analysis")
        self.output_area.setText(output)

        self.btn_sentiment.setEnabled(True)

    def compare_apis(self):
        """Сравниваем результаты двух API"""
        text = self.text_input.text().strip()
        if not text:
            self.output_area.setText("Ошибка: Введите текст")
            return

        # На время выполнения запросов выключаем кнопки
        self.disable_all_buttons()
        self.output_area.clear()

        # Вызываем API Ninjas
        ninjas_result = analyze_ninjas_api(text)
        output = self.format_api_result(ninjas_result, "API Ninjas")
        self.append_output(output)

        # Вызываем Sentiment Analysis API
        sentiment_result = analyze_sentiment_analysis_api(text)
        output = self.format_api_result(sentiment_result, "Sentiment Analysis")
        self.append_output(output)

        # Выполняем сравнение
        comparison = compare_api_results(ninjas_result, sentiment_result)
        comparison_text = self.format_comparison_result(comparison)
        self.append_output(comparison_text)

        # Включаем кнопки обратно
        self.enable_all_buttons()

    def disable_all_buttons(self):
        """Отключить все кнопки"""
        self.btn_ninjas.setEnabled(False)
        self.btn_sentiment.setEnabled(False)
        self.btn_compare.setEnabled(False)

    def enable_all_buttons(self):
        """Включить все кнопки"""
        self.btn_ninjas.setEnabled(True)
        self.btn_sentiment.setEnabled(True)
        self.btn_compare.setEnabled(True)

    def format_comparison_result(self, comparison: dict) -> str:
        """Форматирует результат сравнения API для его вывода"""
        separator = "\n" + "=" * 30
        result_text = separator + "\nРЕЗУЛЬТАТЫ СРАВНЕНИЯ:"

        if comparison['both_api_successful']:
            ninjas_sent = comparison['ninjas_sentiment']
            sentiment_sent = comparison['sentiment_analysis_sentiment']

            result_text += f"\nAPI Ninjas result: {ninjas_sent}"
            result_text += f"\nSentiment Analysis result: {sentiment_sent}"

            if comparison['results_match']:
                result_text += "\n\nОба API вернули один результат"
            else:
                result_text += "\n\nAPI вернули разные результаты"
        else:
            result_text += f"\nСтатус сравнения: {comparison['comparison_status']}"
            if comparison['ninjas_sentiment']:
                result_text += f"\nAPI Ninjas: {comparison['ninjas_sentiment']}"
            if comparison['sentiment_analysis_sentiment']:
                result_text += f"\nSentiment Analysis: {comparison['sentiment_analysis_sentiment']}"

        return result_text


def main():
    app = QApplication(sys.argv)
    window = SentimentAnalyzerGUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
