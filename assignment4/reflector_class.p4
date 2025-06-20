/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>

/*************************************************************************
*********************** H E A D E R S  ***********************************
*************************************************************************/

typedef bit<9>  egressSpec_t;
typedef bit<48> macAddr_t;

header ethernet_t {
	//TODO: define the following header fields
	//macAddr_t type destination address
	macAddr_t dstAddr;
	//macAddr_t type source address
	macAddr_t srcAddr;
	//16 bit etherType
	bit<16> etherType;
}

struct metadata {
    /* empty */
}

struct headers {
	//TODO: define a header ethernet of type ethernet_t
	// below, "ethernet_t" is a header type (as defined above) 
	// ethernet is a name we assign
	ethernet_t ethernet;
}

/*************************************************************************
*********************** P A R S E R  ***********************************
*************************************************************************/
// out, inout etc is the direction is should go. headers refers to the header struct type we defined above. then hdr is the variable name we decide to call it.
parser MyParser(packet_in packet,
                out headers hdr,
                inout metadata meta,
                inout standard_metadata_t standard_metadata) {

    state start {
	//TODO: define a state that extracts the ethernet header
	//and transitions to accept
	packet.extract(hdr.ethernet); // in line 26-30 we have a method called ethernet
	transition accept;
    }

}


/*************************************************************************
************   C H E C K S U M    V E R I F I C A T I O N   *************
*************************************************************************/

control MyVerifyChecksum(inout headers hdr, inout metadata meta) {   
    apply {  }
}


/*************************************************************************
**************  I N G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyIngress(inout headers hdr,
                  inout metadata meta,
                  inout standard_metadata_t standard_metadata) {

    action swap_mac_addresses() {
       macAddr_t tmp_mac;
       //TODO: swap source and destination MAC addresses
       //use the defined temp variable tmp_mac
       //in line 12-19 we defined the type ethernet_t to have the methods dstAddr, srcAddr, and etherType
       tmp_mac = hdr.ethernet.dstAddr;
       hdr.ethernet.dstAddr = hdr.ethernet.srcAddr;
       hdr.ethernet.srcAddr = tmp_mac;

       //TODO: send the packet back to the same port
    	standard_metadata.egress_spec = standard_metadata.ingress_port;
    }
    
    // drop means to discard, dont forward
    action drop() {
	mark_to_drop(standard_metadata);
    }
    
    table src_mac_drop {
        key = {
	   //TODO: define an exact match key using the source MAC address
	   hdr.ethernet.srcAddr: exact;
        }
        actions = {
	   //TODO: define 3 actions: swap_mac_addresses, drop, NoAction.
	   swap_mac_addresses;
	   drop;
	   NoAction;
        }
        //TODO: define a table size of 1024 entries
	size = 1024;
	//TODO: define the default action to return the packet to the source
	default_action = swap_mac_addresses();
    }
    
    apply {
    	//TODO: Check if the Ethernet header is valid
	//if so, lookup the source MAC in the table and decide what to do
	if (hdr.ethernet.isValid()) {
		src_mac_drop.apply();
	}
    }
}
       
       
    


/*************************************************************************
****************  E G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyEgress(inout headers hdr,
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata) {
    apply {  }
}

/*************************************************************************
*************   C H E C K S U M    C O M P U T A T I O N   **************
*************************************************************************/

control MyComputeChecksum(inout headers hdr, inout metadata meta) {
     apply {

     }
}


/*************************************************************************
***********************  D E P A R S E R  *******************************
*************************************************************************/

control MyDeparser(packet_out packet, in headers hdr) {
    apply {
	//TODO: emit the packet with a valid Ethernet header
	// there is a function from the core.p4 file that has a method emit. This sends the packet out.
	packet.emit(hdr.ethernet);
    }
}

/*************************************************************************
***********************  S W I T C H  *******************************
*************************************************************************/

V1Switch(
MyParser(),
MyVerifyChecksum(),
MyIngress(),
MyEgress(),
MyComputeChecksum(),
MyDeparser()
) main;
