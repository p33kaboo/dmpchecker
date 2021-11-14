import os
import shutil
import sys
import time
#import zipfile
from distutils.util import strtobool

from notifypy import Notify

start_msg = """
░█████╗░██╗░░██╗██╗░░██╗░█████╗░███╗░░██╗███╗░░██╗███████╗██╗░░██╗████████╗  ██████╗░██╗░░░██╗███╗░░░███╗██████╗░
██╔══██╗╚██╗██╔╝╚██╗██╔╝██╔══██╗████╗░██║████╗░██║██╔════╝╚██╗██╔╝╚══██╔══╝  ██╔══██╗██║░░░██║████╗░████║██╔══██╗
███████║░╚███╔╝░░╚███╔╝░██║░░██║██╔██╗██║██╔██╗██║█████╗░░░╚███╔╝░░░░██║░░░  ██║░░██║██║░░░██║██╔████╔██║██████╔╝
██╔══██║░██╔██╗░░██╔██╗░██║░░██║██║╚████║██║╚████║██╔══╝░░░██╔██╗░░░░██║░░░  ██║░░██║██║░░░██║██║╚██╔╝██║██╔═══╝░
██║░░██║██╔╝╚██╗██╔╝╚██╗╚█████╔╝██║░╚███║██║░╚███║███████╗██╔╝╚██╗░░░██║░░░  ██████╔╝╚██████╔╝██║░╚═╝░██║██║░░░░░
╚═╝░░╚═╝╚═╝░░╚═╝╚═╝░░╚═╝░╚════╝░╚═╝░░╚══╝╚═╝░░╚══╝╚══════╝╚═╝░░╚═╝░░░╚═╝░░░  ╚═════╝░░╚═════╝░╚═╝░░░░░╚═╝╚═╝░░░░░
░█████╗░██╗░░██╗███████╗░█████╗░██╗░░██╗███████╗██████╗░
██╔══██╗██║░░██║██╔════╝██╔══██╗██║░██╔╝██╔════╝██╔══██╗
██║░░╚═╝███████║█████╗░░██║░░╚═╝█████═╝░█████╗░░██████╔╝
██║░░██╗██╔══██║██╔══╝░░██║░░██╗██╔═██╗░██╔══╝░░██╔══██╗
╚█████╔╝██║░░██║███████╗╚█████╔╝██║░╚██╗███████╗██║░░██║
░╚════╝░╚═╝░░╚═╝╚══════╝░╚════╝░╚═╝░░╚═╝╚══════╝╚═╝░░╚═╝
"""


class DumpGrabber:
    def __init__(self):
        self.notification = Notify()
        self.next_server_logs = os.path.join(os.environ['PROGRAMDATA'], 'AxxonSoft\AxxonNext\Logs')
        self.next_client_logs_archive = os.path.join(self.next_server_logs, 'Archive')
        self.postgresql_logs = os.path.join(os.environ['COMMONPROGRAMFILES'], 'AxxonSoft\PostgreSQL.NGP')
        self.next_client_logs = os.path.join(os.environ['LOCALAPPDATA'], 'AxxonSoft\AxxonNext\Logs')

        self.all_dumps = set()
        self.timeout = 2

    def drop_dmp_file_notify(self):
        self.notification.title = "Упал дамп IPINT.HOST"
        self.notification.message = "ПОРА ЗАБИВАТЬ КРИТИКАЛ ISSUE! :)"
        self.notification.icon = "logo.jpg"
        self.notification.send()

    @classmethod
    def __generate_logs_path(cls, path: str):
        logs = map(lambda file: os.path.join(path, file), os.listdir(path))
        return filter(lambda file: os.path.isfile(file), logs)

    @classmethod
    def __close_program(self):
        sys.exit(0)

    # this function lookind dumps in logs folder every N seconds
    def looking_for_dmp(self):
        print(f"Система запущена. Ждем падения дампов в папке: {self.next_server_logs}")
        while True:
            dumps = set(filter(lambda x: x.startswith('APP_HOST.Ipint') and 'dmp' in x and 'terminated' not in x,
                               os.listdir(self.next_server_logs)))
            if dumps - self.all_dumps:
                self.all_dumps |= dumps
                self.drop_dmp_file_notify()
                print("Упал дамп! Для продолжения работы программы, необходимо очистить логи!")
                self.collect_dumps()
                print("Продолжаем ждать падения дампов.")
            time.sleep(self.timeout)

    def collect_dumps(self):
        answer = input("Удалить логи и продолжить работу? Y/N: ")
        delete_log_flag = bool(strtobool(answer))
        self.stop_ngp_process()
        if delete_log_flag:
            self.delete_logs()
        else:
            self.__close_program()

        self.start_ngp_process()

    @property
    def status_ngp_process(self) -> str:
        return 'Готово'

    def stop_ngp_process(self):
        # print("Остановка NGP-процесса")
        # os.system('NET STOP ngp_host_service"')
        pass

    def start_ngp_process(self):
        pass

    def restart_ngp_process(self):
        self.stop_ngp_process()
        self.start_ngp_process()

    @classmethod
    def __remove_files_in_dir(cls, files):
        for file in files:
            print(f"Удаляем файл {file}")
            os.remove(file)


    def delete_logs(self):
        client_logs_path = self.__generate_logs_path(self.next_client_logs)
        server_logs_path = self.__generate_logs_path(self.next_server_logs)
        postgresql_logs_path = self.__generate_logs_path(self.postgresql_logs)
        server_logs_archive = self.__generate_logs_path(self.next_client_logs_archive)

        # self.stop_ngp_process()
        self.__remove_files_in_dir(client_logs_path)
        self.__remove_files_in_dir(server_logs_path)
        self.__remove_files_in_dir(postgresql_logs_path)
        self.__remove_files_in_dir(server_logs_archive)
        # self.start_ngp_process()


if __name__ == "__main__":
    print(start_msg)
    d = DumpGrabber()
    d.looking_for_dmp()
