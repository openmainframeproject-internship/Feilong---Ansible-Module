# -----------------------------------------------------------
# Main flask file to create endpoints 
# 1. / 
# 2. /storage - allocation of storage using ansible runnner
#
# -----------------------------------------------------------
from flask import Flask, jsonify, request
import ansible_runner
import re

app = Flask(__name__)

@app.route("/", methods=['GET'])
def hello():
    return "<h1 style='color:blue'>Hello There! It's feilong-ansible Project.</h1>"


def check_keys(myDict):
    
    # convert all keys to lowercase
    myDict =  {k.lower(): v for k, v in myDict.items()}

    # using a comparison operator
    myDict.keys()
    return myDict.keys() == {"host_id","size","pool"}

def ansible_runner_func(content):

    runner_object = ansible_runner.run(private_data_dir='/home/ajain/feilong_ansible/', playbook = 'pl_with_rest.yml', extravars={"host_id":content['host_id'],"size":content['size'],"pool":content['pool']}, json_mode=True)
    
    #print(runner_object.stdout.read())
    return runner_object.stdout.read()
        
def ansible_output_parse_ssh(ansible_output_str):

        """
        To parse the string output returned from ansible-runner playbook execution using ssh and 
        parse WWPN and SCSILUN_ID
        """

        wwpn_search = re.search('<hostdetail>(.*)</hostdetail>', ansible_output_str, re.IGNORECASE)

        if wwpn_search:
            wwpn = wwpn_search.group(1).split("</hostdetail>")[0]

        scsilun_search = re.search('<scsi_lun>(.*)</scsi_lun>',ansible_output_str,re.IGNORECASE)
        
        if scsilun_search:
            scsilun = scsilun_search.group(1).split("</scsi_lun>")[0] 
        
        try:
            x = eval(wwpn)

            y = eval(scsilun)
            
            intr = x['stdout_lines'][12].split(' ')
    
            return y['stdout_lines'][0], intr[1]
       
        except NameError:
            print("Required parameters missing")
            return None, None

def ansible_output_parse_rest(ansible_output_str):
        """
        To parse the string output returned from ansible-runner playbook execution using rest and
        parse WWPN and SCSILUN_ID
        """
        wwpn_search = re.search('<hostdetail>(.*)</hostdetail>', ansible_output_str, re.IGNORECASE)

        if wwpn_search:
            wwpn = wwpn_search.group(1).split("</hostdetail>")[0]

        scsilun_search = re.search('<scsi_lun>(.*)</scsi_lun>',ansible_output_str,re.IGNORECASE)
        
        if scsilun_search:
            scsilun = scsilun_search.group(1).split("</scsi_lun>")[0] 
        
        try:
            x = eval(wwpn)

            y = eval(scsilun)
    
            return y['id'], x['nodes'][0]
       
        except NameError:
            print("Required parameters missing")
            return None, None


@app.route("/storage", methods=['POST'])
def allocate_storage():
    """
    This the function doing allocation of storage 
    """

    #1. Condition check of the request,parameters and keys
    if request.is_json:

        content = request.get_json()
        
        if len(content) != 3:
            return '', 400

        if check_keys(content) == False:
            return '' ,400
        
        
        #2. Execute ansible playbook with given body content
        str_r = ansible_runner_func(content)
        
        #3. Parse the output from ansible runner to get desired vars
        scsilun_id, wwpn =  ansible_output_parse_rest(str_r)     
        
        # Check for Error 
        if scsilun_id == None:
            error_msg = re.search('"res": {"content":(.*)"',str_r)
            finalz = jsonify(
                    status = error_msg.group(1).split('\""')[0]       
            )
        
        else:
            finalz = jsonify(
                scsilun_id = scsilun_id,
                wwpn = wwpn
            )
            

        #print(req['pool'])
        return finalz , 200
    
    else:

        return '', 400


@app.errorhandler(404)
def not_found(error):
    return '', 404

if __name__ == "__main__":
    app.run()
