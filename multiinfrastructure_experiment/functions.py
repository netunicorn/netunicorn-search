import subprocess


def benign_traffic(url1: str, url2: str):
    for i in range(500):
        subprocess.check_output(f'curl {url1}', shell=True)
        subprocess.check_output(f'curl {url2}', shell=True)
    return 0


def run_patator(url: str):
    subprocess.check_output(
        "python ./patator.py http_fuzz "
        f"url={url} "
        "persistent=1 user_pass=FILE0:FILE0 0=/opt/patator/passwords.txt -x ignore:code=401"
    )