# Installation Guide for OnRamp

## 1. Preparation

<p>
    This repo assumes that you are running a debian linux disto like ubuntu, so a few of the scripted commands below may need to be adjusted if you are running using a different distro or package management. You will need to install docker on your linux host and obtain a cloudflare API token.
</p>

- Install Docker
    Below are two different methods for installing docker:
    * [Docker Linux Installation steps](https://docs.docker.com/desktop/linux/install/#generic-installation-steps)
    * or using this bash script on ubuntu available [here](https://gist.github.com/ilude/52b775682ec6ea5cc31933f81cef49f6)

    

- Get Cloudflare API Token
<p>You'll need a personal domain that's setup with Cloudflare
and an API token created like so</p>

![Cloudflare api token](/documentation/assets/cloudflare-api.png)

## 2. Installation

    if you need to you can run the following to do the basic setup automagically

    ```
    sudo apt install git make nano -y

    sudo mkdir /apps
    sudo chown -R $USER:$USER /apps
    cd /apps
    git clone https://github.com/traefikturkey/onramp.git onramp
    cd onramp

    make start-staging
    ```

    edit the .env file to include cloudflare credenitals your domain and the hostname of the current machine save the file by typing ctrl-x followed by the letter  traefik will start and attempt to obtain a staging certificate wait and then follow the on screen directions

    ```
    make down-staging
    ```
    you are now ready to bring things up with the production certificates

    ```
    make
    ```

## 3. Usage

