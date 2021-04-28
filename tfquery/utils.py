#!/usr/env python3
from os import listdir
from os.path import isfile
from os.path import join
import json
import logging


import tfquery.tfstate as tfstate
from tfquery.sql_handler import SQLHandler


def get_all_tfstates(dir):
    onlyfiles = [join(dir, f) for f in listdir(dir) if isfile(join(dir, f))]
    output = []
    for i in onlyfiles:
        if i.endswith(".tfstate"):
            output.append(i)
    return output


def import_tfstate(db_path, tfstate_file):
    logging.basicConfig(format='%(message)s')
    log = logging.getLogger("tfquery")
    log.info(f"[i] tfstate file: {tfstate_file}")
    resources = tfstate.parse_resources(tfstate_file, detailed=True)
    s = SQLHandler(hide_attributes=True, db_path=db_path, tfstate_file=tfstate_file)
    log.info(f"[i] DB Path: {s.db_path}")

    s.create_table(resources)
    s.insert_resources(resources)
    log.info(f"[+] Imported {len(resources)} resources from {tfstate_file}.")


def beautify_json(j):
    return json.dumps(j, indent=4, sort_keys=True)
