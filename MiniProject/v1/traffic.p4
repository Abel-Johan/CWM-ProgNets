/* -*- P4_16 -*- */

/*
 * P4 Traffic Lights v1
 * The aim of the P4 script is to be the traffic light.
 * It is supposed to take data from the Python file regarding how many cars are at each junction.
 * The P4 script then sends a red/amber/green signal at each junction back to the Python file.
 * The Python file then simulates traffic flow (e.g. number of cars decrease as they start to pass through the junction, etc.)
 *
 * This program implements a simple protocol. It can be carried over Ethernet
 * (Ethertype 0x1234).
 
 * TODO
 * give a format of what the header should look like
 
 * The Protocol header looks like this:
 *
 *        0                1                  2              3
 * +----------------+----------------+----------------+----------------+
 * |      P         |       4        |     Version    | Current_Green  |
 * +----------------+----------------+----------------+----------------+
 * |     J1_car     |     J2_car     |     J3_car     |     J4_car     |
 * +----------------+----------------+----------------+----------------+
 * |                              Operand B                            |
 * +----------------+----------------+----------------+----------------+
 * |   J1_result    |   J2_result    |   J3_result    |   J4_result    |
 * +----------------+----------------+----------------+----------------+
 *
 * P is an ASCII Letter 'P' (0x50)
 * 4 is an ASCII Letter '4' (0x34)
 * Version is currently 0.1 (0x01)
 * Current_Green is the current junction with a green light
 * JX_car is the number of cars at junction X
 * JX_result is what the traffic lights at junction X should turn to
 *
 * The device receives a packet, performs the requested operation, fills in the
 * result and sends the packet back out of the same port it came in on, while
 * swapping the source and destination addresses.
 *
 * If an unknown operation is specified or the header is not valid, the packet
 * is dropped
 */
 
 
include <core.p4>
include <v1model.p4>


/*
 * Define the headers the program will recognize
 */

/*
 * Standard Ethernet header
 */
header ethernet_t {
    bit<48> dstAddr;
    bit<48> srcAddr;
    bit<16> etherType;
}

/*
 * This is a custom protocol header for the traffic light system. We'll use
 * etherType 0x1234 for it (see parser)
 */
const bit<16> P4TRAFFIC_ETYPE = 0x1234;
const bit<8>  P4TRAFFIC_P     = 0x50;   // 'P'
const bit<8>  P4TRAFFIC_4     = 0x34;   // '4'
const bit<8>  P4TRAFFIC_VER   = 0x01;   // v0.1
/* TODO
 * add more relevant headers to the protocol
 */


header p4traffic_t {
    bit<8> p;
    bit<8> four;
    bit<8> ver;
    bit<8> current_green;
    bit<8> j1_car;
    bit<8> j2_car;
    bit<8> j3_car;
    bit<8> j4_car;
    bit<32> REDUNDANT;
    bit<8> j1_result;
    bit<8> j2_result;
    bit<8> j3_result;
    bit<8> j4_result;
    /* TODO
     * define the other headers in the correct order
     */
  
}

/*
 * All headers, used in the program needs to be assembled into a single struct.
 * We only need to declare the type, but there is no need to instantiate it,
 * because it is done "by the architecture", i.e. outside of P4 functions
 */
struct headers {
    ethernet_t   ethernet;
    p4traffic_t  p4traffic;
}

/*
 * All metadata, globally used in the program, also  needs to be assembled
 * into a single struct. As in the case of the headers, we only need to
 * declare the type, but there is no need to instantiate it,
 * because it is done "by the architecture", i.e. outside of P4 functions
 */
struct metadata {
    /* In our case it is empty */
}

/*************************************************************************
 ***********************  P A R S E R  ***********************************
 *************************************************************************/
parser MyParser(packet_in packet,
                out headers hdr,
                inout metadata meta,
                inout standard_metadata_t standard_metadata) {
    state start {
        packet.extract(hdr.ethernet);
        transition select(hdr.ethernet.etherType) {
            P4TRAFFIC_ETYPE : check_p4traffic;
            default         : accept;
        }
    }

    state check_p4traffic {
        transition select(packet.lookahead<p4traffic_t>().p,
        packet.lookahead<p4traffic_t>().four,
        packet.lookahead<p4traffic_t>().ver) {
            (P4TRAFFIC_P, P4TRAFFIC_4, P4TRAFFIC_VER) : parse_p4traffic;
            default                                   : accept;
        }
    }

    state parse_p4traffic {
        packet.extract(hdr.p4traffic);
        transition accept;
    }
}

/*************************************************************************
 ************   C H E C K S U M    V E R I F I C A T I O N   *************
 *************************************************************************/
control MyVerifyChecksum(inout headers hdr,
                         inout metadata meta) {
    apply { }
}

/*************************************************************************
**************  I N G R E S S   P R O C E S S I N G   *******************
*************************************************************************/
control MyIngress(inout headers hdr,
                  inout metadata meta,
                  inout standard_metadata_t standard_metadata) {
    /* TODO
     * set the bit size of the result
     */
    action send_back(bit<> result) {
        /* TODO
         * - put the result back in hdr.p4traffic.res
         * - swap MAC addresses in hdr.ethernet.dstAddr and
         *   hdr.ethernet.srcAddr using a temp variable
         * - Send the packet back to the port it came from
             by saving standard_metadata.ingress_port into
             standard_metadata.egress_spec
         */
        
        // put result into hdr.p4traffic.res
        hdr.p4traffic.res = result;
        
        // swap mac address
        bit<48> tmp_mac;
        tmp_mac = hdr.ethernet.dstAddr;
        hdr.ethernet.dstAddr = hdr.ethernet.srcAddr;
        hdr.ethernet.srcAddr = tmp_mac;
        
        //send it back to the same port
        standard_metadata.egress_spec = standard_metadata.ingress_port;
    }
    
    action loop_around(bit<8> current_green) {
    	// Lets us loop around all 4 junctions
    	
    }

    action determine_busy() {
    	
    }
    
    
    
    table traffic_control {
        key = {
            hdr.p4traffic.event : exact;
        }
        actions = {
            event_quiet;
            
        }
        const default_action = event_quiet();
        const entries = {
            P4TRAFFIC_QUIET : event_quiet();
            
        }
    }
    
    apply {
        if (hdr.p4calc.isValid()) {
            calculate.apply();
        } else {
            operation_drop();
        }
    }
}

/*************************************************************************
 ****************  E G R E S S   P R O C E S S I N G   *******************
 *************************************************************************/
control MyEgress(inout headers hdr,
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata) {
    apply { }
}

/*************************************************************************
 *************   C H E C K S U M    C O M P U T A T I O N   **************
 *************************************************************************/

control MyComputeChecksum(inout headers hdr, inout metadata meta) {
    apply { }
}

/*************************************************************************
 ***********************  D E P A R S E R  *******************************
 *************************************************************************/
control MyDeparser(packet_out packet, in headers hdr) {
    apply {
        packet.emit(hdr.ethernet);
        packet.emit(hdr.p4calc);
    }
}

/*************************************************************************
 ***********************  S W I T T C H **********************************
 *************************************************************************/

V1Switch(
MyParser(),
MyVerifyChecksum(),
MyIngress(),
MyEgress(),
MyComputeChecksum(),
MyDeparser()
) main;
