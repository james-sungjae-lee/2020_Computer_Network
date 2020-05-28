#!/bin/bash

# Computer Network 2020-1
# 경영학부 경영학전공 20132651 이성재
# 소켓 통신을 활용한 Server, Client 프로그램 작성

# 본 과제의 코드 파일은 다음과 같이 구성되어 있습니다.
# 01. instance.sh
# 02. server.py
# 03. client.py


# 아래의 코드는 이 중에서 01. instance.sh 로 AWS EC2 인스턴스를 자동 실행하고,
# 구현된 server.py 코드를 가져와 작동시키도록 구현된 코드입니다.
# aws cli 를 이용해 instance 를 특정 ami 와 sg, key, type 으로 실행시킵니다.
# 그 후, 사전에 github 에 업로드 해 놓은 코드를 가져와 해당 코드를 실행시킵니다.
# 이 때 ssh 명령어를 이용하여 git clone 과 python3 명령을 script 형태로 실행하게 됩니다.

# Launch Instance with Instance Type
INSTANCE_TYPE=$1
LAUNCH_INFO=$(aws ec2 run-instances --image-id ami-1234 --count 1 \
--instance-type $INSTANCE_TYPE --key-name 1234 --security-group-ids sg-1234)

# Instance ID and Public DNS Parsing
sleep 30
INSTANCE_ID=$(echo $LAUNCH_INFO | jq -r '. | .Instances[0].InstanceId')
INSTANCE_DESCRIBE=$(aws ec2 describe-instances --instance-ids $INSTANCE_ID)

INSTANCE_PUB_DNS=$(echo $INSTANCE_DESCRIBE | jq -r '. | .Reservations[0].Instances[0].PublicDnsName')
INSTANCE_PUB_IP=$(echo $INSTANCE_DESCRIBE | jq -r '. | .Reservations[0].Instances[0].PublicIpAddress')

echo $INSTANCE_PUB_DNS
echo $INSTANCE_PUB_IP

# Get server.py code and run
sleep 30
echo 'clone start'
ssh -o "StrictHostKeyChecking no" -i awspwd.pem ubuntu@$INSTANCE_PUB_DNS 'git clone https://github.com/odobenuskr/2020_Computer_Network.git'
echo 'run server'
ssh -i awspwd.pem -t ubuntu@$INSTANCE_PUB_DNS 'cd /home/ubuntu/2020_Computer_Network/;python3 server.py'
