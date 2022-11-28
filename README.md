# CircleCI

## Table of contents
- [持續整合](#持續整合)
  * [建立專案](#建立專案)
  * [上傳至 Github](#上傳至-Github)
  * [建立 CircleCI 專案](#建立-CircleCI-專案)
- [建立部署環境（Elastic Beanstalk）](#建立部署環境)
  * [申請 access key 及 secret key](#申請-access-key-及-secret-key)
  * [在本地端設定 Elastic Beanstalk](#在本地端設定-Elastic-Beanstalk)
- [持續部署（CircleCI+EB）](#持續部署)
  * [在 CircleCI 中新增環境變數](#在-CircleCI-中新增環境變數)
  * [修改本機端的專案](#修改本機端的專案)
- [參考資料](#參考資料)

## 持續整合
### 建立專案
1. 建立一個專案資料夾叫 `python_circleci`，可以手動建立或執行以下：
    `mkdir python_circleci` 

2. 在 `python_circleci/` 路徑底下建立 `application.py` 主程式。
    ```python
    # application.py
    from flask import Flask
    application = Flask(__name__) # EB looks for an 'application' callable by default.

    @application.route('/', methods=['GET'])
    def home():
        return "Hello World!"

    def init_api():
        application.run(debug=False, use_reloader=False)

    if __name__ == '__main__':
        init_api()
    ```
      > 透過 `python application.py` 來開啟 http://127.0.0.1:5000，看見 Hello World! 表示成功。
    
3. 在 `python_circleci/` 路徑底下建立 `test_application.py` 測試程式。
	```python
	# test_application.py
	import requests
	import application # 這邊是主程式的 py 檔名
	import pytest
	from threading import Thread

	@pytest.fixture(scope="module", autouse=True)
	def setup():
		# Start running mock server in a separate thread.
		# Daemon threads automatically shut down when the main process exits.
		mock_server_thread = Thread(target=application.init_api)
		mock_server_thread.setDaemon(True)
		mock_server_thread.start()

	def test_index():
		# requests http://127.0.0.1:5000/ 的 status_code 要是 200
		rtn = requests.get(url='http://127.0.0.1:5000/')
		print(f'status code: {rtn.status_code}')
		assert rtn.status_code == 200
	```
    > 透過 `pytest -s test_application.py` 來測試，看見類似 === 1 passed in 0.24s === 的樣子，表示成功。

### 上傳至 Github

1. 建立 `.gitignore`，可手動建立或輸入 `touch .gitignore` ，加入不必上傳的檔案，如下：

	```txt
	.pytest_cache
	.DS_Store
	__pycache__
	```

2. 建立 `requirements.txt`，加入專案會需要用到的套件。

	```txt
	Flask==2.2.2
	pytest==7.1.1
	```
	
3. 至 https://github.com/new 建立新的 Repo。

	![](https://i.imgur.com/GNQBTXq.png)

4. 依序輸入以下指令來上傳至 Github。
	- `git init `
	- `git add .`
	- `git commit -m "first commit" `
	- `git branch -M main `
	- `git remote add origin https://github.com/tzuying0312/python_circleci.git`
	- `git push -u origin main`

### 建立 CircleCI 專案
1. 至官網註冊帳號 https://circleci.com/ ，並連結 Github 的專案。

    ![](https://i.imgur.com/e3s9aLz.png)

2. 由於尚未建立 `cofig.yml`，因此先選第三個。

    <img src="https://i.imgur.com/R3mWUYt.png" alt="Graph" width="55%"/>


3. 選擇 Python。

    ![](https://i.imgur.com/BgGaWgL.png)

4. 會挑出預設的 yml，以此來改寫某些地方，這邊只要修正第 13 行，將原先的 `pytest` 改成 `pytest test_application.py`，就是執行我們測試程式。

	```yml
		steps:
		  # 第一步
		  - checkout
		  # 第二步安裝環境
		  - python/install-packages:
			  pkg-manager: pip
			  # app-dir: ~/project/package-directory/  # If you're requirements.txt isn't in the root directory.
			  # pip-dependency-file: test-requirements.txt  # if you have a different name for your requirements file, maybe one that combines your runtime and test requirements.
		  # 第三步執行 flask 的測試
		  - run:
			  name: Run tests
			  # This assumes pytest is installed via the install-package step above
			  command: pytest test_application.py
	```

5. 完成後按 `Commit and Run`。
	
	![](https://i.imgur.com/Zzwtj6f.png)

6. 可以從 `Dashbord` 來看每個運行的結果。

	![](https://i.imgur.com/13MIl38.png)

7. 也可以點擊單一的 Status 來查看該運行的錯誤原因，或執行的情況。
	
	![](https://i.imgur.com/QOpelEQ.png)

8. 回到 Github 會發現多了一個 branch 叫 `circleci-project-setup`。
	
	![](https://i.imgur.com/3CPvucf.png)

9. 如果想要合併分支，就回終端機依序執行以下：
	- `git pull` 把新的 branch 抓下來
	- `git merge origin/circleci-project-setup` 合併分支
	- `git push` 推送至 github

10. 可以發現在第 7 步驟再次 push 時，CircleCI 也會幫我們自動運行，同時也可以看到這次的 branch 是 main。

	![](https://i.imgur.com/qlJf5Ia.png)

## 建立部署環境
### 申請 access key 及 secret key
1. 至 https://aws.amazon.com/tw/?nc2=h_lg 註冊或登入
2. 在左上搜尋的地方打上 `IAM` 搜尋，點擊第一個
	
	![](https://i.imgur.com/n5Kllfr.png)

3. `使用者 > 新增使用者`

	![](https://i.imgur.com/ywi7gZL.png)

4. 輸入`使用者名稱`和勾選`存取金鑰`，完成後點擊`下一個：許可`

	![](https://i.imgur.com/zZg8Spi.png)


5. `直接連結現有政策` > 搜尋以下 3 個 > 勾選並勾選起來 > `下一個：標籤`

	- `AWSElasticBeanstalkManagedUpdatesCustomerRolePolicy`
	- `AWSCodeCommitFullAccess`
	- `AdministratorAccess-AWSElasticBeanstalk`

	![](https://i.imgur.com/vt1t088.png)

6. 點`下一個：檢閱`

	![](https://i.imgur.com/qFM6KiZ.png)

7. 點`建立使用者`

	![](https://i.imgur.com/WsQYxjG.png)


8. 完成後，獲得 `Access key ID` 和 `Secret Access key`，將兩個記下來

	![](https://i.imgur.com/B2iu46y.png)

### 在本地端設定 Elastic Beanstalk
1. 首先要先安裝 AWS 的 command line tool
	- `pip install awscli`  安裝 awscli
	- `aws --version` 確認版本

2. 接著建立憑證，讓我們可以從本機的終端機來對 AWS 做操作
	- `aws configure` # 建立憑證
	- 會說要輸入 `Access key ID` 和 `Secret Access key `，輸入剛剛記錄下來的
	
	![](https://i.imgur.com/txNxP2E.png)

3. 建立 Elastic Beanstalk 環境，此步驟完成後會發現多了 `.elasticbeanstalk/` 的資料夾
	- `cd Desktop/DevOps/python_circleci/` 切換到專案路徑底下
	- `eb init` 建立一個環境依序設定或直接輸入下列建立
	- `eb init -p python-3.7 python_circleci --region us-east-2`
	
		![](https://i.imgur.com/0RPPQCa.png)

	- 
      <details>
        <summary>出現 zsh: command not found: eb</summary>
          至 https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/eb-cli3-install-osx.html 查看怎麼安裝。Mac 可直接用 Homebrew：

          brew install awsebcli
          eb --version 確認是否成功
      </details>

	- `eb create env-dev` 建立測試環境叫 env-dev

		![](https://i.imgur.com/by7XNHb.png)

		
4. 除了終端機外，也可以在 AWS 左上角搜尋 `Elastic Beanstalk`，點第一個進入查看
	
	![](https://i.imgur.com/2nZGAxk.png)

5.  右上角 Regions 清單中選取剛剛建立 AWS 區域 （us-east-2）> `環境` > `env-dev` 來查看，確認是否正在建立

	![](https://i.imgur.com/Cw6GNlJ.png)

6. 完成後，將本機的程式碼部署到 aws
	
	`eb deploy`

	![](https://i.imgur.com/NdZtFZa.png)
    
	![](https://i.imgur.com/dhmcyyF.png)

7. 開啟瀏覽器，看到 `Hello World!` 就表示已成功將本地的 code 成功部署至 EB

	`eb open`
	
    ![](https://i.imgur.com/TMR8USB.png)


## 持續部署
### 在 CircleCI 中新增環境變數

1. `Project` > `...` > `Project Settings`
	
	![](https://i.imgur.com/U1pMBxr.png)

2. `Environment Variables` > `Add Environment Variable`

	![](https://i.imgur.com/7HvjX82.png)

3. 增加 `AWS_REGION`, `AWS_ACCESS_KEY` 和 `AWS_SECRET_KEY`

	![](https://i.imgur.com/xUXJJ56.png)

### 修改本機端的專案
1. 新開一個 branch
	
	`git checkout -b deploy-to-eb`

2. 在 .gitignore 中加入 `!.elasticbeanstalk/config.yml`，表示不能 ignore 該檔案

	```
	# .gitignore
	.pytest_cache
	.DS_Store
	__pycache__
	# Elastic Beanstalk Files
	.elasticbeanstalk/*
	!.elasticbeanstalk/*.cfg.yml
	!.elasticbeanstalk/*.global.yml
	!.elasticbeanstalk/config.yml
	```

3. 在 requirments.txt 加入 awsebcli，表示要安裝該套件

	```
	# requirments.txt
	Flask==2.2.2
	pytest==7.1.1
	requests==2.27.1
	awsebcli
	```

4. 修改 `.circleci/config.yml`

	```yml
    version: 2.1
    orbs:
      python: circleci/python@1.5.0
      aws-cli: circleci/aws-cli@2.0.6

    jobs:
      build-and-test: 
        docker:
          - image: cimg/python:3.10.2
        steps:
          - checkout
          - python/install-packages:
              pkg-manager: pip
          - run:
              name: Run tests
              command:
                pytest test_application.py 

      aws-deploy: 
        executor: aws-cli/default
        steps:
          - run:
              name: Making AWS profile # 建立 aws config/credentials
              command: |
                mkdir  ~/.aws
                echo -e "[default]\n" > ~/.aws/config
                echo -e "[default]\naws_access_key_id=$AWS_ACCESS_KEY\naws_secret_access_key=$AWS_SECRET_KEY\n" > ~/.aws/credentials

          - run:
              name: Installing deployment dependencies # 安裝 awsebcli
              working_directory: /
              command: |
                sudo apt-get -y -qq update
                sudo apt-get install python3-pip python3-dev build-essential
                sudo pip3 install awsebcli
          - run:
              name: Deploying # git clone 專案並 deploy EB
              command: |
                git clone https://github.com/tzuying0312/python_circleci.git
                cd python_circleci
                git checkout deploy-to-eb
                eb deploy env-dev

    workflows:
      sample: 
        jobs:
          - build-and-test
          - aws-deploy:
              filters:
                branches: # 表示只在 branch 是 deploy-to-eb 時執行 commands
                  only:
                    - deploy-to-eb

	```

5. Push 到 Github
	- `git add . `
	- `git commit -m "setting env-dev circleci"`
	- `git push --set-upstream origin deploy-to-eb`


6. 至 CircleCI 和 AWS EB 中查看是否成功
	- CircleCI Success

		![](https://i.imgur.com/Nviobi0.png)
		
	- AWS EB 最後修改的時間是剛剛 push 的時間
	
		![](https://i.imgur.com/fdfZ22n.png)


7. 試著改寫 `application.py` 看是否 push 完後 AWS EB 也自動部署成功，譬如改成 `Hello World! 11/28`

	``` python=
	from flask import Flask
	application = Flask(__name__)

	@application.route('/', methods=['GET'])
	def home():
		return "Hello World! 11/28"

	def init_api():
		application.run(debug=False, use_reloader=False)

	if __name__ == '__main__':
		init_api()
	```

8. 完成！

    ![](https://i.imgur.com/H9bk1EZ.png)


## 參考資料
- [[Python] Create an API with Flask and test with pytest](https://jerryeml.coderbridge.io/2021/07/11/Create-an-API-with-Flask-and-test-with-pytest/)
- [超新手的一日CI/CD初體驗，使用CircleCi、Github-Flow自動部署Node.JS於AWS Elastic Beanstalk](https://medium.com/@paulchen_9650/%E8%B6%85%E6%96%B0%E6%89%8B%E7%9A%84%E4%B8%80%E6%97%A5ci-cd%E5%88%9D%E9%AB%94%E9%A9%97-%E4%BD%BF%E7%94%A8circleci-github-flow%E8%87%AA%E5%8B%95%E9%83%A8%E7%BD%B2node-js%E6%96%BCaws-elastic-beanstalk-e7af3a65ae61)
- [將 Flask 應用程式部署至 Elastic Beanstalk](https://docs.aws.amazon.com/zh_tw/elasticbeanstalk/latest/dg/create-deploy-python-flask.html)
- [Configure AWS Credentials in Circle CI](https://medium.com/geekculture/configure-aws-credentials-in-circle-ci-8353d765aa15)
- [Deploying to Elastic Beanstalk via CircleCi 2.0](https://gist.github.com/ryansimms/808214137d219be649e010a07af44bad)


###### tags: `DevOps`