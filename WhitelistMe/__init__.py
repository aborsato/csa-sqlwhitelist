import logging
import os

import azure.functions as func
from azure.identity import DefaultAzureCredential
from azure.mgmt.sql import SqlManagementClient
from azure.mgmt.sql.models import FirewallRule


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    subscription_id = os.environ['SUBSCRIPTION_ID']
    resource_group = os.environ['RESOURCE_GROUP']
    sql_server = os.environ['SQL_SERVER']

    client_ip = req.headers.get('X-Forwarded-For', None)
    if not client_ip:
        return func.HttpResponse(f"No client IP found.")
    
    default_credential = DefaultAzureCredential()
    access_token = default_credential.get_token('https://management.core.windows.net/.default')

    sql_client = SqlManagementClient(default_credential, subscription_id)
    firewall_rule = sql_client.firewall_rules.create_or_update(
        resource_group,
        sql_server,
        f"AutomaticRuleFor_{client_ip}",
        FirewallRule(
            name=f"RuleFor{client_ip}",
            start_ip_address=client_ip,
            end_ip_address=client_ip

        )
    )

    logging.info(firewall_rule)
    return func.HttpResponse(f"Rule for IP {client_ip} implemented successfully.")
