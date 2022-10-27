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
    def __init__(self, hide_attributes=True, db_path=None, in_memory=False, tfstate_file=None, tfplan_file=None):
        self.hide_attributes = hide_attributes
        self.db_path = db_path
        self.tfstate_file = tfstate_file
        self.tfplan_file = tfplan_file
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

        # tfstate
        if len(resources) == 0:
            tfstate_columns = ['mode', 'type', 'name', 'provider', 'module', 'attributes', 'dependencies']
        else:
            tfstate_columns = list(resources[0].keys())
        tfstate_columns.append("tfstate_file")
        sql = "CREATE TABLE IF NOT EXISTS resources(\n"
        for i in enumerate(tfstate_columns):
            if i[1] in ("attributes", "dependencies"):
                sql += f"`{i[1]}` json default null"
            else:
                sql += f"`{i[1]}` text default null"
            if i[0] != len(tfstate_columns) - 1:
                sql += ",\n"
        sql += '\n)'
        self.cursor.execute(sql)

        # tfplan
        tfplan_columns = ['address', 'mode', 'type', 'name', 'provider', 'change_actions', 'change_before', 'change_after', 'diff_keys', "tfplan_file"]
        sql = "CREATE TABLE IF NOT EXISTS changes(\n"
        for i in enumerate(tfplan_columns):
            if i[1] in ("change_actions", "change_before", "change_after"):
                sql += f"`{i[1]}` json default null"
            else:
                sql += f"`{i[1]}` text default null"
            if i[0] != len(tfplan_columns) - 1:
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
            json_fields = "change_actions", "change_before", "change_after", "attributes", "dependencies", "diff_keys"
            for j in i.keys():
                if j in json_fields and i[j] is not None:
                    i[j] = json.loads(i[j])
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
        tfstate_file = None
        if self.tfstate_file:
            tfstate_file = os.path.basename(self.tfstate_file)
        resource["tfstate_file"] = tfstate_file


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

    def insert_change(self, change):
        tfplan_file = None
        if self.tfplan_file:
            tfplan_file = os.path.basename(self.tfplan_file)

        change["tfplan_file"] = tfplan_file

        columns = ['address', 'mode', 'type', 'name', 'provider', 'change_actions', 'change_before', 'change_after', "diff_keys", "tfplan_file"]
        sql = "INSERT INTO changes("
        for i in columns:
            sql += f"`{i}`"
            sql += ", "
        sql = sql[0:-2]
        sql += ") VALUES ("

        for i in columns:
            sql += f":{i}"
            sql += ", "
        sql = sql[0:-2]
        sql += ");"
        for k in change.keys():
            if type(change[k]) not in [str, type(None)]:
                change[k] = json.dumps(change[k])

        try:
            self.cursor.execute(sql, change)
            self.conn.commit()
        except Exception as e:
            print(e)
