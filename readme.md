## docker vagrant image

## development env
- cpp 
   - ssh -p 1002 vagrant@127.0.0.1
- python
   - ssh -p 1001 vagrant@127.0.0.1

## Template
 - ubuntu-core 
    - ssh -p 1000 vagrant@127.0.0.1
    - ssh -p 1000 root@127.0.0.1

 - ubuntu-cuda
   - ssh -p 2000 vagrant@127.0.0.1
   - ssh -p 2000 root@127.0.0.1

 - ubuntu_cuda_vnc
   - user: vagrant
   - password: vagrant
   - ip: 127.0.0.1
   - port: 6000
   - gui: true # access through vnc

 - ubuntu_vmware
   - user: vagrant
   - password: vagrant
   - gui: true # access through vmware 