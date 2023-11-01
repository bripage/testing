import os
import sst
import argparse

cores = []
core_counter = 0
l1caches = []
core_routers = []
router_counter = 0
agg_routers = []
dirctrls = []
memctrls = []
links = []
link_counter = 0
buses = []
bus_counter = 0

rtr = sst.Component("rtr%d"%router_counter, "merlin.hr_router")
rtr.addParams({
    "id" : router_counter,
    "num_ports" : 9,
    "link_bw" : "56Gb/s",
    "flit_size" : "512B",
    "xbar_bw" : "56Gb/s",
    "input_latency" : "25ps",
    "output_latency" : "25ps",
    "input_buf_size" : "16KB",
    "output_buf_size" : "16KB"
})
rtr_top = rtr.setSubComponent("topology", "merlin.mesh")
rtr_top.addParams({
    "shape" : "4x4x1",
    "width" : "1x1x1",
    "local_ports" : 4
})
agg_routers.append(rtr)
router_counter += 1

dc = sst.Component("dc", "memHierarchy.DirectoryController")
dc.addParams({

})
dirctrls.append(dc)

mc = sst.Component("mc", "memHierarchy.MemController")
mc.addParams({
    "clock" : "3300MHz"
})
mc_backend = mc.setSubComponent("backend", "memHierarchy.simpleMem")
mc_backend.addParams({
    "mem_size" : "32GB"
})
memctrls.append(mc)

bus = sst.Component("bus", "memHierarchy.Bus")
bus.addParams({
    "bus_frequency" : "2GHz"
})
buses.append(bus)

rtr_to_dc = sst.Link("rtr_to_dc")
rtr_to_dc.connect((rtr, "port4", "300ps"),(dc, "network", "300ps"))

dc_to_bus = sst.Link("dc_to_mc")
dc_to_bus.connect((dc, "memory", "300ps"),(bus, "high_network_0", "300ps"))

bus_to_mc = sst.Link("bus_to_mc")
bus_to_mc.connect((bus, "low_network_0", "300ps"),(mc, "direct_link", "300ps"))

for r in range(2):
    rtr = sst.Component("rtr%d"%router_counter, "merlin.hr_router")
    rtr.addParams({
        "id" : router_counter,
        "num_ports" : 9,
        "link_bw" : "56Gb/s",
        "flit_size" : "512B",
        "xbar_bw" : "56Gb/s",
        "input_latency" : "25ps",
        "output_latency" : "25ps",
        "input_buf_size" : "16KB",
        "output_buf_size" : "16KB"
    })
    rtr_top = rtr.setSubComponent("topology", "merlin.mesh")
    rtr_top.addParams({
        "shape" : "4x4x1",
        "width" : "1x1x1",
        "local_ports" : 4
    })
    core_routers.append(rtr)
    router_counter += 1

    for i in range(4):
        cpu = sst.Component("cpu_%d"%core_counter, "miranda.BaseCPU")
        cpu.addParams({
            "id" : 0,
            "clock" : "2GHz"
        })
        cpu_gen = cpu.setSubComponent("generator", "miranda.STREAMBenchGenerator")
        cpu_gen.addParams({
            "n" : 1000,
            "verbose" : 10
        })

        cpu_l1 = sst.Component("c%d_l1"%core_counter, "memHierarchy.Cache")
        cpu_l1.addParams({
            "L1" : 1,
            "cache_frequency" : "2GHz",
            "cache_size" : "32KB",
            "associativity" : 8,
            "access_latency_cycles" : 4
        })

        cpu_l2 = sst.Component("c%d_l2"%core_counter, "memHierarchy.Cache")
        cpu_l2.addParams({
            "cache_frequency" : "2GHz",
            "cache_size" : "6MB",
            "associativity" : 32,
            "access_latency_cycles" : 8
        })

        c_to_l1 = sst.Link("c%d_to_l1"%core_counter)
        c_to_l1.connect((cpu, "cache_link", "300ps"),(cpu_l1, "high_network_0", "300ps"))

        l1_to_l2 = sst.Link("c%dl1_to_l2"%core_counter)
        l1_to_l2.connect((cpu_l1, "low_network_0", "300ps"),(cpu_l2, "high_network_0", "300ps"))

        l2_to_rtr = sst.Link("c%dl2_to_rtr"%core_counter)
        l2_to_rtr.connect((cpu_l2, "directory", "300ps"),(rtr, "port%d"%i, "300ps"))

        core_counter += 1

cr0_to_cr1 = sst.Link("cr0_to_cr1")
cr0_to_cr1.connect((core_routers[0], "port6", "300ps"),(core_routers[1], "port4", "300ps"))

cr0_to_ar0 = sst.Link("cr0_to_ar0")
cr0_to_ar0.connect((core_routers[0], "port6", "300ps"),(agg_routers[0], "port6", "300ps"))

cr1_to_ar0 = sst.Link("cr0_to_ar1")
cr1_to_ar0.connect((core_routers[1], "port6", "300ps"),(agg_routers[0], "port7", "300ps"))

