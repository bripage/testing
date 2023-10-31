import sst
import sys

rtr = sst.Component("rtr", "merlin.hr_router")
rtr.addParams({
    "id" : 0,
    "num_ports" : 4,
    "link_bw" : "56Gb/s",
    "flit_size" : "512B",
    "xbar_bw" : "56Gb/s",
    "input_latency" : "25ps",
    "output_latency" : "25ps",
    "input_buf_size" : "16KB",
    "output_buf_size" : "16KB"
})
rtr_top = rtr.setSubComponent("topology", "merlin.singlerouter")

dc = sst.Component("dc", "memHierarchy.DirectoryController")
dc.addParams({

})

mc = sst.Component("mc", "memHierarchy.MemController")
mc.addParams({
    "clock" : "3300MHz"
})
mc_backend = mc.setSubComponent("backend", "memHierarchy.simpleMem")
mc_backend.addParams({
    "mem_size" : "32GB"
})

rtr_to_dc = sst.Link("rtr_to_dc")
rtr_to_dc.connect((rtr, "port3", "300ps"),(dc, "network", "300ps"))

dc_to_mc = sst.Link("dc_to_mc")
dc_to_mc.connect((dc, "memory", "300ps"),(mc, "direct_link", "300ps"))


for i in range(3):
    cpu = sst.Component("cpu%d"%i, "miranda.BaseCPU")
    cpu.addParams({
        "id" : 0,
        "clock" : "2GHz"
    })
    cpu_gen = cpu1.setSubComponent("generator", "miranda.STREAMBenchGenerator")
    cpu_gen.addParams({
        "n" : 1000,
        "verbose" : 10
    })

    cpu_l1 = sst.Component("c%d_l1"%i, "memHierarchy.Cache")
    cpu_l1.addParams({
        "L1" : 1,
        "cache_frequency" : "2GHz",
        "cache_size" : "32KB",
        "associativity" : 8,
        "access_latency_cycles" : 4
    })

    cpu1_l2 = sst.Component("c%d_l2"%i, "memHierarchy.Cache")
    cpu1_l2.addParams({
        "cache_frequency" : "2GHz",
        "cache_size" : "6MB",
        "associativity" : 32,
        "access_latency_cycles" : 8
    })

    c_to_l1 = sst.Link("c%d_to_l1"%i)
    c_to_l1.connect((cpu, "cache_link", "300ps"),(cpu_l1, "high_network_0", "300ps"))

    l1_to_l2 = sst.Link("c%dl1_to_l2"%i)
    l1_to_l2.connect((cpu_l1, "low_network_0", "300ps"),(cpu_l2, "high_network_0", "300ps"))

    l2_to_rtr = sst.Link("c%dl2_to_rtr"%i)
    l2_to_rtr.connect((cpu_l2, "directory", "300ps"),(rtr, "port%d"%i, "300ps"))
