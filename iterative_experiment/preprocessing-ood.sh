scp server:/tmp/patator-ood.pcap .


tshark -r patator-ood.pcap -Y 'tcp.port==443' -w patator-443-ood.pcap
gradle -p ../../../CICFlowMeter exeCMD -Pmyargs=''$(pwd)'/patator-443-ood.pcap,'$(pwd)'' >> /dev/null
../../src_ttl_extractor/target/release/src_ttl_extractor ./patator-443-ood.pcap_Flow.csv ./patator-443-ood.pcap 128.111.5.227 ./ood_ttl.csv >> /dev/null
rm patator-ood.pcap patator-443-ood.pcap
mv patator-443-ood.pcap_Flow.csv ood_dataset.csv
