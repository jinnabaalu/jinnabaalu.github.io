---
layout: post
title:  "AWS EBS Volmes - Create and attach the EBS volume with mounting"
author: jinna
categories: [ Devops ]
image: assets/images/Logo.png
---

## Create Volume from console
- Login to AWS console
- Goto menu Services -> Compute -> EC2 ->  In Left Sidebar under Elastic Block Store -> click on Volume -> Create Volume
- Fill the following parameter
![Create AWS EBS Volume]({{site.baseurl}}/assets/images/create-aws-ebs-volume.png)

## Attach a volume
- Select the created volume, right click and select the “attach volume” option.
![Atach EBS Volume]({{site.baseurl}}/assets/images/ebs-volume-atach.jpg)

> Note: Volume and EC2 instance need to be in the same availability zone.

## Mount to the folder

-  Now, login to your ec2 instance and list the available disks

   `lsblk'

   The above command will list the disk you attached to your instance

- Check if the volume has any data

   `sudo file -s /dev/xvdf` or `sudo file -s /dev/nvme1n1'

   If the above command output shows “/dev/xvdf: data”, it means your volume is empty.

-  Format the volume to ext4 filesystem
   
   `sudo mkfs -t ext4 /dev/xvdf` or `sudo mkfs -t ext4 /dev/nvme1n1`

- Create a directory of your choice to mount our new ext4 volume. I am using the name “/var/avolume”

   `mkdir -p /var/avolume`

- Mount the volume to “/var/avolume” directory

   `mount /dev/nvme1n1 /var/avolume`

   cd into newvolume directory and check the disk space for confirming the volume mount.

   ```bash
   cd /var/avolume
   df -h .
   ```
   The above command would show the free space in the newvolume directory

- To unmount the volume

  `unmount /dev/nvme1n1`

   