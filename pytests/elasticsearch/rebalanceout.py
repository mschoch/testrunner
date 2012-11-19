import time

from rebalance.rebalanceout import RebalanceOutTests
from couchbase.documentgenerator import BlobGenerator
from remote.remote_util import RemoteMachineShellConnection
from elasticsearch import ElasticSearchSupport

class ElasticSearchRebalanceOutTests(RebalanceOutTests, ElasticSearchSupport):

    def setUp(self):
	"""self.log.warning("before setUp")"""
        super(ElasticSearchRebalanceOutTests, self).setUp()
	self.log.warning("after setUp")

    def tearDown(self):
	self.log.warning("before tearDown")
        super(ElasticSearchRebalanceOutTests, self).tearDown()
	self.log.warning("after tearDown")

    """Rebalances nodes out of a cluster while doing docs ops:create, delete, update.

    This test begins with all servers clustered together and  loads a user defined
    number of items into the cluster. It then remove nodes_out from the cluster at a time
    and rebalances. During the rebalance we perform docs ops(add/remove/update/readd)
    in the cluster( operate with a half of items that were loaded before).
    Once the cluster has been rebalanced we wait for the disk queues to drain,
    and then verify that there has been no data loss.
    Once all nodes have been rebalanced the test is finished."""
    def rebalance_out_with_ops(self):
	self.log.warning("before test")
	super(ElasticSearchRebalanceOutTests, self).rebalance_out_with_ops()
	super(ElasticSearchRebalanceOutTests, self)._wait_for_elasticsearch(self.servers[:self.nodes_in+1])
        super(ElasticSearchRebalanceOutTests, self)._verify_elasticsearch(self.servers[:self.nodes_in+1])
	self.log.warning("after test")
