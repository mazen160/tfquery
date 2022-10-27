import json
from tfquery.sql_handler import SQLHandler
from tfquery.tfstate import load_file  # API reference
import logging

def validate_tfplan(tfplan):
    if "terraform_version" not in tfplan.keys():
        raise ValueError("Invalid tfplan file")
        return False
    if "format_version" not in tfplan.keys():
        raise ValueError("Unsupported tfplan file")
        return False
    return True

def __get_keys(res):
    if type(res) == dict:
        return res.keys()
    return []

def prepare_tfplan(tfplan, include_no_op=False):
    resources = []
    for i in tfplan["resource_changes"]:
        data = {"address": None,
                "mode": None,
                "type": None,"name": None,
                "provider": None,
                "change_actions": {"actions": []},
                "change_before": {},
                "change_after": {},
                "diff_keys": []
                }
        # after_unknown, after_sensitive, before_sensitive
        # before_unknown is not there

        # check no-op actions
        is_no_op = True
        for j in  i["change"]["actions"]:
            if j != "no-op":
                is_no_op = False
        if is_no_op and not include_no_op:
            continue

        data["address"] = i["address"]
        data["mode"] = i["mode"]
        data["type"] = i["type"]
        data["name"] = i["name"]
        data["provider"] = i["provider_name"]
        data["change_actions"]["actions"] = i["change"]["actions"]
        if  i["change"]["before"]:
            data["change_before"] =  i["change"]["before"]
        if i["change"]["after"]:
            data["change_after"] = i["change"]["after"]
        for k in __get_keys(i["change"]["after_unknown"]):
            data["change_after"].update({f"unknown__{k}":  i["change"]["after_unknown"][k]})
        for k in __get_keys(i["change"]["after_sensitive"]):
            data["change_after"].update({f"sensitive__{k}":  i["change"]["after_sensitive"][k]})

        for k in __get_keys(i["change"]["before_sensitive"]):
            data["change_before"].update({f"sensitive__{k}":  i["change"]["before_sensitive"][k]})

        data["diff_keys"] = get_plan_diff_keys(data)
        for k in data["diff_keys"]:
            if k not in data["change_before"]:
                data["change_before"][k] = None
            if k not in data["change_after"]:
                data["change_after"][k] = None

        resources.append(data)

    return resources


def parse_changes(tfplan_file, include_no_op=False):
    tfplan = load_file(tfplan_file)
    if validate_tfplan(tfplan) is False:
        return([])
    changes = prepare_tfplan(tfplan, include_no_op=include_no_op)
    return changes


def run_query(tfplan_file, query, include_no_op=False):
    logging.basicConfig(format='%(message)s')
    log = logging.getLogger("tfquery")
    changes = parse_changes(tfplan_file, include_no_op=include_no_op)
    s = SQLHandler(tfplan_file=tfplan_file, in_memory=True)
    s.create_table([])
    for change in changes:
        s.insert_change(change)
    log.info(f">> {query}")
    res = s.query(query)
    s.remove_db()
    return res

def get_plan_diff_keys(data):
    diff_keys = set()
    for k in data["change_before"].keys():
        if k not in __get_keys(data["change_after"]):
            diff_keys.add(k)
            continue
        if data["change_after"][k] != data["change_before"][k]:
            diff_keys.add(k)

    for k in __get_keys(data["change_after"]):
        if k not in __get_keys(data["change_before"]):
            diff_keys.add(k)
            continue
        if data["change_after"][k] != data["change_before"][k]:
            diff_keys.add(k)

    return list(diff_keys)

