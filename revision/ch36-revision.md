# Chapter 36 — Revision Sheet: Virtualization Internals

> Supplements [the full chapter](../docs/01-foundations/ch36-virtualization-internals.md). Goal: explain the whole chain **CPU → hypervisor → VM → vCPU → memory translation → virtual devices → I/O**, and contrast VMs with containers.

## 30-second mental model

```text
Physical hardware → Hypervisor → Virtual machines → Guest OS → Applications
CPU     → vCPU scheduling              Memory  → GVA → GPA → HPA
Disk    → virtual disk                 Network → virtual NIC
Devices → emulated / paravirtualized / passthrough
Hardware help: VT-x / AMD-V (CPU), EPT / NPT (memory), VirtIO / SR-IOV (I/O)
Containers: host kernel + namespaces + cgroups (no guest kernel)
```

## Hypervisors

| | Type 1 (bare-metal) | Type 2 (hosted) |
|---|---|---|
| Stack | Hardware → Hypervisor → VMs | Hardware → Host OS → Hypervisor app → VMs |
| Examples | VMware ESXi, Hyper-V, Xen, KVM-based | VirtualBox, VMware Workstation, Parallels |
| Where | data centers | desktop development |

## Why it is hard, and the CPU story

- The guest OS **thinks it owns the hardware**; letting it run privileged operations (disable interrupts, edit privileged registers, read another VM's memory) would destroy isolation → the hypervisor must control **privileged instructions**.
- Ring 0 (kernel) vs Ring 3 (apps). Old approach: intercept/transform privileged operations in software. Modern: **hardware-assisted virtualization (VT-x / AMD-V)**.
- **VM exit** = guest → hypervisor transition for operations needing hypervisor handling; then return to the VM. Exits cost time → modern designs minimise them.
- **vCPU** = execution context scheduled onto physical CPUs (another scheduling layer, like an OS scheduling processes). 12 vCPUs on 4 cores is time-sliced.
- **CPU overcommitment**: more vCPUs than cores (e.g. 16 on 8) works while VMs aren't all busy; contention when they are. **CPU pinning/affinity**: fix vCPU→core for predictable performance (rarely needed for normal cloud apps).

## Memory story

```text
GVA --(guest page tables)--> GPA --(EPT/NPT)--> HPA
```

- Three address spaces: Guest Virtual (apps), Guest Physical (what the guest believes is RAM), Host Physical (real RAM). Two VMs can both have GPA `0x1000`; the hypervisor maps them to **different** host pages.
- Old: **shadow page tables** (expensive). Modern: **nested paging** (Intel EPT / AMD NPT) — big performance gain. **TLB** caches translations (hit → physical address; miss → page-table walk); virtualization adds a translation layer.
- Allocation: hypervisor tracks ownership of RAM per VM. **Memory isolation** is critical (VM1 must never read VM2).
- **Ballooning**: guest balloon driver takes memory so the hypervisor can reclaim pages. **Memory overcommitment** (e.g. 96 GB configured on 64 GB): works if VMs don't use it all; tools: ballooning, page sharing, swapping; heavy pressure hurts.

## Storage and networking

- **Virtual disk** (VMDK, VHDX, QCOW2, raw) = abstraction over local SSD / network / cloud block / distributed storage.
- **Copy-on-write**: base image + changed blocks → fast cloning.
- **Snapshot ≠ backup** (needs app/DB consistency, retention, independent storage, restore tests).
- **Virtual NIC** (MAC/IP) → **virtual switch** (switching, VLANs, filtering, bridging) → physical NIC. Cloud extends this into VPCs, security groups, overlays, SDN.

## Devices and I/O

| Technique | Idea | Trade-off |
|---|---|---|
| **Full emulation** | Hypervisor pretends to be real hardware | Compatible, more overhead |
| **Paravirtualization (VirtIO)** | Guest uses virtualization-aware drivers | Lower overhead, needs guest drivers |
| **Hardware passthrough** | Give a physical device (e.g. GPU) to a VM | Best performance; harder sharing, migration, management, isolation |
| **SR-IOV** | One PCIe device exposes multiple virtual functions (VF1..n) to different VMs | Efficient NIC access |

Historic I/O path: Guest → VM exit → hypervisor → device emulation → hardware (slow). Modern: VirtIO, SR-IOV, hardware assist.

## VM boot and program execution

Boot: hypervisor allocates vCPU/RAM/disk/NIC → BIOS/UEFI → GRUB → guest kernel → initialises CPU/memory/devices/network/filesystem → `systemd` → services. Normal CPU instructions run efficiently on the physical CPU; operations needing intervention cause a VM exit and resume.

## VM vs container internals

| | VM | Container |
|---|---|---|
| Stack | Hardware → Hypervisor → VM → Guest OS → App | Hardware → Host OS → Runtime → Container → App |
| Kernel | Own guest kernel | **Shares host kernel** |
| Start | Boot virtual hardware + kernel + userspace | Start a process |
| Isolation | Stronger (hardware-assisted, smaller attack surface) | Lighter; kernel shared |

"Not simply VM bad, container good — they solve different problems." Containers use **namespaces** (isolate PID, network, mounts, hostname, users, IPC — a container sees PID 1, the host sees another PID) and **cgroups** (limit CPU, memory, I/O, processes).

## Cloud context

Virtualization lets one 64-CPU/256 GB server host VMs for customers A–D (utilization + isolation, a foundation of IaaS). On AWS you manage the guest OS/config, AWS manages hardware, hypervisor/infrastructure, data center, power, networking. **Nitro** offloads virtualization/network/storage to dedicated hardware/firmware → lower overhead, better isolation, higher performance (implementation details not needed for a normal SWE OA).

## Live migration

Move a running VM from host A to B: copy memory while running → copy changed pages again → repeat → short pause → transfer remaining state → resume on B. Hard because the VM keeps dirtying pages; the technique is **pre-copy migration** (others exist). **Snapshot ≠ live migration** (state capture for restore/clone vs moving a running VM).

## Security

Hypervisor = huge security boundary. Threats: **VM escape**, hypervisor vulnerabilities, **side channels** (CPU caches, timing, memory behaviour). Interview line: *virtualization provides strong isolation, but shared hardware can introduce sophisticated side-channel risks.*

## Interview Q&A (the source's ten)

1. **Virtualization?** Abstraction of physical resources so multiple isolated VMs share hardware.
2. **Hypervisor?** Layer that creates/manages VMs and controls access to physical resources.
3. **Type 1 vs 2?** Hardware→Hypervisor→VMs vs Hardware→Host OS→Hypervisor→VMs.
4. **How does a VM get CPU?** vCPUs scheduled by the hypervisor onto physical CPUs.
5. **VM exit?** Guest→hypervisor transition for operations needing virtualization-layer handling.
6. **VM memory translation?** GVA→GPA→HPA, with EPT/NPT assisting the second level.
7. **EPT?** Intel's hardware second-level address translation for virtualization.
8. **Ballooning?** Hypervisor reclaims/rebalances memory via a guest balloon driver.
9. **Paravirtualization?** Guest uses virtualization-aware drivers instead of full hardware emulation.
10. **VM vs container?** VM virtualizes a machine with a guest OS; containers isolate processes sharing the host kernel.

## Traps

- "A vCPU is a physical core" — it is a schedulable context.
- "Snapshot = backup" / "snapshot = live migration" — neither.
- "Container = lightweight VM" — different isolation mechanism, shared kernel.
- Overcommit is a bet on non-simultaneous peaks.

## Study scope reminder (from the source)

Know concepts; the chapter explicitly excludes hypervisor implementation, CPU microarchitecture and advanced virtualization security research for a general SWE target.

<!-- NAV -->

---

← [Sheet 35](ch35-revision.md) · [Full chapter 36](../docs/01-foundations/ch36-virtualization-internals.md) · [All revision material](README.md)
