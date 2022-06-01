a = ["backports.functools-lru-cache==1.6.4","beautifulsoup4==4.9.3","certifi==2021.10.8","chardet==4.0.0","idna==2.10","Paste==3.5.0","requests==2.27.1","six==1.16.0","soupsieve==1.9.6","urllib3==1.26.9","webapp2==2.5.2","WebOb==1.8.7"]
for i in a:
    name, version = i.split("==")
    print("- name: "+name)
    print("  version: "+version)
    print("")
