#!/usr/env python3
import argparse
import sys
import logging

from tfquery.sql_handler import SQLHandler
import tfquery.utils as utils
from tfquery.sql_handler import get_random_db_path


def main():
    parser = argparse.ArgumentParser(
        description='tfquery-cli: Run SQL queries on your Terraform infrastructure.')
    parser.add_argument('--tfstate', dest='tfstate', action='store',
                        help='Terraform .tfstate file.')
    parser.add_argument('--tfplan', dest='tfplan', action='store',
                        help='Terraform tfplan JSON file.')
    parser.add_argument('--tfstate-dir', dest='tfstate_dir', action='store',
                        help='Directory of Terraform .tfstate files, for running queries on environments.')
    parser.add_argument('--query', '-q', dest='query', action='store',
                        help='SQL query to execute.')
    parser.add_argument('--db', dest='db_path', action='store',
                        help='DB path (optional. default: temporarily-generated database).')
    parser.add_argument('--interactive', '-i', dest='interactive_mode', action='store_true',
                        help='Interactive mode.')
    parser.add_argument('--import', dest='import_tf_file', action='store_true',
                        help='Import tfstate and tfplan into database.')
    parser.add_argument('--include-tfplan-no-op', dest='include_tfplan_no_np', action='store_true',
                        help='Include tfplan no-op actions.')
    args = parser.parse_args()
    logging.basicConfig(format='%(message)s')
    log = logging.getLogger("tfquery")

    if len(sys.argv) <= 1:
        log.error("tfquery-cli: Run with -h for help")
        exit(1)

    tfstates = []
    if args.tfstate:
        for f in args.tfstate.split(","):
            tfstates.append(f)

    if args.tfstate_dir:
        tfstates.extend(utils.get_all_tfstates(args.tfstate_dir))

    if len(tfstates) == 0 and args.import_tf_file and not args.tfplan:
        log.error("Terraform states are not provided. Run -h for help.")
        exit(1)

    if len(tfstates) == 0 and args.db_path is None and not args.tfplan:
        log.error("Both Terraform states and database are not specified.")
        exit(1)

    if args.db_path is None:
        args.db_path = get_random_db_path()
        args.import_tf_file = True

    if args.import_tf_file:
        for tfstate in tfstates:
            utils.import_tfstate(args.db_path, tfstate)
        if args.tfplan:
            utils.import_tfplan(args.db_path , args.tfplan, include_no_op=args.include_tfplan_no_np)

    if args.query:
        s = SQLHandler(hide_attributes=True, db_path=args.db_path)
        print()
        print(utils.beautify_json(s.query(args.query)))

    if args.interactive_mode:
        while True:
            print("%> ", end="")
            q = input()
            s = SQLHandler(hide_attributes=True, db_path=args.db_path)
            print()
            print(utils.beautify_json(s.query(q)))

if __name__ == "__main__":
    main()
