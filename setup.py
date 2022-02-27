
import setuptools
 
setuptools.setup(
    name="sqs_idempotency",
    version="0.0.1",
    author="aokuyama",
    author_email="mail@aokuyama.work",
    description="AWS SQS \'s idempotency wrapper",
    long_description="AWS SQS \'s idempotency wrapper",
    long_description_content_type="text/markdown",
    url="https://web.aokuyama.work",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
