def get_resources(tfstate):
    def __get_name(k):
        s = k.split(".")
        del s[0]
        return ".".join(s)
    output = []
    for a in tfstate["modules"]:
        for b in a["resources"]:
            data = {"type": None, "path": None, "mode": "version_3", "name": None, "provider": None, "instances": []}
            data["path"] = "/".join(a["path"])
            data["type"] = a["resources"][b]["type"]
            data["name"] = __get_name(b)
            data["provider"] = a["resources"][b]["provider"]

            dependencies = a["resources"][b]["depends_on"]
            attributes = a["resources"][b]["primary"]["attributes"]
            data_object = {"attributes": attributes, "dependencies": dependencies}

            data["instances"].append(data_object)
            output.append(data)
    return output


def upgrade_v3_tfstate(tfstate):
    tfstate["resources"] = get_resources(tfstate)
    tfstate["version"] = 4
    return tfstate
