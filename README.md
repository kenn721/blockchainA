# BlockChain 課題A

クローン元のファイル [https://github.com/satwikkansal/python_blockchain_app](https://github.com/satwikkansal/python_blockchain_app)

## Instructions to run (Mac環境で確認済み)

クローンするかzipファイルをダウンロードし、/blockchainAに入る

```sh
$ git clone git@github.com:kenn721/blockchainA.git
$ cd blockchainA
```

Docker環境の構築(Docker for Macの準備が必要　[参考](https://docs.docker.jp/docker-for-mac/install.html))

開発サーバーでしかないので、取引データ、マイニングなどはサーバーをストップするたびにリセットされる

```sh
$ docker-compose build
```

Dockerを起動して、blockchain node serverを開始する, 
```sh
$ docker-compose up -d
``` 

blockchain node serverは port 8000に起動する

起動したDockerコンテナに入り、 ユーザーデータのデータベースを作成し、アプリケーションサーバーを起動

```sh
$ docker-compose exec flask bash
$ python manage.py init_db
$ python run_app.py
```

アプリケーションサーバーは [http://localhost:5000](http://localhost:5000)　で起動します

ER図
![image.png](https://github.com/kenn721/blockchainA/tree/master/screenshots/ER図.png)

Here are a few screenshots

1. 非ログイン時ホーム

![image.png](https://github.com/kenn721/blockchainA/tree/master/screenshots/1.png)
投稿一覧は見れるが回答はできない、投稿することもできない
ログイン、サインアップができる

2. ログイン、サインアップ

![image.png](https://github.com/kenn721/blockchainA/tree/master/screenshots/2.png)
ユーザーネーム、パスワードでログイン
サインアップ時はユーザーネームがすでにいるユーザーとかぶらないようにする

3. ログイン後

![image.png](https://github.com/kenn721/blockchainA/tree/master/screenshots/3.png)
投稿一覧が見れる、解答を追加することができる、投稿をすることができる
マイニング、ブロックチェーンとの同期を行える
マイニングをクリックするとこれまでの取引データが保存され、同期するとブロックチェーンの最新状態が反映される

4.　投稿、マイニング、同期

![image.png](https://github.com/kenn721/blockchainA/tree/master/screenshots/4.png)
投稿した後、request to mine を押すと上記画面へ遷移する
この後resyncを押すと最新状況にアップデートされる

5.　解答追加

![image.png](https://github.com/kenn721/blockchainA/tree/master/screenshots/5.png)
質問に対しての解答ファイルを追加、送信する→ブロックチェーンに追加されるトランザクションデータになる

6.ユーザーページ

![image.png](https://github.com/kenn721/blockchainA/tree/master/screenshots/6.png)
過去の質問投稿履歴、解答の履歴とそれに対しての評価の履歴が追加される

<!-- To play around by spinning off multiple custom nodes, use the `register_with/` endpoint to register a new node. 

Here's a sample scenario that you might wanna try,

```sh
# Make sure you set the FLASK_APP environment variable to node_server.py before running these nodes
# already running
$ flask run --port 8000 &
# spinning up new nodes
$ flask run --port 8001 &
$ flask run --port 8002 &
```

You can use the following cURL requests to register the nodes at port `8001` and `8002` with the already running `8000`.

```sh
curl -X POST \
  http://127.0.0.1:8001/register_with \
  -H 'Content-Type: application/json' \
  -d '{"node_address": "http://127.0.0.1:8000"}'
```

```sh
curl -X POST \
  http://127.0.0.1:8002/register_with \
  -H 'Content-Type: application/json' \
  -d '{"node_address": "http://127.0.0.1:8000"}'
```

This will make the node at port 8000 aware of the nodes at port 8001 and 8002, and make the newer nodes sync the chain with the node 8000, so that they are able to actively participate in the mining process post registration.

To update the node with which the frontend application syncs (default is localhost port 8000), change `CONNECTED_NODE_ADDRESS` field in the [views.py](/app/views.py) file.

Once you do all this, you can run the application, create transactions (post messages via the web inteface), and once you mine the transactions, all the nodes in the network will update the chain. The chain of the nodes can also be inspected by inovking `/chain` endpoint using cURL.

```sh
$ curl -X GET http://localhost:8001/chain
$ curl -X GET http://localhost:8002/chain
``` -->
