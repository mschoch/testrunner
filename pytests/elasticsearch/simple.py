import time

from couchbase.documentgenerator import BlobGenerator
from remote.remote_util import RemoteMachineShellConnection
from elasticsearch import ElasticSearchSupport

class ElasticSearchSimpleTests(ElasticSearchSupport):

    def setUp(self):
        super(ElasticSearchSimpleTests, self).setUp()
        self.value_size = self.input.param("value_size", 256)
        self.nodes_in = self.input.param("nodes_in", 1)
        self.nodes_out = self.input.param("nodes_out", 1)
        self.doc_ops = self.input.param("doc_ops", None)
        if self.doc_ops is not None:
            self.doc_ops = self.doc_ops.split(";")
        #define the data that will be used to test
        self.blob_generator = self.input.param("blob_generator", True)
        if self.blob_generator:
            #gen_load data is used for upload before each test(1000 items by default)
            self.gen_load = BlobGenerator('mike', 'mike-', self.value_size, end=self.num_items)
            #gen_update is used for doing mutation for 1/2th of uploaded data
            self.gen_update = BlobGenerator('mike', 'mike-', self.value_size, end=(self.num_items / 2 - 1))
            #upload data before each test
            self._load_all_buckets(self.servers[0], self.gen_load, "create", 0)
        else:
            self._load_doc_data_all_buckets()
	self.log.warning("after setUp")

    def tearDown(self):
	self.log.warning("before tearDown")
        super(ElasticSearchSimpleTests, self).tearDown()
	self.log.warning("after tearDown")

    def load_data(self):
	self.log.warning("before simple")
        gen_delete = BlobGenerator('mike', 'mike-', self.value_size, start=self.num_items / 2, end=self.num_items)
        gen_create = BlobGenerator('mike', 'mike-', self.value_size, start=self.num_items + 1, end=self.num_items * 3 / 2)
        if(self.doc_ops is not None):
            tasks = []
            # define which doc's ops will be performed during rebalancing
            # allows multiple of them but one by one
            if("update" in self.doc_ops):
                tasks += self._async_load_all_buckets(self.master, self.gen_update, "update", 0)
            if("create" in self.doc_ops):
                tasks += self._async_load_all_buckets(self.master, gen_create, "create", 0)
            if("delete" in self.doc_ops):
                tasks += self._async_load_all_buckets(self.master, gen_delete, "delete", 0)
            for task in tasks:
                task.result()
        self.verify_cluster_stats(self.servers[:1])
        super(ElasticSearchSimpleTests, self)._wait_for_elasticsearch(self.servers[:1])
        super(ElasticSearchSimpleTests, self)._verify_elasticsearch(self.servers[:1])
        self.log.warning("after simple")
