from terraform_state_processor.terraform.tfstate import TerraformState

with open('./tfstate.json') as fp:
    fp.seek(0)
    test = TerraformState(fp.read())
    for x in test.resources:
        print(x)
