import uuid
import logging
from .hive_node import HiveNode
from robot_hive.errors import HiveClusterEmpty

logger = logging.getLogger('robot_hive')


class HiveCluster:
    account_node = {}
    nodes        = []
    id           = uuid.uuid4()

    def get_node(self, social_account_id):
        if not self.nodes: raise HiveClusterEmpty('No nodes in the hive cluster')
        node = self.account_node.get(social_account_id)
        if not node:
            node      = self.lowest_load_node()
            node.load += 1
            self.account_node[social_account_id] = node
        return node

    def add_node(self, protocol):
        node = HiveNode(protocol)
        self.nodes.append(node)
        return node

    def lowest_load_node(self):
        # TODO check on this
        self.nodes = sorted(self.nodes, key=lambda node: node.load)
        return self.nodes[0]

    def remove_node(self, node):
        remove_accounts = []
        for account_id, account_node in self.account_node.items():
            if account_node == node:
                remove_accounts.append(account_id)

        for account_id in remove_accounts:
            del self.account_node[account_id]

        self.nodes.remove(node)
