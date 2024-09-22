from jnius import autoclass
import os

def send_file(self, instance):
    """Отправка файлов по почте через Android Intent"""
    try:
        Intent = autoclass('android.content.Intent')
        Uri = autoclass('android.net.Uri')
        File = autoclass('java.io.File')
        ArrayList = autoclass('java.util.ArrayList')
        Environment = autoclass('android.os.Environment')
        context = autoclass('org.kivy.android.PythonActivity').mActivity

        # Путь к файлам
        file1_path = os.path.join('/storage/emulated/0/TMP_KOD', 'file_kod1.txt')
        file2_path = os.path.join('/storage/emulated/0/TMP_KOD', 'file_kod2.txt')

        # Проверяем, существуют ли файлы
        if os.path.exists(file1_path) and os.path.exists(file2_path):
            # Создаем Intent для отправки нескольких файлов
            intent = Intent(Intent.ACTION_SEND_MULTIPLE)
            intent.setType("*/*")  # Указываем MIME-тип как "все файлы"

            uris = ArrayList()

            # Преобразование файлов в URI
            file1_uri = Uri.fromFile(File(file1_path))
            file2_uri = Uri.fromFile(File(file2_path))

            # Добавляем URI файлов в список для отправки
            uris.add(file1_uri)
            uris.add(file2_uri)

            # Передаем список URI в Intent
            intent.putParcelableArrayListExtra(Intent.EXTRA_STREAM, uris)
            intent.putExtra(Intent.EXTRA_SUBJECT, "Файлы с данными")  # Тема письма
            intent.putExtra(Intent.EXTRA_TEXT, "Отправляю файлы.")  # Текст письма

            # Запуск Intent через выбор приложения
            chooser = Intent.createChooser(intent, "Отправить через:")
            context.startActivity(chooser)

        else:
            self.log_message("Один или оба файла не найдены!")

    except Exception as e:
        self.log_message(f"Ошибка при отправке файлов: {str(e)}")
        traceback.print_exc()


