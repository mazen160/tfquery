# 🌩️ tfquery 🌩️

## Run SQL queries on your Terraform infrastructure. Ask questions that are hard to answer


<p align="center">
  <img src="https://raw.githubusercontent.com/mazen160/public/master/static/images/tfquery-demo.png" />
</p>

---

# 🚀 What is tfquery?

tfquery is a framework that allows running SQL queries on Terraform code. It's made to analyze your Terraform infrastructure, locate resources, run security compliance checks, spot misconfigured resources, develop CI benchmarks, and much more.

tfquery is made to help in answering questions that are hard to answer about your infrastructure-as-code. It allows querying resources and analyzing its configuration using a SQL-powered framework.

# Why?

infrastructure-as-code is the de-facto today for documenting and deploying infrastructure on cloud providers. As the organization grows, it becomes really hard to understand and analyze the deployed infrastructure. Grepping and searching for researches in Terraform state files is not enough. Terraform Modules are automating processes dynamically for infrastructure deployment, so searching for static resources is also not feasible for good visibility.

With tfquery, you can run SQL queries on Terraform state files, and gain the best possible visibility.

---

# 💡 Use tfquery to

- Have full coverage of your infrastructure, without being locked on a specific provider, including Amazon AWS, Microsoft Azure, Google Cloud Platform, Alibaba Cloud, IBM Cloud, Oracle Cloud, and many others.

- Analyze deployed resources configuration.

- Develop CI and monitoring checks for cloud infrastructure.

- Write custom queries to scan Terraform resources.

---

# tfquery vs. Cloud-specific SQL engines?

There are cloud-specific SQL engines that allow you to run SQL queries to understand resources on their infrastructure, both are covered as provided service by the cloud provider, or given as an open-source tool or a product. The main difference tfquery brings:

- **Maintainability**: Cloud-specific SQL engines require maintenance in case of new services or breaking changes to existing ones. tfquery make use of Terraform schemas as a standard. tfquery will work on all given services, without the need to continuously update it with new API specs.

- **Coverage**: tfquery covers all the cloud providers that Terraform supports out of the box (thanks to Terraform Providers).

---

# 📖 Usage

#### Run SQL query on Terraform states

```python
>>> import tfquery
>>>
>>> result = tfquery.tfstate.run_query("terraform.tfstate", "select count(*) from resources")
>> print(result)
[{'count(*)': 86}]
```

#### Parse all resources from a Terraform state file

```python
>>> import tfquery
>>>
>>> resources = tfquery.tfstate.parse_resources("terraform.tfstate")
>>> print(f"[i] Resources Count: {len(resources)}")
[i] Resources Count: 1475
```

## Advanced Usage

### Migrate Version 3 to Version 4 Terraform states

This is a parsing library to migrate the older Version 3 Terraform states to a Version 4 state. This is made to add backward compatibility for Terraform states that is made for releases older than `Terraform v0.11`.

```python
>>> import tfquery
>>>
>>> tfstate_v3 = tfquery.tfstate.load_file("terraform.tfstate")
>>> tfstate_v4 = tfquery.tfstate_v3_migration.upgrade_v3_tfstate(tfstate)

```

## 🖲️ Command-Line (`tfquery`)

TFquery is also available as a CLI tool. It can be used to run SQL queries directly on Terraform states, and for importing resources into persistent storage.

```shell
mazin@hackbox$> tfquery -h

usage: tfquery [-h] [--tfstate TFSTATE] [--tfstate-dir TFSTATE_DIR]
                      [--query QUERY] [--db DB_PATH] [--interactive] [--import]

tfquery: Run SQL queries on your Terraform infrastructure.

optional arguments:
  -h, --help            show this help message and exit
  --tfstate TFSTATE     Terraform .tfstate file.
  --tfstate-dir TFSTATE_DIR
                        Directory of Terraform .tfstate files, for running queries on
                        environments.
  --query QUERY, -q QUERY
                        SQL query to execute.
  --db DB_PATH          DB path (optional. default: temporarily-generated database).
  --interactive, -i     Interactive mode.
  --import              Import tfstate into database.
```

### Examples

- **Run SQL query for a directory of multiple Terraform states (for multiple workspaces).**:

```python
$ tfquery -q 'select count(*) as count from resources;'  --tfstate-dir /path/to/terraform-states
[i] DB Path: tfstate.db
[+] Imported 4203 resources from ./prod.tfstate.
[i] DB Path: tfstate.db
[+] Imported 3675 resources from ./nonprod.tfstate.
[i] DB Path: tfstate.db
[+] Imported 463 resources from ./qa.tfstate.
```

- **Import Terraform states into Database.**:

```python
$ python3 tfquery --tfstate /path/to/terraform.state --db tfstate.db --import
[i] DB Path: tfstate.db
[+] Imported 386 resources from terraform.tfstate.
```

- **Run queries on imported resources in a database**

```python
$ tfquery --db tfstate.db -q 'select count(*) as count from resources;'
[
    {
        "count": 386
    }
]
```

---

# 💭 Awesome Queries & Scripts

**Find all AWS S3 buckets without versioning being enabled**

```python
import tfquery, sys
results = tfquery.tfstate.run_query(sys.argv[1], "select * from resources where type = 'aws_s3_bucket'")
for result in results:
    attributes = result["attributes"]
    if 'versioning' not in attributes or len(attributes["versioning"]) == 0:
        # print(result)
        continue
    for versioning in attributes["versioning"]:
        if versioning["enabled"] is False:
            # print(result)
            pass
```

**Find all AWS IAM users, and print their ARNs**

```python
import tfquery, sys
results = tfquery.tfstate.run_query(sys.argv[1], "select json_extract(attributes, '$.arn') as arn from resources where type = 'aws_iam_user';")
for result in results:
    print(result["arn"])
```

or

```python
import tfquery, sys
results = tfquery.tfstate.run_query(sys.argv[1], "select attributes from resources where type = 'aws_iam_user';")
for result in results:
    print(result["attributes"]["arn"])
```

**Find all resources in the environment, and show how many instances were deployed**

```python
import tfquery
results = tfquery.tfstate.run_query("terraform.tfstate", "select type, count(*) as count from resources group by type order BY count desc;")
print(results)
```

---

# ✨ Interested in tfquery?

1. **Post a Tweet about the project and tag [`@mazen160`](https://twitter.com/mazen160) 🙏**

2. **🌟 Star it on Github 🌟**

3. **Create a PR for a new awesome feature 💛**

4. **Would like to sponsor the project? Contact me on email!**

---

# 💻 Contribution

Contribution is always welcome! Please feel free to report issues on Github and create PRs for new features.

## 📌 Ideas to Start on

Would like to contribute to tfquery? Here are some ideas that you may start with:

- Better documentation: would be great to enhance the documentation with additional examples and queries.

- CI: Implement CI along with test terraform states for Terragoat.

- Support dependencies for resources lookup: Create a new table called "dependencies", parse V4 Terraform states, and implement a many-to-one relation for dependencies of resources.

- More V3 --> V4 migration support: currently V3 resources migrations are supported. Dependencies are not migrated to the new V4 state. It will be great to continue on V3--> V4 support for Terraform states.

- General validation of Terraform states parser implementation: Validate current implementation of the parser, and enhance it where possible.

- [x] ~~Connect resources with terraform state base name: For environments with many workspaces, each workspace can have a different name, it would be nice to add a column for terraform state file base name, to help in querying across different workspaces.~~

- tfplan parsing: Allow parsing of tfplan files. This can be an opening addition for implementing a new CI security scanner for Terraform deployments.

- Logo design: a logo design would be great.

- Web interface representation with [coleifer/sqlite-web](https://github.com/coleifer/sqlite-web) - Thanks [@securityfu](https://twitter.com/securityfu/) for the idea!

### As you can see, there are many ways to support. Please help us make the project bigger for everyone!

---

# Installation

```shell

mazin@hackbox$> git clone https://github.com/mazen160/tfquery.git
mazin@hackbox$> cd tfquery
mazin@hackbox$> python3 setup.py install

```

or

```shell
mazin@hackbox$> pip install git+https://github.com/mazen160/tfquery
```

---

# 📄 License

The project is licensed under MIT License.

# 💚 Author

**Mazin Ahmed**

- **Website**: [https://mazinahmed.net](https://mazinahmed.net)
- **Email**: `mazin [at] mazinahmed [dot] net`
- **Twitter**: [https://twitter.com/mazen160](https://twitter.com/mazen160)
- **Linkedin**: [http://linkedin.com/in/infosecmazinahmed](http://linkedin.com/in/infosecmazinahmed)
