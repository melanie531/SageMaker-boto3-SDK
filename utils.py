import os
import tarfile
import pandas as pd
from pathlib import Path
import boto3
import time
import json
import datetime
import tqdm

region = boto3.Session().region_name
sm_client = boto3.client("sagemaker", region)
cw = boto3.Session().client("cloudwatch")
sm_runtime = boto3.client("sagemaker-runtime")

def create_tar(tarfile_name: str, local_path: Path):
    """
    Create a tar.gz archive with the content of `local_path`.
    """
    file_list = [k for k in local_path.glob("**/*.*") if f"{k.relative_to(local_path)}"[0] != "."]
    with tarfile.open(tarfile_name, mode="w:gz") as archive:
        for k in (pbar := tqdm.tqdm(file_list, unit="files")):
            pbar.set_description(f"{k}")
            archive.add(k, arcname=f"{k.relative_to(local_path)}")
    tar_size = Path(tarfile_name).stat().st_size / 10**6
    return tar_size


def endpoint_creation_wait(endpoint_name: str):
    """
    Waiting for the endpoint to finish creation
    """
    describe_endpoint_response = sm_client.describe_endpoint(EndpointName=endpoint_name)

    while describe_endpoint_response["EndpointStatus"] == "Creating":
        describe_endpoint_response = sm_client.describe_endpoint(EndpointName=endpoint_name)
        print(describe_endpoint_response["EndpointStatus"])
        time.sleep(15)

    return describe_endpoint_response
