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

起動したDockerコンテナに入り、 (/srcに入ります)アプリケーションサーバーを起動

```sh
$ docker-compose exec flask bash
$ python run_app.py
```

アプリケーションサーバーは [http://localhost:5000](http://localhost:5000)　で起動します

Here are a few screenshots

1. Posting some content

![image.png](https://github.com/satwikkansal/python_blockchain_app/raw/master/screenshots/1.png)

2. Requesting the node to mine

![image.png](https://github.com/satwikkansal/python_blockchain_app/raw/master/screenshots/2.png)

3. Resyncing with the chain for updated data

![image.png](https://github.com/satwikkansal/python_blockchain_app/raw/master/screenshots/3.png)

To play around by spinning off multiple custom nodes, use the `register_with/` endpoint to register a new node. 

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
```
