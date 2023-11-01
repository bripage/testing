import sst
import sys
import random



sst.setProgramOption("timebase", "1 ps")
sst.setProgramOption("stop-at", "300us")

totalCores = 5
totalControllers = 1
router_map = {}
clock_val = "2GHz"


for i in range(totalCores):
    core = sst.Component("core%d"%i, "miranda.BaseCPU")
    core.addParams({
        "clock": clock_val,
        #"verbose": 2,


    })
    coreGen = core.setSubComponent("generator", "miranda.SingleStreamGenerator")
    coreGen.addParams({
        #"verbose": 2,
        #  "startat": 8000 * i,
        #  "max_address" : 8000 * (i + 1) ,
        "clock": clock_val,

    })

    l1 = sst.Component("l1%d"%i, "memHierarchy.Cache")
    l1.addParams({
        "cache_frequency": "2GHz",
        "cache_size": "50KB",
        "associativity": 8,
        "access_latency_cycles": 2,
        "mshr_latency_cycles": 2,
        "L1": 1,
        #"verbose": 2,


    })

    l2 = sst.Component("l2%d"%i, "memHierarchy.Cache")
    l2.addParams({
        "cache_frequency": "2GHz",
        "cache_size": "500KB",
        "associativity": 8,
        "access_latency_cycles": 2,
        "mshr_latency_cycles": 2,
        "L1": 0,
        #"verbose": 2,

    })


    rout = sst.Component("router%d"%i, "merlin.hr_router")
    rout.addParams({
        "id": i,
        "num_ports": 3,
        "link_bw": "90GB/s",
        "flit_size": "8B",
        "xbar_bw": "90GB/s",
        "input_latency" : "30ps",
        "output_latency": "30ps",
        "input_buf_size": "2KB",
        "output_buf_size": "2KB",
        #"verbose": 2,


    })
    top = rout.setSubComponent("topology", "merlin.torus")
    top.addParams({
        "local_ports" : 1,
        "shape": totalCores + totalControllers,
        #"verbose": 2,

    })

    router_map["rout%d"%i] = rout

    cpu_cache_link = sst.Link("cpu_cache_link%d"%i)
    cpu_cache_link.connect((core, "cache_link", "300ps"), (l1, "high_network_0", "300ps"))
    cache_link = sst.Link("cache_link%d"%i)
    cache_link.connect((l1, "low_network_0", "300ps"), (l2, "high_network_0", "300ps"))
    cache_router_link = sst.Link("cache_router_link%d"%i)
    cache_router_link.connect((l2, "directory", "300ps"), (router_map["rout%d"%i], "port2", "300ps"))




for i in range(totalControllers):
    memory = sst.Component("memory%d"%i, "memHierarchy.MemController")
    memory.addParams({
        "clock": "2GHz",
        "addr_range_start": 0,
        #"verbose": 2,


    })
    back = memory.setSubComponent("backend", "memHierarchy.simpleMem")
    back.addParams({
        "mem_size": "10GB",
        #"verbose": 2,
        "access_time": "30ns",
        "max_requests_per_cycle": -1,


    })

    dc = sst.Component("dc%d"%i, "memHierarchy.DirectoryController")
    dc.addParams({
        #"verbose": 2,
        #"interleave_size": "64MB",
        #"interleave_step": "%dMB"%(64 * (totalControllers - 1)),
        #"node" : totalControllers,
        #"max_requests_per_cycle": -1,
        #"mem_addr_start": 0,
        "addr_range_start": i * 0x2540BE400,
        "addr_range_end": (i + 1) * 0x2540BE400,

    })
    rout = sst.Component("router%d"%(totalCores + i), "merlin.hr_router")
    rout.addParams({
        "id": totalCores + i,
        "num_ports": 3,
        "link_bw": "90GB/s",
        "flit_size": "8B",
        "xbar_bw": "90GB/s",
        "input_latency" : "30ps",
        "output_latency": "30ps",
        "input_buf_size": "2KB",
        "output_buf_size": "2KB",
        "verbose": 2,

    })

    spin = rout.setSubComponent("topology", "merlin.torus")
    spin.addParams({
        "local_ports" : 1,
        "shape": totalCores + totalControllers,
        #"verbose": 2,


    })
    router_map["rout%d"%(totalCores + i)] = rout

    mem_to_dc = sst.Link("mem_to_dc%d"%i)
    mem_to_dc.connect((memory, "direct_link", "300ps"), (dc, "memory", "300ps"))
    dc_to_rout = sst.Link("dc_to_rout%d"%i)
    dc_to_rout.connect((dc, "network", "300ps"), (rout, "port2", "300ps"))


list = []
for i in range(totalCores + totalControllers):
    list.append(i)

random.shuffle(list)
for i in range(totalCores + totalControllers):

    x = list[i]
    y = list[(i + 1)%(totalCores + totalControllers)]
    #x = i
    #y = (i + 1) % (totalCores + totalControllers)
    # print("cycle %d and router %d to router %d"%(i,x,y))
    rout_to_rout = sst.Link("rout_to_rout%d"%i)
    rout_to_rout.connect((router_map["rout%d"%x], "port0", "300ps"), (router_map["rout%d"%y], "port1", "300ps"))



print("done")