import os

def accept_licence():
    if "ACCEPT_TC" not in os.environ:
        os.environ["ACCEPT_TC"] = "tôi đồng ý"
    print("Đã chấp nhận điều khoản...")