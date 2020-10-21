# Detailed Guide

This is a detailed guide to recreate or setup the project.

So the project is divided into 2 parts running the ansible playbook and the web
app to request and respond to the client.So I have created lightweight flask web
backend with 5 worker nodes to execute ansible playbook and respond to client
with allocated storage.

This guide uses ubuntu and if you use something else just choose the respective
alternative packages.

##  Installing the components 
	
	$ sudo apt update
    	$ sudo apt install python3-pip python3-dev build-essential libssl-dev
	$ sudo apt install python3-venv nginx sshpass libffi-dev python3-setuptools ansible


## Creating the Project dir.
	
We need to create the project directory where all ansible related configs and 
directories reside.

	$ mkdir ~/project_dir
	$ cd ~/project_dir


## Creation of Virtual Environment and required pip packages

We need to create the virtual env inside the project directory for the flask app
and install the python packages
	ansible-runner - Helps  interfacing with Ansible 
	uwsgi - (Web Server Gateway Interface) - Serving Python application on Nginx web server. 
	flask - Python Web based lightframework
	
	
	$ python3.6 -m venv myprojectenv
	$ source myprojectenv/bin/activate 
	$ pip install wheel uwsgi flask ansible-runner
	
and if you want to use ssh instead of REST call
	
	$ pip install paramiko
		
## Creation of appropriate directory structure

So as our application uses ansible-runner module to execute ansible playbook
we need to place the playbooks,inventory,vars in a specific format described

	
	$ cd ~/myproject
  
	and then create a directory structure like this which ansible runner could understand 
	and execute correctly to give response.
	
	.
	├── env
	│   ├── envvars
	│   ├── extravars
	│   ├── passwords
	│   ├── cmdline
	│   ├── settings
	│   └── ssh_key
	├── inventory
	│   └── hosts
	└── project
	    	├── play_with_rest.yml
  		├── play_with_ssh.yml
		├── playbook.yml
        	└── roles
        	    └── testrole
            		├── defaults
            		├── handlers
            		├── meta
            		├── README.md
            		├── tasks
            		├── tests
            		└── vars
	
## Updating files or folders

As we need to communicate to IBM FS8K particularly.If we need to communicate to
some other storages we just need to add the playbooks in here

1. I have added those playbooks inside `project/` dir. 
2. And add the `ansible_user` and `ansible_password` var in inventory/hosts file


### Creation of the App

We will create a single file as our application is not complex.That will 
basically execute ansible playbook using ansible runner and then parse the 
ansible output for the required parameters and pass them as response.

	
	(myprojectenv)$ vi feilong_ansible.py
	

The application code will live in this file and can be taken from github repo 
and you can run and check or update the code accroding to playbook names etc.

# PART-2 Hosting/Deploying the app

## Creating a wsgi file 

	
	$ cd ~/myproject.ini
	$ vi wsgi.py
	

	+. Inside the wsgi.py add the following code and modify accordingly

	
	from myprojectenv.feilong_ansible import app

	if __name__ == "__main__":
    		app.run()

	

### Configuring uWSGI using configuration file

This is a file for long-term deployment and usage purpose.

	
	$ cd ~/project_dir
	$ vi myproject.ini
	
+. Inside the myproject.ini add 
	
	
	[uwsgi]
	module = wsgi:app

	master = true
	processes = 5

	socket = myproject.sock
	chmod-socket = 660
	vacuum = true

	die-on-term = true
	


## Creating a systemd Unit file

This may allow the init system in ubuntu to automatically start when server boots 
and this may vary for other distros.

	
	$ sudo vi /etc/systemd/system/myproject.service

and put the configs accordingly.

	
	[Unit]
	Description=uWSGI instance to serve myproject
	After=network.target

	[Service]
	User=sammy
	Group=www-data
	WorkingDirectory=/home/sammy/myproject
	Environment="PATH=/home/sammy/myproject/myprojectenv/bin"
	ExecStart=/home/sammy/myproject/myprojectenv/bin/uwsgi --ini myproject.ini

	[Install]
	WantedBy=multi-user.target
	
	
Start the service 
	
	$ sudo systemctl start myproject
	$ sudo systemctl enable myproject	
	
	
## Configuring Nginx to Proxy Requests
	
Now configure Nginx to pass web requests to that socket using the uwsgi protocol.


	
	$ sudo vi /etc/nginx/sites-available/myproject
	
And 

	
	server {
    	listen 80;
    	server_name your_domain www.your_domain;

   	 location / {
        	include uwsgi_params;
        	uwsgi_pass unix:/home/sammy/myproject/myproject.sock;
    	}
	}

	
To enable the Nginx server block configuration we need to link the file

	
	$ sudo ln -s /etc/nginx/sites-available/myproject /etc/nginx/sites-enabled
	
We need to restart the Nginx and allow firewall access to Nginx

	
	$ sudo systemctl restart nginx
	$ sudo ufw allow 'Nginx Full'
	
## Encounter error- Check the following

1. `sudo less /var/log/nginx/error.log`: checks the Nginx error logs.
2. `sudo less /var/log/nginx/access.log`: checks the Nginx access logs.
3. `sudo journalctl -u nginx`: checks the Nginx process logs.
4. `sudo journalctl -u myproject`: checks your Flask app’s uWSGI logs.



## Note

If the following error throws up errors like ssh failed then try adding 
1. installing paramiko into virtualenv
2. `ansible_connection=paramiko` in invetory/hosts and that will solve the issues.

This is because of the ansible_version you're using isn't supporting sshpass.

## Finished 

Now you could fire up the curl request to the domain and check the storage block
allocated parameters.
