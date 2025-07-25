### docker在linux下安装

教程地址：[Install Docker Engine And Docker Compose In Ubuntu - OSTechNix](https://ostechnix.com/install-docker-ubuntu/)

```bash
uname -a  #检查是否为64位

####1 更新ubuntu
sudo apt update
sudo apt upgrade
sudo apt full-upgrade
```

#### 2 添加docker库

```bash
#2.1首先，安装必要的证书并允许 apt 包管理器使用 HTTPS 使用存储库，使用以下命令：
sudo apt install apt-transport-https ca-certificates curl software-properties-common gnupg lsb-release  	

#2.2添加GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

#如显示代理问题可使用 curl -fsSL --noproxy "*"  https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

#2.3 添加Docker官方软件源
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt update  #更新 
```
#### 3 安装Docker
```bash
sudo apt install docker-ce docker-ce-cli containerd.io docker-compose-plugin  

apt-cache madison docker-ce	 #查看可安装版本

#sudo apt install docker-ce=5:19.03.9~3-0~ubuntu-focal docker-ce=5:19.03.9~3-0~ubuntu-focal containerd.io  #ubtuntu20.04下的例版本
sudo apt install docker-ce=5:20.10.16~3-0~ubuntu-jammy docker-ce-cli=5:20.10.16~3-0~ubuntu-jammy containerd.io  #安装任意版本的docker（Ubuntu22.04下例版本）

systemcl status docker  #检查docker服务是否已经支持
sudo systemctl enable docker #使得docker服务在开机时自启动
sudo docker version #检查docker版本
```
#### 4. 测试docker

```bash
sudo docker run hello-world
	#失败时进行docker换源
	sudo mkdir -p /etc/docker  #
	#添加以下内容到文件
    sudo tee /etc/docker/daemon.json <<-'EOF'
    {
      "registry-mirrors" : [
        "https://docker.m.daocloud.io",
        "https://docker-cf.registry.cyou"
      ],
      "insecure-registries" : [
        "docker.mirrors.ustc.edu.cn"
      ],
      "debug": true,
      "experimental": false
    }
    EOF

    sudo systemctl restart docker #重启
    docker info #查看配置
```
#### 5.安装docker-compose

```bash
##安装2.6.1版本
sudo curl -L "https://github.com/docker/compose/releases/download/v2.6.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose 
  
sudo chmod +x /usr/local/bin/docker-compose #权限
docker-compose version
```

#### 6.设置docker全局代理

```bash
sudo mkdir -p /etc/systemd/system/docker.service.d
sudo nano /etc/systemd/system/docker.service.d/http-proxy.conf
#将以下内容填入.conf文件,其中http和https的代理按本机代理修改
[Service]
Environment="HTTP_PROXY=http://127.0.0.1:7890"
Environment="HTTPS_PROXY=http://127.0.0.1:7890"
Environment="NO_PROXY=localhost,127.0.0.1,::1"
sudo systemctl daemon-reload	
sudo systemctl restart docker
systemctl show --property=Environment docker #查看是否生效
```

