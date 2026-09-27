from rest_framework.exceptions import APIException

class WalletAlreadyExists(APIException):
    status_code = 409
    default_detail = "This user already has a wallet."