"""
   Python script for testing upload performance of an Artifactory installation.
   Supporting usecase to measure "user experience" when uploading artifacts 
   via API. Test output aims to give data about performance impact when 
   experimenting using different filestorage configurations for Artifactory.

   Author:     jon.svendsen@conoa.se
   License:    Free as in beer

"""

import os
import sys
import logging
import json
import time
import datetime
from argparse import ArgumentParser
from argparse import RawTextHelpFormatter
import requests

# Disable https warnings
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

epilog = """
Example)
  {} -H https://segotl3939.got.volvo.net --user <user> --pwd <pass> -r reponame


/j0nixRulez
""".format(
    sys.argv[0]
)

## Argument parser setup
parser = ArgumentParser(
    formatter_class=RawTextHelpFormatter,
    description=__doc__,
    epilog=epilog,
)
parser.add_argument(
    "-H",
    "--host",
    dest="host",
    default="https://localhost",
    help="URL to Artifactory server",
)

parser.add_argument(
    "-P",
    "--port",
    dest="port",
    default="8081",
    help="Port where Artifactory REST API listen",
)

parser.add_argument(
    "-r",
    "--repo",
    metavar="REPO",
    dest="repository",
    default="example-repo-local",
    help="Artifactory repository to use",
)

parser.add_argument(
    "-v", "--verbose", action="count", default=0, help="increase log level"
)

parser.add_argument(
    "--user",
    dest="user",
    default=None,
    required=True,
    help="Username for Basic Auth",
)
parser.add_argument(
    "--pwd",
    dest="pwd",
    default=None,
    required=True,
    help="Password for Basic Auth",
)

args = parser.parse_args()

"""Logging setup"""
log_adjust = max(min(0 - args.verbose, 2), -2)

logging.basicConfig(
    level=logging.INFO + log_adjust * 10,
    format="%(asctime)s [%(levelname)s] [%(module)s:%(lineno)d] %(message)s",
)

logger = logging.getLogger("script-logger")


class Artifactory:
    """
    Class for common Artifactory tasks against API

    :param host:        url to artifactory
    :param port:        port where you can access api
    :param username:    username for an Artifactory account
                         with admin permission
    :param password     password for your user
    """

    def __init__(self, host, port, username, password):
        self.HOST = host
        self.PORT = port
        self.USERNAME = username
        self.PASSWORD = password

        self.URL = None

        self.HTTP_HEADERS = {"Content-Type": "application/json"}

        try:
            if self.systemPing():
                logger.info(
                    "Successfully API ping to {}:{}".format(self.HOST, self.PORT)
                )
                self.URL = "{}:{}".format(self.HOST, self.PORT)
            else:
                logger.error("Failed API ping to {}:{}".format(self.HOST, self.PORT))
                raise ConnectionAbortedError

        except Exception as error:
            print(error)
            sys.exit(1)

    def systemPing(self):
        """
        Test if we get an reply from api
        :param <none>:
        :return Boolean:
                > True              When api give valid response
                > False             When api is not responding
        """
        try:
            url = "{}:{}/access/api/v1/system/ping".format(self.HOST, self.PORT)
            response = requests.get(url, verify=False)

            logger.debug(
                "[{}] - {} - {}".format(response.status_code, self.URL, response.text)
            )

            if response.status_code != requests.codes.ok and response.text != "OK":
                return False

        except Exception as error:
            logger.error("[{}]".format(error))

        else:
            return True

    def repoExists(self, repository_name):
        """
        check if a repo already exists

        :param (String) repository_name:    name of the repository to check after
        :return Boolean:
                > True                      if repository exists
                > False                     if repository don't exists
        """
        try:
            url = "{}/artifactory/api/repositories/{}".format(self.URL, repository_name)
            response = requests.get(
                url,
                headers=self.HTTP_HEADERS,
                auth=(self.USERNAME, self.PASSWORD),
                verify=False,
            )
            if response.status_code == requests.codes.ok:
                logger.info("Repository '{}' found".format(repository_name))
                logger.debug("{}".format(response.text))

            else:
                logger.info("Repository '{}' NOT found".format(repository_name))
                logger.debug("{}".format(response.text))
                return False
        except Exception as error:
            logger.error(
                "Oooops... some error when communicate with api -> {}".format(error)
            )
            return False

        else:
            return True

    def createRepository(
        self, repository_name, repo_type="local", repo_package_type="generic"
    ):
        """
        creates a repository
        :param (String) repository_name:        name of the repository to create
        :param (String) repo_type:              local|remote|virtual|federated
        :param (string) repo_package_type;      type of repository, visit api
                                                -doc for possible values

        :return Boolean:
                > True                 If repository is created successfully
                > False                If failing to create repository
        """
        try:
            url = "{}/artifactory/api/repositories/{}".format(self.URL, repository_name)
            payload = {"rclass": repo_type, "packageType": repo_package_type}

            logger.debug(
                "Url: {} - Payload '{}', Headers: '{}' ".format(
                    url, json.dumps(payload), json.dumps(self.HTTP_HEADERS)
                )
            )

            response = requests.put(
                url,
                data=json.dumps(payload),
                headers=self.HTTP_HEADERS,
                auth=(self.USERNAME, self.PASSWORD),
                verify=False,
            )

            if response.status_code == requests.codes.ok:
                logger.info("Repository '{}' created".format(repository_name))

            else:
                logger.info("Failed create Repository '{}'".format(repository_name))
                return False

            logger.debug("{}".format(response.text))

        except Exception as error:
            logger.error(
                "Oooops... some error when communicate with api -> {}".format(error)
            )
            return False

        else:
            return True

    def getRepository(self, repository_name, repo_type="local"):
        return True
        # GET /api/repositories/{repoKey}

    def updateRepository(self, repository_name, repo_type="local"):
        return True
        # POST /api/repositories/{repoKey}

    def deleteRepository(self, repository_name):
        """
        deletes a repository
        :param (String) repository_name:        name of the repository to delete

        :return Boolean:
                > True                 If repository is deleted successfully
                > False                If failing to delte repository
        """
        try:
            url = "{}/artifactory/api/repositories/{}".format(self.URL, repository_name)

            logger.debug("Url: {}".format(url))

            response = requests.delete(
                url, auth=(self.USERNAME, self.PASSWORD), verify=False
            )

            if response.status_code == requests.codes.ok:
                logger.info("Repository '{}' deleted".format(repository_name))

            else:
                logger.info(
                    "Failed to delete Repository '{}' with the following error {}".format(
                        repository_name, response.text
                    )
                )
                return False

            logger.debug("{}".format(response.text))

        except Exception as error:
            logger.error(
                "Oooops... some error when communicate with api -> {}".format(error)
            )
            return False

        else:
            return True

    def deleteArtifact(self, repository_name, file_name):
        """
        delete file from a repository

        :param (String) repository_name:        name of the repository to delete artifact
        :param (String) file_name:              name of the file to delete

        :return Boolean:
                > True                 If file is deleted successfully
                > False                If failed to delete file
        """
        try:
            url = "{}/artifactory/{}/{}".format(self.URL, repository_name, file_name)

            response = requests.delete(
                url, auth=(self.USERNAME, self.PASSWORD), verify=False
            )

            logger.debug("[{}] {}".format(response.status_code, response.text))

            if response.status_code == 204:
                logger.info(
                    "'{}' deleted from Repository '{}'".format(
                        file_name, repository_name
                    )
                )

            else:
                logger.error(
                    "Failed to delete file '{}' from Repository '{}'".format(
                        file_name, repository_name
                    )
                )
                return False

        except Exception as error:
            logger.error(
                "Oooops... some error when communicate with api -> {}".format(error)
            )
            return False

        else:
            return True

    def uploadArtifact(self, repository_name, file_name, file_content):
        """
        upload file to a repository
        :param (String) repository_name:        name of the repository to upload artifact
        :param (String) file_name:              name of the file to upload, implies file is
                                                located in same folder as script
        :param (String) file_content            Content of file

        :return Boolean:
                > True                 If file is uploaded successfully
                > False                If failed to upload file
        """
        try:
            url = "{}/artifactory/{}/{}".format(self.URL, repository_name, file_name)

            response = requests.put(
                url,
                data=file_content,
                auth=(self.USERNAME, self.PASSWORD),
                verify=False,
            )

            logger.debug("[{}] {}".format(response.status_code, response.text))

            if response.status_code == 201:
                logger.info(
                    "Uploaded '{}' to Repository '{}'".format(
                        file_name, repository_name
                    )
                )

            else:
                logger.error(
                    "Failed to upload file '{}' to Repository '{}'".format(
                        file_name, repository_name
                    )
                )
                return False

        except Exception as error:
            logger.error(
                "Oooops... some error when communicate with api -> {}".format(error)
            )
            return False

        else:
            return True


# Helper functions for tests
def convert_size_to_bytes(size_str):
    """
    Convert human filesize definitions to bytes.

    :param size_str:     A human-readable string representing a file size, e.g. "22 mb".
    :return:             The number of bytes represented by the string.
    """
    multipliers = {
        "kb": 1024,
        "mb": 1024**2,
        "gb": 1024**3,
        "tb": 1024**4,
        "pb": 1024**5,
        "eb": 1024**6,
        "zb": 1024**7,
        "yb": 1024**8,
    }

    for suffix in multipliers:
        size_str = size_str.lower().strip().strip("s")
        if size_str.lower().endswith(suffix):
            return int(float(size_str[0 : -len(suffix)]) * multipliers[suffix])
    else:
        if size_str.endswith("b"):
            size_str = size_str[0:-1]

    return int(size_str)


def generate_testfile(file_name, size):
    """
    generate a file with content from os.urandom

    :param file_name:     name of the file to generate
    :param size:          size of the file to generate
    """
    try:
        size_bytes = convert_size_to_bytes(size)

        logger.debug("Generate file '{}' with size '{}'".format(file_name, size))

        with open(file_name, "wb") as fout:
            while size_bytes > 0:
                wrote = min(size_bytes, 1024)  # chunk
                fout.write(os.urandom(wrote))
                size_bytes -= wrote

    except Exception as error:
        logger.error("Failed to generate file '{}'".format(file_name))
        logger.error("{}".format(error))


if __name__ == "__main__":
    # Initiate connection to artifactory server
    artifactory = Artifactory(args.host, args.port, args.user, args.pwd)

    # Check if repo already exists, else create it
    if not artifactory.repoExists(args.repository):
        try:
            artifactory.createRepository(args.repository)
        except Exception as error:
            logger.error(error)

    """
    Hardcoded TEST case
      TL;DR
      Generates files from os.urandom with sizes defined in a tuple.
      Uploads generated file to artifactory and measure time it took to upload.
      After measurement is saved, test file is removed locally and from Artifactory server
      When all upload tests are done, outputs result to a json formatted file with timestamp
    """
    result_file = "{}_test-results.json".format(
        datetime.datetime.now().strftime("%Y-%m-%d_%H_%M_%S")
    )
    test_result = dict()
    for SiZe in ("100kb", "1mb", "100mb", "1gb"):
        test_result["{}".format(SiZe)] = dict()
        try:
            for i in range(1, 11):
                # Generate a test file
                test_file = "TestFile-{}-{}.bin".format(SiZe, i)
                generate_testfile(test_file, SiZe)
                # Read file content info variable for upload
                with open(test_file, "rb") as fh:
                    file_content = fh.read()
                # take timestamp and start uploas that file
                start = time.time()
                if artifactory.uploadArtifact(args.repository, test_file, file_content):
                    STATUS = "SUCCESS"
                else:
                    STATUS = "FAIL"

                stop = time.time()
                upload_time = stop - start

                # Add result to test result dict
                test_result[SiZe][i] = "{};{}s".format(STATUS, round(upload_time, 3))
                logger.debug("Uplad test result: {}".format(test_result[SiZe][i]))

                # Cleanup testfiles
                if os.path.exists(test_file):
                    os.remove(test_file)
                    logger.debug("local file {} removed".format(test_file))

                if artifactory.deleteArtifact(args.repository, test_file):
                    logger.debug(
                        "Removed {} from Repository {}".format(
                            test_file, args.repository
                        )
                    )
                else:
                    logger.error(
                        "Failed to remove {} from {}".format(test_file, args.repository)
                    )

        except Exception as error:
            logger.error("Tests borked!?")
            logger.debug("{}".format(error))
            sys.exit(1)

    try:
        # Write test result to file
        with open(result_file, "w") as fh:
            fh.write(json.dumps(test_result, indent=2))

        # ADD remove repo when done? ... could be dangerous if a fool operates this script

    except Exception as error:
        logger.error(error)

    logger.info("All done, checkout '{}' for all the test results".format(result_file))


#   j0nix 2023
