import sqlite3
import json
import os
import uuid


def get_random_db_path():
    return f"/tmp/.{uuid.uuid4()}.db"


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


class SQLHandler(object):
    def __init__(self, hide_attributes=True, db_path=None, in_memory=False, tfstate_file=None):
        self.hide_attributes = hide_attributes
        self.db_path = db_path
        self.tfstate_file = tfstate_file
        if self.db_path is None:
            self.db_path = get_random_db_path()
        if in_memory:
            self.db_path = "file::memory:"
        self.conn = self.get_new_db()
        self.conn.row_factory = dict_factory
        self.cursor = self.conn.cursor()

    def create_table(self, resources):
        if self.hide_attributes:
            resources = self.__hide_attributes(resources)
        if len(resources) == 0:
            k = ['mode', 'type', 'name', 'provider', 'module', 'attributes', 'dependencies']
        else:
            k = list(resources[0].keys())

        k.append("tfstate_file")


        sql = "CREATE TABLE IF NOT EXISTS resources(\n"
        for i in enumerate(k):
            if i[1] in ("attributes", "dependencies"):
                sql += f"`{i[1]}` json default null"
            else:
                sql += f"`{i[1]}` text default null"
            if i[0] != len(k) - 1:
                sql += ",\n"
        sql += '\n)'

        self.cursor.execute(sql)

    def get_new_db(self):
        self.conn = sqlite3.connect(self.db_path)
        return self.conn

    def remove_db(self):
        if self.db_path:
            if os.path.exists(self.db_path):
                os.remove(self.db_path)

    def return_db(self):
        return self.conn

    def query(self, sql, parse_attributes=True):
        self.cursor.execute(sql)
        res = self.cursor.fetchall()
        if parse_attributes is False:
            return res
        output = []
        for i in res:
            if "attributes" in i:
                i["attributes"] = json.loads(i["attributes"])
            if "dependencies" in i:
                i["dependencies"] = json.loads(i["dependencies"])
            output.append(i)

        return output

    def insert_resources(self, resources):
        if self.hide_attributes:
            resources = self.__hide_attributes(resources)
        for resource in resources:
            self.insert_resource(resource)

    def __hide_attributes(self, resources):
        output = []
        for resource in resources:
            new_resource = {}
            for j in resource.keys():
                if j.startswith("__"):
                    continue
                new_resource[j] = resource[j]
            output.append(new_resource)
        return output

    def insert_resource(self, resource):
        resource["tfstate_file"] = os.path.basename(self.tfstate_file)

        sql = "INSERT INTO resources("
        for i in enumerate(resource):
            sql += f"`{i[1]}`"
            sql += ", "

        sql = sql[0:-2]
        sql += ") VALUES ("

        for i in enumerate(resource):
            sql += f":{i[1]}"
            sql += ", "
        sql = sql[0:-2]
        sql += ");"

        for k in resource.keys():
            if type(resource[k]) not in [str, type(None)]:
                resource[k] = json.dumps(resource[k])

        try:
            self.cursor.execute(sql, resource)
            self.conn.commit()
        except Exception as e:
            print(e)
