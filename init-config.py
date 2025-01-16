import csv
import os
from jinja2 import Environment, FileSystemLoader

def get_env_credentials():
    username = os.environ.get("SWITCH_ADMIN_USER", "admin")
    password = os.environ.get("SWITCH_ADMIN_PASS", "cisco123")
    return username, password

def read_acl_csv(csv_path):
    acl_entries = []
    with open(csv_path, mode='r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            entry = {
                "source_subnet": row.get("source_subnet"),
                "protocol": row.get("protocol"),
                "dest_port": row.get("dest_port"),
                "action": row.get("action"),
                "remark": row.get("remark")
            }
            acl_entries.append(entry)
    return acl_entries

def read_hosts_csv(csv_path):
    hosts_data = []
    with open(csv_path, mode='r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            hosts_data.append({
                "hostname": row.get("hostname"),
                "mgmt_ip": row.get("mgmt_ip"),
                "mgmt_gw": row.get("mgmt_gw"),
                "session_limit": row.get("session_limit"),
                "nxapi_port": row.get("nxapi_port")
            })
    return hosts_data

def render_config(template_env, template_file, data_dict):
    template = template_env.get_template(template_file)
    return template.render(data_dict)

def save_config(config_str, hostname):
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    filename = f"init-config-{hostname}.txt"
    full_path = os.path.join(OUTPUT_FOLDER, filename)
    with open(full_path, 'w') as f:
        f.write(config_str)
    print(f"Saved config for '{hostname}' to: {full_path}")

def main():

    TEMPLATE_FOLDER = "templates"
    DATA_FOLDER = "data"
    OUTPUT_FOLDER = "outputs"
    TEMPLATE_FILE = "init-config.j2"
    ACL_CSV_FILE = "init-config-acl.csv"
    HOSTS_CSV_FILE = "init-config-hosts.csv" 

    env = Environment(
        loader=FileSystemLoader(TEMPLATE_FOLDER),
        trim_blocks=True,
        lstrip_blocks=True
    )

    acl_file_path = os.path.join(DATA_FOLDER, ACL_CSV_FILE)
    try:
        acl_entries = read_acl_csv(acl_file_path)
    except FileNotFoundError:
        print(f"Error: CSV file '{acl_file_path}' not found.")
        return
    except Exception as e:
        print(f"Error reading CSV file '{acl_file_path}': {e}")
        return

    hosts_file_path = os.path.join(DATA_FOLDER, HOSTS_CSV_FILE)
    try:
        hosts_data = read_hosts_csv(hosts_file_path)
    except FileNotFoundError:
        print(f"Error: CSV file '{hosts_file_path}' not found.")
        return
    except Exception as e:
        print(f"Error reading CSV file '{hosts_file_path}': {e}")
        return

    username, password = get_env_credentials()

    for host in hosts_data:
        data_dict = {
            "hostname": host["hostname"],
            "mgmt_ip": host["mgmt_ip"],
            "mgmt_gw": host["mgmt_gw"],
            "session_limit": host["session_limit"],
            "nxapi_port": host["nxapi_port"],
            "username": username,
            "password": password,
            "acl_entries": acl_entries
        }

        config_output = render_config(env, TEMPLATE_FILE, data_dict)
        save_config(config_output, host["hostname"])

    print("\nAll host configs generated successfully!")

if __name__ == "__main__":
    main()