from setuptools import setup, find_packages

setup(
    name="facemesh-server",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        "opencv-python>=4.5.3",
        "mediapipe>=0.8.9",
        "numpy>=1.21.0",
        "python-multipart>=0.0.5",
        "python-dotenv>=0.19.0",
        "pydantic-settings>=2.0.0",
    ]
)