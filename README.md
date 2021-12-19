# Prognolite Web Exporter Module

You need data, but there is no API to get it. This module holds several classes to bridge this incomprehensible gap. For each service (website), there is a class and its corresponding implementation. The implementations are all defined in `Configuration_Handler.py`.

## Usage

2.  Make the call:

```bash
python3 -c 'from prognolite_web_exporter import Configuration_Handler;Configuration_Handler.implementation_selector("./config.txt","service2")'
```

In this example, the arguments of 'service2' will get loaded and the module will interact with that service. **The control of which service is going to be interacted with lies in the call, not the configuration file.**

#### Relevant arguments for the function 'implementation/_selector'
This function has 2 arguments:

- conf_path: Mandatory. The path to the configuration file, including the file. This has to be a path in string format. It can be absolute or relative. Default value: Not supported.
- service: The name of the desired service, in string format, matching the one supplied in the config file.

Example call:

```bash
python3 -c 'from prognolite_web_exporter import Configuration_Handler;Configuration_Handler.implementation_selector("./config.txt","gastromatic")'
```
### Configuration files can be provided in two ways:

- One can add a `config.ini` (or `config.txt`) which holds configurations for several services. The module can be called to just load a specific set of parameters and interact with the corresponding service. This is demonstrated with the above example.
- Another option is to just provide one configuration. The module will just grab the first config header and set of parameters provided. In that case, the python call can be made with only one argument, pointing to the config file:

```bash
python3 -c 'from prognolite_web_exporter import Configuration_Handler;Configuration_Handler.implementation_selector("~/Desktop/config.txt")'
```

This also works with a config file with several headers, with no service specified, the module will just process the first one. **This way, the control of which service is going to be interacted with depends on the configuration file, not on the call.**

## While Developing

Before building, one can develop and directly call the Configuration handler script, without needing to change any code:

```bash
python3 Configuration_Handler.py './config.txt' 'gastromatic'
```
When satisfied with the result, build the package manually (if no automation is implemented yet):

```bash
poetry build
```

## Installation/Dependencies

### System Depenencies

#### Building: poetry

For MacOS, Linux, and WSL:

```bash
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python
```
To apply changes for your current shell session, run

```bash
source $HOME/.poetry/env
```

You may add this to the auto-run shell script like .bashrc or .zshrc if Poetry doesn’t appear in a new shell session:

```bash
export PATH="$HOME/.poetry/bin:$PATH"
```

#### Geckodriver

- Go to the geckodriver releases page. Find the latest version of the driver for your platform and download it. For example:

```bash 
wget https://github.com/mozilla/geckodriver/releases/download/v0.24.0/geckodriver-v0.24.0-linux64.tar.gz
```

Extract the file with:
```bash 
tar -xvzf geckodriver*
``` 

Make it executable:
```bash 
chmod +x geckodriver
``` 

Add the driver to your PATH so other tools can find it:
```bash 
export PATH=$PATH:/path-to-extracted-file/
```

OR
        
```bash 
cp geckodriver /usr/local/bin/
```      

### Installation

- Install pip (Python dependency manager): 

```bash 
sudo apt-get install python3-pip
```

- Clone this repo and cd-in:

```bash 
git clone git@github.com:prognolite/web_exporter.git

cd prognolite_web_export/dist/
```

- Install package and all dependencies:

By general rule, clone repo or pull latest changes before reinstalling.
In the `dist` folder inside the repository:

```bash 
sudo pip3 install prognolite_web_exporter*
```
- IF the package has already been installed previously and one wishes to update:

```bash 
sudo pip3 install --upgrade --force-reinstall prognolite_web_exporter*
```



### Installation on live server:

```bash
cd /home/prognolitedev/web_exporter/1.0/dist && pip3 install prognolite_web_exporter*
```


