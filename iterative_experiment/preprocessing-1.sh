scp server:/tmp/patator-dirty-1.pcap .
tshark -r patator-dirty-1.pcap -Y 'tcp.port==443' -w patator-443-1.pcap
docker run -v $(pwd)/patator-443-1.pcap:/tmp/patator-443-1.pcap -v $(pwd):/tmp/output --rm pinot.cs.ucsb.edu/cicflowmeter:latest /tmp/patator-443-1.pcap /tmp/output
../../tools/    src_ttl_extractor/target/release/src_ttl_extractor ./patator-443-1.pcap_Flow.csv ./patator-443-1.pcap 128.111.5.227 ./campus_ttl_1.csv >> /dev/null
rm patator-dirty-1.pcap patator-443-1.pcap
mv patator-443-1.pcap_Flow.csv campus_cicfeatures_1.csv



scp netunicorn-azure-1:/tmp/patator-azure-1.pcap .
tshark -r patator-azure-1.pcap -Y 'tcp.port==26511 || tcp.port==80' -w patator-443-azure-1.pcap
gradle -p ../../../CICFlowMeter exeCMD -Pmyargs=''$(pwd)'/patator-443-azure-1.pcap,'$(pwd)'' >> /dev/null
../../src_ttl_extractor/target/release/src_ttl_extractor ./patator-443-azure-1.pcap_Flow.csv ./patator-443-azure-1.pcap 10.1.0.4 ./azure_ttl_1.csv >> /dev/null
rm patator-azure-1.pcap patator-443-azure-1.pcap
mv patator-443-azure-1.pcap_Flow.csv azure_cicfeatures_1.csv



scp netunicorn-azure-1:/tmp/patator-multicloud-1.pcap .
tshark -r patator-multicloud-1.pcap -Y 'tcp.port==26511 || tcp.port==80' -w patator-443-multicloud-1.pcap
gradle -p ../../../CICFlowMeter exeCMD -Pmyargs=''$(pwd)'/patator-443-multicloud-1.pcap,'$(pwd)'' >> /dev/null
../../src_ttl_extractor/target/release/src_ttl_extractor ./patator-443-multicloud-1.pcap_Flow.csv ./patator-443-multicloud-1.pcap 10.1.0.4 ./multicloud_ttl_1.csv >> /dev/null
rm patator-multicloud-1.pcap patator-443-multicloud-1.pcap
mv patator-443-multicloud-1.pcap_Flow.csv multicloud_cicfeatures_1.csv
