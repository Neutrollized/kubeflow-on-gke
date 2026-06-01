import re
from urllib.parse import urlsplit, urlencode
import kfp
import requests
import urllib3

# suppresses "FutureWarning: This client only works with Kubeflow Pipeline v2.0.0-beta.2 and later versions."
# which doesn't apply to us as we are using v2+
import warnings
from kfp.client import client as kfp_client_module
warnings.filterwarnings("ignore", category=FutureWarning, module="kfp.client.client")


class KFPClientManager:
    def __init__(self, api_url, dex_username, dex_password,
                 dex_auth_type="local", skip_tls_verify=False):
        self._api_url = api_url
        self._skip_tls_verify = skip_tls_verify
        self._dex_username = dex_username
        self._dex_password = dex_password
        self._dex_auth_type = dex_auth_type
        if skip_tls_verify:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def _get_session_cookies(self):
        s = requests.Session()
        resp = s.get(self._api_url, allow_redirects=True, verify=not self._skip_tls_verify)
        if resp.status_code == 403:
            url_obj = urlsplit(resp.url)
            url_obj = url_obj._replace(path="/oauth2/start",
                                       query=urlencode({"rd": url_obj.path}))
            resp = s.get(url_obj.geturl(), allow_redirects=True,
                         verify=not self._skip_tls_verify)
        if len(resp.history) == 0:
            return ""
        url_obj = urlsplit(resp.url)
        if re.search(r"/auth$", url_obj.path):
            url_obj = url_obj._replace(
                path=re.sub(r"/auth$", f"/auth/{self._dex_auth_type}", url_obj.path))
        if re.search(r"/auth/.*/login$", url_obj.path):
            dex_login_url = url_obj.geturl()
        else:
            resp = s.get(url_obj.geturl(), allow_redirects=True,
                         verify=not self._skip_tls_verify)
            dex_login_url = resp.url
        resp = s.post(dex_login_url,
                      data={"login": self._dex_username, "password": self._dex_password},
                      allow_redirects=True, verify=not self._skip_tls_verify)
        url_obj = urlsplit(resp.url)
        if re.search(r"/approval$", url_obj.path):
            s.post(url_obj.geturl(), data={"approval": "approve"},
                   allow_redirects=True, verify=not self._skip_tls_verify)
        return "; ".join([f"{c.name}={c.value}" for c in s.cookies])

    def create_kfp_client(self):
        cookies = self._get_session_cookies()
        return kfp.Client(host=self._api_url, cookies=cookies)


#------------------------------
# pipeline functions
#------------------------------
from kfp import dsl, compiler

@dsl.component(base_image='python:3.13-slim')
def say_hello(name: str) -> str:
    msg = f"Hello, {name}!"
    print(msg)
    return msg

@dsl.pipeline(name="hello-pipeline")
def hello_pipeline(recipient: str) -> str:
    task = say_hello(name=recipient)
    return task.output


#------------------------------
# main
#------------------------------
kfp_client_manager = KFPClientManager(
    api_url="http://localhost:8080/pipeline",
    dex_username="user@example.com",
    dex_password="12341234",
    dex_auth_type="local",
    skip_tls_verify=True,
)

kfp_client = kfp_client_manager.create_kfp_client()


# submit directly from the Python function (skips the YAML step)
kfp_client.create_run_from_pipeline_func(
    hello_pipeline,
    arguments={"recipient": "world"},
    namespace="kubeflow-user-example-com",
    experiment_name="my-first-experiment",
)

# Option:  compile to YAML then submit
#compiler.Compiler().compile(hello_pipeline, "hello_pipeline.yaml")
#kfp_client.create_run_from_pipeline_package(
#    "hello_pipeline.yaml",
#    arguments={"recipient": "world"},
#    namespace="kubeflow-user-example-com",  # your user namespace
#    experiment_name="my-first-experiment",
#)
