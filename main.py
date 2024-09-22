

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
import os
from kivy.utils import platform
from kivy.core.window import Window
from plyer import email
import traceback
from kivy.properties import StringProperty, BooleanProperty

try:
    from android.permissions import request_permissions, Permission, check_permission
    from android import activity
    from jnius import autoclass, cast
except ImportError:
    # Заглушка для тестирования на ПК
    class Permission:
        WRITE_EXTERNAL_STORAGE = 'WRITE_EXTERNAL_STORAGE'
        READ_EXTERNAL_STORAGE = 'READ_EXTERNAL_STORAGE'

    def request_permissions(permissions, callback):
        pass

    def check_permission(permission):
        return True


class MainApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Виджет для вывода текста ошибок
        self.error_label = Label(
            size_hint_y=0.25,
            text="Здесь будут отображаться ошибки:\n",
            halign="center",
            font_size='9sp',  # Мелкий шрифт, можно изменить на нужный размер
            color=(1, 0, 0, 1)  # Цвет текста красный
        )
        layout.add_widget(self.error_label)

        # Поле для ввода текста
        self.text_input = TextInput(hint_text="Введите текст для сохранения\n", size_hint_y=0.25)
        layout.add_widget(self.text_input)

        # Кнопка для сохранения текста в файл
        save_button = Button(text="Сохранить текст", size_hint_y=0.25)
        save_button.bind(on_press=self.save_files)
        layout.add_widget(save_button)

        # Кнопка для пересылки файла
        send_button = Button(text="Переслать файл", size_hint_y=0.25)
        send_button.bind(on_press=self.send_file)
        layout.add_widget(send_button)

        return layout

    def log_message(self, message):
        """Функция для вывода сообщений на экран с разбивкой по 50 символов"""
        wrapped_message = self.wrap_text(message, 50)
        self.error_label.text += wrapped_message + "\n"

    def wrap_text(self, text, width):
        """Функция для разбивки текста по длине строки (ширине)"""
        return '\n'.join([text[i:i + width] for i in range(0, len(text), width)])

    def check_storage_permissions(self):
        if check_permission(Permission.READ_EXTERNAL_STORAGE) and check_permission(Permission.WRITE_EXTERNAL_STORAGE):
            self.log_message("Разрешения предоставлены")
        else:
            self.log_message("Разрешения не предоставлены, необходимо запросить.")

    def save_files(self, instance):
        """Создание папки и файлов с учётом разных версий Android"""
        try:
            if platform == 'android':
                from jnius import autoclass

                # Для Android 10 и выше используется Scoped Storage
                Environment = autoclass('android.os.Environment')
                Build = autoclass('android.os.Build')
                VERSION = autoclass('android.os.Build$VERSION')

                if int(VERSION.SDK_INT) >= 29:  # Scoped Storage для Android 10+
                    context = autoclass('org.kivy.android.PythonActivity').mActivity.getApplicationContext()
                    dir_path = context.getExternalFilesDir(None).getAbsolutePath()
                else:
                    # Для Android 9 и ниже используем стандартный путь к внешнему хранилищу
                    def callback(permission, results):
                        if not all(results):
                            self.log_message("Необходимо предоставить разрешения для работы с файлами")

                    # Запрашиваем разрешения на чтение и запись в хранилище
                    # Запрос разрешений для записи в внешнее хранилище
                    if not check_permission(Permission.WRITE_EXTERNAL_STORAGE):
                        request_permissions([Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE], callback)

                    dir_path = os.path.join(Environment.getExternalStorageDirectory().getAbsolutePath(), 'TMP_KOD')

            else:
                # Путь для ПК (Linux, Windows, macOS)
                dir_path = os.path.expanduser('~/TMP_KOD')

            # Создаем файлы
            self.file1 = os.path.join(dir_path, 'file_kod1.txt')  # Используем self.file1 для доступа из других методов
            self.file2 = os.path.join(dir_path, 'file_kod2.txt')

            # Если папки нет, создаем её
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
                self.log_message(f"Создана папка: {dir_path}")

            # Запись текста в файл1
            with open(self.file1, 'w') as f:
                f.write(self.text_input.text)  # Записываем текст из TextInput
            self.log_message(f"Создан файл: {self.file1}")

            # Создание пустого файла file2
            with open(self.file2, 'w') as f:
                f.write('')  # Пустой файл
            self.log_message(f"Создан файл: {self.file2}")

            return self.file1, self.file2

        except Exception as e:
            self.log_message(f"Ошибка создания файлов: \n {str(e)}")
            traceback.print_exc()

    from jnius import autoclass
    import os
    from jnius import autoclass, cast
    import os
    from kivy.utils import platform
    from jnius import autoclass, cast
     #/ storage / emulated / 0 / TMP_KOD / file_kod2.txt

    def send_file(self, instance):
        """Отправка файлов через Android Intent"""
        try:
            # Классы для работы с Intent
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Intent = autoclass('android.content.Intent')
            Uri = autoclass('android.net.Uri')
            File = autoclass('java.io.File')
            ArrayList = autoclass('java.util.ArrayList')

            # Получение текущего контекста
            context = PythonActivity.mActivity

            # Создаем Intent для отправки файлов
            intent = Intent(Intent.ACTION_SEND_MULTIPLE)
            intent.setType("application/txt")  # Убедитесь, что MIME-тип соответствует вашим файлам

            # Путь к файлам
            file1 = File(self.file1)
            file2 = File(self.file2)

            # Получаем URI для файлов
            uri1 = Uri.fromFile(file1)
            uri2 = Uri.fromFile(file2)

            # Список для хранения URI
            uris = ArrayList()
            uris.add(uri1)
            uris.add(uri2)

            # Добавляем файлы в Intent
            intent.putParcelableArrayListExtra(Intent.EXTRA_STREAM, uris)
            intent.putExtra(Intent.EXTRA_SUBJECT, "Файлы с данными")
            intent.putExtra(Intent.EXTRA_TEXT, "Прикреплены два файла.")

            # Создаем диалог для выбора приложения
            chooser_text = cast('java.lang.CharSequence', autoclass('java.lang.String')("Отправить через:"))
            chooser = Intent.createChooser(intent, chooser_text)

            # Запуск диалога отправки через выбранное приложение
            context.startActivity(chooser)

        except Exception as e:
            self.log_message(f"Ошибка при отправке файлов: \n{str(e)}")

    # Test 17_09_2024 0.163
    def send_file_8(self, instance):
        """Отправка файлов по почте через Android Intent"""

        try:
            Intent = autoclass('android.content.Intent')
            Uri = autoclass('android.net.Uri')
            File = autoclass('java.io.File')

            intent = Intent(Intent.ACTION_SEND_MULTIPLE)
            intent.setType("application/txt")  # Или другой подходящий MIME-тип

            file1 = File(self.file1)
            file2 = File(self.file2)

            uri1 = Uri.fromFile(file1)
            uri2 = Uri.fromFile(file2)

            ArrayList = autoclass('java.util.ArrayList')
            uris = ArrayList()
            uris.add(uri1)
            uris.add(uri2)

            intent.putParcelableArrayListExtra(Intent.EXTRA_STREAM, uris)
            intent.putExtra(Intent.EXTRA_SUBJECT, "Файлы с данными")
            intent.putExtra(Intent.EXTRA_TEXT, "Приклеплены два файла.")

            chooser_text = cast('java.lang.CharSequence', autoclass('java.lang.String')("Отправить через:"))
            chooser = Intent.createChooser(intent, chooser_text)
            activity.startActivity(chooser)


        except Exception as e:
            self.log_message(f"Ошибка при отправке файлов: \n {str(e)}")







    # Test 16_09_2024 0.162
    def send_file_7(self, instance):
        """Отправка файлов по почте через Android Intent"""

        try:
            FileProvider = autoclass('androidx.core.content.FileProvider')
        except Exception as e:
            self.log_message(f"Ошибка АВВА: \n {str(e)}")
            traceback.print_exc()

        try:
            Intent = autoclass('android.content.Intent')
            Uri = autoclass('android.net.Uri')
            File = autoclass('java.io.File')

            ArrayList = autoclass('java.util.ArrayList')
            PythonActivity = autoclass('org.kivy.android.PythonActivity').mActivity
            FileProvider = autoclass('androidx.core.content.FileProvider')
            CharSequence = autoclass('java.lang.CharSequence')  # Импортируем CharSequence

            # Замените 'your.package.name.fileprovider' на ваш authority
            authority = "your.package.name.fileprovider"

            # Список файлов для отправки
            files = [self.file1, self.file2]
            uris = ArrayList()
            missing_files = []

            for file_path in files:
                if os.path.exists(file_path):
                    java_file = File(file_path)
                    file_uri = FileProvider.getUriForFile(PythonActivity, authority, java_file)
                    uris.add(file_uri)
                else:
                    missing_files.append(file_path)

            if uris.size() > 0:
                intent = Intent(Intent.ACTION_SEND_MULTIPLE)
                intent.setType("application/txt")  # Или другой подходящий MIME-тип
                intent.putParcelableArrayListExtra(Intent.EXTRA_STREAM, uris)
                intent.putExtra(Intent.EXTRA_SUBJECT, "Файлы с данными")
                intent.putExtra(Intent.EXTRA_TEXT, "Отправка файлов.")
                intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)

                # Конвертируем строку в CharSequence
                chooser_text = cast('java.lang.CharSequence', autoclass('java.lang.String')("Отправить через:"))
                chooser = Intent.createChooser(intent, chooser_text)
                chooser.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                PythonActivity.startActivity(chooser)

            if missing_files:
                self.log_message(f"Файлы не найдены: {', '.join(missing_files)}")

        except Exception as e:
            self.log_message(f"Ошибка при отправке файлов: \n {str(e)}")
            traceback.print_exc()

    def send_file_6(self, instance):
        """Отправка файлов по почте через Android Intent с использованием FileProvider"""
        try:
            Intent = autoclass('android.content.Intent')
            Uri = autoclass('android.net.Uri')
            File = autoclass('java.io.File')
            ArrayList = autoclass('java.util.ArrayList')
            FileProvider = autoclass('androidx.core.content.FileProvider')
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

                # Использование FileProvider для получения URI файлов
                file1 = File(file1_path)
                file2 = File(file2_path)

                file1_uri = FileProvider.getUriForFile(
                    context,
                    context.getPackageName() + ".provider",
                    file1
                )

                file2_uri = FileProvider.getUriForFile(
                    context,
                    context.getPackageName() + ".provider",
                    file2
                )

                # Добавляем URI файлов в список для отправки
                uris.add(file1_uri)
                uris.add(file2_uri)

                # Передаем список URI в Intent
                intent.putParcelableArrayListExtra(Intent.EXTRA_STREAM, uris)
                intent.putExtra(Intent.EXTRA_SUBJECT, "Файлы с данными")
                intent.putExtra(Intent.EXTRA_TEXT, "Отправляю файлы.")

                # Установка флагов для разрешения доступа
                intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)

                # Запуск Intent через выбор приложения
                chooser = Intent.createChooser(intent, "Отправить через:")
                context.startActivity(chooser)

            else:
                self.log_message("Один или оба файла не найдены!")

        except Exception as e:
            self.log_message(f"Ошибка при отправке файлов: {str(e)}")
            traceback.print_exc()

    def send_file_5(self, instance):
        """Отправка файлов по почте через Android Intent"""
        try:
            # Запрашиваем разрешения на чтение и запись внешнего хранилища
            request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])
            #check_storage_permissions()

            Intent = autoclass('android.content.Intent')
            Uri = autoclass('android.net.Uri')
            FileProvider = autoclass('androidx.core.content.FileProvider')
            File = autoclass('java.io.File')
            ArrayList = autoclass('java.util.ArrayList')
            Context = autoclass('android.content.Context')
            PythonActivity = autoclass('org.kivy.android.PythonActivity')

            context = PythonActivity.mActivity

            # Путь к файлам
            file1_path = os.path.join('/storage/emulated/0/TMP_KOD', 'file_kod1.txt')
            file2_path = os.path.join('/storage/emulated/0/TMP_KOD', 'file_kod2.txt')

            # Проверяем, существуют ли файлы
            if os.path.exists(file1_path) and os.path.exists(file2_path):
                # Создаем URI для файлов через FileProvider
                file1 = File(file1_path)
                file2 = File(file2_path)
                file1_uri = FileProvider.getUriForFile(context, f"{context.getPackageName()}.provider", file1)
                file2_uri = FileProvider.getUriForFile(context, f"{context.getPackageName()}.provider", file2)

                # Создаем Intent для отправки нескольких файлов
                intent = Intent(Intent.ACTION_SEND_MULTIPLE)
                intent.setType("*/*")  # MIME-тип для всех файлов

                uris = ArrayList()
                uris.add(file1_uri)
                uris.add(file2_uri)

                # Передаем URI файлов в Intent
                intent.putParcelableArrayListExtra(Intent.EXTRA_STREAM, uris)
                intent.putExtra(Intent.EXTRA_SUBJECT, "Файлы с данными")  # Тема письма
                intent.putExtra(Intent.EXTRA_TEXT, "Отправляю файлы.")  # Текст письма

                # Добавляем флаг для предоставления доступа к URI
                intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)

                # Запуск Intent через выбор приложения
                chooser = Intent.createChooser(intent, "Отправить через:")
                context.startActivity(chooser)

            else:
                self.log_message("Один или оба файла не найдены!")

        except Exception as e:
            self.log_message(f"Ошибка при отправке файлов: {str(e)}")
            traceback.print_exc()

    def send_file4(self, instance):
        """Отправка файлов по почте через Android Intent"""
        try:
            request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])

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

                # Передаем список URI в Intenth
                intent.putParcelableArrayListExtra(Intent.EXTRA_STREAM, uris)
                intent.putExtra(Intent.EXTRA_SUBJECT, "Файлы с данными")  # Тема письма
                intent.putExtra(Intent.EXTRA_TEXT, "Отправляю файлы.")  # Текст письма

                # Запуск Intent через выбор приложения

                # Для Android 10 и выше используется Scoped Storage
                VERSION = autoclass('android.os.Build$VERSION')
                if int(VERSION.SDK_INT) >= 29:  # Scoped Storage для Android 10+
                    chooser = Intent.createChooser(intent, autoclass('java.lang.CharSequence')("Отправить через:"))
                # Для Android 9 и ниже используем
                else: chooser = Intent.createChooser(intent, "Отправить через:")

                context.startActivity(chooser)

            else:
                self.log_message("Один или оба файла не найдены!")

        except Exception as e:
            self.log_message(f"Ошибка при отправке файлов: {str(e)}")
            traceback.print_exc()
# Test 16_09_2024 0.161
    def send_file_3(self, instance):
        """Отправка файлов по почте через Android Intent"""
        try:
            from jnius import autoclass
            Intent = autoclass('android.content.Intent')
            Uri = autoclass('android.net.Uri')
            File = autoclass('java.io.File')
            ArrayList = autoclass('java.util.ArrayList')

            # Проверяем существование файлов
            if os.path.exists(self.file1) and os.path.exists(self.file2):
                context = autoclass('org.kivy.android.PythonActivity').mActivity

                # Создаем Intent для отправки нескольких файлов
                intent = Intent(Intent.ACTION_SEND_MULTIPLE)
                intent.setType("message/rfc822")  # Тип данных для почтового клиента

                uris = ArrayList()

                # Добавляем файлы в Intent
                file1_uri = Uri.fromFile(File(self.file1))
                file2_uri = Uri.fromFile(File(self.file2))
                uris.add(file1_uri)
                uris.add(file2_uri)

                # Передаем список URI в Intent
                intent.putParcelableArrayListExtra(Intent.EXTRA_STREAM, uris)
                intent.putExtra(Intent.EXTRA_SUBJECT, "Файлы с данными")
                intent.putExtra(Intent.EXTRA_TEXT, "Отправка файлов.")

                # Запускаем почтовый клиент
                context.startActivity(Intent.createChooser(intent, "Отправить через:"))

            else:
                self.log_message("Один или оба файла не найдены!")

        except Exception as e:
            self.log_message(f"Ошибка при отправке файлов: \n {str(e)}")
            traceback.print_exc()

    def send_file_2(self, instance):
        """Отправка файлов через Android Intent"""
        try:
            # Проверка, что файлы существуют
            if os.path.exists(self.file1) and os.path.exists(self.file2):
                # Получаем доступ к необходимым классам
                Intent = autoclass('android.content.Intent')
                Uri = autoclass('android.net.Uri')
                File = autoclass('java.io.File')
                Environment = autoclass('android.os.Environment')
                PythonActivity = autoclass('org.kivy.android.PythonActivity')

                # Создаем Intent для отправки файлов
                intent = Intent(Intent.ACTION_SEND_MULTIPLE)
                intent.setType("application/octet-stream")  # Тип файлов (можно изменить на нужный)

                # Подготавливаем файлы для отправки
                file1 = File(self.file1)
                file2 = File(self.file2)

                uri1 = Uri.fromFile(file1)
                uri2 = Uri.fromFile(file2)

                # Список URI файлов
                uris = [uri1, uri2]

                # Добавляем файлы в Intent
                intent.putParcelableArrayListExtra(Intent.EXTRA_STREAM, uris)

                # Заголовок письма и его содержимое
                intent.putExtra(Intent.EXTRA_SUBJECT, "Файлы с данными")
                intent.putExtra(Intent.EXTRA_TEXT, "Отправляю два файла во вложении.")

                # Открытие диалога выбора приложения для отправки
                current_activity = PythonActivity.mActivity
                chooser = Intent.createChooser(intent, "Отправить файлы через...")
                current_activity.startActivity(chooser)

                self.log_message(f"Файлы готовы к отправке:\n{self.file1}\n{self.file2}")
            else:
                self.log_message("Один или оба файла не найдены!")

        except Exception as e:
            self.log_message(f"Ошибка при отправке файла: \n {str(e)}")
            traceback.print_exc()


    def send_text(self, instance):
        """Отправка пути к файлам по почте"""
        try:
            # Проверка, что файлы существуют
            if os.path.exists(self.file1) and os.path.exists(self.file2):
                # Отправляем письмо с путями к файлам
                email.send(
                    recipient="vitaly.kukoba@gmail.com",  # Укажите реального получателя
                    subject="Файлы с данными",  # Тема письма
                    text=f"Во вложении пути к файлам:\n{self.file1}\n{self.file2}",  # Текст письма с путями к файлам
                    create_chooser=False
                )
                self.log_message(f"Файлы готовы к отправке:\n{self.file1}\n{self.file2}")
            else:
                self.log_message("Один или оба файла не найдены!")

        except Exception as e:
            self.log_message(f"Ошибка при отправке файла: \n {str(e)}")
            traceback.print_exc()


if __name__ == '__main__':
    MainApp().run()

'''    def request_storage_permissions():
        # Запрашиваем разрешения на чтение и запись в хранилище
        request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])

    def check_storage_permissions():
        if check_permission(Permission.READ_EXTERNAL_STORAGE) and check_permission(Permission.WRITE_EXTERNAL_STORAGE):
            MainApp.log_message("Разрешения предоставлены")
        else:
            MainApp.log_message("Разрешения не предоставлены, необходимо запросить.")
            request_storage_permissions()'''