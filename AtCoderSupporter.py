#!/usr/bin/env python3
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pickle
import json
import re
import subprocess
from getpass import getpass
import time

SAVE_DIR = "./save"
ACCOUNT_JSON_PATH = os.path.join(SAVE_DIR, "account.json")
SRC_PATH_TXT_PATH = os.path.join(SAVE_DIR, "src_path.txt")
SESSION_PICKLE_PATH = os.path.join(SAVE_DIR, "session.pickle")
TESTCASES_DIR = os.path.join(SAVE_DIR, "testcases")

BASE_URL = "https://atcoder.jp/"
LOGIN_URL = urljoin(BASE_URL, "login")


def save_src_path(src_path=''):
    if not src_path:
        print("Enter a path to source code.")
        src_path = input().strip('"'' ').replace('\\', '/')
    if os.path.isfile(src_path):
        with open(SRC_PATH_TXT_PATH, 'w') as f:
            f.write(src_path)
        print("Successfully saved a path to source code in "
              f"{os.path.basename(SRC_PATH_TXT_PATH)}.")
    else:
        print("The path is invalid ...")
        save_src_path()


def load_src_path():
    try:
        with open(SRC_PATH_TXT_PATH, 'r') as f:
            return f.read()
    except OSError:
        save_src_path()
        return load_src_path()


def get_src_dir():
    return os.path.dirname(load_src_path())


def get_src_name():
    return os.path.basename(load_src_path())


def get_src_name_without_ext():
    return os.path.splitext(get_src_name())[0]


def get_src_ext():
    return os.path.splitext(load_src_path())[-1]


def rcv_entered_account_info():
    username = input("Enter your username: ")
    password = getpass("Enter your password: ")
    account_info = {
        'username': username,
        'password': password
    }
    return account_info


def save_account_info(account_info):
    with open(ACCOUNT_JSON_PATH, 'w') as f:
        json.dump(account_info, f, indent=4)
    print(f"Successfully saved in {os.path.basename(ACCOUNT_JSON_PATH)}.")


def load_account_info():
    try:
        with open(ACCOUNT_JSON_PATH, 'r') as f:
            return json.load(f)
    except OSError:
        return []


def save_session(obj):
    with open(SESSION_PICKLE_PATH, 'wb') as fp:
        pickle.dump(obj, fp)


def load_session_pickle():
    try:
        with open(SESSION_PICKLE_PATH, 'rb') as fp:
            return pickle.load(fp)
    except OSError:
        login()
        return load_session_pickle()


def load_ses():
    return load_session_pickle()[0]


def load_csrf_token():
    return load_session_pickle()[1]


def login(reset_account=False):

    account_info = []
    if not reset_account:
        account_info = load_account_info()
    if account_info == []:
        account_info = rcv_entered_account_info()

    ses = requests.session()

    r = ses.get(LOGIN_URL)
    soup = BeautifulSoup(r.text, 'lxml')
    csrf_token = soup.find(attrs={'name': 'csrf_token'}).get('value')

    login_info = {
        'csrf_token': csrf_token,
        'username': account_info['username'],
        'password': account_info['password']
    }

    result = ses.post(LOGIN_URL, data=login_info)

    if result.status_code == 200 and result.url != LOGIN_URL:
        print("Login successful!")
        if account_info != load_account_info():
            save_account_info(account_info)
        save_session((ses, csrf_token))
    else:
        print("Login failed ...")
        login(True)


def check(command):
    check_dict = {'src_path': False, 'account': False}
    if len(command) == 1:
        check_dict['src_path'] = True
        check_dict['account'] = True
    elif len(command) >= 2:
        check_dict[command[1]] = True

    if check_dict['src_path']:
        print(f"Path to source code : {load_src_path()}")
    if check_dict['account']:
        print(f"Account info : {load_account_info()}")


def correct_contest_name(crt_contest_name, new_contest_name):
    ses = load_ses()

    new_contest_name = new_contest_name.lower()
    contest_url = urljoin(BASE_URL, f"contests/{new_contest_name}")
    r = ses.get(contest_url)
    if r.status_code == 200:
        print("The contest name has been updated!")
        return new_contest_name
    else:
        return crt_contest_name


def convert_to_task_number(task_name):
    if task_name.isdecimal():
        return int(task_name) - 1
    elif len(task_name) == 1:
        return ord(task_name.lower()) - ord('a')
    else:
        return -1


def convert_to_task_name(task_number):
    if task_number < 0:
        return ''
    else:
        return chr(task_number + ord('a')).upper()


def download_all_testcases(contest_name, redownload=False):
    testcases_path = f"{TESTCASES_DIR}/{contest_name}.json"

    if os.path.exists(testcases_path) and not redownload:
        print(f"Testcases for {contest_name} are already downloaded.")
        return True
    else:
        ses = load_ses()

        r = ses.get(urljoin(BASE_URL, f"contests/{contest_name}/tasks"))
        if r.status_code != 200:
            print(f"Failed in downloading testcases for {contest_name} ...")
            return False
        else:
            soup = BeautifulSoup(r.text, 'lxml')
            anchors = soup.find_all('a',
                                    href=re.compile(r"/contests/.*/tasks/.*"))
            hrefs = [href.get('href') for href in anchors]
            task_url_list = [urljoin(BASE_URL, href) for href in hrefs]
            task_url_list = list(dict.fromkeys(task_url_list))

            sec_tds = soup.find_all('td', string=re.compile(r' sec'))
            secs = [sec.text for sec in sec_tds]
            time_limit_list = [float(sec.replace(' sec', '')) for sec in secs]

            testcases_dict = dict()
            for (i, task_url) in enumerate(task_url_list):
                testcases = download_testcases(task_url)
                testcases['info']['time limit'] = time_limit_list[i]
                testcases_dict[f'task {i}'] = testcases

            with open(testcases_path, 'w') as f:
                json.dump(testcases_dict, f, indent=4)

            print(f"Finished downloading testcases for {contest_name}.")
            return True


def download_testcases(task_url):
    task_full_name = os.path.basename(task_url)
    print(f"Downloading testcases for {task_full_name} ...")

    ses = load_ses()

    r = ses.get(task_url)
    if r.status_code != 200:
        print(f"Failed in downloading testcases for {task_full_name} ...")
        return dict()
    else:
        soup = BeautifulSoup(r.text, 'lxml')
        soup_ja = soup.find('span', class_='lang-ja')
        soup = soup_ja if soup_ja else soup
        pres = soup.find_all('pre')
        testcases = [pre.string for pre in pres if pre.string]

        input_list = testcases[::2]
        output_list = testcases[1::2]

        testcases = dict()
        testcases['info'] = dict()
        paragraphs = soup.find_all('p')
        maximum_error_paragraph = [p for p in paragraphs if '誤差' in p.text]
        maximum_error = 0
        if maximum_error_paragraph:
            variables = maximum_error_paragraph[0].find_all('var')
            match = re.search(r'{.*?}', variables[-1].text)
            error_exponent = int(match.group()[1:-1])
            maximum_error = pow(10, error_exponent)
        testcases['info']["maximum error"] = maximum_error

        for i, (testcase_input, testcase_output)\
                in enumerate(zip(input_list, output_list)):
            testcase = {'input': testcase_input, 'output': testcase_output}
            testcases[f'testcase {i + 1}'] = testcase

        return testcases


def load_testcases(contest_name, task_number):
    testcases_path = f"{TESTCASES_DIR}/{contest_name}.json"
    try:
        with open(testcases_path, 'r') as f:
            testcases_dict = json.load(f)
        return testcases_dict.get(f'task {task_number}', dict())
    except OSError:
        return dict()


def get_build_command():
    ext = get_src_ext()
    if ext == '.java':
        return ['javac', get_src_name()]
    elif ext == '.cpp':
        return ['g++', get_src_name(), '-o',
                f"{get_src_name_without_ext()}.exe"]
    elif ext == '.py':
        return ['python', '-m', 'py_compile', get_src_name()]
    else:
        return []


def build():
    print("Building ...")
    result = subprocess.run(get_build_command(),
                            cwd=get_src_dir(),
                            stderr=subprocess.PIPE)
    error_message = result.stderr.decode('cp932')
    if len(error_message) > 0:
        print("Compilation error : ")
        print(error_message)
    return not error_message


def get_run_command():
    ext = get_src_ext()
    if ext == '.java':
        return ['java', get_src_name_without_ext()]
    elif ext == '.cpp':
        return [f'{get_src_name_without_ext()}.exe']
    elif ext == '.py':
        return ['python', get_src_name()]
    else:
        return []


def run():
    if build():
        print("Running!")
        subprocess.run(get_run_command(), cwd=get_src_dir())


def format_output(output):
    return [line.strip().split() for line in output.splitlines() if line]


def equals(response, answer, maximum_error):
    return (abs(response - answer) <= maximum_error
            or abs((response - answer) / answer) <= maximum_error)


def judge(response, answer, maximum_error):
    if answer == response:
        return True

    if len(response) != len(answer):
        return False
    for line_res, line_ans in zip(response, answer):
        if len(line_res) != len(line_ans):
            return False
        for elem_res, elem_ans in zip(line_res, line_ans):
            if not equals(float(elem_res), float(elem_ans), maximum_error):
                return False

    return True


def test(testcases):
    if not build():
        print("----- CE -----")
        return False

    is_all_ac = True
    time_limit = testcases['info']['time limit']
    for key, testcase in testcases.items():
        if key == 'info':
            continue

        status = ''
        print("-------------------------------")
        print(f'{key} : ', end='')

        testcase_input = testcase['input']
        testcase_output = testcase['output']

        temp_path = "temp.txt"
        with open(temp_path, 'w') as f:
            f.write(testcase_input)
        with open(temp_path, 'r') as f:
            start_time = time.time()
            try:
                result = subprocess.run(get_run_command(),
                                        cwd=get_src_dir(),
                                        stdin=f,
                                        stdout=subprocess.PIPE,
                                        timeout=time_limit * 2)
            except subprocess.TimeoutExpired:
                status = 'TLE'
        os.remove(temp_path)

        run_time = round((time.time() - start_time) * 1000)

        if status == 'TLE':
            print("TLE")
            is_all_ac = False
        elif run_time >= time_limit * 1000:
            print(f"TLE ({run_time} ms)")
            is_all_ac = False
        else:
            output = result.stdout.decode()
            answer = format_output(testcase_output)
            response = format_output(output)

            if judge(response, answer, testcases['info']['maximum error']):
                print(f"AC! ({run_time} ms)")
            else:
                print(f"WA ({run_time} ms)")
                print("----input-----")
                print(testcase_input)
                print("----result----")
                print(output)
                print("---expected---")
                print(testcase_output)
                is_all_ac = False

    if not is_all_ac:
        print("----- WA -----")
    return is_all_ac


def test_all(contest_name, task_number):
    print(("Testing your source code for "
          f"{contest_name}_{convert_to_task_name(task_number)} ..."))
    if test(load_testcases(contest_name, task_number)):
        print(" ! ! ! AC ! ! ! ")
        print("Would you submit your source code? y/n")
        if(input() == 'y'):
            submit(contest_name, task_number)


def load_src_code():
    try:
        with open(load_src_path(), 'r') as f:
            return f.read()
    except OSError:
        return ''


def get_language_id():
    ext = get_src_ext()
    if ext == '.java':
        return '3016'
    elif ext == '.cpp':
        return '3003'
    elif ext == '.py':
        return '3023'
    else:
        return ''


def fetch_task_name(submit_url, task_number):
    ses = load_ses()
    r = ses.get(submit_url)
    soup = BeautifulSoup(r.text, 'lxml')
    select_task_list = soup.find('select', id='select-task').find_all('option')
    task_names = [select_task.get('value') for select_task in select_task_list]
    return task_names[task_number]


def submit(contest_name, task_number):
    submit_url = urljoin(BASE_URL, f"contests/{contest_name}/submit")

    ses = load_ses()
    csrf_token = load_csrf_token()

    src_code = load_src_code()
    language_id = get_language_id()
    task_screen_name = fetch_task_name(submit_url, task_number)

    data = {
        'csrf_token': csrf_token,
        'data.LanguageId': language_id,
        'data.TaskScreenName': task_screen_name,
        'sourceCode': src_code
    }

    result = ses.post(submit_url, data)

    if result.status_code == 200 and result.url != submit_url:
        print("Submit successful!")
    else:
        print("Submit failed ...")


if __name__ == "__main__":
    print("--- AtCoder Supporter ---")

    if not os.path.exists(SAVE_DIR):
        os.mkdir(SAVE_DIR)

    if not os.path.exists(SRC_PATH_TXT_PATH):
        save_src_path()

    if not os.path.exists(TESTCASES_DIR):
        os.mkdir(TESTCASES_DIR)

    login()

    contest_name = ''
    task_number = -1
    command = []
    while True:
        print("Enter a command.")
        tmp_command = input().split()

        if len(command) == 0 and len(tmp_command) == 0:
            continue
        if len(tmp_command) > 0:
            command = tmp_command

        if re.fullmatch(r'src_path', command[0]):
            save_src_path(command[1] if len(command) >= 2 else '')

        elif re.fullmatch(r'login|l', command[0]):
            login(True)

        elif re.fullmatch(r'check|c', command[0]):
            check(command)

        elif re.fullmatch(r'download|d', command[0]):
            if len(command) >= 2:
                contest_name = correct_contest_name(contest_name, command[1])
            download_all_testcases(contest_name, True)

        elif re.fullmatch(r'run|r', command[0]):
            run()

        elif re.fullmatch(r'test|t|submit', command[0]):
            new_task_number = task_number
            if len(command) >= 3:
                contest_name = correct_contest_name(contest_name, command[1])
                new_task_number = convert_to_task_number(command[2])
            elif len(command) == 2:
                new_task_number = convert_to_task_number(command[1])

            if not download_all_testcases(contest_name):
                continue

            new_testcases = load_testcases(contest_name, new_task_number)
            if len(new_testcases) > 0:
                task_number = new_task_number
            if task_number < 0:
                print("Testcases cannot be found.")
                continue

            if re.fullmatch(r'test|t', command[0]):
                test_all(contest_name, task_number)

            elif re.fullmatch(r'submit', command[0]):
                submit(contest_name, task_number)

        elif re.fullmatch(r'exit|e', command[0]):
            break

        else:
            contest_name = correct_contest_name(contest_name, command[0])
