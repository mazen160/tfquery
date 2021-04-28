from tfquery.tfstate_v3_migration import upgrade_v3_tfstate
import json
from tfquery.sql_handler import SQLHandler
import logging


def validate_tfstate(tfstate):
    if "terraform_version" not in tfstate.keys():
        raise ValueError("Invalid tfstate file")
        return False
    if tfstate["version"] < 3:
        raise ValueError("Unsupported tfstate version")
        return False
    return True


def prepare_tfstate(tfstate):
    resources = []
    if tfstate["version"] == 3:
        tfstate = upgrade_v3_tfstate(tfstate)
    tfstate_updated = tfstate

    for i in tfstate["resources"]:
        data = {}
        data.update(i)
        if "module" not in data:
            data["module"] = "none"
        assert data["mode"]
        assert data["type"]
        assert data["name"]
        assert data["provider"]
        assert "instances" in data
        assert "module" in data
        resources.append(data)
    tfstate_updated["resources"] = resources
    return tfstate_updated


def get_all_attributes(tfstate):
    attributes = []
    for i in tfstate["resources"]:
        for j in i["instances"]:
            attributes.extend(j["attributes"].keys())

    def lowercase_all(k):
        return [i.lower() for i in k]

    attributes = lowercase_all(attributes)
    attributes = list(set(attributes))
    return attributes


def get_resources(tfstate):
    tfstate = prepare_tfstate(tfstate)
    resources = []
    for resource in tfstate["resources"]:
        for instance in resource["instances"]:
            data = {}
            data["mode"] = resource["mode"]
            data["type"] = resource["type"]
            data["name"] = resource["name"]
            data["provider"] = resource["provider"]
            data["module"] = resource["module"]
            data["attributes"] = instance["attributes"]
            if "dependencies" in instance:
                data["dependencies"] = instance["dependencies"]
            else:
                data["dependencies"] = []
            resources.append(data)
    return resources


def get_detailed_resources(tfstate):
    resources = get_resources(tfstate)
    detailed_resources = []
    all_attributes = get_all_attributes(tfstate)
    for resource in resources:
        data = {}
        data.update(resource)

        for i in all_attributes:
            data["__" + i] = None
        for k in resource["attributes"].keys():
            data["__" + k] = resource["attributes"][k]
        detailed_resources.append(data)
    return detailed_resources


def load_file(tfstate_file):
    f = open(tfstate_file, "r")
    tfstate = json.loads(f.read())
    f.close()
    return tfstate


def parse_resources(tfstate_file, detailed=False):
    tfstate = load_file(tfstate_file)
    if validate_tfstate(tfstate) is False:
        return([])
    if detailed:
        resources = get_detailed_resources(tfstate)
    else:
        resources = get_resources(tfstate)

    return resources


def run_query(tfstate_file, query):
    logging.basicConfig(format='%(message)s')
    log = logging.getLogger("tfquery")
    resources = parse_resources(tfstate_file)
    s = SQLHandler(in_memory=True)
    s.create_table(resources)
    s.insert_resources(resources)
    log.info(f">> {query}")
    res = s.query(query)
    s.remove_db()
    return res
