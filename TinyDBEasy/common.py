import json
import os.path
from typing import Optional

from ImageWin.util.config import LOGDIR, DBDIR
from os import path
from ImageWin.util.task_crawler import CrawlerTask
from TaskManger.task_manager import Task
from tinydb import TinyDB


class db_core(object):
    @classmethod
    def key_filter(cls, key: str) -> str:
        disable_symbols = [".", "/", "|", "-", "\\", "?", "\"", "｜", "*", ":", ">", "<"]
        for symbol in disable_symbols:
            key = key.replace(symbol, "_")

        return key
    pass

    def insert_by_key(self, key: str, value: dict):
        raise NotImplementedError
    def find_by_key(self, key: str):
        raise NotImplementedError
    def update_by_key(self, key: str, column: str, value):
        raise NotImplementedError
    def delete_by_key(self, key: str):
        raise NotImplementedError
    def find_all(self) -> [tuple]:
        raise NotImplementedError


class db_tiny(db_core):
    def __init__(self,db_save_path=None, db_name = "db_event_information",tabel_name="default"):
        self._opened = True
        db_save_path = DBDIR if db_save_path is None else db_save_path
        self.db_dir = f"{db_save_path}{db_name}.json"
        self.db_file = TinyDB(self.db_dir, ensure_ascii=False)
        self.key_label = "id"
        self.tabel_name = tabel_name
        self.db = self.db_file.table(self.tabel_name)

    def __enter__(self):
        """
        Use the database as a context manager.

        Using the database as a context manager ensures that the
        :meth:`~tinydb.database.TinyDB.close` method is called upon leaving
        the context.

        :return: The current instance
        """
        return self

    def __exit__(self, *args):
        """
        Close the storage instance when leaving a context.
        """
        if self._opened:
            self._opened = False
            self.close()

    def close(self):
        self.db_file.close()

    #
    def insert(self, value: dict, table: str = None):
        if table is not None:
            db_table = self.db_file.table(table)
        else:
            db_table = self.db
        db_table.insert(value)

    def insert_by_key(self, key: str, value: dict):

        new_key = self.key_filter(key=key)
        assert self.find_by_key(key=new_key) == [], f"key is exist: {new_key}"

        value.update({self.key_label:new_key})
        self.insert(value=value)

    def find(self, requirements: [tuple]):
        """

        :param requirements:
        requirements=[
            (field_name, "==", want_field_name)
        ]
        :return:
        """
        return self.db.search(lambda row: self._basic_cond(row, requirements))

    def find_by_key(self, key: str):
        requirements=[
            (self.key_label, "==", self.key_filter(key=key))
        ]
        return self.find(requirements=requirements)

    def update(self, update_fields: dict, requirements: [tuple]):
        """

        :param update_fields:
            {
                "want_updated_field1": "New Value 1",
                "want_updated_field2": "New Value 2",
            }
        :param requirements:
        :return:
        """
        return self.db.update(fields=update_fields, cond=lambda row: self._basic_cond(row, requirements))

    def update_by_key(self, key: str, column: str, value):
        update_fields = {
            column: value,
        }

        new_key = self.key_filter(key=key)
        if column == self.key_label:
            assert self.find_by_key(key=new_key) == [], f"key is exist: {self.find_by_key(key=new_key)}"
        requirements = [
            (self.key_label, "==", self.key_filter(key=new_key))
        ]
        return self.update(update_fields=update_fields, requirements=requirements)

    def delete(self, requirements: [tuple]):
        return self.db.remove(cond=lambda db: self._basic_cond(db, requirements))

    def delete_by_key(self, key: str):
        requirements = [
            (self.key_label, "==", self.key_filter(key=key))
        ]
        return self.delete(requirements=requirements)

    #
    def find_all(self) -> [tuple]:
        return [(row[self.key_label], row) for row in self.db.all()]

    def drop_all(self):
        self.db_file.drop_table(name=self.tabel_name)

    def key_exist(self, key) -> bool:
        filtered_key = self.key_filter(key=key)
        return False if self.find_by_key(filtered_key) == [] else True

    #
    def _basic_cond(self, row, requirements: [tuple]):
        for column, cond, value in requirements:
            if column not in row:
                return False
            if cond == '==' and not row[column] == value:
                return False
            if cond == '!=' and not row[column] != value:
                return False
            if cond == '>' and not row[column] > value:
                return False
            if cond == '<' and not row[column] < value:
                return False
            if cond == '>=' and not row[column] >= value:
                return False
            if cond == '<=' and not row[column] <= value:
                return False
            if cond == 'substring' or cond == 'contain':
                try:
                    str(row[column]).index(value)
                except Exception:
                    return False
        return True

    """
    def loading_logfile(self):
        logfiles = os.listdir(f"{LOGDIR}")
        logfiles = [path for path in logfiles if path.endswith("json")]
        logfiles.sort()
        # print(logfiles)
        for logfile in logfiles:
            try:
                objs = CrawlerTask.load_result(filename=f"{LOGDIR}{logfile}")
                for obj in objs:
                    filtered_key = self.key_filter(obj['name'])
                    #if self.find_by_key(filtered_key) == []:
                    if not self.key_exist(filtered_key):
                        print(f"insert a new post: {filtered_key}")
                        self.insert_by_key(key=filtered_key, value=obj)
            except json.decoder.JSONDecodeError as e:
                print(f"log file error: {logfile},{e}")
    """


class db(db_core):
    def __init__(self,db_save_path=None, db_name = "db_event_information"):
        db_save_path = DBDIR if db_save_path is None else db_save_path
        if not os.path.exists(db_save_path):
            os.makedirs(db_save_path)
        self.db_dir = f"{db_save_path}{db_name}.json"
        if path.exists(self.db_dir):
            #print("loading DB")
            self.loading4file()
        else:
            #print("creating DB")
            self.db = {}
            self.output2file()

    def output2file(self):
        json.dump(obj=self.db, fp=open(self.db_dir, "w+"), ensure_ascii=False)

    def loading4file(self) -> None:
        self.db = json.load(fp=open(self.db_dir, "r+"))

    def loading_logfile(self):
        self.loading4file()
        logfiles = os.listdir(f"{LOGDIR}")
        logfiles = [path for path in logfiles if path.endswith("json")]
        logfiles.sort()
        # print(logfiles)
        for logfile in logfiles:

            try:
                objs = CrawlerTask.load_result(filename=f"{LOGDIR}{logfile}")
                for obj in objs:
                    if obj['name'] not in self.db:
                        self.insert_by_key(key=self.key_filter(obj['name']), value=obj)
            except json.decoder.JSONDecodeError as e:
                print(f"log file error: {logfile},{e}")

        self.output2file()

    def insert_by_key(self, key: str, value: dict) -> Optional[str]:
        """
        insert a new data.
        return Null if the key is exist.

        :param key:
        :param value:
        :return:
        """
        self.loading4file()
        key_filterify = self.key_filter(key=key)
        if key_filterify in self.db:
            return None
        self.db[key_filterify] = value
        self.output2file()
        return key

    def find_by_key(self, key: str) -> Optional[dict]:
        """
        Get data by key search.
        return None if key isn't exist.

        :param key:
        :return:
        """
        self.loading4file()
        key_filterify = self.key_filter(key=key)
        if key_filterify not in self.db:
            return None
        return self.db[key_filterify]

    def update_by_key(self, key: str, column: str, value) -> bool:
        """
        updated a value of column.

        :param key:
        :param column:
        :param value:
        :return: return True or False for symbol of success or not
        """
        self.loading4file()
        key_filterify = self.key_filter(key=key)
        if key_filterify not in self.db:
            return False
        if column not in db[key_filterify]:
            return False

        self.db[key_filterify][column] = value
        self.output2file()
        return True

    def delete_by_key(self, key: str):
        self.loading4file()
        self.loading_logfile()
        self.db[self.key_filter(key=key)]= None
        self.output2file()


    def find_all(self) -> list:
        self.loading4file()
        return [(key, val) for key, val in self.db.items()]


class DbTaskUpdateLoop(Task):
    def __init__(self, task_type="delay:0.1"):
        super().__init__(task_label="db")
        self.task_type = task_type

    def task_exe(self):
        with db_tiny() as db:
            self._loading_logfile(db=db)
            db.close()

    def task_exe_and_save_result(self) -> str:
        self.task_exe()
        with db_tiny() as db:
            return db.db_dir

    def _loading_logfile(self, db):
        log_files = os.listdir(f"{LOGDIR}")
        log_files = [path for path in log_files if path.endswith("json")]
        log_files.sort()
        for logfile in log_files:
            try:
                objs = CrawlerTask.load_result(filename=f"{LOGDIR}{logfile}")
                for obj in objs:
                    filtered_key = db.key_filter(obj['name'])
                    if not db.key_exist(filtered_key):
                        print(f"insert a new post: {filtered_key}")
                        db.insert_by_key(key=filtered_key, value=obj)
            except json.decoder.JSONDecodeError as e:
                print(f"log file error: {logfile},{e}")
