# Building a Django Blog: A Technical Journey Through FreeBSD, bhyve, and Network Architecture

_A story of discovery, debugging, and deployment in the world of enterprise-grade infrastructure_

## The Vision: More Than Just Another Blog

When I set out to build a book review blog, I could have easily deployed it on a shared hosting platform or cloud service. But where's the learning in that? As a professional developer, I wanted to create something that would demonstrate not just web development skills, but systems administration, network security, and infrastructure design. The goal wasn't just to build a blog—it was to build a **production-ready, enterprise-grade platform** that could impress both users and potential employers.

## The Architecture: A Network Engineering Puzzle

The infrastructure I envisioned was ambitious:

```
Internet Users → books.clexp.net → OpenBSD Cloud Server (24.23.95.221)
    ↓ relayd reverse proxy
    ↓ WireGuard VPN tunnel (10.100.0.1 → 10.100.0.2)
FreeBSD Host (tb02) → bhyve VM (10.100.0.6) → Django Application
```

Why this complexity? Several reasons:

1. **Security**: The application server would never touch the public internet directly
2. **Scalability**: The reverse proxy could load-balance across multiple backend servers
3. **Flexibility**: VMs could be migrated, backed up, or scaled independently
4. **Learning**: This setup touches on virtualization, networking, security, and web servers

The plan was to have the Django application running in a FreeBSD VM, accessible via WireGuard VPN at `10.100.0.6`, with an OpenBSD server in the cloud proxying traffic through the encrypted tunnel.

## Chapter 1: The Django Foundation

Before tackling the infrastructure, I built a solid Django application. This wasn't just a basic blog—it featured:

- **Professional Models**: Author, Book, and Review models with proper relationships
- **Custom Admin**: Enhanced Django admin with search, filtering, and bulk operations
- **Optimized Queries**: Using `select_related()` and `prefetch_related()` for performance
- **SEO-Friendly URLs**: Automatic slug generation and clean URL structure
- **Responsive Design**: Professional CSS with hover effects and transitions

The application worked beautifully on my development machine, but now came the real challenge: deploying it to production infrastructure.

## Chapter 2: Meeting bhyve - FreeBSD's Virtualization

FreeBSD's bhyve hypervisor promised enterprise-grade virtualization. The plan was simple: create a VM, install FreeBSD, deploy Django with Apache, and configure networking. How hard could it be?

### The First Hurdle: Service Configuration

My first attempt to use vm-bhyve was met with this error:

```bash
clexp@tb02:~ $ vm list
/usr/local/sbin/vm: ERROR: $vm_dir has not been configured or is not a valid directory
```

**The Problem**: vm-bhyve wasn't properly configured in the FreeBSD service system.

**The Investigation**: I needed to understand how FreeBSD services work. The `sysrc` command manages `/etc/rc.conf` settings:

```bash
# Check current settings
clexp@tb02:~ $ sysrc -a | grep vm
# (no output - vm not configured)

# Configure vm-bhyve
clexp@tb02:~ $ doas sysrc vm_enable=YES
vm_enable:  -> YES

clexp@tb02:~ $ doas sysrc vm_dir=/usr/local/vm
vm_dir:  -> /usr/local/vm
```

**The Learning**: FreeBSD services require explicit configuration in `/etc/rc.conf`. The `sysrc` command is the professional way to manage these settings, ensuring proper syntax and avoiding manual file editing errors.

### The Second Hurdle: Directory Structure

Even with proper configuration, the service still failed:

```bash
clexp@tb02:~ $ doas service vm start
/usr/local/sbin/vm: ERROR: $vm_dir has not been configured or is not a valid directory
```

**The Problem**: The directory didn't exist yet.

**The Solution**:

```bash
clexp@tb02:~ $ doas mkdir -p /usr/local/vm
clexp@tb02:~ $ doas service vm start
# (success - no output)
```

**The Learning**: Services often require their working directories to exist. This is a common pattern in Unix systems—services assume their environment is prepared.

### The Third Hurdle: Initialization

With the service running, I tried to initialize vm-bhyve:

```bash
clexp@tb02:~ $ doas vm init
clexp@tb02:~ $ doas vm list
NAME  DATASTORE  LOADER  CPU  MEMORY  VNC  AUTO  STATE
# (empty list - ready to create VMs)
```

**Success!** The virtualization system was now ready.

## Chapter 3: Network Architecture - The Bridge to Success

Creating VMs is one thing, but networking them properly is another. I needed the VM to be accessible at `10.100.0.6` on the WireGuard network.

### Understanding the Network Topology

First, I examined the existing network setup:

```bash
clexp@tb02:~ $ ifconfig -l
igb0 igb1 lo0 lo1 wg0 vm-public

clexp@tb02:~ $ ifconfig igb0
igb0: flags=1008943<UP,BROADCAST,RUNNING,PROMISC,SIMPLEX,MULTICAST,LOWER_UP> metric 0 mtu 1500
        inet 10.0.0.50 netmask 0xffffff00 broadcast 10.0.0.255
        media: Ethernet autoselect (1000baseT <full-duplex>)
        status: active

clexp@tb02:~ $ ifconfig wg0
wg0: flags=10080c1<UP,RUNNING,NOARP,MULTICAST,LOWER_UP> metric 0 mtu 1420
        inet 10.100.0.2 netmask 0xffffff00
        groups: wg
```

**The Learning**: The FreeBSD host had multiple network interfaces:

- `igb0`: Main LAN interface (10.0.0.50)
- `wg0`: WireGuard VPN interface (10.100.0.2)
- `vm-public`: Bridge interface created by vm-bhyve

### Creating the Virtual Network

vm-bhyve uses "switches" (bridge interfaces) to connect VMs to networks:

```bash
clexp@tb02:~ $ doas vm switch create public
clexp@tb02:~ $ doas vm switch list
NAME    TYPE      IFACE      ADDRESS  PRIVATE  MTU  VLAN  PORTS
public  standard  vm-public  -        no       -    -     -
```

To connect VMs to the physical network, I needed to add the physical interface to the bridge:

```bash
clexp@tb02:~ $ doas vm switch add public igb0
clexp@tb02:~ $ doas vm switch list
NAME    TYPE      IFACE      ADDRESS  PRIVATE  MTU  VLAN  PORTS
public  standard  vm-public  -        no       -    -     igb0
```

**The Learning**: vm-bhyve creates bridge interfaces that act as virtual switches. Adding a physical interface to the bridge allows VMs to communicate with the physical network.

## Chapter 4: The Template Mystery

With networking configured, I attempted to create the VM:

```bash
clexp@tb02:~ $ doas vm create -t freebsd -s 15G -m 1536 -c 2 django-vm
/usr/local/sbin/vm: ERROR: unable to find template /usr/local/vm/.templates/freebsd.conf
```

**The Problem**: vm-bhyve templates are configuration files that define how to create VMs for specific operating systems.

**The Investigation**: I needed to understand vm-bhyve's template system:

```bash
clexp@tb02:~ $ ls /usr/local/vm/.templates/
# (directory doesn't exist)

clexp@tb02:~ $ find /usr/local/share/ -name "*bhyve*" -o -name "*template*"
# (searching for template files)
```

**The Discovery**: vm-bhyve doesn't come with built-in templates. They need to be created or downloaded.

## Chapter 5: Resource Planning - The Art of Capacity Management

Before proceeding with VM creation, I took a step back to assess system resources—a crucial skill for any systems administrator.

### System Resource Assessment

```bash
clexp@tb02:~ $ sysctl hw.physmem hw.ncpu
hw.physmem: 8374620160  # ~8GB RAM
hw.ncpu: 4              # 4 CPU cores

clexp@tb02:~ $ top -n | head -20
last pid: 92910;  load averages:  0.17,  0.18,  0.16  up 28+12:33:09
27 processes:  1 running, 26 sleeping
CPU:  0.0% user,  0.0% nice,  0.0% system,  0.0% interrupt,  100% idle
Mem: 3360K Active, 192M Inact, 1756M Wired, 104K Buf, 5769M Free
```

**The Analysis**:

- **Total RAM**: 8GB with ~5.7GB free
- **CPU Usage**: Nearly idle (100% idle)
- **Current Load**: Very low (0.17 average)

**The Decision**: With plans for a mail server and additional sites, I allocated conservatively:

- **VM RAM**: 1.5GB (19% of total)
- **VM CPU**: 2 cores (50% of total)
- **VM Disk**: 15GB (sufficient for OS + Django)

This leaves plenty of resources for future expansion while ensuring the Django site has adequate performance.

## Chapter 6: The ISO Quest - Finding Installation Media

To create a FreeBSD VM, I needed installation media:

```bash
clexp@tb02:~ $ ls /usr/local/vm/.iso/ 2>/dev/null || echo 'No ISO directory found'
No ISO directory found

clexp@tb02:~ $ doas mkdir -p /usr/local/vm/.iso
```

### The URL Investigation

My first attempt to download FreeBSD failed:

```bash
clexp@tb02:~ $ doas fetch https://download.freebsd.org/releases/amd64/amd64/ISO-IMAGES/14.1/FreeBSD-14.1-RELEASE-amd64-disc1.iso
fetch: https://download.freebsd.org/releases/amd64/amd64/ISO-IMAGES/14.1/FreeBSD-14.1-RELEASE-amd64-disc1.iso: Not Found
```

**The Problem**: The URL structure had changed or the version didn't exist.

**The Investigation**: I needed to explore the FreeBSD release directory:

```bash
clexp@tb02:~ $ doas fetch -o - https://download.freebsd.org/releases/amd64/amd64/ISO-IMAGES/ | grep -E '(14\.[0-9]+)'
<tr><td class="link"><a href="14.2/" title="14.2">14.2/</a></td><td class="size">-</td><td class="date">2024-Dec-10 17:37</td></tr>
<tr><td class="link"><a href="14.3/" title="14.3">14.3/</a></td><td class="size">-</td><td class="date">2025-Jun-12 16:47</td></tr>
```

**The Solution**: FreeBSD 14.3 was available:

```bash
clexp@tb02:~ $ cd /usr/local/vm/.iso && doas fetch https://download.freebsd.org/releases/amd64/amd64/ISO-IMAGES/14.3/FreeBSD-14.3-RELEASE-amd64-disc1.iso
FreeBSD-14.3-RELEASE-amd64-disc1.iso                  1242 MB   10 MBps 02m01s
```

**The Learning**: When automation fails, investigation is key. Web scraping with `fetch` and `grep` revealed the correct URL structure.

## Chapter 7: The Template Challenge - Understanding VM Configuration

With the ISO downloaded, I still needed to resolve the template issue. This led me deeper into vm-bhyve's architecture.

### Understanding vm-bhyve Templates

Templates in vm-bhyve are configuration files that define:

- Boot loader settings
- Network configuration
- Device emulation
- Guest OS-specific parameters

**The Challenge**: Creating a proper FreeBSD template requires understanding:

- bhyve's boot process
- Network device emulation
- Disk controller types
- Console configuration

### The Template Solution

Rather than creating a complex template from scratch, I could use vm-bhyve's built-in template system or create a minimal one:

```bash
clexp@tb02:~ $ doas mkdir -p /usr/local/vm/.templates
clexp@tb02:~ $ doas vm template list
# (shows available templates)
```

_[This is where our story continues...]_

## What We've Learned So Far

This journey has already taught us several valuable lessons:

1. **Service Configuration**: FreeBSD services require explicit configuration in `/etc/rc.conf`
2. **Directory Dependencies**: Services often need their working directories pre-created
3. **Network Bridging**: vm-bhyve uses bridge interfaces to connect VMs to networks
4. **Resource Planning**: Proper capacity planning is crucial for multi-service environments
5. **Template Systems**: Virtualization platforms use templates to standardize VM creation
6. **URL Structure Investigation**: When downloads fail, investigation reveals the correct paths

## The Journey Continues...

We're now at the threshold of creating our first VM. The infrastructure is configured, resources are allocated, and installation media is ready. The next chapters will cover:

- Creating and configuring the FreeBSD template
- Installing FreeBSD in the VM with network configuration
- Setting up Apache and mod_wsgi
- Deploying the Django application
- Configuring pf firewall rules for WireGuard routing
- Testing the complete end-to-end connection
- Performance optimization and monitoring

Each step will bring new challenges and learning opportunities, deepening our understanding of enterprise infrastructure.

## The Technical Skills Demonstrated

Through this journey, we've already showcased:

- **Systems Administration**: Service configuration, directory management, resource planning
- **Network Engineering**: Understanding bridge interfaces, VPN topology, routing concepts
- **Troubleshooting**: Methodical problem-solving, log analysis, hypothesis testing
- **Automation**: Using command-line tools for investigation and configuration
- **Documentation**: Creating professional technical documentation

This project demonstrates not just the ability to build a web application, but the deeper skills required for enterprise infrastructure management—skills that separate senior developers from junior ones.

---

_This story continues as we build out the complete infrastructure. Each challenge overcome adds to our expertise and demonstrates the problem-solving skills that define professional software engineering._
