#! /bin/sh

tempfoo=`basename $0`
TMPFILE=`mktemp /tmp/${tempfoo}.XXXXXX` || exit 1
export EXTRA_JVM_ARGUMENTS=-Xmx1024M
/home/marty/scrutineer-1.0.6-SNAPSHOT/bin/scrutineer --clusterName couchbase-test-es --indexName default --query "_type: couchbaseDocument" --couchbaseURL http://10.5.2.12:8091/couchBase/ --couchbaseBucket default --elasticSearchRevField meta.rev > $TMPFILE 2>&1

# pass the output through to the main progream
cat $TMPFILE

# change the return code to in indicate pass/fail
grep -E "NOTINPRIMARY|NOTINSECONDARY|MISMATCH" $TMPFILE

# invert the return code
if [ $? -eq 1 ]
  then exit  0
fi
exit 1
