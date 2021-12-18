from setuptools import find_packages, setup

setup(
    name='flaskr',
    version='1.0.0',
    packages=find_packages(),   # package告诉 Python 包所包括的文件夹（及其所包含的 Python 文件）
                                # find_packages() 自动查找
    include_package_data=True,  # 为了包含其他文件夹，如静态文件和模板文件所在的文件夹
    zip_safe=False,
    install_requires=[
        'flask',
    ],
)