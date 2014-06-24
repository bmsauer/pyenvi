import sys
import json


def send_message(message):
    """
    Send a message back to PyEnvi.  Params: a string message."
    """
    message= str(message)+"\n"
    sys.stdout.write(message)
    sys.stdout.flush()

def main():
    """
    The main loop for the sub process.  Waits for commands written to pipe
    and writes responses back to PyEnvi.
    """
    if len(sys.argv)<=1:
        raise Exception("Too few arguments") #TODO: add custom exception
    
    environment_variables = json.loads(sys.argv[1][1:-1])
    
    while True:
        next_line = str(sys.stdin.readline())
        if not next_line:
            continue
        else:
            next_line_json = json.loads(next_line)
            
            if next_line_json["action"] == "STOP":
                send_message("OK")
                break;
            
            elif next_line_json["action"] == "SET":
                key = next_line_json["data"]["key"]
                value = next_line_json["data"]["value"]
                environment_variables[key] = value
                send_message(value)
                
            elif next_line_json["action"] == "GET":
                try:
                    key = next_line_json["data"]["key"]
                    message = environment_variables[key]
                    send_message(message)
                except KeyError:
                    send_message("_NOT_SET")
            
            elif next_line_json["action"] == "EXISTS":  
                key = next_line_json["data"]["key"]
                if key in environment_variables:
                    send_message("YES")
                else:
                    send_message("NO")
              
            else:
                sys.stdout.write("_UNKNOWN_ACTION\n") #TODO: error codes
                sys.stdout.flush()
           

if __name__ == "__main__":
    main()
    
