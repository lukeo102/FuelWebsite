from datetime import date, datetime, timedelta
from os import listdir, remove, fsync, mkdir, getcwd
from os.path import isfile, join, isdir


class Log:
    log_level_colours = {
        1: "\033[35;1m",  # Debug
        2: "\033[0;36m",  # Info
        3: "\033[38;5;208m",  # Warning
        4: "\033[38;2;220;20;20m"  # Error
    }

    log_level_text = {
        1: "[DEBUG]",
        2: "[INFO]",
        3: "[WARNING]",
        4: "[ERROR]"
    }

    time = lambda: datetime.now().strftime('%H:%M:%S')

    def __init__(self, dir='log/', days_to_keep=14, init_msg=True, Id: str = None):
        """
        :param dir: directory to store log files in
        :param days_to_keep: how many days to keep log files for
        :param init_msg: whether to log an initialisation message
        :param Id: the ID of the log, only used in printing and storage of files
        """

        if Id is None:
            self.id = ""

        else:
            self.id = f"[{Id}]"

        self.dir = dir
        if not isdir(self.dir):
            mkdir(f'{getcwd()}/{self.dir[:-1]}')

        self.day = date.today().strftime('%Y-%m-%d')
        self.file = open(f'{self.dir}{self.id} - {self.day}.log', 'a', encoding="utf-8")
        self.days_to_keep = days_to_keep
        if init_msg:
            self.append_log('Start of log')

    def reset_file(self):  # Resets the log file for a new day
        self.file.write('Log roll over')
        self.file.flush()
        fsync(self.file.fileno())

        self.file.close()
        self.day = date.today().strftime('%Y-%m-%d')
        self.file = open(f'{self.dir}{self.id}{self.day}.log', 'a', encoding="utf-8")
        self.remove_old_log(self.days_to_keep)
        self.append_log('Log roll over')

    def append_log(self, message, level=2, console=True):
        if not 0 < level < 5:
            self.append_log(f"level {level} is not valid", level=4)
            return

        if self.day != date.today().strftime('%Y-%m-%d'):  # Check whether log roll over is required
            self.reset_file()

        message = f'[{Log.time()}]{self.log_level_text[level]} {message}\n'
        if console:
            print(f"{self.id}{self.log_level_colours[level]}{message[:-1]} \033[00m")

        self.file.write(message)
        self.file.flush()
        fsync(self.file.fileno())

    def remove_old_log(self, days_old=14):
        # Assumes the date portion starts at the end of the file name and is 10 characters long
        files = [f[len(f) - 14:len(f) - 4] for f in listdir(self.dir) if isfile(join(self.dir, f))]
        self.append_log(f'Deleting logs {days_old} days old')
        no_logs = 0
        for file in files:
            if file < (datetime.today() - timedelta(days=days_old)).strftime('%Y-%m-%d'):
                no_logs += 1
                remove(f'{self.dir}{file}.log')

        self.append_log(f'{no_logs} logs deleted')
