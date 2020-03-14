import os


# TODO Please change this to something proper
def run(script, argument_list):
    """Execute specified script with arguments."""
    cmd = os.path.dirname(os.path.dirname(os.path.realpath(__file__))) + os.sep
    cmd += script.script_file if script.script_file else script.command
    cmd += " "

    for argument, arg_data in argument_list:
        cmd += (
            argument.short_flag if argument.short_flag else argument.long_flag
        )
        cmd += " " + str(arg_data) + " "

    cmd = cmd.strip()
    os.system(cmd)
