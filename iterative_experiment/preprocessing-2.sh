scp server:/tmp/patator-dirty-1.pcap .
scp server:/tmp/patator-dirty-2.pcap .
scp netunicorn-azure-1:/tmp/patator-azure-1.pcap .
scp netunicorn-azure-1:/tmp/patator-azure-2.pcap .
scp netunicorn-azure-1:/tmp/patator-multicloud-1.pcap .
scp netunicorn-azure-1:/tmp/patator-multicloud-2.pcap .



tshark -r patator-dirty-1.pcap -Y 'tcp.port==443' -w patator-443-1.pcap
gradle -p ../../../CICFlowMeter exeCMD -Pmyargs=''$(pwd)'/patator-443-1.pcap,'$(pwd)'' >> /dev/null
../../src_ttl_extractor/target/release/src_ttl_extractor ./patator-443-1.pcap_Flow.csv ./patator-443-1.pcap 128.111.5.227 ./campus_ttl_1.csv >> /dev/null
rm patator-dirty-1.pcap patator-443-1.pcap

tshark -r patator-dirty-2.pcap -Y 'tcp.port==443' -w patator-443-2.pcap
gradle -p ../../../CICFlowMeter exeCMD -Pmyargs=''$(pwd)'/patator-443-2.pcap,'$(pwd)'' >> /dev/null
../../src_ttl_extractor/target/release/src_ttl_extractor ./patator-443-2.pcap_Flow.csv ./patator-443-2.pcap 128.111.5.227 ./campus_ttl_2.csv >> /dev/null
rm patator-dirty-2.pcap patator-443-2.pcap

mv patator-443-1.pcap_Flow.csv campus_dataset_1.csv
mv patator-443-2.pcap_Flow.csv campus_dataset_2.csv



tshark -r patator-azure-1.pcap -Y 'tcp.port==26511 || tcp.port==80' -w patator-443-azure-1.pcap
gradle -p ../../../CICFlowMeter exeCMD -Pmyargs=''$(pwd)'/patator-443-azure-1.pcap,'$(pwd)'' >> /dev/null
../../src_ttl_extractor/target/release/src_ttl_extractor ./patator-443-azure-1.pcap_Flow.csv ./patator-443-azure-1.pcap 10.1.0.4 ./azure_ttl_1.csv >> /dev/null
rm patator-azure-1.pcap patator-443-azure-1.pcap

tshark -r patator-azure-2.pcap -Y 'tcp.port==26511 || tcp.port==80' -w patator-443-azure-2.pcap
gradle -p ../../../CICFlowMeter exeCMD -Pmyargs=''$(pwd)'/patator-443-azure-2.pcap,'$(pwd)'' >> /dev/null
../../src_ttl_extractor/target/release/src_ttl_extractor ./patator-443-azure-2.pcap_Flow.csv ./patator-443-azure-2.pcap 10.1.0.4 ./azure_ttl_2.csv >> /dev/null
rm patator-azure-2.pcap patator-443-azure-2.pcap

mv patator-443-azure-1.pcap_Flow.csv azure_dataset_1.csv
mv patator-443-azure-2.pcap_Flow.csv azure_dataset_2.csv



tshark -r patator-multicloud-1.pcap -Y 'tcp.port==26511 || tcp.port==80' -w patator-443-multicloud-1.pcap
gradle -p ../../../CICFlowMeter exeCMD -Pmyargs=''$(pwd)'/patator-443-multicloud-1.pcap,'$(pwd)'' >> /dev/null
../../src_ttl_extractor/target/release/src_ttl_extractor ./patator-443-multicloud-1.pcap_Flow.csv ./patator-443-multicloud-1.pcap 10.1.0.4 ./multicloud_ttl_1.csv >> /dev/null
rm patator-multicloud-1.pcap patator-443-multicloud-1.pcap

tshark -r patator-multicloud-2.pcap -Y 'tcp.port==26511 || tcp.port==80' -w patator-443-multicloud-2.pcap
gradle -p ../../../CICFlowMeter exeCMD -Pmyargs=''$(pwd)'/patator-443-multicloud-2.pcap,'$(pwd)'' >> /dev/null
../../src_ttl_extractor/target/release/src_ttl_extractor ./patator-443-multicloud-2.pcap_Flow.csv ./patator-443-multicloud-2.pcap 10.1.0.4 ./multicloud_ttl_2.csv >> /dev/null
rm patator-multicloud-2.pcap patator-443-multicloud-2.pcap

mv patator-443-multicloud-1.pcap_Flow.csv multicloud_dataset_1.csv
mv patator-443-multicloud-2.pcap_Flow.csv multicloud_dataset_2.csv
