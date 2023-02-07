use std::collections::HashMap;
use std::fs::File;
use std::net::Ipv4Addr;
use std::env;
use std::process::exit;

use csv::Writer;

use pnet::datalink::{self};
use pnet::datalink::pcap::Config;
use pnet::packet::ethernet::{EthernetPacket};
use pnet::packet::ipv4::Ipv4Packet;
use pnet::packet::Packet;
use pnet::packet::tcp::TcpPacket;


fn read_and_create_flow_hashmap(filename: &str) -> HashMap<String, u8> {
    // read csv file, take first field and create hashmap with key = first field and value = 0
    let file = File::open(filename).unwrap();
    let mut flow_hashmap = HashMap::new();

    let mut rdr = csv::ReaderBuilder::new()
        .has_headers(true)
        .from_reader(file);

    let mut counter = 0;
    for record in rdr.records() {
        counter += 1;
        let record = record.unwrap();
        flow_hashmap.insert(record.get(0).unwrap().to_string(), 0);
    }

    println!("Total flows in the file: {}, total flows in the flow hashmap: {}", counter, flow_hashmap.len());

    flow_hashmap
}

fn main() {
    let args = env::args();
    if args.len() != 5 {
        println!("Usage: ./src_ttl_extractor /path/to/flow_filename.csv /path/to/pcap_filename.pcap <server ip> /path/to/output.csv");
        exit(1);
    }

    let v: Vec<String> = args.collect();
    let csv_filename = v[1].as_str();
    let pcap_filename = v[2].as_str();
    let server_ip = v[3].as_str();
    let output_csv_file = v[4].as_str();

    let server_ip = server_ip.parse::<Ipv4Addr>().unwrap();

    let mut flow_hashmap = read_and_create_flow_hashmap(csv_filename);

    let filechannel = datalink::pcap::from_file(
        pcap_filename,
        Config::default(),
    ).unwrap();

    let (_, mut rx) = match filechannel {
        datalink::Channel::Ethernet(tx, rx) => (tx, rx),
        _ => panic!("unhandled channel type"),
    };

    let mut counter = 0;
    loop {
        match rx.next() {
            Ok(packet) => {
                let ether_packet = match EthernetPacket::new(packet) {
                    Some(ether_packet) => ether_packet,
                    None => continue,
                };

                let ip_packet = match Ipv4Packet::new(ether_packet.payload()) {
                    Some(ip_packet) => ip_packet,
                    None => continue,
                };

                let source_ip = ip_packet.get_source();
                let destination_ip = ip_packet.get_destination();
                let ttl_value: u8 = ip_packet.get_ttl();

                let tcp_packet = match TcpPacket::new(ip_packet.payload()) {
                    Some(tcp_packet) => tcp_packet,
                    None => continue,
                };

                let source_port = tcp_packet.get_source();
                let destination_port = tcp_packet.get_destination();

                let first_flow = format!("{}-{}-{}-{}-6", source_ip, destination_ip, source_port, destination_port);
                let second_flow = format!("{}-{}-{}-{}-6", destination_ip, source_ip, destination_port, source_port);

                let key: String;
                if flow_hashmap.contains_key(&first_flow) {
                    key = first_flow;
                } else if flow_hashmap.contains_key(&second_flow) {
                    key = second_flow;
                } else {
                    counter += 1;
                    continue;
                }

                if source_ip == server_ip {
                    continue;
                }

                let current_ttl_value = flow_hashmap.get(key.as_str()).unwrap();
                if current_ttl_value != &0 && current_ttl_value != &ttl_value {
                    println!("Warning: different TTL values in the flow! Current TTL value: {}, new TTL value: {}", current_ttl_value, ttl_value);
                    println!("Flow: {}", key);
                }

                flow_hashmap.insert(key, ttl_value);
            }
            Err(e) => {
                if e.to_string() != "no more packets to read from the file" {
                    println!("error: {:?}", e);
                }
                break;
            }
        }
    }

    println!("Missed flows: {}", counter);

    let mut wrt = Writer::from_path(output_csv_file).unwrap();
    wrt.write_record(&["Flow ID", "TTL"]).unwrap();

    for record in flow_hashmap.iter() {
        if record.1 == &0 {
            println!("Warning: TTL value is 0 for the flow: {}", record.0);
        }
        wrt.write_record(&[format!("{}", record.0), format!("{}", record.1)]).unwrap();
    }

    println!("Successfully created {}", output_csv_file);
}


