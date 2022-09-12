from pprint import pprint as print

from terraform_state_processor.terraform.tfstate import TerraformState


class CurrentState:
    tfstate = None

    def __init__(self, path: str = None, package_base: str = None):
        with open(path, "r") as fp:
            self.tfstate = TerraformState(fp.read(), package_base)


# #################################################################################################################### #


path = "./tfstate.json"
test = CurrentState(path)

print(test.tfstate.data)
print(test.tfstate.resources)
