

## Project Description:-

Create sustainable open source Ansible modules for creating/managing virtual server instances and storage devices connected to IBM Z. The final target state products could be used to communicate to various storage devices connected to mainframe and control HW function to automate storage managements. Intermediate target state would be communicating to IBM DS8K CLIs and/or RestfulAPIs to help initialization of storage device for virtual servers.


## State of the Project:- 

1. Ansible is already supported on zlinux/linuxone(s390x) with some support for Z/OS.

2. Currently zvm (Feilong project) uses mini disks (around 30gb) for storage

3. There's no current infrastructure for different kind of storage allocation.



## Value of Feilong-Ansible project:-

1. Switch the ZVM Storage to Flash Based/Disk Based storage.(We have focused on FS9K).

2. Create a initial setup to use different type of storage using intermediate as ansible.


## Project Requirements:-

We have divided the project into 2 phases:-

1. Storage request module from Storage device
	- Commands to prepare required storage
	- Integration of commands into Ansible to use REST/CLI

2. Integration with Feilong
	- Work on the call to ansible 
	- Parameters Inputs --- > Parameters Output
	- Testing the integration. 



