import time
import logger
from subprocess import call
from basetestcase import BaseTestCase
from membase.api.rest_client import RestConnection
from pyes import ES

class ElasticSearchSupport(BaseTestCase):

    def setUp(self):
	self.es_host = None
	self.es_cluster_name = None
	self._state = []
        super(ElasticSearchSupport, self).setUp()
        self.es_host = self.input.param("es_host", "127.0.0.1")
        self.es_port = self.input.param("es_port", 9091)
	conn = ES(self.es_host + ":9200")
        if not self.input.param("skip_cleanup", True) or self.case_number == 1:
                conn.delete_index_if_exists("default")
	conn.create_index("default")
        self.log.warning("waiting for ES index to be ready to use")
        time.sleep(30)
	self._link_es_cluster()
	self._start_es_replication()
        self.log.warning("after setUp es")

    def tearDown(self):
        self.log.warning("before tearDown es")
	self._unlink_es_cluster()
	self._stop_es_replication()
	if self.es_host != None:
		conn = ES(self.es_host + ":9200")
	        conn.delete_index_if_exists("default")
        super(ElasticSearchSupport, self).tearDown()
        self.log.warning("after tearDown es")

    def _wait_for_elasticsearch(self, servers):
	self.log.warning("waiting for replication to finish")
	time.sleep(60)

    def _verify_elasticsearch(self, server, kv_store=1):
	self.log.warning("invoking scrutineer to verify elasticsearch index")
	try:
		retcode = call("scrutineer-1.0.6-SNAPSHOT/compare.sh", shell=True)
		if retcode != 0:
			self.log.info("Child returned {0}".format(retcode))
			self.fail("scrutineer returned error")
		else:
			self.log.info("Child returned {0}".format(retcode))
	except OSError, e:
		self.log.info("Execution failed {0}".format(e))
		self.fail("execution failed")

    def _link_es_cluster(self):
	rest_conn_src = RestConnection(self.master)
        rest_conn_src.add_remote_cluster(self.es_host, self.es_port,
            "Administrator",
            "password", "ElasticSearch")
	self.es_cluster_name = "ElasticSearch"

    def _start_es_replication(self):
	rest_conn_src = RestConnection(self.master)
	(rep_database, rep_id) = rest_conn_src.start_replication("continuous",
                                                               "default",
                                                               self.es_cluster_name)
        self._state.append((rep_database, rep_id))

    def _unlink_es_cluster(self):
        rest_conn_src = RestConnection(self.master)
        rest_conn_src.remove_all_remote_clusters()

    def _stop_es_replication(self):
	rest_conn_src = RestConnection(self.master)
        rest_conn_src.remove_all_replications()
